from typing import List, Dict, Set

import pandas as pd

from config.br_covid.datatypes import Dimension
from log import LOG
from pipeline.brazil_covid.bin.shared.convert_occupation_codes import (
    FAMILY_COLUMN,
    GROUP_COLUMN,
    PRINCIPAL_SUBGROUP_COLUMN,
    SUBGROUP_COLUMN,
    TITLE_COLUMN as OCCUPATION_TITLE_COLUMN,
)

UNKNOWN = 'Ignorado'
INCONSISTENT_DATA = 'Dados inconsistentes'
NOT_APPLICABLE = 'Não se aplica'


class Column:
    def __init__(
        self,
        # Column name used in the raw data
        input_name: str,
        # Dimension name
        output_name: str = None,
        # Mapping from input values to display values
        mapping: Dict[str, str] = None,
        # Placeholder values that should be converted to unknown
        placeholders: List[str] = None,
        # If there was a different column name in the raw data prior to 1996
        pre_1996_name: str = None,
        # Whether the column should be pivoted to fields
        is_field: bool = False,
    ):
        self.input_name = input_name
        self.output_name = output_name
        # Default empty string and 9 to Ignorado, leave as None if there are no mappings
        self.mapping = {'': UNKNOWN, '9': UNKNOWN, **mapping} if mapping else None
        # Default 99 to Ignorado, leave as None if there are no placeholders
        self.placeholders = ['99', *placeholders] if placeholders is not None else None
        self.pre_1996_name = pre_1996_name
        self.is_field = is_field


class NumericColumn(Column):
    def __init__(
        self,
        # Column name used in the raw data
        input_name: str,
        # Dimension name
        output_name: str = None,
        # Placeholder values that should be converted to unknown
        placeholders: List[str] = None,
        # Minimum value that is valid, values below this will be converted to inconsistent data
        minimum: int = None,
        # Maximum value that is valid, values above this will be converted to inconsistent data
        maximum: int = None,
        # If there was a different column name in the raw data prior to 1996
        pre_1996_name: str = None,
    ):
        super().__init__(
            input_name,
            output_name=output_name,
            placeholders=placeholders,
            pre_1996_name=pre_1996_name,
        )
        self.minimum = minimum
        self.maximum = maximum


class ColumnManager:
    def __init__(self, columns: List[Column]):
        self.columns = columns

    # Mapping from column name to a dictionary containing values that should be replaced in
    # that column.
    def get_mappings(self) -> Dict[str, Dict[str, str]]:
        column_mapping_values = {}
        for column in self.columns:
            if column.mapping is not None:
                column_mapping_values[column.input_name] = column.mapping
        return column_mapping_values

    # These columns should be pivoted out into fields
    def get_fields(self) -> Dict[str, Dict[str, str]]:
        fields = {}
        for column in self.columns:
            if column.is_field:
                assert column.mapping is not None, (
                    'Column %s is a field, but has no mapping',
                    column.input_name,
                )
                fields[column.input_name] = column.mapping
        return fields

    # These columns have numerical values and require special processing.
    def get_numeric_columns(self) -> List[NumericColumn]:
        numeric_columns = []
        for column in self.columns:
            if isinstance(column, NumericColumn):
                numeric_columns.append(column)
        return numeric_columns

    # Map from input column name to the dimension name.
    def get_renaming_mapping(self) -> Dict[str, str]:
        renaming_mapping = {}
        for column in self.columns:
            if column.output_name is not None:
                renaming_mapping[column.input_name] = column.output_name
        return renaming_mapping

    # Some columns have different names prior to 1996 and they need to be mapped
    # to the post-1996 name
    def get_pre_1996_renaming_mapping(self) -> Dict[str, str]:
        renaming_mapping = {}
        for column in self.columns:
            if column.pre_1996_name is not None:
                renaming_mapping[column.pre_1996_name] = column.input_name
        return renaming_mapping

    # Get all columns that should be read in from the dataframe. This is all input
    # names as well as any pre 1996 names.
    def get_input_columns(self) -> Set[str]:
        input_columns = set()
        for column in self.columns:
            input_columns.add(column.input_name)
            if column.pre_1996_name is not None:
                input_columns.add(column.pre_1996_name)
        return input_columns

    # Get all columns that are expected in the data. This is all input
    # names.
    def get_required_columns(self) -> Set[str]:
        return {column.input_name for column in self.columns}


# These mappings are used across multiple input columns
ESC2010_COLUMN_MAPPING = {
    '0': 'Sem Escolaridade',
    '1': 'Fundamental (1º ao 5º ano)',
    '2': 'Fundamental (6º ao 9º ano)',
    '3': 'Ensino Médio',
    '4': 'Superior Incompleto',
    '5': 'Superior Completo',
}
YES_NO_RESPONSE_MAPPING = {
    '1': 'Sim',
    '2': 'Não',
    '3': NOT_APPLICABLE,
}
GRAVIDEZ_MAPPING = {
    '1': 'Única',
    '2': 'Dupla',
    '3': 'Tripla ou mais',
}
SEX_MAPPING = {
    '1': 'Masculino',
    '2': 'Feminino',
    '0': UNKNOWN,
    'M': 'Masculino',
    'F': 'Feminino',
    'I': UNKNOWN,
}


RACE_MAPPING = {
    '1': 'Branca',
    '2': 'Preta',
    '3': 'Amarela',
    '4': 'Parda',
    '5': 'Indígena',
}

PREGNANCY_KIND_MAPPING = {
    '1': 'Vaginal',
    '2': 'Cesáreo',
}

MOTHER_OCCUPATION_COLUMNS_RENAME = {
    OCCUPATION_TITLE_COLUMN: Dimension.MOTHERS_OCCUPATION_TITLE,
    FAMILY_COLUMN: Dimension.MOTHERS_OCCUPATION_FAMILY,
    SUBGROUP_COLUMN: Dimension.MOTHERS_OCCUPATION_SUBGROUP,
    PRINCIPAL_SUBGROUP_COLUMN: Dimension.MOTHERS_OCCUPATION_PRINCIPAL_SUBGROUP,
    GROUP_COLUMN: Dimension.MOTHERS_OCCUPATION_GROUP,
}


def convert_numerical_column(df: pd.DataFrame, column: NumericColumn) -> pd.DataFrame:
    column_name = column.input_name
    # Convert all values to numbers
    df.loc[df[column_name] != '', column_name] = (
        pd.to_numeric(df.loc[df[column_name] != '', column_name], errors='coerce')
        .astype('Int64')
        .astype(pd.StringDtype())
    )
    # Convert empty values to unknown
    df.loc[df[column_name] == '', column_name] = UNKNOWN
    # Convert values that could not be parsed as numbers to inconsistent data
    df.loc[df[column_name].isna(), column_name] = INCONSISTENT_DATA

    # Convert missing value placeholders to unknown
    if column.placeholders is not None:
        LOG.info(
            'Removing %s placeholder values from column %s',
            len(df[df[column_name].isin(column.placeholders)]),
            column_name,
        )
        df.loc[df[column_name].isin(column.placeholders), column_name] = UNKNOWN

    # Convert values below the min to inconsistent data
    if column.minimum is not None:
        min_rows = pd.to_numeric(df[column_name], errors='coerce') < column.minimum
        LOG.info(
            'Removing %s values below the min from column %s',
            min_rows.sum(),
            column_name,
        )
        df.loc[min_rows, column_name] = INCONSISTENT_DATA

    # Convert values above the max to inconsistent data
    if column.maximum is not None:
        max_rows = pd.to_numeric(df[column_name], errors='coerce') > column.maximum
        LOG.info(
            'Removing %s values above the max from column %s',
            max_rows.sum(),
            column_name,
        )
        df.loc[max_rows, column_name] = INCONSISTENT_DATA

    numeric_rows = ~df[column_name].isin({INCONSISTENT_DATA, UNKNOWN})
    # Add in zero padding
    max_length = df.loc[numeric_rows, column_name].str.len().max()
    if not pd.isna(max_length):
        # NOTE(abby): Since the data is bucketed and all of it isn't processed at once,
        # use the placeholders to help determine the max length of text.
        if column.placeholders:
            max_length = max(max_length, *(len(p) for p in column.placeholders))
        df.loc[numeric_rows, column_name] = df[column_name].str.zfill(max_length)

    return df


def clean_and_replace_occupation_column(
    df: pd.DataFrame,
    occupation_df: pd.DataFrame,
    input_column: str,
    column_list: List[str],
) -> pd.DataFrame:
    # Some rows have punctuation in the code, remove them.
    df.loc[
        ~df[input_column].str.isnumeric() & (df[input_column] != ''), input_column
    ] = ''
    # Convert the unknown 5 digit codes to 3 digit ones.
    known_codes = set(occupation_df.index)
    unmatched_rows = (
        (df[input_column] != '')
        & ~df[input_column].isin(known_codes)
        & (df[input_column].str.len() == 5)
    )
    df.loc[unmatched_rows, input_column] = df.loc[unmatched_rows, input_column].str[:3]

    # Use the occupation lookup file to convert from occupation code to title.
    df = df.merge(
        occupation_df,
        left_on=input_column,
        right_index=True,
        how='left',
    )
    # For rows that have an occupation but it can't be matched, log the values then
    # set the value to "unknown occupation".
    title_column = column_list[0]
    missing_rows_index = df[title_column].isna() & (df[input_column] != '')
    LOG.info(
        '%s %s rows had codes that could not be matched. Unmatched codes: \n %s',
        missing_rows_index.sum(),
        input_column,
        df[missing_rows_index][input_column].unique(),
    )
    for column in column_list:
        df.loc[missing_rows_index, column] = 'Ocupação desconhecida'
    df = df.drop(columns=[input_column])

    return df
