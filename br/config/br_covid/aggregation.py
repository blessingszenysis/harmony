from config.br_covid.datatypes import (
    Dimension,
    DIMENSION_PARENTS,
    HIERARCHICAL_DIMENSIONS,
)
from data.query.models.granularity import GranularityExtraction
from db.druid.js_formulas.week_extraction import CDC_EPI_WEEK_EXTRACTION_FORMULA
from models.python.config.calendar_settings import CalendarSettings, DateOption


# Geo fields from least specific to most specific.
GEO_FIELD_ORDERING = HIERARCHICAL_DIMENSIONS

# Given a query on a field, which fields should we ask Druid for?
# Unless otherwise specified, querying on a field will just ask for itself.
DIMENSION_SLICES = {
    dimension: [dimension] + parents for dimension, parents in DIMENSION_PARENTS.items()
}

DIMENSION_ID_MAP = {
    dimension: dimension.replace('Name', 'ID') for dimension in HIERARCHICAL_DIMENSIONS
}

# Map from whereType API query param to latlng fields.
GEO_TO_LATLNG_FIELD = {
    dimension: (dimension.replace('Name', 'Lat'), dimension.replace('Name', 'Lon'))
    for dimension in HIERARCHICAL_DIMENSIONS
}

# Dimension category mapping from parent name to list of dimensions. Used by AQT.
DIMENSION_CATEGORIES = [
    ('Geografia', GEO_FIELD_ORDERING),
    (
        'Compartilhado',
        [
            Dimension.MOTHERS_AGE,
            Dimension.MOTHERS_SCHOOLING,
            Dimension.MOTHERS_OCCUPATION_TITLE,
            Dimension.MOTHERS_OCCUPATION_FAMILY,
            Dimension.MOTHERS_OCCUPATION_SUBGROUP,
            Dimension.MOTHERS_OCCUPATION_PRINCIPAL_SUBGROUP,
            Dimension.MOTHERS_OCCUPATION_GROUP,
            Dimension.BIRTH_WEIGHT_GRAMS,
            Dimension.NUMBER_LIVING_CHILDREN,
            Dimension.NUMBER_DECEASED_CHILDREN,
            Dimension.PREGNANCY_TYPE,
            Dimension.GESTATION_WEEKS,
            Dimension.PREGNANCY_KIND,
        ],
    ),
    (
        'SIVEP',
        [
            Dimension.DEAD,
            Dimension.COMORBIDITIES_AND_RISK_FACTORS,
            Dimension.FINAL_CLASSIFICATION_OF_CASE,
            Dimension.HOSPITALIZATION,
        ],
    ),
    (
        'SIM',
        [
            Dimension.AGE_GROUP_2,
            Dimension.AGE_GROUP_INFANT_5_YEAR_GROUPS,
            Dimension.SCHOOLING,
            Dimension.MARITAL_STATUS,
            Dimension.PHYSICIAN_ATTENDED,
            Dimension.SVO_IML_MUNI_CODE,
            Dimension.OCCUPATION_TITLE,
            Dimension.OCCUPATION_FAMILY,
            Dimension.OCCUPATION_SUBGROUP,
            Dimension.OCCUPATION_PRINCIPAL_SUBGROUP,
            Dimension.OCCUPATION_GROUP,
            Dimension.PLACE_OF_DEATH,
            Dimension.MEDICAL_CARE,
            Dimension.IS_AUTOPSY,
            Dimension.VIOLENT_DEATH_TYPE,
            Dimension.IS_WORK_RELATED,
            Dimension.GESTATIONAL_PHASE,
            Dimension.MOMENT_OF_CHILDBIRTH,
            Dimension.DEATH_TYPE,
            Dimension.INVESTIGATED_DEATH,
            Dimension.PRIMARY_CAUSE_CHAPTER,
            Dimension.PRIMARY_CAUSE_GROUP,
            Dimension.PRIMARY_CAUSE_CATEGORY,
            Dimension.PRIMARY_CAUSE_CODE,
            Dimension.PRIMARY_CAUSE_GARBAGE,
            Dimension.INITIAL_CAUSE_CODE,
            Dimension.DANT_PLAN,
            Dimension.MOMENT_OF_DEATH,
            Dimension.ALCOHOL_CAUSE_OF_DEATH,
        ],
    ),
    (
        'SINASC',
        [
            Dimension.APGAR_1,
            Dimension.APGAR_1_GROUPED,
            Dimension.APGAR_5,
            Dimension.APGAR_5_GROUPED,
            Dimension.CODIGO_ANOMALIA,
            Dimension.CODIGO_ANOMALIA_MULTI_VALUE,
            Dimension.CODIGO_ANOMALIA_GROUP,
            Dimension.CODIGO_ANOMALIA_PRIORITY,
            Dimension.ANOMALIA_MULTIPLA,
            Dimension.MOTHERS_SCHOOL_GRADE,
            Dimension.CESAREAN_PRIOR_TO_BIRTH,
            Dimension.LABOR_INDUCED,
            Dimension.TYPE_BIRTH_PRESENTATION,
            Dimension.TYPE_RESPONSIBLE_PARTY,
            Dimension.BIRTH_ASSISTED_BY,
            Dimension.ROBSONS_GROUP_CODE,
            Dimension.IDADE_PAI,
            Dimension.ESTCIVMAE,
            Dimension.GESTACAO,
            Dimension.HORANASC,
            Dimension.IDANOMAL,
            Dimension.KOTELCHUCK,
            Dimension.LOCNASC,
            Dimension.MESPRENAT,
            Dimension.OPORT_DN,
            Dimension.COD_MUN_NATU,
            Dimension.CONS_PRE_NAT,
            Dimension.CODESTAB,
            Dimension.BIRTH_WEIGHT_GRAMS_GROUPED,
            Dimension.NUMBER_DECEASED_CHILDREN_GROUPED,
            Dimension.QTD_PARTCES,
            Dimension.QTD_PARTNOR,
            Dimension.QTD_GESTANT,
            Dimension.PARIDADE,
            Dimension.RACA_COR_MAE,
            Dimension.DATA_CADASTRO,
            Dimension.DATA_DECLARACAO,
            Dimension.DATA_NASCIMENTO_MAE,
            Dimension.DATA_ULTIMA_MENSTRUACAO,
            Dimension.ESCOLARIDADE_MAE_ANOS_ESTUDO,
            Dimension.MOTHERS_AGE_GROUPED,
        ],
    ),
    (
        'Outras variáveis demográficas',
        [Dimension.AGE_GROUP, Dimension.GENDER, Dimension.RACE],
    ),
]

# List of queryable dimensions.
DIMENSIONS = [
    dimension for _, dimensions in DIMENSION_CATEGORIES for dimension in dimensions
]

CALENDAR_SETTINGS = CalendarSettings.create_default(enable_all_granularities=True)

# Translations
CALENDAR_SETTINGS.granularity_settings.day.name = 'Dia'
CALENDAR_SETTINGS.granularity_settings.week.name = 'Semana'
CALENDAR_SETTINGS.granularity_settings.month.name = 'Mês'
CALENDAR_SETTINGS.granularity_settings.quarter.name = 'Quarto'
CALENDAR_SETTINGS.granularity_settings.year.name = 'Ano'

# Date Extraction
CALENDAR_SETTINGS.granularity_settings.day_of_year.name = 'Dia do Ano'
CALENDAR_SETTINGS.granularity_settings.week_of_year.name = 'Semana do Ano'
CALENDAR_SETTINGS.granularity_settings.month_of_year.name = 'Mês do Ano'
CALENDAR_SETTINGS.granularity_settings.quarter_of_year.name = 'Quarto do Ano'

# NOTE(stephen): BR COVID uses the CDC epi week definition (starting on Sunday). They
# also do not want to use the W## prefix since that is language specific.
CALENDAR_SETTINGS.granularity_settings.epi_week = DateOption(
    CALENDAR_SETTINGS.granularity_settings.epi_week.id,
    'Semana Epidemiológica',
    'cc YYYY',
    'cc',
)
CALENDAR_SETTINGS.granularity_settings.epi_week_of_year = DateOption(
    CALENDAR_SETTINGS.granularity_settings.epi_week_of_year.id,
    'Semana Epidemiológica do Ano',
    'cc',
)

# HACK(stephen): GIANT ENORMOUS HACK. DO NOT REPEAT THIS ANYWHERE ELSE. We don't have a
# great way of switching the `epi_week_of_year` granularity extraction to use the CDC
# epi week definition instead of the WHO one which is the default. This hack swaps it
# out for us.
# pylint: disable=protected-access
GranularityExtraction.EXTRACTION_MAP[
    'epi_week_of_year'
]._func = CDC_EPI_WEEK_EXTRACTION_FORMULA
