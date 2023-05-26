#!/usr/bin/env python
''' Converts the raw CID 9 and 10 codes into a csv lookup from code to cause of death
    parent and categories that the code falls into. Although the input data needs
    to be converted, it is highly structured, which is used to build the output. CID 9
    vs 10 are generally structured the same although they have some key differences.

    The output columns (category, group, and chapter have a `cause_of_death_` prefix):
      - cid_id: These are the CID codes found in the SIM data.
      - category: The two digit parent code.
      - group: The most specific group for the code available.
      - chapter: The top level group.

    CID 9:
    The codes are 4 digit numbers, ex. 0010.
    There are parent categories with a 3 digit number and then 'X', ex. 001X.
    There is only one level of categories with 3 digit ranges, ex. 001-139. Therefore,
    group is empty.

    Example:
    For the following input rows:
        cause_of_death_title                cid_id
        Doenças infecciosas e parasitárias  001-139
        Cólera                              001X
        Devida a Vibrio cholerae            0010
        Devida a Vibrio cholerae el tor     0011
        Não especificada                    0019
    The output would be:
        cid_id  category        group   chapter
        001X    001X Cólera     -       Doenças infecciosas e parasitárias
        0010    001X Cólera     -       Doenças infecciosas e parasitárias
        0011    001X Cólera     -       Doenças infecciosas e parasitárias
        0019    001X Cólera     -       Doenças infecciosas e parasitárias

    CID 10:
    The codes are a letter and then 3 digit number, ex. A000.
    There are categories with a letter and then 2 digit number, ex. A00.
    There are 1 to 4 levels of groups with 1 letter and 2 digit ranges, ex. A00-B99.

    The data is read in as a single column that must be split into code and title columns.

    Example:
    For the following input rows:
        cid
        (A00-B99) I. Algumas doenças infecciosas e parasitárias
        (A00-A09) Doenças infecciosas intestinais
        (A00) Cólera
        (A00.0) Cólera devida a Vibrio cholerae 01 biótipo cholerae
        (A00.1) Cólera devida a Vibrio cholerae 01 biótipo El Tor
        (A00.9) Cólera não especificada
    The output would be:
        cid_id  category        group                                       chapter
        A00     A00 Cólera      (A00-A09) Doenças infecciosas intestinais   I. Algumas doenças infecciosas e parasitárias
        A000    A00 Cólera      (A00-A09) Doenças infecciosas intestinais   I. Algumas doenças infecciosas e parasitárias
        A001    A00 Cólera      (A00-A09) Doenças infecciosas intestinais   I. Algumas doenças infecciosas e parasitárias
        A009    A00 Cólera      (A00-A09) Doenças infecciosas intestinais   I. Algumas doenças infecciosas e parasitárias
'''

from collections import defaultdict
import os
import sys
from typing import List, Tuple

import pandas as pd
from pylib.base.flags import Flags

from log import LOG

# pylint: disable=unsupported-assignment-operation,unsubscriptable-object,no-member

ALPHABET_LOCATION = {letter: i for i, letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
ALPHABET_LOOKUP = dict(enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))

CHAPTER_LOOKUP = {}

ID_COL = 'cid_id'
SHORT_ID_COL = 'short_cid_id'
TITLE_COL = 'cause_of_death_title'
CATEGORY_COL = 'cause_of_death_category'
GROUP_COL = 'cause_of_death_group'
CHAPTER_COL = 'cause_of_death_chapter'


def less_than(start_cid, end_cid, inclusive=True):
    if ALPHABET_LOCATION[start_cid.letter] < ALPHABET_LOCATION[end_cid.letter]:
        return True
    if ALPHABET_LOCATION[start_cid.letter] == ALPHABET_LOCATION[end_cid.letter]:
        if start_cid.number < end_cid.number:
            return True
        if start_cid.number == end_cid.number:
            return inclusive
        return False
    return False


def format_cid(cid):
    return cid[0], int(cid[1:])


class CID:
    def __init__(self, letter, number):
        self.letter = letter
        self.number = number

    def to_id(self):
        number = str(self.number)
        return f'{self.letter}{number.zfill(2)}'

    def add_one(self):
        if self.number < 99:
            return CID(self.letter, self.number + 1)
        return CID(ALPHABET_LOOKUP[ALPHABET_LOCATION[self.letter] + 1], 0)


# Separate CID id and title into different columns
def separate_title_id(dataframe):
    output = []
    for row in dataframe['cid']:
        cid, title = row.split(')', 1)
        cid = cid.replace('(', '')
        output.append({ID_COL: cid, TITLE_COL: title.strip()})
    return pd.DataFrame(output)


# For the CID 9 rows with a 3 digit numerical range and title, add an
# entry to CHAPTER_LOOKUP for each code in the range. Ex. "001-139,Doenças
# infecciosas e parasitárias" would give keys 001, 002, ..., 139 with values
# "Doenças infecciosas e parasitárias".
def build_cid9_chapter_lookup(row):
    floor, ceil = [int(val) for val in row[ID_COL].split('-')]
    for val in range(floor, ceil + 1):
        CHAPTER_LOOKUP[str(val).zfill(3)] = row[TITLE_COL]


# Given a function to determine if a row is a category from the CID ID column,
# convert those rows to be categories. This function relies on the category row
# being first to then forward fill the values.
def build_category_column(df, is_category):
    # Create category column and set titles to be empty for category rows
    df.loc[is_category(df[ID_COL]), CATEGORY_COL] = df[[ID_COL, TITLE_COL]].agg(
        ' '.join, axis=1
    )
    df[CATEGORY_COL] = df[CATEGORY_COL].ffill()
    df.loc[is_category(df[ID_COL]), TITLE_COL] = pd.NA
    return df


# For the CID 10 groups with a letter and 2 digit numerical range, return a
# list of all codes in the range. Ex. A00-B99 would give A00, A01, ..., B99.
def list_cid10_codes_in_range(range_str):
    start_str, end_str = range_str.split('-')
    start = CID(*format_cid(start_str))
    end = CID(*format_cid(end_str))
    codes = []
    while less_than(start, end, inclusive=True):
        codes.append(start.to_id())
        if ALPHABET_LOCATION[start.letter] == 25 and start.number == 99:
            break
        start = start.add_one()
    return codes


def process_cid_9_codes(input_file_name: str) -> pd.DataFrame:
    LOG.info('Reading in CID 9 mapping')
    cid9_df = pd.read_csv(input_file_name)
    LOG.info(cid9_df.head(10))

    # Build cid 9 chapter lookup
    cid9_df[cid9_df[ID_COL].str.contains('-')].apply(build_cid9_chapter_lookup, axis=1)

    # Create the chapter column
    cid9_df = cid9_df[~cid9_df[ID_COL].str.contains('-')]
    cid9_df[CHAPTER_COL] = cid9_df[ID_COL].str[:3].replace(CHAPTER_LOOKUP)

    # Cid 9 has no group equivalent, so create an empty column
    cid9_df[GROUP_COL] = ''

    # Create category column
    cid9_df = build_category_column(cid9_df, lambda x: x.str.contains('X'))

    LOG.info(cid9_df.head(10))
    LOG.info('Finished processing CID 9 codes')

    return cid9_df


def process_additional_mappings(
    df: pd.DataFrame, input_additional_mappings: List[str]
) -> Tuple[pd.DataFrame, List[str]]:
    # Parse the additional mapping flags
    additional_mappings = {}
    for raw_mapping in input_additional_mappings:
        mapping = raw_mapping.split(',')
        assert (
            len(mapping) >= 1
        ), f'Additional mapping "{raw_mapping}" could not be parsed'
        additional_columns = {}
        for column in mapping[1:]:
            column_pair = column.split(':')
            assert (
                len(column_pair) == 2
            ), f'Additional mapping "{raw_mapping}" could not be parsed'
            additional_columns[column_pair[0]] = column_pair[1]
        additional_mappings[mapping[0]] = additional_columns
    additional_columns = {
        column
        for column_lookup in additional_mappings.values()
        for column in column_lookup.values()
    }

    # Loop through each of the additional mappings
    for file_info, column_rename in additional_mappings.items():
        df = df.reset_index(drop=True)

        file_name, merge_type = file_info.split(':')
        assert merge_type in (
            'exact',
            'parent',
        ), f'Unsupported merge type {merge_type}'

        # Read in the supplemental file
        supplemental_name = os.path.basename(file_name).split('.')[0]
        LOG.info(
            'Merging in %s info and using columns %s',
            supplemental_name,
            list(column_rename.keys()),
        )
        supplemental_df = pd.read_csv(
            file_name,
            usecols=[ID_COL, *column_rename.keys()],
        ).rename(columns=column_rename)

        # Check if this dataframe uses ranges for row
        if supplemental_df[ID_COL].str.contains('-').any():
            # If so, convert this dataframe to only have a single code per row
            supplemental_df[ID_COL] = supplemental_df[ID_COL].apply(
                lambda x: list_cid10_codes_in_range(x) if '-' in x else [x]
            )
            supplemental_df = supplemental_df.explode(ID_COL).reset_index(drop=True)

        # If any codes are duplicated, take the last.
        supplemental_df = supplemental_df.groupby(ID_COL).last().reset_index()

        # Merge in the additional mapping. First try to merge on the full 4 digit code.
        full_id_merge = df.merge(
            supplemental_df,
            left_on=ID_COL,
            right_on=ID_COL,
            how='outer',
            indicator=True,
        )
        full_id_merge[SHORT_ID_COL] = full_id_merge[ID_COL].str[:3]
        # If enabled, try to merge on the short code. Otherwise, use the full merge.
        if merge_type == 'parent':
            short_id_merge = (
                df.loc[full_id_merge['_merge'] == 'left_only']
                .merge(
                    supplemental_df,
                    left_on=SHORT_ID_COL,
                    right_on=ID_COL,
                    how='left',
                    suffixes=(None, '_drop'),
                )
                .drop(columns=[f'{ID_COL}_drop'])
            )
            full_id_merge = full_id_merge[full_id_merge['_merge'] != 'left_only'].drop(
                columns=['_merge']
            )
            df = pd.concat([full_id_merge, short_id_merge])
        else:
            df = full_id_merge.drop(columns=['_merge'])
    return df, additional_columns


def main():
    Flags.PARSER.add_argument(
        '--input_cid9',
        type=str,
        required=False,
        help='Raw csv lookup of cause of death (CID 9) to id.',
    )
    Flags.PARSER.add_argument(
        '--input_cid10',
        type=str,
        required=True,
        help='Raw csv lookup of cause of death (CID 10) to id.',
    )
    Flags.PARSER.add_argument(
        '--additional_mappings',
        nargs='+',
        type=str,
        required=False,
        help='Any additional files to merge into the output. They should be structured like '
        '"<CSV file path>:<merge type>,<input column 1>:<dimension id 1>,<etc>" where there are '
        'any number of column mappings >= 1. The merge type should be either "exact" meaning '
        'exact CID code matches are required or "parent" meaning the code will try to fill in '
        'any additional matches where the 3 digit CID codes matched the parent category. The '
        'merge is an outer merge so codes may be added in from the additional files. The CID '
        'code column should be named "cid_id".',
    )
    Flags.PARSER.add_argument(
        '--output_file',
        type=str,
        required=True,
        help='File path for the output cause of death lookup',
    )
    Flags.InitArgs()

    input_cid_9_file_name = Flags.ARGS.input_cid9
    cid9_df = None
    if input_cid_9_file_name:
        cid9_df = process_cid_9_codes(input_cid_9_file_name)

    LOG.info('Reading in CID 10 mapping')
    cid10_df = separate_title_id(pd.read_csv(Flags.ARGS.input_cid10))
    LOG.info(cid10_df.head(10))

    # Build a lookup from group code range to its text chapter or group name (called TITLE_COL here)
    groups = cid10_df[cid10_df[ID_COL].str.contains('-')]
    name_lookup = {
        row[ID_COL]: (row[TITLE_COL], f'({row[ID_COL]}) {row[TITLE_COL]}')
        for _, row in groups.iterrows()
    }
    # Build a lookup from code to the chapter and group it falls into
    code_to_names = defaultdict(list)
    for range_str in groups[ID_COL]:
        for code in list_cid10_codes_in_range(range_str):
            chapter_name, group_name = name_lookup[range_str]
            name = group_name if len(code_to_names[code]) > 0 else chapter_name

            # We want only the top level group (chapter) and the most specific group (group)
            if len(code_to_names[code]) == 2:
                code_to_names[code][1] = name
            else:
                code_to_names[code].append(name)
    groups_lookup_df = pd.DataFrame.from_dict(
        code_to_names,
        orient='index',
        columns=[CHAPTER_COL, GROUP_COL],
    ).reset_index()

    # Build category column and clean codes
    cid10_df = cid10_df[~cid10_df[ID_COL].str.contains('-')]
    cid10_df = build_category_column(
        cid10_df, lambda x: ~x.str.contains('.', regex=False)
    )
    cid10_df[ID_COL] = cid10_df[ID_COL].str.replace('.', '', regex=False)

    # Add in the categories generated above
    cid10_df[SHORT_ID_COL] = cid10_df[ID_COL].str[:3]
    cid10_df = cid10_df.merge(
        groups_lookup_df, left_on=SHORT_ID_COL, right_on='index', how='outer'
    )
    # Some codes don't have a parent, keep them anyways and fill in the code
    cid10_df.loc[cid10_df[ID_COL].isna(), ID_COL] = cid10_df['index']
    cid10_df[SHORT_ID_COL] = cid10_df[ID_COL].str[:3]

    # Add the additional mappings
    cid10_df, additional_output_columns = process_additional_mappings(
        cid10_df, Flags.ARGS.additional_mappings
    )
    # For any overlapping columns like chapter, etc let them be filled in by the
    # groups lookup.
    non_overlapping_columns = list(
        set(cid10_df.columns) - set(groups_lookup_df.columns)
    )
    cid10_df = cid10_df[non_overlapping_columns].merge(
        groups_lookup_df, left_on=SHORT_ID_COL, right_on='index', how='left'
    )

    # HACK(abby): B342 is the covid cause of death code. They wanted all dimensions
    # to have a "COVID: " prefix.
    cid10_df.loc[cid10_df[ID_COL] == 'B342', CHAPTER_COL] = (
        'COVID: ' + cid10_df.loc[cid10_df[ID_COL] == 'B342', CHAPTER_COL]
    )
    cid10_df.loc[cid10_df[ID_COL] == 'B342', GROUP_COL] = (
        'COVID: ' + cid10_df.loc[cid10_df[ID_COL] == 'B342', GROUP_COL]
    )
    cid10_df.loc[cid10_df[ID_COL] == 'B342', CATEGORY_COL] = (
        'COVID: ' + cid10_df.loc[cid10_df[ID_COL] == 'B342', CATEGORY_COL]
    )

    LOG.info(cid10_df.head(10))
    LOG.info('Finished processing CID 10 mapping')

    if cid9_df is not None:
        LOG.info('Combining CID 9 and 10')
        merged_df = pd.concat([cid9_df, cid10_df])
    else:
        merged_df = cid10_df

    assert len(merged_df) == len(
        merged_df[ID_COL].unique()
    ), 'Full CID mapping contains duplicate ID codes'

    # Order the columns here so the output is easier to read
    merged_df = merged_df[
        [
            ID_COL,
            CHAPTER_COL,
            GROUP_COL,
            CATEGORY_COL,
            *additional_output_columns,
        ]
    ].sort_values(ID_COL)
    LOG.info('Outputting mapping')
    merged_df.to_csv(Flags.ARGS.output_file, index=False)


if __name__ == '__main__':
    sys.exit(main())
