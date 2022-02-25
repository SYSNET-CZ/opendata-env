from pytds import connect, LoginError, Error

from defaults import DATASOURCE_DOCTYPE_FAKTURA, DATASOURCE_DOCTYPE_OBJEDNAVKA, DATASOURCE_DOCTYPE_SMLOUVA, \
    ITEM_HOSTNAME, ITEM_PORT, ITEM_USER, ITEM_PASSWORD, ITEM_DATABASE, \
    ITEM_OBJEDNAVKA, ITEM_SMLOUVA, ITEM_ZAVAZEK, ITEM_SQL, ITEM_ORIGINATOR, ITEM_ORIGINATOR_ICO, ITEM_KEYWORD
from settings import LOG, CONFIG

DATA_VERSION = '3'

DATASET_MAP = {
    DATASOURCE_DOCTYPE_FAKTURA: ITEM_ZAVAZEK,
    DATASOURCE_DOCTYPE_OBJEDNAVKA: ITEM_OBJEDNAVKA,
    DATASOURCE_DOCTYPE_SMLOUVA: ITEM_SMLOUVA
}


class JasuClient:
    def __init__(self, company=None):
        self.hostname = CONFIG['jasu'][company.lower()][ITEM_HOSTNAME]
        self.port = CONFIG['jasu'][company.lower()][ITEM_PORT]
        self.user = CONFIG['jasu'][company.lower()][ITEM_USER]
        self.password = CONFIG['jasu'][company.lower()][ITEM_PASSWORD]
        self.database = CONFIG['jasu'][company.lower()][ITEM_DATABASE]
        self.conn = None
        LOG.logger.info('JasuClient created: {}:{}, {}, {}/{}'.format(
            self.hostname, self.port, self.database, self.user, self.password))

    def __del__(self):
        if self.conn is not None:
            self.conn.close()
            del self.conn
        LOG.logger.info('JasuClient deleted')

    def open_connection(self):
        try:
            user = str(self.user)
            password = str(self.password)
            database = None
            if self.database is not None:
                database = str(self.database)
            self.conn = connect(
                dsn=self.hostname,
                port=self.port,
                user=user,
                password=password,
                database=database,
                autocommit=False)
            LOG.logger.info('Connection opened: {}'.format(self.conn.product_version))
        except LoginError as e:
            LOG.logger.error(e)
            self.conn = None
        return self.conn

    def execute_sql(self, sql=None):
        LOG.logger.info('SQL: {}'.format(sql))
        try:
            self.open_connection()
            cur = self.conn.cursor()
            cur.execute(sql)
            out = cur.fetchall()
            count = cur.rowcount
            LOG.logger.info('Returned rows: {}'.format(count))
            cur.close()
            return out
        except Error as e:
            LOG.logger.error(e)
            return None


def strip_string(source: str):
    if source is None:
        return None
    return source.strip()


def remove_newlines(source: str):
    if source is None:
        return None
    out = source.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    return out


class JasuObjednavka:
    def __init__(self, company, data):
        self.Rok = data[0]
        self.OrderId = strip_string(data[1])
        self.Title = strip_string(data[2])
        self.ContractorId = strip_string(data[3])
        self.ContractorName = strip_string(data[4])
        self.DateConclusion = data[5]
        self.DateValidity = data[6]
        self.ValueWithVAT = data[7]
        self.RadaEvidCislo = strip_string(data[8])

        self.id = '{}-{}'.format(str(self.Rok), self.RadaEvidCislo)
        self.version = DATA_VERSION
        self.ico = self.ContractorId
        self.contractor = self.ContractorName
        self.total = self.ValueWithVAT
        self.form = 'objednávka'
        self.originatorico = CONFIG['jasu'][company.lower()][ITEM_ORIGINATOR_ICO]
        self.originator = CONFIG['jasu'][company.lower()][ITEM_ORIGINATOR]
        self.keyword = CONFIG['jasu'][company.lower()][ITEM_OBJEDNAVKA][ITEM_KEYWORD]


class JasuSmlouva:
    def __init__(self, company, data):
        self.Rok = data[0]
        self.ContractId = strip_string(data[1])
        self.ContractTitle = strip_string(data[2])
        self.ContractType = strip_string(data[3])
        self.ContractorId = strip_string(data[4])
        self.ContractorCompany = strip_string(data[5])
        self.ContractorAddressStreet = strip_string(data[6])
        self.ContractorAddressCity = strip_string(data[7])
        self.ContractorAddressZip = strip_string(data[8])
        self.DateConclusion = data[9]
        self.DateValidity = data[10]
        self.ValueWithVAT = data[11]
        self.RadaEvidCislo = strip_string(data[12])

        self.id = '{}-{}'.format(str(self.Rok), self.RadaEvidCislo)
        self.version = DATA_VERSION
        self.ico = self.ContractorId
        self.contractor = self.ContractorCompany
        self.total = self.ValueWithVAT
        self.form = 'smlouva'
        self.originatorico = CONFIG['jasu'][company.lower()][ITEM_ORIGINATOR_ICO]
        self.originator = CONFIG['jasu'][company.lower()][ITEM_ORIGINATOR]
        self.keyword = CONFIG['jasu'][company.lower()][ITEM_SMLOUVA][ITEM_KEYWORD]


class JasuZavazek:
    def __init__(self, company, data):
        self.Rok = data[0]
        self.CisloFaktury = strip_string(data[1])
        self.CisloSmlouvy = strip_string(data[2])
        self.CisloObjednavky = strip_string(data[3])
        self.Dodavatel = remove_newlines(strip_string(data[4]))
        self.ICO = strip_string(data[5])
        self.CelkovaCastka = data[6]
        self.CastkaPolozky = data[7]
        self.DatumPrijeti = data[8]
        self.DatumSplatnosti = data[9]
        self.DatumUhrady = data[10]
        self.UcelPlatby = remove_newlines(strip_string(data[11]))
        self.Suc = strip_string(data[12])
        self.RParagraf = strip_string(data[13])
        self.RPolozka = strip_string(data[14])
        self.Auc = strip_string(data[15])
        self.NazevPolozkyRozpoctu = strip_string(data[16])
        self.RadaEvidCislo = strip_string(data[17])
        self.DatumVystaveni = data[18]
        self.IdPolozky = data[19]

        self.id = '{}-{}-{}'.format(str(self.Rok), self.RadaEvidCislo, str(self.IdPolozky))
        self.version = DATA_VERSION
        self.invoice = self.CisloFaktury
        self.total = self.CelkovaCastka
        self.contractid = self.CisloSmlouvy
        self.orderid = self.CisloObjednavky
        self.contractor = self.Dodavatel
        self.form = 'faktura'
        self.originatorico = CONFIG['jasu'][company.lower()][ITEM_ORIGINATOR_ICO]
        self.originator = CONFIG['jasu'][company.lower()][ITEM_ORIGINATOR]
        self.keyword = CONFIG['jasu'][company.lower()][ITEM_ZAVAZEK][ITEM_KEYWORD]


def load_data(company, data_source):
    company = company.upper()
    data_source = data_source.lower()
    if data_source not in CONFIG['jasu'][company.lower()]:
        LOG.logger.error('Datasource {} does not exist for the company {}'.format(data_source, company))
        return None
    LOG.logger.info('Load data source: {}/{} START.'.format(company.lower(), data_source))
    client = JasuClient(company=company)
    sql = CONFIG['jasu'][company.lower()][data_source][ITEM_SQL]
    reply = client.execute_sql(sql)
    if reply is None:
        LOG.logger.error('No data returned for data source {}/{}'.format(company.lower(), data_source))
        return None
    out = []
    for row in reply:
        if data_source == ITEM_OBJEDNAVKA:
            out.append(JasuObjednavka(company=company, data=row))
        elif data_source == ITEM_SMLOUVA:
            out.append(JasuSmlouva(company=company, data=row))
        elif data_source == ITEM_ZAVAZEK:
            out.append(JasuZavazek(company=company, data=row))
    del client
    LOG.logger.info('Load data source: {}/{} END (Loaded rows: {}).'.format(company.lower(), data_source, len(out)))
    return out
