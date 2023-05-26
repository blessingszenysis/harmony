#!/usr/bin/env python
import math
import os
import re
import sys

import pandas as pd
from pylib.base.flags import Flags

from config.br_covid.datatypes import Dimension
from log import LOG
from pipeline.brazil_covid.bin.shared.convert_cid_csv import (
    GROUP_COL,
    ID_COL as ANOMALY_CODE,
)
from pipeline.brazil_covid.bin.shared.datasus_common import (
    MOTHER_OCCUPATION_COLUMNS_RENAME,
    NOT_APPLICABLE,
    INCONSISTENT_DATA,
    clean_and_replace_occupation_column,
    convert_numerical_column,
)
from pipeline.brazil_covid.bin.shared.convert_occupation_codes import (
    CODE_COLUMN as OCCUPATION_CODE_COLUMN,
)
from pipeline.brazil_covid.bin.sinasc.sinasc_mappings import (
    INPUT_BIRTH_TIME_HOURS_COLUMN,
    INPUT_DATE_COLUMN,
    INPUT_MOTHER_OCCUPATION_COLUMN,
    SINASC_COLUMN_MANAGER,
)

from util.file.compression.lz4 import LZ4Reader, LZ4Writer
from util.file.file_config import FilePattern

# pylint: disable=no-member

# Only read in 5 million lines at a time.
LINE_THRESHOLD = 5000000


def create_multivalue_anomaly_codes(
    df: pd.DataFrame, anomaly_code_df: pd.DataFrame
) -> pd.DataFrame:
    # Convert the anomaly codes to a multi-value dimension. There are max 5 codes that
    # can be in the anomaly codes column, so split that into 5 columns for process_csv.
    LOG.info('Processing the anomaly codes')
    multivalue_anomaly_codes = pd.DataFrame(
        df[Dimension.CODIGO_ANOMALIA].str.findall(r'[A-Z]\d{2,3}').values.tolist()
    )
    if len(multivalue_anomaly_codes.columns) > 5:
        LOG.error(
            'Unexpected anomaly code columns detected. Expected max 5 and saw %s',
            len(multivalue_anomaly_codes.columns),
        )
    # The code below expects 5 columns, so fill in any that weren't created.
    for col in range(len(multivalue_anomaly_codes.columns), 5):
        multivalue_anomaly_codes[col] = None

    number_bad_codes = 0
    bad_codes = set()
    known_codes = set(anomaly_code_df.index)
    number_missing_codes = 0
    missing_codes = set()
    for col in multivalue_anomaly_codes.columns:
        valid_codes_filter = multivalue_anomaly_codes[col].str.startswith('Q') | (
            multivalue_anomaly_codes[col].str.startswith('D18')
        )
        invalid_codes_filter = (
            ~multivalue_anomaly_codes[col].isna() & ~valid_codes_filter
        )
        number_bad_codes += sum(invalid_codes_filter)
        bad_codes.update(multivalue_anomaly_codes.loc[invalid_codes_filter, col])
        column_name = f'CodigoAnomaliaMultiValue{col}'
        df[column_name] = multivalue_anomaly_codes.loc[
            valid_codes_filter,
            col,
        ]
        df.loc[invalid_codes_filter, column_name] = INCONSISTENT_DATA

        # Track any codes that aren't present in anomaly_code_df
        _missing_codes = df[
            ~df[column_name].isna()
            & ~invalid_codes_filter
            & ~df[column_name].isin(known_codes)
        ][column_name]
        number_missing_codes += len(_missing_codes)
        missing_codes.update(_missing_codes)

        # Merge in the code group information
        df = df.merge(
            anomaly_code_df[[GROUP_COL, Dimension.CODIGO_ANOMALIA_PRIORITY]],
            left_on=column_name,
            right_index=True,
            how='left',
        ).rename(
            columns={
                GROUP_COL: f'{column_name}_group',
                Dimension.CODIGO_ANOMALIA_PRIORITY: f'{column_name}_priority',
            }
        )

    if number_bad_codes > 0:
        LOG.info(
            '%s bad anomaly codes were dropped: %s',
            number_bad_codes,
            ', '.join(bad_codes),
        )
    if number_missing_codes > 0:
        LOG.info('Unmatched CID IDs: %s', ', '.join(missing_codes))

    LOG.info('Finished processing the anomaly codes')
    return df


def process_dataframe(
    df: pd.DataFrame,
    anomaly_code_df: pd.DataFrame,
    occupation_df: pd.DataFrame,
    output_file_name: str,
) -> None:
    input_rows = len(df)
    LOG.info('Number of rows in input: %s', input_rows)

    # Add any columns that might be missing, but expected
    df = df.reindex(
        df.columns.union(SINASC_COLUMN_MANAGER.get_required_columns(), sort=False),
        axis=1,
        fill_value='',
    )

    LOG.info('Beginning date parsing')
    # After 1996, the date column is `DTOBITO` and typically the format is ddmmyyyy.
    df['date'] = pd.to_datetime(
        df.loc[df[INPUT_DATE_COLUMN] != '', INPUT_DATE_COLUMN],
        format='%d%m%Y',
        errors='coerce',
    )
    # If it wasn't in that format, then it was in ?mmyyyy, so assign those to the first of
    # the month.
    row_index = (df[INPUT_DATE_COLUMN] != '') & df['date'].isna()
    df.loc[row_index, 'date'] = pd.to_datetime(
        df.loc[row_index, INPUT_DATE_COLUMN].str[-6:],
        format='%m%Y',
        errors='coerce',
    )
    # If it wasn't in that format, then it was in ?yyyy, so assign those to the first of
    # the year.
    row_index = (df[INPUT_DATE_COLUMN] != '') & df['date'].isna()
    df.loc[row_index, 'date'] = pd.to_datetime(
        df.loc[row_index, INPUT_DATE_COLUMN].str[-4:],
        format='%Y',
        errors='coerce',
    )
    LOG.info('Finished date parsing')

    LOG.info('Starting remapping column values to human readable strings')
    for column_name, mapping_values in SINASC_COLUMN_MANAGER.get_mappings().items():
        df[column_name] = df[column_name].apply(
            lambda x, m=mapping_values: m[x] if x in m else INCONSISTENT_DATA
        )

    # Convert Birth Time in Hours column to HH:MM
    def clean_birth_time(birth_time: str) -> str:
        if birth_time.isnumeric():
            return f'{birth_time[:2]}:{birth_time[2:]}'
        return ':'.join(re.split(r'[^0-9]', birth_time)[:2])

    df[INPUT_BIRTH_TIME_HOURS_COLUMN] = df[INPUT_BIRTH_TIME_HOURS_COLUMN].apply(
        clean_birth_time
    )

    # Convert numerical columns
    for column in SINASC_COLUMN_MANAGER.get_numeric_columns():
        df = convert_numerical_column(df, column)
    LOG.info('Finished remapping column values')

    LOG.info('Starting processing occupation columns')
    df = clean_and_replace_occupation_column(
        df,
        occupation_df.rename(columns=MOTHER_OCCUPATION_COLUMNS_RENAME),
        INPUT_MOTHER_OCCUPATION_COLUMN,
        list(MOTHER_OCCUPATION_COLUMNS_RENAME.values()),
    )
    LOG.info('Finished processing occupation columns')

    LOG.info('Building numeric field columns')
    # Build a unique numeric field for each dimension value in all the columns that we care
    # about. This will allow the user to query for a specific value without grouping.
    for column, dimension_mapping in SINASC_COLUMN_MANAGER.get_fields().items():
        for dimension_value in dimension_mapping.values():
            # If there is no value for this dimension in the dataframe, we don't need to
            # create a field for it.
            if not dimension_value:
                continue

            field_name = f'*field_{column} - {dimension_value}'  # 'ESCMAE2010 - Sem escolaridade'
            df_row_filter = (
                df[column] == dimension_value
            )  # df['ESCMAE2010'] == 'Sem escolaridade'

            # Initialize the field to na since all rows that do not match the dimension value
            # should not have a field value.
            df[field_name] = pd.NA

            # Set all rows that match the filter to 1.
            df.loc[df_row_filter, field_name] = 1

    LOG.info('Finished building numeric field columns')

    LOG.info('Renaming columns')
    df = df.rename(columns=SINASC_COLUMN_MANAGER.get_renaming_mapping())
    LOG.info('Finished renaming columns')

    LOG.info('Special processing')
    # Create the Dimension.ANOMALIA_MULTIPLA column
    df[Dimension.ANOMALIA_MULTIPLA] = NOT_APPLICABLE
    df.loc[
        df[Dimension.CODIGO_ANOMALIA].str.len() == 4, Dimension.ANOMALIA_MULTIPLA
    ] = 'Não'
    df.loc[
        df[Dimension.CODIGO_ANOMALIA].str.len() > 4, Dimension.ANOMALIA_MULTIPLA
    ] = 'Sim'

    df = create_multivalue_anomaly_codes(df, anomaly_code_df)

    def make_grouped_columns(df, col_name, group_col_name, buckets):
        df[group_col_name] = df[col_name]
        for bucket in buckets:
            lower, upper, group_val = bucket
            df.loc[
                df[col_name].apply(
                    lambda x, l=lower, u=upper: x.isdigit() and l <= int(x) <= u
                ),
                group_col_name,
            ] = group_val

        return df

    # Create the Dimension.MOTHERS_AGE_GROUPED column
    mothers_age_buckets = [
        [10, 14, '10 a 14 anos'],
        [15, 19, '15 a 19 anos'],
        [20, 34, '20 a 34 anos'],
        [35, math.inf, '35 anos ou mais'],
    ]
    df = make_grouped_columns(
        df, Dimension.MOTHERS_AGE, Dimension.MOTHERS_AGE_GROUPED, mothers_age_buckets
    )

    # Create the Dimension.NUMBER_DECEASED_CHILDREN_GROUPED column
    num_deceased_children_buckets = [
        [0, 0, '0'],
        [1, 1, '1'],
        [2, math.inf, '>=2'],
    ]
    df = make_grouped_columns(
        df,
        Dimension.NUMBER_DECEASED_CHILDREN,
        Dimension.NUMBER_DECEASED_CHILDREN_GROUPED,
        num_deceased_children_buckets,
    )

    # Create the Dimension.BIRTH_WEIGHT_GRAMS_GROUPED column
    birth_weight_grams_buckets = [
        [-math.inf, 500, '<500'],
        [500, 999, '>=500 a <=999'],
        [1000, 1499, '>=1000 a <=1499'],
        [1500, 2499, '>=1500 a <=2499'],
        [2500, math.inf, '>=2500'],
    ]
    df = make_grouped_columns(
        df,
        Dimension.BIRTH_WEIGHT_GRAMS,
        Dimension.BIRTH_WEIGHT_GRAMS_GROUPED,
        birth_weight_grams_buckets,
    )

    # Create the Dimension.APGAR_1_GROUPED column
    apgar_1_buckets = [
        [-math.inf, 6, 'Baixo (<7)'],
        [7, math.inf, 'Normal (>=7)'],
    ]
    df = make_grouped_columns(
        df, Dimension.APGAR_1, Dimension.APGAR_1_GROUPED, apgar_1_buckets
    )

    # Create the Dimension.APGAR_5_GROUPED column
    apgar_5_buckets = [
        [-math.inf, 6, 'Baixo (<7)'],
        [7, math.inf, 'Normal (>=7)'],
    ]
    df = make_grouped_columns(
        df, Dimension.APGAR_5, Dimension.APGAR_5_GROUPED, apgar_5_buckets
    )

    assert len(df) == input_rows, (
        'Number of rows post-processing does not match the initial number of rows. '
        f'Initial rows: {input_rows}. Final rows: {len(df)}'
    )

    LOG.info('Writing the output CSV %s', os.path.basename(output_file_name))
    # Since these are large files, use high compression
    with LZ4Writer(output_file_name, level=9) as output_file:
        df.to_csv(output_file, index=False)
    LOG.info('Finished writing output CSV')


def main():
    Flags.PARSER.add_argument(
        '--input_folder',
        type=str,
        required=True,
        help='Input folder with years of raw SIM files to convert',
    )
    Flags.PARSER.add_argument(
        '--output_file_pattern', type=str, required=True, help='Converted file location'
    )
    Flags.PARSER.add_argument(
        '--anomaly_codes_csv',
        type=str,
        required=True,
        help='File path for anomaly codes lookup',
    )
    Flags.PARSER.add_argument(
        '--occupation_codes_csv',
        type=str,
        required=True,
        help='File path for occupation codes lookup',
    )
    Flags.InitArgs()

    output_file_pattern = FilePattern(Flags.ARGS.output_file_pattern)

    LOG.info('Starting anomaly codes load')
    anomaly_code_df = pd.read_csv(
        Flags.ARGS.anomaly_codes_csv, dtype=str, keep_default_na=False
    )
    anomaly_code_df.set_index(ANOMALY_CODE, inplace=True)
    LOG.info(anomaly_code_df.head(10))

    LOG.info('Starting occupation load')
    occupation_df = pd.read_csv(
        Flags.ARGS.occupation_codes_csv, dtype=str, keep_default_na=False
    )
    occupation_df.set_index(OCCUPATION_CODE_COLUMN, inplace=True)
    LOG.info(occupation_df.head(10))

    LOG.info('Reading in input files into dataframe')
    df = pd.DataFrame()
    total_file_line_counter = 0
    count = 0
    for input_file_name in os.listdir(Flags.ARGS.input_folder):
        # There are other files in the feed durectory, filter to just data files.
        if input_file_name.endswith('.csv.lz4'):
            LOG.info('Processing file %s', input_file_name)
            file_name = os.path.join(Flags.ARGS.input_folder, input_file_name)

            with LZ4Reader(file_name) as input_file:
                input_df = pd.read_csv(
                    input_file,
                    sep=';',
                    dtype=str,
                    keep_default_na=False,
                    usecols=lambda col: col
                    in SINASC_COLUMN_MANAGER.get_input_columns(),
                )
            assert len(input_df) > 0, f'Input file {input_file_name} has no rows'

            # Check the number of lines after the file has already been read in
            # so the file doesn't need to be read in twice.
            if total_file_line_counter + len(input_df) > LINE_THRESHOLD:
                LOG.info('Processing previous data and creating new dataframe')
                # Process the current dataframe
                process_dataframe(
                    df,
                    anomaly_code_df,
                    occupation_df,
                    output_file_pattern.build(f'{count:02d}'),
                )
                # Create a new data frame
                total_file_line_counter = 0
                count += 1
                df = pd.DataFrame()
                LOG.info('Reading in input files into dataframe')

            # Add fillna here to account for earlier years where the missing
            # columns would be added as na.
            df = pd.concat([df, input_df], ignore_index=True).fillna('')
            total_file_line_counter += len(input_df)
    LOG.info('Finished reading input files')

    if len(df) > 0:
        LOG.info('Processing final dataframe')
        process_dataframe(
            df,
            anomaly_code_df,
            occupation_df,
            output_file_pattern.build(f'{count:02d}'),
        )

    return 0


if __name__ == '__main__':
    sys.exit(main())
