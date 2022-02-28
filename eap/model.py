# unused - test only
import datetime
import re

from elasticsearch_dsl import Document, Keyword, Text, Date, Integer, Float
from elasticsearch_dsl.exceptions import ElasticsearchDslException

INDEX_MZP_SMLOUVA = "muzo-mzp-smlouva"
INDEX_XXX_SMLOUVA = "muzo-xxx-smlouva"
INDEX_XXX_FAKTURA = "muzo-xxx-faktura"

KEYWORD_MZP_SMLOUVA = ["MZP", "MŽP", "smlouva", "OpenData", "MUZO", "JASU", "EKIS"]
KEYWORD_XXX_SMLOUVA = ["MZP", "MŽP", "smlouva", "OpenData"]
KEYWORD_XXX_FAKTURA = ["MZP", "MŽP", "faktura", "OpenData"]
VAT = 0.21

TEST_SMLOUVA = {
    'ContractID': 'OBJ-24-1262/2015',
    'ContractTitle': 'Objednávka oprava vodoinstalace Temný Důl čp. 1 inspekční pokoj. Kontakt. L. Sedláček.',
    'ContractType': 'SMLJ',
    'ContractorID': '74824945',
    'ContractorCompany': 'Vojtěch Matuška',
    'ContractorName': '',
    'ContractorAddressStreet': 'Mladé Buky 65',
    'ContractorAddressCity': 'Mladé Buky',
    'ContractorAddressZIP': '54223',
    'DateConclusion': '21. 12. 2015',
    'DateValidity': '31. 12. 2015',
    'Duration': 'doba určitá',
    'ValueWithoutVAT': '661'}


class SmlouvaUnused(Document):
    contractid = Keyword()
    contractor = Keyword()
    contractoraddresscity = Keyword()
    contractoraddressstreet = Keyword()
    contractoraddresszip = Keyword()
    contractorcompany = Keyword()
    contractorid = Keyword()
    contracttitle = Text(fields={'raw': Keyword()})
    contracttype = Keyword()
    dateconclusion = Date()
    datevalidity = Date()
    date_updated = Date()
    form = Keyword()
    ico = Keyword()
    id = Keyword()
    keyword = Keyword()
    originator = Keyword()
    originatorico = Keyword()
    radaevidcislo = Keyword()
    rok = Integer()
    title = Text(fields={'raw': Keyword()})
    total = Keyword()
    valuewithvat = Float()
    valuewithoutvat = Float()

    def __init__(self, index=INDEX_XXX_SMLOUVA, keywords=None, **kwargs):
        super().__init__(**kwargs)
        if keywords is None:
            keywords = KEYWORD_XXX_SMLOUVA
        self.__index = index
        self.__keywords = keywords

    class Index:
        name = INDEX_XXX_SMLOUVA

    def save(self, **kwargs):
        try:
            self.date_updated = datetime.datetime.now()
            return super(SmlouvaUnused, self).save(**kwargs)
        except ElasticsearchDslException as err:
            print("CHYBA ES: {0}".format(err))
            return None

    def load_csv_row(self, row):
        self.rok = -1
        self.dateconclusion = None
        dc_iso = date_cz_to_iso(row['DateConclusion'])
        if dc_iso is not None:
            dca = dc_iso.split('-')
            self.dateconclusion = datetime.date(int(dca[0]), int(dca[1]), int(dca[2]))
        self.datevalidity = None
        dv_iso = date_cz_to_iso(row['DateValidity'])
        if dv_iso is not None:
            dva = dv_iso.split('-')
            self.datevalidity = datetime.date(int(dva[0]), int(dva[1]), int(dva[2]))
        self.contractid = row['ContractID']
        self.title = row['ContractTitle']
        self.contractorid = row['ContractorID']
        self.contractorcompany = row['ContractorCompany']
        t: str = str(row['ValueWithoutVAT'])
        t = t.replace(' ', '')
        t = t.replace('Kč', '')
        t = t.replace(',', '.')
        if not isfloat(t):
            t1 = re.findall(r'\d+', t)
            if t1:
                t = t1[0]
            else:
                t = '-1'
        self.valuewithoutvat = float(t)
        if self.dateconclusion is not None:
            self.rok = int(dc_iso.split('-')[0])
        else:
            if self.contractid is not None:
                ci = str(self.contractid).split("/")
                if len(ci) > 1:
                    self.rok = int(ci[len(ci) - 1])
        self.contracttitle = self.title
        self.contractor = self.contractorcompany
        self.keyword = self.__keywords
        self.form = "smlouva"
        self.ico = self.contractorid
        self.total = str(self.valuewithvat)
        self.originator = "Ministerstvo životního prostředí"
        self.originatorico = "00164801"
        self.id = self.contractid

    def load_data(self, data):
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
        self.valuewithoutvat = self.valuewithvat / (1 + VAT)
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
        # self.id = self.contractid + "_" + dc_iso


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def consolidate_date(value: str):
    if value is None:
        return None
    date_string_iso = None
    value_array = value.split(' ')
    date_string = value_array[0]
    d = date_string.split('.')
    if d:
        if len(d) == 3:
            if len(d[2]) < 4:  # je rok mensi nez 2000?
                date_string_iso = '19' + d[2] + '-' + d[1] + '-' + d[0]
            else:
                date_string_iso = d[2] + '-' + d[1] + '-' + d[0]
    return date_string_iso


def date_cz_to_iso(value: str):
    if value is None:
        return None
    elif value == "":
        return None
    date_string_iso = None
    value_array = value.split('. ')
    if len(value_array) == 3:
        date_string_iso = value_array[2] + "-" + value_array[1] + "-" + value_array[0]
    return date_string_iso
