#!/usr/bin/env python
# pylint: disable=C0301
from config.br_covid.datatypes import Dimension
from pipeline.brazil_covid.bin.shared.datasus_common import (
    Column,
    ColumnManager,
    ESC2010_COLUMN_MAPPING,
    GRAVIDEZ_MAPPING,
    INCONSISTENT_DATA,
    NOT_APPLICABLE,
    NumericColumn,
    PREGNANCY_KIND_MAPPING,
    RACE_MAPPING,
    SEX_MAPPING,
    UNKNOWN,
    YES_NO_RESPONSE_MAPPING,
)


# These columns all have special processing in the convert step
INPUT_MOTHER_OCCUPATION_COLUMN = 'CODOCUPMAE'
INPUT_DATE_COLUMN = 'DTNASC'
INPUT_BIRTH_TIME_HOURS_COLUMN = 'HORANASC'

# These are all input columns that should be included in the SIM integration. There is also
# some info about processing for them.
SINASC_COLUMN_MANAGER = ColumnManager(
    [
        NumericColumn(
            'APGAR1', output_name=Dimension.APGAR_1, placeholders=[], maximum=10
        ),
        NumericColumn(
            'APGAR5', output_name=Dimension.APGAR_5, placeholders=[], maximum=10
        ),
        Column('CODANOMAL', output_name=Dimension.CODIGO_ANOMALIA),
        Column(INPUT_MOTHER_OCCUPATION_COLUMN),
        Column('CODESTAB', output_name=Dimension.CODESTAB),
        Column('CODMUNRES'),
        Column('CODMUNNASC'),
        Column('CODMUNNATU', output_name=Dimension.COD_MUN_NATU),
        Column(
            'CONSULTAS',
            output_name=Dimension.CONS_PRE_NAT,
            mapping={
                '1': 'Nenhuma',
                '2': 'de 1 a 3',
                '3': 'de 4 a 6',
                '4': '7 e mais',
            },
        ),
        Column('DTCADASTRO', output_name=Dimension.DATA_CADASTRO),
        Column('DTDECLARAC', output_name=Dimension.DATA_DECLARACAO),
        Column(INPUT_DATE_COLUMN),
        Column('DTNASCMAE', output_name=Dimension.DATA_NASCIMENTO_MAE),
        Column('DTULTMENST', output_name=Dimension.DATA_ULTIMA_MENSTRUACAO),
        Column(
            'ESCMAE',
            output_name=Dimension.ESCOLARIDADE_MAE_ANOS_ESTUDO,
            mapping={
                '1': 'Nenhuma',
                '2': '1 a 3 anos',
                '3': '4 a 7 anos',
                '4': '8 a 11 anos',
                '5': '12 ou mais anos',
            },
        ),
        Column(
            'ESCMAE2010',
            output_name=Dimension.MOTHERS_SCHOOLING,
            mapping=ESC2010_COLUMN_MAPPING,
        ),
        NumericColumn('DIFDATA', output_name=Dimension.OPORT_DN),
        Column(
            'ESTCIVMAE',
            output_name=Dimension.ESTCIVMAE,
            mapping={
                '1': 'Solteira',
                '2': 'Casada',
                '3': 'Viúva',
                '4': 'Separada judicialmente/divorciada',
                '5': 'União estável',
            },
        ),
        Column(
            'GESTACAO',
            output_name=Dimension.GESTACAO,
            mapping={
                '1': 'Menos de 22 Semanas',
                '2': '22 a 27 Semanas',
                '3': '28 a 31 Semanas',
                '4': '32 a 36 Semanas',
                '5': '37 a 41 Semanas',
                '6': '42 Semanas e Mais',
            },
        ),
        Column(
            'GRAVIDEZ',
            output_name=Dimension.PREGNANCY_TYPE,
            mapping={**GRAVIDEZ_MAPPING},
        ),
        Column(INPUT_BIRTH_TIME_HOURS_COLUMN, output_name=Dimension.HORANASC),
        NumericColumn(
            'IDADEMAE',
            output_name=Dimension.MOTHERS_AGE,
            minimum=10,
            maximum=65,
            placeholders=[],
        ),
        NumericColumn('IDADEPAI', output_name=Dimension.IDADE_PAI, minimum=9),
        Column(
            'IDANOMAL',
            output_name=Dimension.IDANOMAL,
            mapping={
                '1': 'Sim',
                '2': 'Não',
            },
        ),
        Column(
            'KOTELCHUCK',
            output_name=Dimension.KOTELCHUCK,
            mapping={
                '1': 'Não fez pré-natal (Campo33=0)',
                '2': 'Inadequado (Campo34>3 ou Campo34<=3 e Campo33<3)',
                '3': 'Intermediário (Campo34<=3 e Campo33 entre 3 e 5)',
                '4': 'Adequado (Campo34<=3 e Campo33=6)',
                '5': 'Mais que adequado (Campo34<=3 e Campo33>=7)',
                '9': 'Não Classificados (campos 33 ou 34, Nulo ou Ign)',
            },
        ),
        Column(
            'LOCNASC',
            output_name=Dimension.LOCNASC,
            mapping={
                '1': 'Hospital',
                '2': 'Outros estabelecimentos de saúde',
                '3': 'Domicílio',
                '4': 'Outros',
                '5': 'Aldeia Indígena',
            },
        ),
        NumericColumn('MESPRENAT', output_name=Dimension.MESPRENAT, placeholders=[]),
        Column(
            'PARIDADE',
            output_name=Dimension.PARIDADE,
            mapping={'0': 'Nulipara', '1': 'Multipara'},
        ),
        Column(
            'PARTO',
            output_name=Dimension.PREGNANCY_KIND,
            mapping=PREGNANCY_KIND_MAPPING,
        ),
        NumericColumn(
            'PESO',
            output_name=Dimension.BIRTH_WEIGHT_GRAMS,
            placeholders=['0', '9999'],
        ),
        NumericColumn(
            'QTDFILMORT',
            output_name=Dimension.NUMBER_DECEASED_CHILDREN,
            placeholders=[],
        ),
        NumericColumn(
            'QTDFILVIVO', output_name=Dimension.NUMBER_LIVING_CHILDREN, placeholders=[]
        ),
        NumericColumn('QTDGESTANT', output_name=Dimension.QTD_GESTANT, placeholders=[]),
        NumericColumn('QTDPARTCES', output_name=Dimension.QTD_PARTCES, placeholders=[]),
        NumericColumn('QTDPARTNOR', output_name=Dimension.QTD_PARTNOR, placeholders=[]),
        Column('RACACOR', output_name=Dimension.RACE, mapping=RACE_MAPPING),
        Column('RACACORMAE', output_name=Dimension.RACA_COR_MAE, mapping=RACE_MAPPING),
        NumericColumn(
            'SEMAGESTAC',
            output_name=Dimension.GESTATION_WEEKS,
            minimum=18,
            maximum=45,
            placeholders=[],
        ),
        NumericColumn(
            'SERIESCMAE',
            output_name=Dimension.MOTHERS_SCHOOL_GRADE,
            minimum=1,
            maximum=8,
        ),
        Column('SEXO', output_name=Dimension.GENDER, mapping=SEX_MAPPING),
        Column(
            'STCESPARTO',
            output_name=Dimension.CESAREAN_PRIOR_TO_BIRTH,
            mapping={**YES_NO_RESPONSE_MAPPING, '': NOT_APPLICABLE},
        ),
        Column(
            'STTRABPART',
            output_name=Dimension.LABOR_INDUCED,
            mapping=YES_NO_RESPONSE_MAPPING,
        ),
        Column(
            'TPAPRESENT',
            output_name=Dimension.TYPE_BIRTH_PRESENTATION,
            mapping={
                '1': 'Cefálico',
                '2': 'Pélvica ou podálica',
                '3': 'Transversa',
            },
        ),
        Column(
            'TPFUNCRESP',
            output_name=Dimension.TYPE_RESPONSIBLE_PARTY,
            mapping={
                '1': 'Médico',
                '2': 'Enfermeiro',
                '3': 'Parteira',
                '4': 'Funcionário do cartório',
                '5': 'Outros',
            },
        ),
        Column(
            'TPNASCASSI',
            output_name=Dimension.BIRTH_ASSISTED_BY,
            mapping={
                '1': 'Médico',
                '2': 'Enfermagem ou Obstetriz',
                '3': 'Parteira',
                '4': 'Outros',
            },
        ),
        Column(
            'TPROBSON',
            output_name=Dimension.ROBSONS_GROUP_CODE,
            mapping={
                '01': 'Nulípara, gestação única, cefálica, ≥ 37 semanas, em trabalho de parto espontâneo',
                '02': 'Nulípara, gestação única, cefálica, ≥ 37 semanas, com indução ou cesárea anterior ao trabalho de parto',
                '03': 'Multípara (sem antecedente de cesárea), gestação única, cefálica, ≥ 37 semanas, em trabalho de parto espontâneo',
                '04': 'Multípara (sem antecedente de cesárea), gestação única, cefálica, ≥ 37 semanas, com indução ou cesárea realizada antes do início do trabalho de parto',
                '05': 'Com antecedente de cesárea, gestação única, cefálica ≥ 37 semanas',
                '06': 'Todos partos pélvicos em nulíparas',
                '07': 'Todos partos pélvicos em multíparas (incluindo antecedente de cesárea)',
                '08': 'Todas as gestações múltiplas (incluindo antecedente de cesárea)',
                '09': 'Todas as apresentações anormais (incluindo antecedente de cesárea)',
                '10': 'Todas as gestações únicas, cefálicas, ≥ 37 semanas (incluindo antecedente de cesárea)',
                '11': 'Nascidos vivos não classificados por ausência dados aos itens necessários',
            },
        ),
    ]
)
