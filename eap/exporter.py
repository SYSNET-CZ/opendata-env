#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         export
# Purpose:      Export MUZO opendata from Elasticsearch
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2020
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------

import codecs
import csv
import getopt
import numbers
import os
import sys
from datetime import datetime

from dateutil.parser import parse
from elasticsearch import Elasticsearch, TransportError, ElasticsearchException
from elasticsearch_dsl import Search

from defaults import DATASOURCE_DOCTYPE_FAKTURA, DATASOURCE_DOCTYPE_OBJEDNAVKA, DATASOURCE_DOCTYPE_SMLOUVA, \
    DATASOURCE_INDEX_V1, DATASOURCE_FIELDNAMES, DATASOURCE_SORTITEM_V1, DATASOURCE_FILENAME, DATASOURCE_INDEX_V2
from elastic import ElasticFactory
from settings import CSV_FILE_SUFFIX, CSV_OUTPUT_DIRECTORY, ES_HOST, LOG, EXPORT_DATA_DIR, CONFIG


def consolidate_date(date_str):
    out = ''
    try:
        if (date_str is not None) and (date_str != ''):
            d = parse(date_str)
            if d.year > 2200:
                d = d.replace(year=2199)
            out = d.astimezone().date().isoformat()

    except (OSError, ValueError) as err:
        LOG.logger.error('consolidate_date {}: {} {}'.format(date_str, type(err), err))
        out = 'DATE ERROR: ' + date_str
    return out


def safe_read_item(data, attribute):
    if hasattr(data, attribute):
        return getattr(data, attribute)
    # return '-MISSING-'
    return None


def remove_newlines(input_string):
    if input_string is None:
        return ''
    out = input_string.replace("\r", " ")
    out = out.replace("\n", " ")
    return out


def format_float(input_number):
    if input_number is None:
        return ""
    elif not isinstance(input_number, numbers.Number):
        return ""
    return "%.2f" % input_number


def add_utf8_bom(filename):
    f = codecs.open(filename, 'r', 'utf-8')
    content = f.read()
    f.close()
    f2 = codecs.open(filename, 'w', 'utf-8')
    f2.write(u'\ufeff')
    f2.write(content)
    f2.close()


def export_data_source(company, doctype, year=None, path=EXPORT_DATA_DIR, version='2'):
    # print("export_data_source", "START")
    if company is None:
        LOG.logger.error('export_data_source: {}'.format('company is None'))
        return None
    company = company.lower()
    if company not in CONFIG['data_source']:
        LOG.logger.error('export_data_source: {} {}'.format('illegal company', company))
        return None
    if doctype is None:
        LOG.logger.error('export_data_source: {}'.format('doctype is None'))
        return None
    setting = CONFIG['data_source'][company]
    doctype = doctype.lower()
    if doctype not in setting:
        LOG.logger.error('export_data_source: {} {}'.format('illegal doctype', doctype))
        return None
    LOG.logger.info('export_data_source: {}'.format('create exporter'))
    if path is None:
        path = EXPORT_DATA_DIR
    exporter = ExporterFactory(company=company, doctype=doctype, year=year, path=path)
    LOG.logger.info('export_data_source: {}, version {}'.format('export data', version))
    exporter.export_data()
    LOG.logger.info('export_data_source: {}'.format('delete exporter'))
    out = exporter.file
    del exporter
    return out


def get_latest_index(index_pattern, client=None):
    close_client = False
    if client is None:
        client = Elasticsearch()
        close_client = True
    LOG.logger.info('GET LATEST INDEX: {}, {}'.format(index_pattern, client.info))
    # indices = sorted(client.indices.get_alias(index_pattern).keys(), reverse=True)
    indices = client.indices.get_alias(index_pattern).keys()
    if indices is None:
        LOG.logger.error('GET LATEST INDEX: {}, {}'.format(index_pattern, 'indices is None'))
        if close_client:
            if client is not None:
                client.transport.close()
                del client
        return None
    if bool(indices):
        LOG.logger.error('GET LATEST INDEX: {}, {}'.format(index_pattern, 'indices is empty'))
        if client is not None:
            client.transport.close()
            del client
        return None
    LOG.logger.info('GET LATEST INDEX: {}, {}'.format(index_pattern, indices[0]))
    index = indices[0]
    if client is not None:
        client.transport.close()
        del client
    return index


class ExporterFactory:
    def __init__(self, company, doctype, year=None, path=None, version='2'):
        self.index = None
        self.index_pattern = None
        self.done = False
        self.from_item = 1
        self.buffer_size = CONFIG['exporter']['buffer']
        self.total = 0
        self.hits = None
        self.writer = None
        self.file = None
        # self.client = Elasticsearch(ES_HOST)
        self.factory = ElasticFactory(ES_HOST)
        self.filename = None
        self.search = None
        self.sort_item = None
        self.company = company.lower()
        self.doctype = doctype.lower()
        self.year = year
        self.version = version
        self.init_output(path=path)
        self.init_search()
        # self.factory.init_search(company=self.company, doctype=self.doctype, year=self.year)
        LOG.logger.info('Exporter created')

    def init_output(self, path):
        ds = CONFIG['data_source']
        self.filename = ds[self.company][self.doctype][DATASOURCE_FILENAME]
        # self.filename = self.company + '-' + self.doctype
        if self.year is not None:
            self.filename += '_' + str(self.year)
        self.filename += CSV_FILE_SUFFIX
        if path is None:
            if CSV_OUTPUT_DIRECTORY is not None:
                if CSV_OUTPUT_DIRECTORY != '':
                    self.filename = os.path.join(CSV_OUTPUT_DIRECTORY, self.filename)
        else:
            self.filename = os.path.join(path, self.filename)
        self.file = open(self.filename, 'w', encoding='utf-8', newline='')
        self.writer = csv.DictWriter(
            self.file, fieldnames=ds[self.company][self.doctype][DATASOURCE_FIELDNAMES]
        )
        LOG.logger.info('Exporter {}, {}'.format('file', self.file.name))
        self.writer.writeheader()

        if self.version == '2':
            self.index_pattern = ds[self.company][self.doctype][DATASOURCE_INDEX_V2]
        else:
            self.index_pattern = ds[self.company][self.doctype][DATASOURCE_INDEX_V1]
        LOG.logger.info('Exporter {}, {}'.format('index_pattern', self.index_pattern))
        self.index = self.get_latest_index(self.index_pattern)

    def init_search(self):
        if self.index is not None:
            ds = CONFIG['data_source']
            LOG.logger.info('Exporter {}, {}'.format('index', self.index))
            self.sort_item = ds[self.company][self.doctype][DATASOURCE_SORTITEM_V1]
            LOG.logger.info('Exporter {}, {}'.format('sort_item', self.sort_item))
            self.search = Search(using=self.factory.client, index=self.index) \
                .sort({self.sort_item: {"order": "asc"}})
            if self.year is not None:
                self.search = Search(using=self.factory.client, index=self.index) \
                    .query("match", rok=self.year) \
                    .sort({self.sort_item: {"order": "asc"}})
        else:
            LOG.logger.error('Exporter {}, {}'.format(self.index_pattern, 'Index neexistuje'))

    def get_latest_index(self, index_pattern):
        # print('Exporter.get_latest_index', index_pattern, str(self.client.info()))
        out = None
        try:
            indices = self.factory.client.indices.get_alias(index_pattern).keys()
            if indices is None:
                LOG.logger.error('Exporter.get_latest_index {}, {}'.format(index_pattern, 'indices is None'))
                self.index = None
            elif not bool(indices):
                LOG.logger.error('Exporter.get_latest_index {}, {}'.format(index_pattern, 'indices is empty'))
                self.index = None
            else:
                indices_list = list(indices)
                indices_list.sort(reverse=True)
                # print('Exporter.get_latest_index', index_pattern, indices_list[0])
                self.index = indices_list[0]
                out = self.index

        except (TransportError, ElasticsearchException) as err:
            LOG.logger.error('Exporter.get_latest_index {}, {}'.format(type(err), err))
            self.index = None
            out = None

        return out

    def close(self, bom=True):
        if self.factory.client is not None:
            # self.client.transport.close()
            # del self.client
            del self.factory
        self.close_csv_file(bom=bom)
        LOG.logger.info('Exporter.close {}'.format('Object Exporter closed'))

    def close_csv_file(self, bom=True):
        if self.file is not None:
            self.file.flush()
            self.file.close()
        if bom:
            add_utf8_bom(self.filename)

    def __del__(self):
        self.close()
        LOG.logger.info('Exporter destroyed')

    def export_data(self):      # hlavní procedura
        if self.index is None:
            return
        error_occured = False
        while not self.done:
            LOG.logger.info('Exporter.export_data company={}, doctype={}, year={}, index={}'.format(
                self.company, self.doctype, self.year, self.index))
            if self.version == '2':
                LOG.logger.info('Load data version 2')
                loaded = self.factory.load_data(company=self.company, doctype=self.doctype, year=self.year)
                self.hits = self.factory.hits
                self.done = self.factory.done
            else:
                LOG.logger.info('Load data version 1')
                loaded = self.load_data_from_eap()
            if loaded:
                self.add_hits()
                LOG.logger.info('Exporter.export_data {}, {}, exportováno: {}'.format(
                    self.company, self.doctype, self.total
                ))
            else:
                error_occured = True
                LOG.logger.error('Exporter.export_data {}, {}, {}'.format(self.company, self.doctype, 'CHYBA EXPORTU'))
                break
        if not error_occured:
            LOG.logger.info('Exporter.export_data {}, {}, {} {}'.format(
                self.company, self.doctype, 'export dokončen. Celkem: ', self.total))
        else:
            LOG.logger.error('Exporter.export_data {}, {}, {} {}'.format(
                self.company, self.doctype, 'export dokončen s chybou. Celkem: ', 0
            ))

    def load_data_from_eap(self):
        out = False
        if self.index is None:
            return out
        try:
            if self.done:
                LOG.logger.info('Exporter.load_data_from_eap {}'.format('DONE'))
            else:
                # print('Exporter.load_data_from_eap', 'SCAN EAP START ...')
                self.hits = self.search.scan()
                self.done = True
                out = True
                # print('Exporter.__load_data_from_eap', '... SCAN EAP FINISHED')
        except (TransportError, ElasticsearchException) as err:
            LOG.logger.error('Exporter.load_data_from_eap {} {}'.format(type(err), err))
            out = False
        return out

    def add_hits(self):
        if self.index is None:
            return
        if self.hits is not None:
            count = 0
            for hit in self.hits:
                if self.doctype == DATASOURCE_DOCTYPE_FAKTURA:
                    self.writer.writerow({
                            'cislo_smlouvy': safe_read_item(hit, 'cislosmlouvy'),
                            'cislo_objednavky': safe_read_item(hit, 'cisloobjednavky'),
                            'dodavatel': remove_newlines(safe_read_item(hit, 'dodavatel')),
                            'ico': safe_read_item(hit, 'ico'),
                            'cislo_faktury': safe_read_item(hit, 'cislofaktury'),
                            'datum_vystaveni': consolidate_date(safe_read_item(hit, 'datumvystaveni')),
                            'datum_prijeti': consolidate_date(safe_read_item(hit, 'datumprijeti')),
                            'datum_splatnosti': consolidate_date(safe_read_item(hit, 'datumsplatnosti')),
                            'datum_uhrady': consolidate_date(safe_read_item(hit, 'datumuhrady')),
                            'celkova_castka': format_float(safe_read_item(hit, 'celkovacastka')),
                            'castka_polozky': format_float(safe_read_item(hit, 'castkapolozky')),
                            'mena': 'CZK',
                            'ucel_platby': remove_newlines(safe_read_item(hit, 'ucelplatby')),
                            'polozka_rozpoctu': safe_read_item(hit, 'rpolozka'),
                            'nazev_plozky_rozpoctu': remove_newlines(safe_read_item(hit, 'nazevpolozkyrozpoctu')),
                            'kapitola': '315',
                            'nazev_kapitoly': 'Ministerstvo životního prostředí'
                        }
                    )
                elif self.doctype == DATASOURCE_DOCTYPE_OBJEDNAVKA:
                    self.writer.writerow(
                        {
                            'cislo_objednavky': safe_read_item(hit, 'radaevidcislo'),
                            'popis': remove_newlines(safe_read_item(hit, 'title')),
                            'dodavatel': remove_newlines(safe_read_item(hit, 'contractorname')),
                            'ico': safe_read_item(hit, 'contractorid'),
                            'datum_objednani': consolidate_date(safe_read_item(hit, 'dateconclusion')),
                            'datum_dodani': consolidate_date(safe_read_item(hit, 'datevalidity')),
                            'celkova_castka': format_float(safe_read_item(hit, 'valuewithvat')),
                            'mena': 'CZK'
                        }
                    )
                elif self.doctype == DATASOURCE_DOCTYPE_SMLOUVA:
                    dv = ''
                    if 'datevalidity' in hit:
                        dv = consolidate_date(safe_read_item(hit, 'datevalidity'))
                    self.writer.writerow(
                        {
                            'cislo_smlouvy': safe_read_item(hit, 'contractid'),
                            'predmet': remove_newlines(safe_read_item(hit, 'contracttitle')),
                            'dodavatel': remove_newlines(safe_read_item(hit, 'contractorcompany')),
                            'ico': safe_read_item(hit, 'contractorid'),
                            'datum_uzavreni': consolidate_date(safe_read_item(hit, 'dateconclusion')),
                            'datum_trvani': dv,
                            'celkova_castka': format_float(safe_read_item(hit, 'valuewithvat')),
                            'mena': 'CZK'
                        }
                    )
                count += 1
                print(".", end='')
            self.total = count
            print(" ")


def export_all_data(year=None, path=EXPORT_DATA_DIR, version='2'):
    ds = CONFIG['data_source']
    for company in ds.keys():
        for doctype in ds[company]:
            out = export_data_source(company=company, doctype=doctype, year=year, path=path, version=version)
            if out is not None:
                LOG.logger.info('Datasource {}/{} stored to {}'.format(company, doctype, out))
            else:
                LOG.logger.error('Datasource {}/{} failed to store'.format(company, doctype))


def main(argv):
    company = None
    doctype = None
    year = None
    output_path = None
    help_string = 'Usage: exporter.py --company=<company> --doc-type=<doctype> --year=<year> ' \
                  '--output-path=<path> --version=<version> --all'
    help_string += '\nUse exporter.py -h for help'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['company=', 'doc-type=', 'year=', 'output-path=', 'version=', 'all'])

    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
    version = '1'
    all_exports = False
    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit()
        elif opt in ("-c", "--company"):
            company = arg
        elif opt in ("-d", "--doc-type"):
            doctype = arg
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-p", "--output-path"):
            output_path = arg
        elif opt in ("-v", "--version"):
            version = arg
        elif opt in ("-a", "--all"):
            all_exports = True

    msg = 'company: {} | doctype: {} | year: {} | path: {} | version: {} | all: {}'.format(
        company, doctype, year, output_path, version, all_exports
    )
    LOG.logger.info(msg=msg)
    if all_exports:
        years = [str(datetime.now().year), str(datetime.now().year-1), str(datetime.now().year-2)]
        for y in years:
            export_all_data(year=y)
        export_all_data()
    else:
        if not export_data_source(company=company, doctype=doctype, year=year, path=output_path, version=version):
            print(help_string)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])
