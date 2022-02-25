import datetime
import re

import elasticsearch_dsl
from elasticsearch import Elasticsearch, TransportError, ElasticsearchException
from elasticsearch_dsl import Document, Keyword, Text, Date, Integer, Float, Index, Search, Q
from elasticsearch_dsl.exceptions import ElasticsearchDslException
from elasticsearch_dsl.query import Bool, Match

from defaults import EAP_DOC_FAKTURA, EAP_DOC_OBJEDNAVKA, EAP_DOC_SMLOUVA, ITEM_OBJEDNAVKA, ITEM_SMLOUVA, ITEM_ZAVAZEK, \
    ITEM_ORIGINATOR, ITEM_ORIGINATOR_ICO, ITEM_KEYWORD
from jasu import JasuSmlouva, strip_string, DATA_VERSION, JasuZavazek, remove_newlines, JasuObjednavka
from settings import LOG, ES_HOST, isfloat, consolidate_date, INDEX_DICTIONARY, CONFIG

DSL_VERSION = elasticsearch_dsl.__version__[0]


def elk_get_client(host=ES_HOST, protocol='http', host_name='elasticsearch', port=9200, user=None, password=None):
    if host is not None:
        hosts = [host]
    else:
        hosts = ['{}://{}:{}/'.format(protocol, host_name, port)]
        if (user is not None) and (password is not None):
            hosts = ['{}://{}:{}@{}:{}/'.format(protocol, user, password, host_name, port)]
    out = Elasticsearch(hosts=hosts)
    return out


def elk_get_info(using=None):
    try:
        inner_client = False
        if using is None:
            using = elk_get_client(host=ES_HOST)
            inner_client = True
        out = using.info()
        if inner_client:
            # using.close()
            del using
        return out
    except ElasticsearchException as e:
        LOG.logger.error('{} - ELK error {}'.format(__name__, str(e)))
        return None


def elk_get_version(using=None):
    info = elk_get_info(using=using)
    out = 'Elasticseach is not connected'
    if info is not None:
        out = info['version']['number']
    return out


class ElasticFactory:
    def __init__(self, hosts=ES_HOST):
        self.done = False
        self.hits = None
        self.search = None
        self.client = Elasticsearch(hosts=hosts)
        LOG.logger.info('ElasticFactory created')

    def __del__(self):
        if self.client is not None:
            self.client.transport.close()
            del self.client
        LOG.logger.info('ElasticFactory destroyed')

    def clear_index(self, index):
        idx_client = self.client.indices
        if idx_client.exists(index):
            idx_client.delete(index)
            LOG.logger.info('Index deleted: {}'.format(index))

    def store_jasu_objednavky(self, company, jasu_data):
        if jasu_data is None:
            return False
        i = 0
        dot = 0
        for item in jasu_data:
            eap_id = '{}-{}'.format(company.upper(), item.id)
            objednavka = EapObjednavka(company=company, meta={'id': eap_id})
            objednavka.load_data_jasu(item)
            objednavka.save(using=self.client, index=INDEX_DICTIONARY[EAP_DOC_OBJEDNAVKA])
            i += 1
            dot = print_dot(dot)
        if i > 0:
            print_last_dot()
        LOG.logger.info('List of {} ({}) for {} stored to {}'.format(
            EAP_DOC_OBJEDNAVKA, i, company, INDEX_DICTIONARY[EAP_DOC_OBJEDNAVKA]))
        return True

    def store_jasu_faktury(self, company, jasu_data):
        if jasu_data is None:
            return False
        i = 0
        dot = 0
        for item in jasu_data:
            eap_id = '{}-{}'.format(company.upper(), item.id)
            faktura = EapFaktura(company=company, meta={'id': eap_id})
            faktura.load_data_jasu(item)
            faktura.save(using=self.client, index=INDEX_DICTIONARY[EAP_DOC_FAKTURA])
            i += 1
            dot = print_dot(dot)
        if i > 0:
            print_last_dot()
        LOG.logger.info('List of {} ({}) for {} stored to {}'.format(
            EAP_DOC_FAKTURA, i, company, INDEX_DICTIONARY[EAP_DOC_FAKTURA]))
        return True

    def store_jasu_smlouvy(self, company, jasu_data):
        if jasu_data is None:
            return False
        i = 0
        dot = 0
        for item in jasu_data:
            eap_id = '{}-{}'.format(company.upper(), item.id)
            smlouva = EapSmlouva(company=company, meta={'id': eap_id})
            smlouva.load_data_jasu(item)
            smlouva.save(using=self.client, index=INDEX_DICTIONARY[EAP_DOC_SMLOUVA])
            i += 1
            dot = print_dot(dot)
        if i > 0:
            print_last_dot()
        LOG.logger.info('List of {} ({}) for {} stored to {}'.format(
            EAP_DOC_SMLOUVA, i, company, INDEX_DICTIONARY[EAP_DOC_SMLOUVA]))
        return True

    def init_search(self, company, doctype, year=None):
        sort_item = '_id'
        try:
            index = INDEX_DICTIONARY[doctype]
            self.search = Search(using=self.client, index=index) \
                .query("match", company=company) \
                .sort({sort_item: {"order": "asc"}})
            if year is not None:
                query = Q(Bool(must=[Match(rok=year), Match(company=company)]))
                self.search = Search(using=self.client, index=index) \
                    .sort({sort_item: {"order": "asc"}})
                self.search.query = query
            else:
                self.search = Search(using=self.client, index=index) \
                    .query("match", company=company) \
                    .sort({sort_item: {"order": "asc"}})
            LOG.logger.info('Index: {}; Query: {}'.format(index, str(self.search.query)))
            self.done = False
            return True
        except Exception as e:
            LOG.logger.error('{}: {}'.format(type(e), e))
            return False

    def load_data(self, company, doctype, year=None):
        out = False
        self.done = False
        self.hits = None
        if self.search is None:
            self.init_search(company=company, doctype=doctype, year=year)
        try:
            if self.done:
                LOG.logger.info('load_data {}'.format('DONE'))
            else:
                self.hits = self.search.scan()
                self.done = True
                out = True
        except (TransportError, ElasticsearchException) as err:
            LOG.logger.error('Exporter.load_data_from_eap {} {}'.format(type(err), err))
            out = False
        return out


INDEX = {
    EAP_DOC_FAKTURA: Index(INDEX_DICTIONARY[EAP_DOC_FAKTURA]),
    EAP_DOC_OBJEDNAVKA: Index(INDEX_DICTIONARY[EAP_DOC_OBJEDNAVKA]),
    EAP_DOC_SMLOUVA: Index(INDEX_DICTIONARY[EAP_DOC_SMLOUVA])
}


class EapDocument(Document):
    company = Keyword()
    contractor = Keyword()
    date_updated = Date()
    form = Keyword()
    ico = Keyword()
    id = Keyword()
    originator = Keyword()
    originatorico = Keyword()
    rok = Integer()
    title = Text(fields={'raw': Keyword()})
    total = Float()
    keyword = Keyword()
    version = Keyword()


class EapFaktura(EapDocument):
    auc = Keyword()
    castkapolozky = Float()
    celkovacastka = Float()
    cislofaktury = Keyword()
    cislosmlouvy = Keyword()
    cisloobjednavky = Keyword()
    contractid = Keyword()
    datumprijeti = Date()
    datumsplatnosti = Date()
    datumuhrady = Date()
    datumvystaveni = Date()
    dodavatel = Text(fields={'raw': Keyword()})
    idpolozky = Integer()
    invoice = Keyword()
    nazevpolozkyrozpoctu = Keyword()
    orderid = Keyword()
    radaevidcislo = Keyword()
    rparagraf = Keyword()
    rpolozka = Keyword()
    suc = Keyword()
    grandtotal = Float()
    ucelplatby = Text(fields={'raw': Keyword()})

    class Index:
        name = INDEX[EAP_DOC_FAKTURA]

    def __init__(self, company=None, meta=None, **kwargs):
        super().__init__(meta=meta, **kwargs)
        self.company = company

    def save(self, **kwargs):
        try:
            self.date_updated = elasticsearch_dsl.datetime.now()
            return super(EapFaktura, self).save(**kwargs)
        except ElasticsearchDslException as err:
            LOG.logger.error("ES {}: {}".format(EAP_DOC_FAKTURA.upper(), err))
            return None

    def load_data_jasu(self, zavazek: JasuZavazek):
        self.auc = zavazek.Auc
        self.castkapolozky = zavazek.CastkaPolozky
        self.celkovacastka = zavazek.CelkovaCastka
        self.cislofaktury = zavazek.CisloFaktury
        self.cisloobjednavky = zavazek.CisloObjednavky
        self.cislosmlouvy = zavazek.CisloSmlouvy
        self.contractid = zavazek.contractid
        self.contractor = zavazek.contractor
        self.datumprijeti = zavazek.DatumPrijeti
        self.datumsplatnosti = zavazek.DatumSplatnosti
        self.datumuhrady = zavazek.DatumUhrady
        self.datumvystaveni = zavazek.DatumVystaveni
        self.dodavatel = zavazek.Dodavatel
        self.form = zavazek.form
        self.ico = zavazek.ICO
        self.id = zavazek.id
        self.idpolozky = zavazek.IdPolozky
        self.invoice = zavazek.invoice
        self.keyword = zavazek.keyword
        self.nazevpolozkyrozpoctu = zavazek.NazevPolozkyRozpoctu
        self.orderid = zavazek.orderid
        self.originator = zavazek.originator
        self.originatorico = zavazek.originatorico
        self.radaevidcislo = zavazek.RadaEvidCislo
        self.rok = zavazek.Rok
        self.rparagraf = zavazek.RParagraf
        self.rpolozka = zavazek.RPolozka
        self.total = zavazek.CastkaPolozky
        self.suc = zavazek.Suc
        self.grandtotal = zavazek.total
        self.ucelplatby = zavazek.UcelPlatby
        self.version = zavazek.version
        self.title = zavazek.UcelPlatby

    def load_data_sql(self, data):
        self.rok = data[0]
        self.cislofaktury = strip_string(data[1])
        self.cislosmlouvy = strip_string(data[2])
        self.cisloobjednavky = strip_string(data[3])
        self.dodavatel = remove_newlines(strip_string(data[4]))
        self.ico = strip_string(data[5])
        self.celkovacastka = data[6]
        self.castkapolozky = data[7]
        self.datumprijeti = data[8]
        self.datumsplatnosti = data[9]
        self.datumuhrady = data[10]
        self.ucelplatby = remove_newlines(strip_string(data[11]))
        self.suc = strip_string(data[12])
        self.rparagraf = strip_string(data[13])
        self.rpolozka = strip_string(data[14])
        self.auc = strip_string(data[15])
        self.nazevpolozkyrozpoctu = strip_string(data[16])
        self.radaevidcislo = strip_string(data[17])
        self.datumvystaveni = data[18]
        self.idpolozky = data[19]

        self.id = '{}-{}-{}'.format(str(self.rok), self.radaevidcislo, str(self.idpolozky))
        self.version = DATA_VERSION
        self.invoice = self.cislofaktury
        self.grandtotal = self.celkovacastka
        self.contractid = self.cislosmlouvy
        self.orderid = self.cisloobjednavky
        self.contractor = self.dodavatel
        self.form = EAP_DOC_FAKTURA
        self.originatorico = CONFIG['jasu'][self.company.lower()][ITEM_ORIGINATOR_ICO]
        self.originator = CONFIG['jasu'][self.company.lower()][ITEM_ORIGINATOR]
        self.keyword = CONFIG['jasu'][self.company.lower()][ITEM_ZAVAZEK][ITEM_KEYWORD]
        self.total = self.castkapolozky
        self.title = self.ucelplatby


class EapObjednavka(EapDocument):
    contractorid = Keyword()
    contractorname = Keyword()
    dateconclusion = Date()
    datevalidity = Date()
    orderid = Keyword()
    radaevidcislo = Keyword()
    valuewithvat = Float()

    class Index:
        name = INDEX[EAP_DOC_OBJEDNAVKA]

    def __init__(self, company=None, meta=None, **kwargs):
        super().__init__(meta=meta, **kwargs)
        self.company = company

    def save(self, **kwargs):
        try:
            self.date_updated = elasticsearch_dsl.datetime.now()
            return super(EapObjednavka, self).save(**kwargs)
        except ElasticsearchDslException as err:
            LOG.logger.error("ES {}: {}".format(EAP_DOC_OBJEDNAVKA.upper(), err))
            return None

    def load_data_jasu(self, o: JasuObjednavka):
        self.contractor = o.contractor
        self.contractorid = o.ContractorId
        self.contractorname = o.ContractorName
        self.dateconclusion = o.DateConclusion
        self.datevalidity = o.DateValidity
        self.form = o.form
        self.ico = o.ico
        self.id = o.id
        self.keyword = o.keyword
        self.orderid = o.OrderId
        self.originator = o.originator
        self.originatorico = o.originatorico
        self.radaevidcislo = o.RadaEvidCislo
        self.rok = o.Rok
        self.title = o.Title
        self.total = o.total
        self.valuewithvat = o.ValueWithVAT
        self.version = o.version

    def load_data_sql(self, data):
        self.rok = data[0]
        self.orderid = strip_string(data[1])
        self.title = strip_string(data[2])
        self.contractorid = strip_string(data[3])
        self.contractorname = strip_string(data[4])
        self.dateconclusion = data[5]
        self.datevalidity = data[6]
        self.valuewithvat = data[7]
        self.radaevidcislo = strip_string(data[8])

        self.id = '{}-{}'.format(str(self.rok), self.radaevidcislo)
        self.version = DATA_VERSION
        self.ico = self.contractorid
        self.contractor = self.contractorname
        self.total = self.valuewithvat
        self.form = 'objednávka'
        self.originatorico = CONFIG['jasu'][self.company.lower()][ITEM_ORIGINATOR_ICO]
        self.originator = CONFIG['jasu'][self.company.lower()][ITEM_ORIGINATOR]
        self.keyword = CONFIG['jasu'][self.company.lower()][ITEM_OBJEDNAVKA][ITEM_KEYWORD]


class EapSmlouva(EapDocument):
    contractid = Keyword()
    contractoraddresscity = Keyword()
    contractoraddressstreet = Keyword()
    contractoraddresszip = Keyword()
    contractorcompany = Keyword()
    contractorid = Keyword()
    contracttitle = Text(fields={'raw': Keyword()})
    contracttype = Keyword()
    dateconclusion = Date()
    datevalidity = Date()
    radaevidcislo = Keyword()
    valuewithvat = Float()

    class Index:
        name = INDEX[EAP_DOC_SMLOUVA]

    def __init__(self, company=None, meta=None, **kwargs):
        super().__init__(meta=meta, **kwargs)
        self.company = company

    def save(self, **kwargs):
        try:
            self.date_updated = elasticsearch_dsl.datetime.now()
            return super(EapSmlouva, self).save(**kwargs)
        except ElasticsearchDslException as err:
            LOG.logger.error("ES {}: {}".format(EAP_DOC_SMLOUVA.upper(), err))
            return None

    def load_data_esmlouvy(self, data):
        self.rok = -1
        self.dateconclusion = None
        dc_iso = consolidate_date(data['DateConclusion'])
        if dc_iso is not None:
            dca = dc_iso.split('-')
            self.dateconclusion = datetime.date(int(dca[0]), int(dca[1]), int(dca[2]))
        self.datevalidity = None
        dv_iso = consolidate_date(data['DateValidity'])
        if dv_iso is not None:
            dva = dv_iso.split('-')
            self.datevalidity = datetime.date(int(dva[0]), int(dva[1]), int(dva[2]))
        self.contractid = data['ContractID']
        self.title = data['Title']
        self.contractorid = data['ContractorID']
        self.contractorcompany = data['ContractorName']
        t: str = str(data['ValueWithVAT'])
        t = t.replace(' ', '')
        t = t.replace('Kč', '')
        t = t.replace(',', '.')
        if not isfloat(t):
            t1 = re.findall(r'\d+', t)
            if t1:
                t = t1[0]
            else:
                t = '-1'
        self.valuewithvat = float(t)
        if self.dateconclusion is not None:
            self.rok = int(dc_iso.split('-')[0])
        self.contracttitle = self.title
        self.contractor = self.contractorcompany
        self.keyword = ["MZP", "MŽP", "smlouva", "OpenData", "MUZO", "JASU", "EKIS"]
        self.form = "smlouva"
        self.ico = self.contractorid
        self.total = str(self.valuewithvat)
        self.originator = "Ministerstvo životního prostředí"
        self.originatorico = "00164801"
        self.id = self.contractid
        self.version = '1'
        # self.id = self.contractid + "_" + dc_iso

    def load_data_jasu(self, smlouva: JasuSmlouva):
        self.contractid = smlouva.ContractId
        self.contractor = smlouva.contractor
        self.contractoraddresscity = smlouva.ContractorAddressCity
        self.contractoraddressstreet = smlouva.ContractorAddressStreet
        self.contractoraddresszip = smlouva.ContractorAddressZip
        self.contractorcompany = smlouva.ContractorCompany
        self.contractorid = smlouva.ContractorId
        self.contracttitle = smlouva.ContractTitle
        self.contracttype = smlouva.ContractType
        self.dateconclusion = smlouva.DateConclusion
        self.datevalidity = smlouva.DateValidity
        self.form = smlouva.form
        self.ico = smlouva.ico
        self.id = smlouva.id
        self.keyword = smlouva.keyword
        self.originator = smlouva.originator
        self.originatorico = smlouva.originatorico
        self.radaevidcislo = smlouva.RadaEvidCislo
        self.rok = smlouva.Rok
        self.title = smlouva.ContractTitle
        self.total = smlouva.total
        self.valuewithvat = smlouva.ValueWithVAT
        self.version = smlouva.version

    def load_data_sql(self, data):

        self.contractid = strip_string(data[1])
        self.contracttitle = strip_string(data[2])
        self.contracttype = strip_string(data[3])
        self.contractorid = strip_string(data[4])
        self.contractorcompany = strip_string(data[5])
        self.contractoraddressstreet = strip_string(data[6])
        self.contractoraddresscity = strip_string(data[7])
        self.contractoraddresszip = strip_string(data[8])
        self.dateconclusion = data[9]
        self.datevalidity = data[10]
        self.valuewithvat = data[11]
        self.radaevidcislo = strip_string(data[12])

        self.id = '{}-{}'.format(str(self.Rok), self.RadaEvidCislo)
        self.version = DATA_VERSION
        self.ico = self.contractorid
        self.contractor = self.contractorcompany
        self.total = self.valuewithvat
        self.form = EAP_DOC_SMLOUVA
        self.originatorico = CONFIG['jasu'][self.company.lower()][ITEM_ORIGINATOR_ICO]
        self.originator = CONFIG['jasu'][self.company.lower()][ITEM_ORIGINATOR]
        self.keyword = CONFIG['jasu'][self.company.lower()][ITEM_SMLOUVA][ITEM_KEYWORD]


def index_date_suffix(index):
    index += '-' + elasticsearch_dsl.date.today().isoformat().replace('-', '.')
    return index


def store_data_jasu(company=None, data_source=None, data=None, host=ES_HOST):
    out = False
    if data is None:
        return out
    data_source = data_source.lower()
    if data_source not in [ITEM_OBJEDNAVKA, ITEM_SMLOUVA, ITEM_ZAVAZEK]:
        return out
    factory = ElasticFactory(hosts=host)
    if data_source == ITEM_OBJEDNAVKA:
        out = factory.store_jasu_objednavky(company=company, jasu_data=data)
    elif data_source == ITEM_SMLOUVA:
        out = factory.store_jasu_smlouvy(company=company, jasu_data=data)
    elif data_source == ITEM_ZAVAZEK:
        out = factory.store_jasu_faktury(company=company, jasu_data=data)
    del factory
    return out


def remove_index(data_source=None, host=ES_HOST):
    if data_source not in INDEX_DICTIONARY:
        return False
    factory = ElasticFactory(hosts=host)
    factory.clear_index(INDEX_DICTIONARY[data_source])
    del factory
    return True


def print_dot(counter):
    counter += 1
    if counter <= 100:
        print(".", end="")
    else:
        print(".")
        counter = 0
    return counter


def print_last_dot():
    print(".")
