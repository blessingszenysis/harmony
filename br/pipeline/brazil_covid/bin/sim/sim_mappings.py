#!/usr/bin/env python
from config.br_covid.datatypes import Dimension
from pipeline.brazil_covid.bin.shared.datasus_common import (
    Column,
    ColumnManager,
    ESC2010_COLUMN_MAPPING,
    NOT_APPLICABLE,
    NumericColumn,
    PREGNANCY_KIND_MAPPING,
    GRAVIDEZ_MAPPING,
    RACE_MAPPING,
    SEX_MAPPING,
    YES_NO_RESPONSE_MAPPING,
)
from pipeline.brazil_covid.bin.shared.convert_cid_csv import (
    CATEGORY_COL,
    CHAPTER_COL,
    GROUP_COL,
)
from pipeline.brazil_covid.bin.shared.convert_occupation_codes import (
    FAMILY_COLUMN,
    GROUP_COLUMN,
    PRINCIPAL_SUBGROUP_COLUMN,
    SUBGROUP_COLUMN,
    TITLE_COLUMN as OCCUPATION_TITLE_COLUMN,
)


# These columns all have special processing in the convert step
INPUT_AGE_COLUMN = 'IDADE'
INPUT_CAUSE_OF_DEATH_COLUMN = 'CAUSABAS'
INPUT_DATE_COLUMN_BEFORE_1996 = 'DATAOBITO'
INPUT_DATE_COLUMN_AFTER_1996 = 'DTOBITO'
INPUT_DEATH_TYPE_COLUMN = 'TIPOBITO'
INPUT_MOTHER_AGE_COLUMN = 'IDADEMAE'
INPUT_MOTHER_OCCUPATION_COLUMN = 'OCUPMAE'
INPUT_OCCUPATION_COLUMN = 'OCUP'
# These aren't used as dimensions, just in the special processing for mother mortality
MOTHER_MORTALITY_OBITOGRAV = 'OBITOGRAV'
MOTHER_MORTALITY_OBITOPUERP = 'OBITOPUERP'


# The cause of death and occupation columns are converted from a single input column to multiple
# dimension columns. These dictionaries convert from new column names to dimensions.
CAUSE_OF_DEATH_COL_RENAME = {
    INPUT_CAUSE_OF_DEATH_COLUMN: Dimension.PRIMARY_CAUSE_CODE,
    CATEGORY_COL: Dimension.PRIMARY_CAUSE_CATEGORY,
    GROUP_COL: Dimension.PRIMARY_CAUSE_GROUP,
    CHAPTER_COL: Dimension.PRIMARY_CAUSE_CHAPTER,
}
OCCUPATION_COLUMNS_RENAME = {
    OCCUPATION_TITLE_COLUMN: Dimension.OCCUPATION_TITLE,
    FAMILY_COLUMN: Dimension.OCCUPATION_FAMILY,
    SUBGROUP_COLUMN: Dimension.OCCUPATION_SUBGROUP,
    PRINCIPAL_SUBGROUP_COLUMN: Dimension.OCCUPATION_PRINCIPAL_SUBGROUP,
    GROUP_COLUMN: Dimension.OCCUPATION_GROUP,
}


# These are all input columns that should be included in the SIM integration. There is also
# some info about processing for them.
SIM_COLUMN_MANAGER = ColumnManager(
    [
        Column(
            'ACIDTRAB',
            output_name=Dimension.IS_WORK_RELATED,
            mapping=YES_NO_RESPONSE_MAPPING,
        ),
        Column(
            'ASSISTMED',
            output_name=Dimension.MEDICAL_CARE,
            mapping=YES_NO_RESPONSE_MAPPING,
        ),
        Column(
            'ATESTANTE',
            output_name=Dimension.PHYSICIAN_ATTENDED,
            mapping={
                '1': 'Sim',
                '2': 'Substituto',
                '3': 'IML',
                '4': 'SVO',
                '5': 'Outros',
            },
        ),
        Column(INPUT_CAUSE_OF_DEATH_COLUMN),
        Column(
            'CAUSABAS_O',
            output_name=Dimension.INITIAL_CAUSE_CODE,
        ),
        Column(
            'CIRCOBITO',
            output_name=Dimension.VIOLENT_DEATH_TYPE,
            mapping={
                '1': 'Acidente',
                '2': 'Suicídio',
                '3': 'Homicídio',
                '4': 'Outros',
                # This column will be empty for non-violent deaths
                '': NOT_APPLICABLE,
            },
        ),
        Column('CODMUNOCOR', pre_1996_name='MUNIOCOR'),
        Column('CODMUNRES', pre_1996_name='MUNIRES'),
        Column('COMUNSVOIM', output_name=Dimension.SVO_IML_MUNI_CODE),
        Column(INPUT_DATE_COLUMN_BEFORE_1996),
        Column(INPUT_DATE_COLUMN_AFTER_1996),
        Column(
            'ESC2010', output_name=Dimension.SCHOOLING, mapping=ESC2010_COLUMN_MAPPING
        ),
        Column(
            'ESCMAE2010',
            output_name=Dimension.MOTHERS_SCHOOLING,
            mapping=ESC2010_COLUMN_MAPPING,
        ),
        Column(
            'ESTCIV',
            output_name=Dimension.MARITAL_STATUS,
            mapping={
                '1': 'Solteiro',
                '2': 'Casado',
                '3': 'Viúvo',
                '4': 'Separado judicialmente',
                '5': 'União estável',
            },
            pre_1996_name='ESTCIVIL',
        ),
        Column(
            'GRAVIDEZ',
            output_name=Dimension.PREGNANCY_TYPE,
            # Most deaths aren't pregnancy related and this column will be empty
            mapping={**GRAVIDEZ_MAPPING, '': NOT_APPLICABLE},
        ),
        Column('IDADE', output_name=Dimension.AGE_GROUP_2),
        NumericColumn(
            INPUT_MOTHER_AGE_COLUMN,
            output_name=Dimension.MOTHERS_AGE,
            minimum=10,
            placeholders=['0'],
        ),
        Column(
            'LOCOCOR',
            output_name=Dimension.PLACE_OF_DEATH,
            mapping={
                '1': 'Hospital',
                '2': 'Outros estabelecimentos de saúde',
                '3': 'Domicílio',
                '4': 'Via pública',
                '5': 'Outros',
                '6': 'Aldeia indígena',
            },
        ),
        Column(
            'NECROPSIA',
            output_name=Dimension.IS_AUTOPSY,
            mapping=YES_NO_RESPONSE_MAPPING,
        ),
        Column(MOTHER_MORTALITY_OBITOGRAV),
        Column(
            'OBITOPARTO',
            output_name=Dimension.MOMENT_OF_CHILDBIRTH,
            mapping={
                '1': 'Antes',
                '2': 'Durante',
                '3': 'Depois',
                # Most deaths aren't pregnancy related and this column will be empty
                '': NOT_APPLICABLE,
            },
        ),
        Column(MOTHER_MORTALITY_OBITOPUERP),
        Column(INPUT_OCCUPATION_COLUMN, pre_1996_name='OCUPACAO'),
        Column(INPUT_MOTHER_OCCUPATION_COLUMN),
        Column(
            'PARTO',
            output_name=Dimension.PREGNANCY_KIND,
            # Most deaths aren't pregnancy related and this column will be empty
            mapping={**PREGNANCY_KIND_MAPPING, '': NOT_APPLICABLE},
        ),
        NumericColumn('PESO', output_name=Dimension.BIRTH_WEIGHT_GRAMS),
        NumericColumn(
            'QTDFILMORT',
            output_name=Dimension.NUMBER_DECEASED_CHILDREN,
            placeholders=[],
        ),
        NumericColumn(
            'QTDFILVIVO',
            output_name=Dimension.NUMBER_LIVING_CHILDREN,
            placeholders=[],
        ),
        Column('RACACOR', output_name=Dimension.RACE, mapping=RACE_MAPPING),
        NumericColumn(
            'SEMAGESTAC', output_name=Dimension.GESTATION_WEEKS, placeholders=[]
        ),
        Column(
            'SEXO',
            output_name=Dimension.GENDER,
            mapping=SEX_MAPPING,
        ),
        Column(
            'TIPOBITO',
            output_name=Dimension.DEATH_TYPE,
            mapping={'1': 'Fetal', '2': 'Não Fetal'},
            is_field=True,
        ),
        Column(
            'TPMORTEOCO',
            output_name=Dimension.GESTATIONAL_PHASE,
            mapping={
                '1': 'Na gravidez',
                '2': 'No parto',
                '3': 'No abortamento',
                '4': 'Até 42 dias após o término do parto',
                '5': 'De 43 dias a 1 ano após o término da gestação',
                '8': 'Não ocorreu nestes períodos',
                # Most deaths aren't pregnancy related and this column will be empty
                '': NOT_APPLICABLE,
            },
        ),
        Column(
            'TPOBITOCOR',
            output_name=Dimension.MOMENT_OF_DEATH,
            mapping={
                '1': 'Durante a gestação',
                '2': 'Durante o abortamento',
                '3': 'Após o abortamento',
                '4': 'No parto ou até 1 hora após o parto',
                '5': 'No puerpério - até 42 dias após o parto',
                '6': 'Entre 43 dias e até 1 ano após o parto',
                '7': 'A investigação não identificou o momento do óbito',
                '8': 'Mais de um ano após o parto',
                '9': 'O óbito não ocorreu nas circunstâncias anteriores',
                '': 'Não investigado',
            },
        ),
        Column(
            'TPPOS',
            output_name=Dimension.INVESTIGATED_DEATH,
            mapping={'S': 'Sim', 'N': 'Não'},
        ),
    ],
)
