#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         upload
# Purpose:      Upload MUZO opendata datasets to CKAN
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2020
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------
import datetime
import glob
import os

from defaults import DATASOURCE_COMPANIES, DATASOURCE_CKAN, DATASOURCE_CKAN_SCHEME, CKAN_FORMAT_SCHEMA
from eap.settings import FILENAMES_DICTIONARY, LOG, CONFIG


def upload_all(data_path='.'):
    file_list = glob.glob(os.path.join(data_path, "*.csv"))
    for file_name in file_list:
        company = parse_company(file_name=file_name)
        doctype = parse_doctype(file_name=file_name)
        year = parse_year(file_name=file_name)
        if (year is None) or (company == '') or (doctype == ''):
            print("upload_all", "CHYBA", "chybný název souboru", file_name)
            pass
        else:
            file_path = os.path.join(data_path, file_name)
            print("upload_all", "OK", company, doctype, year, file_path)
            upload_file(company=company, doctype=doctype, year=year, data_path=file_path)


def parse_company(file_name: str):
    if file_name is None:
        return ''
    elif any(company in file_name for company in DATASOURCE_COMPANIES):
        for company in DATASOURCE_COMPANIES:
            if company in file_name:
                return company
    else:
        return ''


def parse_doctype(file_name: str):
    if file_name is None:
        return ''
    elif any(fname in file_name for fname in list(FILENAMES_DICTIONARY.keys())):
        for fname in list(FILENAMES_DICTIONARY.keys()):
            if fname in file_name:
                return FILENAMES_DICTIONARY[fname]
    else:
        return ''


def parse_file_name(file_name: str):
    if file_name is None:
        return ''
    elif any(fname in file_name for fname in list(FILENAMES_DICTIONARY.keys())):
        for fname in list(FILENAMES_DICTIONARY.keys()):
            if fname in file_name:
                return fname
    else:
        return ''


def parse_year(file_name: str):
    out = datetime.datetime.today().year
    xx = file_name.split('_')[-1]
    if len(xx) != 14:
        return None
    yc = file_name.split('_')[-2]
    if yc.isnumeric():
        out = int(yc)
    return out


def upload_file(company, doctype, year, data_path):
    datasource_ckan = CONFIG['data_source'][company][doctype][DATASOURCE_CKAN]
    ident = None
    for c in datasource_ckan:
        if ('default' in c) and (ident is None):
            ident = c['default']
        elif str(year) in c:
            ident = c[str(year)]
    if ident is None:
        LOG.logger.error('Datasource {}/{} is not catalogized.'.format(company, doctype))
        return
    scheme = CONFIG['data_source'][company][doctype][DATASOURCE_CKAN_SCHEME]
    data = {
        "id": ident,
        "license_link": CONFIG['ckan']['license'],
        "describedBy": scheme,
        "describedByType": CKAN_FORMAT_SCHEMA
    }
    headers = {"X-CKAN-API-Key": CONFIG['ckan']['api_key']}
    files = [('upload', open(data_path, 'r', encoding='utf-8'))]
    # requests.post(CONFIG['ckan']['endpoint'], data=data, headers=headers, files=files)
    print(CONFIG['ckan']['endpoint'])
    print(data)
    print(headers)
    print(files)
    LOG.logger.info('Datasource {}/{} update in the catalog {}.'.format(company, doctype, ident))
