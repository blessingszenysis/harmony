############################################################################
# Datatypes

from typing import List

from pylib.base.flags import Flags

from data.pipeline.datatypes.base_row import BaseRow
from data.pipeline.datatypes.base_row_factory import BaseRowFactory
from data.pipeline.datatypes.dimension_factory import DimensionFactory

# Output field information
RAW_PREFIX = 'Raw'
CLEANED_PREFIX = 'Clean'
CANONICAL_PREFIX = 'Canonical'


class Dimension:
    SOURCE = (BaseRow.SOURCE_FIELD,)
    DATE = (BaseRow.DATE_FIELD,)
    REGION = 'RegionName'
    STATE = 'StateName'
    HEALTH_REGION = 'HealthRegionName'
    MUNICIPALITY = 'MunicipalityName'

    AGE_GROUP = 'AgeGroup'
    GENDER = 'Gender'
    RACE = 'Race'

    DEAD = 'Dead'
    COMORBIDITIES_AND_RISK_FACTORS = 'ComorbiditiesAndRiskFactors'
    FINAL_CLASSIFICATION_OF_CASE = 'FinalClassificationOfCase'
    HOSPITALIZATION = 'Hospitalization'

    # Common DataSUS dimensions
    BIRTH_WEIGHT_GRAMS = 'BirthWeightGrams'
    GESTATION_WEEKS = 'GestationWeeks'
    MOTHERS_AGE = 'MothersAge'
    MOTHERS_OCCUPATION_TITLE = 'MothersOccupationTitle'
    MOTHERS_OCCUPATION_FAMILY = 'MothersOccupationFamily'
    MOTHERS_OCCUPATION_SUBGROUP = 'MothersOccupationSubgroup'
    MOTHERS_OCCUPATION_PRINCIPAL_SUBGROUP = 'MothersOccupationPrincipalSubgroup'
    MOTHERS_OCCUPATION_GROUP = 'MothersOccupationGroup'
    MOTHERS_SCHOOLING = 'MothersSchooling'
    NUMBER_DECEASED_CHILDREN = 'NumberDeceasedChildren'
    NUMBER_LIVING_CHILDREN = 'NumberLivingChildren'
    PREGNANCY_KIND = 'PregnancyKind'
    PREGNANCY_TYPE = 'PregnancyType'

    # SIM integration
    AGE_GROUP_2 = 'AgeGroup2'
    AGE_GROUP_INFANT_5_YEAR_GROUPS = 'AgeGroupInfant5YearGroups'
    SCHOOLING = 'Schooling'
    MARITAL_STATUS = 'MaritalStatus'
    PHYSICIAN_ATTENDED = 'PhysicianAttended'
    SVO_IML_MUNI_CODE = 'SvoImlMuniCode'
    OCCUPATION_TITLE = 'OccupationTitle'
    OCCUPATION_FAMILY = 'OccupationFamily'
    OCCUPATION_SUBGROUP = 'OccupationSubgroup'
    OCCUPATION_PRINCIPAL_SUBGROUP = 'OccupationPrincipalSubgroup'
    OCCUPATION_GROUP = 'OccupationGroup'
    PLACE_OF_DEATH = 'PlaceOfDeath'
    MEDICAL_CARE = 'MedicalCare'
    IS_AUTOPSY = 'IsAutopsy'
    VIOLENT_DEATH_TYPE = 'ViolentDeathType'
    IS_WORK_RELATED = 'IsWorkRelated'
    GESTATIONAL_PHASE = 'GestationalPhase'
    MOMENT_OF_CHILDBIRTH = 'MomentOfChildbirth'
    DEATH_TYPE = 'DeathType'
    INVESTIGATED_DEATH = 'InvestigatedDeath'
    PRIMARY_CAUSE_CHAPTER = 'PrimaryCauseChapter'
    PRIMARY_CAUSE_GROUP = 'PrimaryCauseGroup'
    PRIMARY_CAUSE_CATEGORY = 'PrimaryCauseCategory'
    PRIMARY_CAUSE_CODE = 'PrimaryCauseCode'
    PRIMARY_CAUSE_GARBAGE = 'PrimaryCauseGarbage'
    INITIAL_CAUSE_CODE = 'InitialCauseCode'
    DANT_PLAN = 'PlanoDant'
    MOMENT_OF_DEATH = 'MomentOfDeath'
    ALCOHOL_CAUSE_OF_DEATH = 'AlcoholCauseOfDeath'

    # SINASC dimensions
    APGAR_1 = 'Apgar1'
    APGAR_5 = 'Apgar5'
    CODIGO_ANOMALIA = 'CodigoAnomalia'
    CODIGO_ANOMALIA_MULTI_VALUE = 'CodigoAnomaliaMultiValue'
    # Note these two are also multi value dimensions
    CODIGO_ANOMALIA_GROUP = 'CodigoAnomaliaGroup'
    CODIGO_ANOMALIA_PRIORITY = 'CodigoAnomaliaPriority'
    # TODO(abby): Explore Druid Virtual Columns to store derived dimensions
    ANOMALIA_MULTIPLA = 'AnomaliaMultipla'
    MOTHERS_AGE_GROUPED = 'MothersAgeGrouped'
    NUMBER_DECEASED_CHILDREN_GROUPED = 'NumberDeceasedChildrenGrouped'
    BIRTH_WEIGHT_GRAMS_GROUPED = 'BirthWeightGramsGrouped'
    APGAR_1_GROUPED = 'Apgar1Grouped'
    APGAR_5_GROUPED = 'Apgar5Grouped'
    MOTHERS_SCHOOL_GRADE = 'MothersSchoolGrade'
    CESAREAN_PRIOR_TO_BIRTH = 'CesareanPriorToBirth'
    LABOR_INDUCED = 'LaborInduced'
    TYPE_BIRTH_PRESENTATION = 'TypeBirthPresentation'
    TYPE_RESPONSIBLE_PARTY = 'TypeResponsibleParty'
    BIRTH_ASSISTED_BY = 'BirthAssistedBy'
    ROBSONS_GROUP_CODE = 'RobsonsGroupCode'
    IDADE_PAI = 'IdadePai'
    ESTCIVMAE = 'SituacaoCivil'
    GESTACAO = 'SemanasGstacao'
    GRAVIDEZ = 'TipoGravidez'
    HORANASC = 'HoraNascimento'
    IDANOMAL = 'AnomaliaIdentificada'
    KOTELCHUCK = 'Kotelchuck'
    LOCNASC = 'LocalNascimento'
    MESPRENAT = 'MesGestaoPreNatal'
    OPORT_DN = 'Oportunidade'
    COD_MUN_NATU = 'MunicipioNaturalidade'
    CONS_PRE_NAT = 'ConsultasPreNatal'
    CODESTAB = 'CodigoEstabelecimento'
    QTD_PARTNOR = 'QuantityOfVaginalBirths'
    QTD_PARTCES = 'QuantityOfCesareas'
    QTD_GESTANT = 'QuantityOfPreviousGestations'
    PARIDADE = 'Paridade'
    RACA_COR_MAE = 'RaceOfMother'
    DATA_CADASTRO = 'DataCadastro'
    DATA_DECLARACAO = 'DataDeclaracao'
    DATA_NASCIMENTO_MAE = 'DataNascimentoMae'
    DATA_ULTIMA_MENSTRUACAO = 'DataUltimaMenstruacao'
    ESCOLARIDADE_MAE_ANOS_ESTUDO = 'EscolaridadeMaeAnosEstudo'


HIERARCHICAL_DIMENSIONS = [
    Dimension.REGION,
    Dimension.STATE,
    Dimension.HEALTH_REGION,
    Dimension.MUNICIPALITY,
]
DIMENSION_PARENTS = {
    parent: HIERARCHICAL_DIMENSIONS[: parent_index + 1]
    for parent_index, parent in enumerate(HIERARCHICAL_DIMENSIONS[1:])
}

NON_HIERARCHICAL_DIMENSIONS: List[str] = []

# pylint: disable=invalid-name
BrazilCovidDimensionFactory = DimensionFactory(
    HIERARCHICAL_DIMENSIONS,
    NON_HIERARCHICAL_DIMENSIONS,
    RAW_PREFIX,
    CLEANED_PREFIX,
    CANONICAL_PREFIX,
)

BaseRowType = BaseRowFactory(
    Dimension, HIERARCHICAL_DIMENSIONS, DIMENSION_PARENTS, NON_HIERARCHICAL_DIMENSIONS
)
DimensionFactoryType = BrazilCovidDimensionFactory


class PipelineArgs:
    @classmethod
    def add_source_processing_args(cls):
        Flags.PARSER.add_argument(
            '--output_file', type=str, required=True, help='Processed data output file'
        )
        Flags.PARSER.add_argument(
            '--location_list',
            type=str,
            required=True,
            help='Output list of region/district/facility for matching',
        )
        Flags.PARSER.add_argument(
            '--field_list',
            type=str,
            required=True,
            help='Output list of all possible fields with data for this source',
        )
