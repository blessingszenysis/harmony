#!/usr/bin/env python
import math
import os
import sys
from typing import Optional

import pandas as pd

from pylib.base.flags import Flags

from config.br_covid.datatypes import Dimension
from log import LOG
from pipeline.brazil_covid.bin.shared.convert_cid_csv import (
    ID_COL as CAUSE_OF_DEATH_CODE,
)
from pipeline.brazil_covid.bin.shared.convert_occupation_codes import (
    CODE_COLUMN as OCCUPATION_CODE_COLUMN,
)
from pipeline.brazil_covid.bin.shared.datasus_common import (
    INCONSISTENT_DATA,
    MOTHER_OCCUPATION_COLUMNS_RENAME,
    UNKNOWN,
    clean_and_replace_occupation_column,
    convert_numerical_column,
)
from pipeline.brazil_covid.bin.sim.sim_mappings import (
    CAUSE_OF_DEATH_COL_RENAME,
    INPUT_AGE_COLUMN,
    INPUT_CAUSE_OF_DEATH_COLUMN,
    INPUT_DATE_COLUMN_AFTER_1996,
    INPUT_DATE_COLUMN_BEFORE_1996,
    INPUT_DEATH_TYPE_COLUMN,
    INPUT_MOTHER_AGE_COLUMN,
    INPUT_MOTHER_OCCUPATION_COLUMN,
    INPUT_OCCUPATION_COLUMN,
    MOTHER_MORTALITY_OBITOGRAV,
    MOTHER_MORTALITY_OBITOPUERP,
    OCCUPATION_COLUMNS_RENAME,
    SIM_COLUMN_MANAGER,
)
from util.file.compression.lz4 import LZ4Reader, LZ4Writer
from util.file.file_config import FilePattern

# pylint: disable=no-member

# Only read in 5 million lines at a time.
LINE_THRESHOLD = 5000000

OUTPUT_DEATHS_FIELD = '*field_obitos'
OUTPUT_MOTHER_MORTALITY_FIELD = '*field_mother_mortality'


# The first digit of the age value is the unit. Return the age group, which should align
# with the population integration.
def convert_age(age: str, use_infant_groups: Optional[bool] = False) -> str:
    # NOTE(abby): There is a very small number of invalid values, just handle them here.
    if age == '1 d':
        return '0 a 6 dias' if use_infant_groups else '< 1 ano'
    if age == '0':
        # NOTE(abby): This a bad value and the exact age is unknown, so "0 a 6 dias" is a
        # best guess.
        return '0 a 6 dias' if use_infant_groups else '< 1 ano'

    if age != '':
        first_digit = age[0]
        age_number = int(age[1:])

        if first_digit == '0':
            # Minutes
            return '0 a 6 dias' if use_infant_groups else '< 1 ano'
        if first_digit == '1':
            # Hours
            return '0 a 6 dias' if use_infant_groups else '< 1 ano'
        if first_digit == '2':
            # Days
            if not use_infant_groups:
                return '< 1 ano'

            if age_number <= 6:
                return '0 a 6 dias'
            return '7 a 27 dias'
        if first_digit == '3':
            # Months
            if use_infant_groups and age_number == 0:
                # NOTE(abby): This a bad value and the exact age is unknown, so
                # "7 a 27 dias" is a best guess.
                return '7 a 27 dias'
            return '28 dias a menos de 1 ano' if use_infant_groups else '< 1 ano'
        if first_digit == '4':
            # Years
            if age_number >= 80:
                return '80 anos e mais'

            if age_number == 0:
                # NOTE(abby): This a bad value and the exact age is unknown, so
                # "28 dias a menos de 1 ano" is a best guess.
                return '28 dias a menos de 1 ano' if use_infant_groups else '< 1 ano'
            if age_number < 5:
                return '1 a 4 anos'

            age_group = math.floor(age_number / 5) * 5
            return f'{age_group} a {age_group+4} anos'
        if first_digit == '5':
            # 100+ years
            return '80 anos e mais'

    return 's/informação'


# For just fetal deaths, if mother's age > 65 then set to inconsistent data
def convert_mothers_age(df: pd.DataFrame) -> pd.DataFrame:
    numeric_mothers_age = pd.to_numeric(df[INPUT_MOTHER_AGE_COLUMN], errors='coerce')
    # pylint: disable=invalid-unary-operand-type
    applicable_rows = ~numeric_mothers_age.isna()

    df.loc[
        applicable_rows
        & (df[INPUT_DEATH_TYPE_COLUMN] == 'Fetal')
        & (numeric_mothers_age > 65),
        INPUT_MOTHER_AGE_COLUMN,
    ] = INCONSISTENT_DATA

    return df


def process_cause_of_death(
    df: pd.DataFrame, cause_of_death_df: pd.DataFrame
) -> pd.DataFrame:
    LOG.info('Processing cause of death column %s', INPUT_CAUSE_OF_DEATH_COLUMN)

    # Log any codes that aren't present in cause_of_death_df
    known_codes = set(cause_of_death_df.index)
    unmatched_count = (~df[INPUT_CAUSE_OF_DEATH_COLUMN].isin(known_codes)).sum()
    if unmatched_count > 0:
        unique_missing_codes = df[~df[INPUT_CAUSE_OF_DEATH_COLUMN].isin(known_codes)][
            INPUT_CAUSE_OF_DEATH_COLUMN
        ].unique()
        LOG.info(
            'Remaining rows with unmatched CID IDs: %s',
            ', '.join(unique_missing_codes),
        )

    df = df.merge(
        cause_of_death_df,
        left_on=INPUT_CAUSE_OF_DEATH_COLUMN,
        right_index=True,
        how='left',
    ).rename(columns=CAUSE_OF_DEATH_COL_RENAME)

    # HACK(abby): B342 is the covid cause of death code. They wanted all dimensions
    # to have a "COVID: " prefix.
    df.loc[
        df[Dimension.PRIMARY_CAUSE_CODE] == 'B342', Dimension.PRIMARY_CAUSE_CODE
    ] = 'COVID: B342'

    return df


def process_dataframe(
    df: pd.DataFrame,
    cause_of_death_df: pd.DataFrame,
    occupation_df: pd.DataFrame,
    output_file_name: str,
) -> None:
    input_rows = len(df)
    LOG.info('Number of rows in input: %s', input_rows)

    # Add any columns that might be missing, but expected
    df = df.reindex(
        df.columns.union(SIM_COLUMN_MANAGER.get_required_columns(), sort=False),
        axis=1,
        fill_value='',
    )

    LOG.info('Beginning date parsing')
    # After 1996, the date column is `DTOBITO` and typically the format is ddmmyyyy.
    df['date'] = pd.to_datetime(
        df.loc[df[INPUT_DATE_COLUMN_AFTER_1996] != '', INPUT_DATE_COLUMN_AFTER_1996],
        format='%d%m%Y',
        errors='coerce',
    )
    # If it wasn't in that format, then it was in ?mmyyyy, so assign those to the first of
    # the month.
    row_index = (df[INPUT_DATE_COLUMN_AFTER_1996] != '') & df['date'].isna()
    df.loc[row_index, 'date'] = pd.to_datetime(
        df.loc[row_index, INPUT_DATE_COLUMN_AFTER_1996].str[-6:],
        format='%m%Y',
        errors='coerce',
    )
    # If it wasn't in that format, then it was in ?yyyy, so assign those to the first of
    # the year.
    row_index = (df[INPUT_DATE_COLUMN_AFTER_1996] != '') & df['date'].isna()
    df.loc[row_index, 'date'] = pd.to_datetime(
        df.loc[row_index, INPUT_DATE_COLUMN_AFTER_1996].str[-4:],
        format='%Y',
        errors='coerce',
    )

    # Before 1996, the date column is `DATAOBITO` and typically the format is yymmdd.
    row_index = (df[INPUT_DATE_COLUMN_BEFORE_1996] != '') & df['date'].isna()
    df.loc[row_index, 'date'] = pd.to_datetime(
        df.loc[row_index, INPUT_DATE_COLUMN_BEFORE_1996],
        format='%y%m%d',
        errors='coerce',
    )
    # If it wasn't in that format, then it was in yymm?, so assign those to the first of
    # the month.
    row_index = (df[INPUT_DATE_COLUMN_BEFORE_1996] != '') & df['date'].isna()
    df.loc[row_index, 'date'] = pd.to_datetime(
        df.loc[row_index, INPUT_DATE_COLUMN_BEFORE_1996].str[:4],
        format='%y%m',
        errors='coerce',
    )
    # If it wasn't in that format, then it was in yy?. Take the first two characters
    # for the year and make it the first of the year.
    row_index = (df[INPUT_DATE_COLUMN_BEFORE_1996] != '') & df['date'].isna()
    df.loc[row_index, 'date'] = pd.to_datetime(
        df.loc[row_index, INPUT_DATE_COLUMN_BEFORE_1996].str[:2],
        format='%y',
        errors='coerce',
    )

    # No rows should have been dropped, but log and filter just in case.
    LOG.info(
        'Number of rows dropped with invalid dates: %s', len(df[df['date'].isna()])
    )
    df = df[~df['date'].isna()].drop(
        columns=[INPUT_DATE_COLUMN_BEFORE_1996, INPUT_DATE_COLUMN_AFTER_1996]
    )
    LOG.info('Finished date parsing')

    LOG.info('Starting remapping column values to human readable strings')
    for column_name, mapping_values in SIM_COLUMN_MANAGER.get_mappings().items():
        df[column_name] = df[column_name].apply(
            lambda x, m=mapping_values: m.get(x, INCONSISTENT_DATA)
        )

    # Bucket age into age groups
    df[Dimension.AGE_GROUP_2] = df[INPUT_AGE_COLUMN].map(convert_age)
    df[Dimension.AGE_GROUP_INFANT_5_YEAR_GROUPS] = df[INPUT_AGE_COLUMN].map(
        lambda x: convert_age(x, use_infant_groups=True)
    )
    # Set the fetal deaths to be 'Fetal'.
    df.loc[df[INPUT_DEATH_TYPE_COLUMN] == 'Fetal', Dimension.AGE_GROUP_2] = 'Fetal'
    df.loc[
        df[INPUT_DEATH_TYPE_COLUMN] == 'Fetal', Dimension.AGE_GROUP_INFANT_5_YEAR_GROUPS
    ] = 'Fetal'

    # Convert numerical columns
    for column in SIM_COLUMN_MANAGER.get_numeric_columns():
        df = convert_numerical_column(df, column)

    # Remove mothers ages that are < 10 (all) or > 65 (just fetal)
    df = convert_mothers_age(df)
    LOG.info('Finished remapping column values')

    LOG.info('Starting processing cause of death')
    df = process_cause_of_death(df, cause_of_death_df)
    LOG.info('Finished processing cause of death')

    LOG.info('Starting processing occupation columns')
    df = clean_and_replace_occupation_column(
        df,
        occupation_df.rename(columns=OCCUPATION_COLUMNS_RENAME),
        INPUT_OCCUPATION_COLUMN,
        list(OCCUPATION_COLUMNS_RENAME.values()),
    )
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
    for column, dimension_mapping in SIM_COLUMN_MANAGER.get_fields().items():
        for dimension_value in dimension_mapping.values():
            # If there is no value for this dimension in the dataframe, we don't need to
            # create a field for it. Also skip it if it's unknown or inconsistent data.
            if (
                not dimension_value
                or dimension_value == UNKNOWN
                or dimension_value == INCONSISTENT_DATA
            ):
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

    # Add a field for all deaths
    df[OUTPUT_DEATHS_FIELD] = 1
    LOG.info('Finished building numeric field columns')

    LOG.info('Renaming columns')
    df = df.rename(columns=SIM_COLUMN_MANAGER.get_renaming_mapping())
    LOG.info('Finished renaming columns')

    # These are steps that require special processing
    LOG.info('Special processing')
    # Build a field for mother mortality deaths. To simplify the logic here, the cause of
    # death conditions are defined in the "mother_mortality.csv" file and applied in the
    # 03_convert_cid step. See that file for info on what A-H means.
    df.loc[
        (df[Dimension.GENDER] == 'Feminino')
        & (
            (df['MotherMortality'] == 'A')
            | (df['MotherMortality'] == 'B')
            | (
                ((df['MotherMortality'] == 'C') | (df['MotherMortality'] == 'D'))
                & (df[MOTHER_MORTALITY_OBITOPUERP] != '2')
            )
            | (
                (df['MotherMortality'] == 'E')
                & (
                    (df[MOTHER_MORTALITY_OBITOPUERP] != '2')
                    | (df[MOTHER_MORTALITY_OBITOPUERP] == '')
                )
            )
            | (
                (
                    (df['MotherMortality'] == 'F')
                    | (df['MotherMortality'] == 'G')
                    | (df['MotherMortality'] == 'H')
                )
                & (
                    (df[MOTHER_MORTALITY_OBITOGRAV] == '1')
                    | (df[MOTHER_MORTALITY_OBITOPUERP] == '1')
                )
            )
        ),
        OUTPUT_MOTHER_MORTALITY_FIELD,
    ] = 1
    LOG.info('Finished special processing')

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
        '--cause_of_death_codes_csv',
        type=str,
        required=True,
        help='File path for cause of death codes to fields',
    )
    Flags.PARSER.add_argument(
        '--occupation_codes_csv',
        type=str,
        required=True,
        help='File path for occupation codes lookup',
    )
    Flags.InitArgs()

    output_file_pattern = FilePattern(Flags.ARGS.output_file_pattern)

    LOG.info('Starting cause of death load')
    cause_of_death_df = pd.read_csv(
        Flags.ARGS.cause_of_death_codes_csv, dtype=str, keep_default_na=False
    )
    cause_of_death_df.set_index(CAUSE_OF_DEATH_CODE, inplace=True)
    LOG.info(cause_of_death_df.head(10))

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
            # NOTE(abby): The fetal deaths files are delimited by a comma and the
            # others use a semicolon.
            sep = ',' if 'DOFET' in file_name else ';'
            with LZ4Reader(file_name) as input_file:
                input_df = pd.read_csv(
                    input_file,
                    sep=sep,
                    dtype=str,
                    keep_default_na=False,
                    usecols=lambda col: col in SIM_COLUMN_MANAGER.get_input_columns(),
                )
            assert len(input_df) > 0, f'Input file {input_file_name} has no rows'

            # Pre 1996, some columns had different names
            if INPUT_DATE_COLUMN_BEFORE_1996 in input_df.columns:
                input_df = input_df.rename(
                    columns=SIM_COLUMN_MANAGER.get_pre_1996_renaming_mapping()
                )

            # Check the number of lines after the file has already been read in
            # so the file doesn't need to be read in twice.
            if total_file_line_counter + len(input_df) > LINE_THRESHOLD:
                LOG.info('Processing previous data and creating new dataframe')
                # Process the current dataframe
                process_dataframe(
                    df,
                    cause_of_death_df,
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
            cause_of_death_df,
            occupation_df,
            output_file_pattern.build(f'{count:02d}'),
        )

    return 0


if __name__ == '__main__':
    sys.exit(main())
