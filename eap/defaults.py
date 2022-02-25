import os

# CONSTATNTS

CRON_IMPORT_ALL = os.getenv('CRON_IMPORT_ALL', '5 3 * * 6')
CRON_EXPORT_ALL = os.getenv('CRON_EXPORT_ALL', '5 4 * * 6')
CRON_EXPORT_2020 = os.getenv('CRON_EXPORT_2020', '5 5 * * 6')
CRON_EXPORT_2021 = os.getenv('CRON_EXPORT_2021', '15 5 * * 6')
CRON_EXPORT_2022 = os.getenv('CRON_EXPORT_2022', '25 5 * * 6')
CRON_EXPORT_2023 = os.getenv('CRON_EXPORT_2023', None)
CRON_EXPORT_2024 = os.getenv('CRON_EXPORT_2024', None)
CRON_EXPORT_2025 = os.getenv('CRON_EXPORT_2025', None)
CRON_EXPORT_2026 = os.getenv('CRON_EXPORT_2026', None)
CRON_MAP = [
    {'import_all': CRON_IMPORT_ALL},
    {'export_all': CRON_EXPORT_ALL},
    {'export_2020': CRON_EXPORT_2020},
    {'export_2021': CRON_EXPORT_2021},
    {'export_2022': CRON_EXPORT_2022},
    {'export_2023': CRON_EXPORT_2023},
    {'export_2024': CRON_EXPORT_2024},
    {'export_2025': CRON_EXPORT_2025},
    {'export_2026': CRON_EXPORT_2026},
]
ES_HOST_NAME = os.getenv('ES_HOST_NAME', 'elasticsearch')  # pro lokální testování nastavte elasticsearch na localhost
ES_PROTOCOL = os.getenv('ES_PROTOCOL', 'http')
ES_PORT = os.getenv('ES_PORT', '9200')
ES_USER = os.getenv('ES_USER', 'elastic')
ES_PASSWORD = os.getenv('ES_PASSWORD', 'F8qfSQMmNC1oU1XD1oS4')
ES_CONFIG = {
    'hostname': ES_HOST_NAME,
    'protocol': ES_PROTOCOL,
    'port': ES_PORT,
    'user': ES_USER,
    'password': ES_PASSWORD
}
COMPANY_AOPK = 'AOPK'
COMPANY_CENIA = 'CENIA'
COMPANY_CGS = 'CGS'
COMPANY_CIZP = 'CIZP'
COMPANY_MZP = 'MZP'
COMPANY_SJCR = 'SJCR'
ITEM_HOSTNAME = 'hostname'
ITEM_PORT = 'port'
ITEM_USER = 'user'
ITEM_PASSWORD = 'password'
ITEM_DATABASE = 'database'
ITEM_OBJEDNAVKA = 'objednavka'
ITEM_SMLOUVA = 'smlouva'
ITEM_ZAVAZEK = 'zavazek'
ITEM_SQL = 'sql'
ITEM_CRON = 'cron'
ITEM_ORIGINATOR = 'originator'
ITEM_ORIGINATOR_ICO = 'originator_ico'
ITEM_KEYWORD = 'keyword'
ITEM_INDEX = 'index'
JASU_CONFIG_DEFAULT = {
    COMPANY_AOPK.lower(): {
        ITEM_HOSTNAME: '10.2.4.20',
        ITEM_PORT: 1433,
        ITEM_USER: 'sysnet',
        ITEM_PASSWORD: 'Opendata2016',
        ITEM_DATABASE: 'EIS_ostra',
        ITEM_ORIGINATOR: 'Agentura ochrany přírody a krajiny ČR',
        ITEM_ORIGINATOR_ICO: '62933591',
        ITEM_OBJEDNAVKA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Objednavky'),
            ITEM_CRON: '5 5 * * 7',
            ITEM_KEYWORD: ['AOPK', 'objednávka', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-aopk-objednavka'
        },
        ITEM_SMLOUVA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Smlouvy'),
            ITEM_CRON: '15 5 * * 7',
            ITEM_KEYWORD: ['AOPK', 'smlouva', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-aopk-smlouva'
        },
        ITEM_ZAVAZEK: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Zavazky'),
            ITEM_CRON: '25 5 * * 7',
            ITEM_KEYWORD: ['AOPK', 'faktura', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-aopk-zavazek'
        }
    },
    COMPANY_CENIA.lower(): {
        ITEM_HOSTNAME: 'issis.env.cz',
        ITEM_PORT: 1433,
        ITEM_USER: 'SYSNET',
        ITEM_PASSWORD: 'OpenData2016',
        ITEM_DATABASE: 'EIS_CENIA_Ostra',
        ITEM_ORIGINATOR: 'CENIA',
        ITEM_ORIGINATOR_ICO: '45249130',
        ITEM_SMLOUVA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Smlouvy'),
            ITEM_CRON: '55 6 * * 7',
            ITEM_KEYWORD: ['CENIA', 'smlouva', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-cenia-smlouva'
        },
        ITEM_ZAVAZEK: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Zavazky'),
            ITEM_CRON: '45 6 * * 7',
            ITEM_KEYWORD: ['CENIA', 'faktura', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-cenia-zavazek'
        }
    },
    COMPANY_CGS.lower(): {
        ITEM_HOSTNAME: '10.0.152.20',
        ITEM_PORT: 1433,
        ITEM_USER: 'SYSNET',
        ITEM_PASSWORD: 'Opendata2016',
        ITEM_DATABASE: 'EIS_CGS_ostra',
        ITEM_ORIGINATOR: 'Česká geologická služba',
        ITEM_ORIGINATOR_ICO: '00025798',
        ITEM_OBJEDNAVKA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Objednavky'),
            ITEM_CRON: '25 6 * * 7',
            ITEM_KEYWORD: ['ČGS', 'objednávka', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-cgs-objednavka'
        },
        ITEM_SMLOUVA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Smlouvy'),
            ITEM_CRON: '35 6 * * 7',
            ITEM_KEYWORD: ['ČGS', 'smlouva', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-cgs-smlouva'
        },
        ITEM_ZAVAZEK: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Zavazky'),
            ITEM_CRON: '15 6 * * 7',
            ITEM_KEYWORD: ['ČGS', 'faktura', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-cgs-zavazek'
        }
    },
    COMPANY_CIZP.lower(): {
        ITEM_HOSTNAME: '10.2.130.20',
        ITEM_PORT: 65015,
        ITEM_USER: 'SYSNET',
        ITEM_PASSWORD: 'Opendata2016',
        ITEM_DATABASE: 'EIS_Ostra',
        ITEM_ORIGINATOR: 'ČIŽP',
        ITEM_ORIGINATOR_ICO: '41693205',
        ITEM_OBJEDNAVKA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Objednavky'),
            ITEM_CRON: '5 7 * * 7',
            ITEM_KEYWORD: ['ČIŽP', 'objednávka', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-cizp-objednavka'
        },
        ITEM_SMLOUVA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Smlouvy'),
            ITEM_CRON: '15 7 * * 7',
            ITEM_KEYWORD: ['ČIŽP', 'smlouva', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-cizp-smlouva'
        },
        ITEM_ZAVAZEK: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Zavazky'),
            ITEM_CRON: '25 7 * * 7',
            ITEM_KEYWORD: ['ČIŽP', 'faktura', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-cizp-zavazek'
        }
    },
    COMPANY_MZP.lower(): {
        ITEM_HOSTNAME: 'issis.env.cz',
        ITEM_PORT: 1433,
        ITEM_USER: 'SYSNET',
        ITEM_PASSWORD: 'OpenData2016',
        ITEM_DATABASE: None,
        ITEM_ORIGINATOR: 'Ministerstvo životního prostředí',
        ITEM_ORIGINATOR_ICO: '00164801',
        ITEM_OBJEDNAVKA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Objednavky'),
            ITEM_CRON: '35 5 * * 7',
            ITEM_KEYWORD: ['MŽP', 'objednávka', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-mzp-objednavka'
        },
        ITEM_SMLOUVA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Smlouvy'),
            ITEM_CRON: '35 7 * * 7',
            ITEM_KEYWORD: ['MŽP', 'smlouva', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-mzp-smlouva'
        },
        ITEM_ZAVAZEK: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Zavazky'),
            ITEM_CRON: '45 5 * * 7',
            ITEM_KEYWORD: ['MŽP', 'faktura', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-mzp-zavazek'
        }
    },
    COMPANY_SJCR.lower(): {
        ITEM_HOSTNAME: 'issis.env.cz',
        ITEM_PORT: 1433,
        ITEM_USER: 'SYSNET',
        ITEM_PASSWORD: 'OpenData2016',
        ITEM_DATABASE: 'EIS_SJCR_Ostra',
        ITEM_ORIGINATOR: 'Správa jeskyní České republiky',
        ITEM_ORIGINATOR_ICO: '75073331',
        ITEM_SMLOUVA: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Smlouvy'),
            ITEM_CRON: '5 6 * * 7',
            ITEM_KEYWORD: ['SJČR', 'smlouva', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-sjcr-smlouva'
        },
        ITEM_ZAVAZEK: {
            ITEM_SQL: 'SELECT {} FROM {}'.format('*', 'OpenData_Zavazky'),
            ITEM_CRON: '55 5 * * 7',
            ITEM_KEYWORD: ['SJČR', 'faktura', 'OpenData', 'MUZO', 'JASU', 'EKIS'],
            ITEM_INDEX: 'muzo-sjcr-zavazek'
        }
    },
}
DATASOURCE_COMPANY_AOPK = 'aopk'
DATASOURCE_COMPANY_CENIA = 'cenia'
DATASOURCE_COMPANY_CGS = 'cgs'
DATASOURCE_COMPANY_CIZP = 'cizp'
DATASOURCE_COMPANY_MZP = 'mzp'
DATASOURCE_COMPANY_SJCR = 'sjcr'
FILENAME_FAKTURA = 'uhrazene_faktury'
FILENAME_OBJEDNAVKA = 'objednavky'
FILENAME_SMLOUVA = 'smlouvy_platne_neplatne'
DATASOURCE_DOCTYPE_FAKTURA = 'faktura'
DATASOURCE_DOCTYPE_OBJEDNAVKA = 'objednavka'
DATASOURCE_DOCTYPE_SMLOUVA = 'smlouva'
FILENAMES_DICTIONARY_DEAFULT = {
    DATASOURCE_DOCTYPE_FAKTURA: FILENAME_FAKTURA,
    DATASOURCE_DOCTYPE_OBJEDNAVKA: FILENAME_OBJEDNAVKA,
    DATASOURCE_DOCTYPE_SMLOUVA: FILENAME_SMLOUVA
}
DATASOURCE_COMPANIES = (
    DATASOURCE_COMPANY_AOPK,
    DATASOURCE_COMPANY_CENIA,
    DATASOURCE_COMPANY_CGS,
    DATASOURCE_COMPANY_CIZP,
    DATASOURCE_COMPANY_MZP,
    DATASOURCE_COMPANY_SJCR
)
DATASOURCE_INDEX_V1 = 'index'
DATASOURCE_INDEX_V2 = 'index2'
DATASOURCE_CKAN = 'ckan'
DATASOURCE_CKAN_SCHEME = 'scheme'
DATASOURCE_FIELDNAMES = 'fieldnames'
DATASOURCE_SORTITEM_V1 = 'sort'
DATASOURCE_SORTITEM_V2 = 'sort2'
DATASOURCE_FILENAME = 'filename'
EAP_DOC_FAKTURA = 'faktura'
EAP_DOC_OBJEDNAVKA = 'objednavka'
EAP_DOC_SMLOUVA = 'smlouva'
FIELD_NAMES_FAKTURA = [
    'cislo_smlouvy', 'cislo_objednavky', 'dodavatel', 'ico', 'cislo_faktury', 'datum_vystaveni', 'datum_prijeti',
    'datum_splatnosti', 'datum_uhrady', 'celkova_castka', 'castka_polozky', 'mena', 'ucel_platby', 'polozka_rozpoctu',
    'nazev_plozky_rozpoctu', 'kapitola', 'nazev_kapitoly'
]
FIELD_NAMES_OBJEDNAVKA = [
    'cislo_objednavky', 'popis', 'dodavatel', 'ico', 'datum_objednani', 'datum_dodani', 'celkova_castka', 'mena'
]
FIELD_NAMES_SMLOUVA = [
    'cislo_smlouvy', 'predmet', 'dodavatel', 'ico', 'datum_uzavreni', 'datum_trvani', 'celkova_castka', 'mena'
]
INDEX_FAKTURA = 'jasu-{}'.format(EAP_DOC_FAKTURA)
INDEX_OBJEDNAVKA = 'jasu-{}'.format(EAP_DOC_OBJEDNAVKA)
INDEX_SMLOUVA = 'jasu-{}'.format(EAP_DOC_SMLOUVA)
SORTITEM_FAKTURA = "idpolozky"
SORTITEM_OBJEDNAVKA = "_id"
SORTITEM_SMLOUVA = "_id"
SORTITEM_ID = "_id"
CKAN_SCHEMA_FAKTURA = 'https://opendata.mzp.cz/schema/schema_faktura.json'
CKAN_SCHEMA_OBJEDNAVKA = 'https://opendata.mzp.cz/schema/schema_objednavka.json'
CKAN_SCHEMA_SMLOUVA = 'https://opendata.mzp.cz/schema/schema_smlouva.json'
DATA_SOURCE_DICTIONARY = {
    DATASOURCE_COMPANY_AOPK: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX_V1: 'muzo-aopk-zavazek',
            DATASOURCE_INDEX_V2: INDEX_FAKTURA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM_V1: SORTITEM_FAKTURA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_AOPK + '_' + FILENAME_FAKTURA,
            DATASOURCE_CKAN: [
                {'2019': 'd41c0a4b-00c7-42ea-b610-39265b3e83ef'},
                {'2020': 'bfe802e2-9567-46f5-99c5-f231a8500591'},
                {'default': 'bfe802e2-9567-46f5-99c5-f231a8500591'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_FAKTURA,
        },
        DATASOURCE_DOCTYPE_OBJEDNAVKA: {
            DATASOURCE_INDEX_V1: 'muzo-aopk-objednavka',
            DATASOURCE_INDEX_V2: INDEX_OBJEDNAVKA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_OBJEDNAVKA,
            DATASOURCE_SORTITEM_V1: SORTITEM_OBJEDNAVKA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_AOPK + '_' + FILENAME_OBJEDNAVKA,
            DATASOURCE_CKAN: [
                {'2019': '32d88a90-5dfd-4f56-aee0-2a05d93cf016'},
                {'2020': '83fbdb47-f51a-419f-a0f2-4073a790c272'},
                {'default': '83fbdb47-f51a-419f-a0f2-4073a790c272'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_OBJEDNAVKA,
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX_V1: 'muzo-aopk-smlouva',
            DATASOURCE_INDEX_V2: INDEX_SMLOUVA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM_V1: SORTITEM_SMLOUVA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_AOPK + '_' + FILENAME_SMLOUVA,
            DATASOURCE_CKAN: [
                {'default': '14ffd3c8-4569-4e6d-b7c1-abba65b18878'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_SMLOUVA,
        },
    },
    DATASOURCE_COMPANY_CENIA: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX_V1: 'muzo-cenia-zavazek',
            DATASOURCE_INDEX_V2: INDEX_FAKTURA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM_V1: SORTITEM_FAKTURA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_CENIA + '_' + FILENAME_FAKTURA,
            DATASOURCE_CKAN: [
                {'2019': 'd8901035-c268-46a2-bf2a-80db0ad418c5'},
                {'2020': 'e982fbfc-20ce-4730-ada9-bfa053b916d8'},
                {'default': 'e982fbfc-20ce-4730-ada9-bfa053b916d8'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_FAKTURA,
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX_V1: 'muzo-cenia-smlouva',
            DATASOURCE_INDEX_V2: INDEX_SMLOUVA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM_V1: SORTITEM_SMLOUVA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_CENIA + '_' + FILENAME_SMLOUVA,
            DATASOURCE_CKAN: [
                {'default': 'a2497d61-19db-4c3e-a74f-8f8098cb520b'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_SMLOUVA,
        },
    },
    DATASOURCE_COMPANY_CGS: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX_V1: 'muzo-cgs-zavazek',
            DATASOURCE_INDEX_V2: INDEX_FAKTURA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM_V1: SORTITEM_FAKTURA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_CGS + '_' + FILENAME_FAKTURA,
            DATASOURCE_CKAN: [
                {'2019': 'd32400f9-d43d-4609-98bb-32591d72b1f5'},
                {'2020': 'aad9a0ac-0754-48ea-b327-89b73fe58a48'},
                {'default': 'aad9a0ac-0754-48ea-b327-89b73fe58a48'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_FAKTURA,
        },
        DATASOURCE_DOCTYPE_OBJEDNAVKA: {
            DATASOURCE_INDEX_V1: 'muzo-cgs-objednavka',
            DATASOURCE_INDEX_V2: INDEX_OBJEDNAVKA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_OBJEDNAVKA,
            DATASOURCE_SORTITEM_V1: SORTITEM_OBJEDNAVKA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_CGS + '_' + FILENAME_OBJEDNAVKA,
            DATASOURCE_CKAN: [
                {'2019': '741d6906-8725-4e1e-b9da-d21a668f369d'},
                {'2020': '316b77a0-a017-4dd5-909b-a0b393009640'},
                {'default': '316b77a0-a017-4dd5-909b-a0b393009640'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_OBJEDNAVKA,
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX_V1: 'muzo-cgs-smlouva',
            DATASOURCE_INDEX_V2: INDEX_SMLOUVA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM_V1: SORTITEM_SMLOUVA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_CGS + '_' + FILENAME_SMLOUVA,
            DATASOURCE_CKAN: [
                {'default': '96753501-1ed5-4897-aa49-7db6212e3a0a'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_SMLOUVA,
        },
    },
    DATASOURCE_COMPANY_CIZP: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX_V1: 'muzo-cizp-zavazek',
            DATASOURCE_INDEX_V2: INDEX_FAKTURA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM_V1: SORTITEM_FAKTURA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_CIZP + '_' + FILENAME_FAKTURA,
            DATASOURCE_CKAN: [
                {'2019': 'f2c9006a-315c-4b61-b488-ff3b333ba660'},
                {'2020': 'fdc75abd-2f17-4382-9cbe-ef8df6cfed49'},
                {'default': 'fdc75abd-2f17-4382-9cbe-ef8df6cfed49'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_FAKTURA,
        },
        DATASOURCE_DOCTYPE_OBJEDNAVKA: {
            DATASOURCE_INDEX_V1: 'muzo-cizp-objednavka',
            DATASOURCE_INDEX_V2: INDEX_OBJEDNAVKA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_OBJEDNAVKA,
            DATASOURCE_SORTITEM_V1: SORTITEM_OBJEDNAVKA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_CIZP + '_' + FILENAME_OBJEDNAVKA,
            DATASOURCE_CKAN: [
                {'2019': 'dae00835-8515-4527-ae0f-510a7905a276'},
                {'2020': '1caa294d-d810-4f84-93e1-4f0464a3c40a'},
                {'default': '1caa294d-d810-4f84-93e1-4f0464a3c40a'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_OBJEDNAVKA,
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX_V1: 'muzo-cizp-smlouva',
            DATASOURCE_INDEX_V2: INDEX_SMLOUVA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM_V1: SORTITEM_SMLOUVA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_CIZP + '_' + FILENAME_SMLOUVA,
            DATASOURCE_CKAN: [
                {'default': '673cf597-539e-405f-a371-05a5a53858f2'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_SMLOUVA,
        },
    },
    DATASOURCE_COMPANY_MZP: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX_V1: 'muzo-mzp-zavazek*',
            DATASOURCE_INDEX_V2: INDEX_FAKTURA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM_V1: SORTITEM_FAKTURA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_MZP + '_' + FILENAME_FAKTURA,
            DATASOURCE_CKAN: [
                {'2019': '8221caa9-3df6-4c09-880b-3b18386c330a'},
                {'2020': '233ff4c8-2baa-4670-bcc1-ae9a105d3c2e'},
                {'default': '233ff4c8-2baa-4670-bcc1-ae9a105d3c2e'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_FAKTURA,
        },
        DATASOURCE_DOCTYPE_OBJEDNAVKA: {
            DATASOURCE_INDEX_V1: 'muzo-mzp-objednavka',
            DATASOURCE_INDEX_V2: INDEX_OBJEDNAVKA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_OBJEDNAVKA,
            DATASOURCE_SORTITEM_V1: SORTITEM_OBJEDNAVKA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_MZP + '_' + FILENAME_OBJEDNAVKA,
            DATASOURCE_CKAN: [
                {'2019': '5dab30ac-dba4-4c8c-b9b9-da394133bdad'},
                {'2020': '349f2667-e690-4680-8a2d-dd3fff9ba08e'},
                {'default': '349f2667-e690-4680-8a2d-dd3fff9ba08e'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_OBJEDNAVKA,
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX_V1: 'muzo-mzp-smlouva',
            DATASOURCE_INDEX_V2: INDEX_SMLOUVA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM_V1: SORTITEM_SMLOUVA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_MZP + '_' + FILENAME_SMLOUVA,
            DATASOURCE_CKAN: [],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_SMLOUVA,
        },
    },
    DATASOURCE_COMPANY_SJCR: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX_V1: 'muzo-sjcr-zavazek',
            DATASOURCE_INDEX_V2: INDEX_FAKTURA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM_V1: SORTITEM_FAKTURA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_SJCR + '_' + FILENAME_FAKTURA,
            DATASOURCE_CKAN: {
                '2019': 'b8ae66e6-4d7e-4b50-9e29-25b9f5379dc0',
                '2020': '085947bf-0194-4783-9d8f-362b62740946',
                'default': '085947bf-0194-4783-9d8f-362b62740946',
            },
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_FAKTURA,
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX_V1: 'muzo-sjcr-smlouva',
            DATASOURCE_INDEX_V2: INDEX_SMLOUVA,
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM_V1: SORTITEM_SMLOUVA,
            DATASOURCE_SORTITEM_V2: SORTITEM_ID,
            DATASOURCE_FILENAME: DATASOURCE_COMPANY_SJCR + '_' + FILENAME_SMLOUVA,
            DATASOURCE_CKAN: [
                {'default': '0ac4ba6b-7e11-44b5-8e88-e6a056990446'},
            ],
            DATASOURCE_CKAN_SCHEME: CKAN_SCHEMA_SMLOUVA,
        },
    }
}
CKAN_FORMAT_SCHEMA = 'application/json'
CKAN_ENDPOINT = 'https://opendata.mzp.cz/api/3/action/resource_update'
CKAN_API_KEY = '0753e953-a26a-4c1a-8805-84b12f655ebf'
CKAN_OPENDATA_LICENSE = 'https://portal.gov.cz/portal/ostatni/volny-pristup-k-ds.html'
