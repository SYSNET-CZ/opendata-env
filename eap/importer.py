#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         importer
# Purpose:      Import MUZO data to Elasticsearch
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2022
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------
import getopt
import sys

from elastic import store_data_jasu
from jasu import load_data, DATASET_MAP
from settings import LOG, CONFIG


def import_jasu(company, data_source):
    company = company.upper()
    data_source = data_source.lower()
    if data_source not in DATASET_MAP:
        LOG.logger.error('Data slource {} is invalid'.format(data_source))
        return False
    data_source = DATASET_MAP[data_source]
    data = load_data(company=company, data_source=data_source)
    if data is None:
        LOG.logger.warning('No data impoerted from JASU')
        return False
    if store_data_jasu(company=company, data_source=data_source, data=data):
        LOG.logger.info('For {} imported data {} ({})'.format(company.upper(), data_source.upper(), len(data)))
        return True
    LOG.logger.error('Import failed for {} data {} ({})'.format(company.upper(), data_source.upper(), len(data)))
    return False


def import_jasu_all():
    for company in CONFIG['jasu'].keys():
        for data_source in DATASET_MAP.keys():
            import_jasu(company=company, data_source=data_source)
            LOG.logger.info('Import JASU done: {}/{}'.format(company, data_source))


def main(argv):
    company = None
    doctype = None
    # year = None
    # output_path = None
    help_string = 'Usage: importer.py --company=<company> --doc-type=<doctype> --all'
    help_string += '\nUse importer.py -h for help'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['company=', 'doc-type=', 'all'])

    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
    test_value = False
    all_imports = False
    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit()
        elif opt in ("-c", "--company"):
            company = arg
        elif opt in ("-d", "--doc-type"):
            doctype = arg
        elif opt in ("-a", "--all"):
            all_imports = True

    msg = 'company: {} | doctype: {} | all: {}'.format(
        company, doctype, all_imports
    )
    LOG.logger.info(msg=msg)
    out = False
    if all_imports:
        import_jasu_all()
        out = True
        # print('out = import_jasu_all()')
    else:
        import_jasu(company=company, data_source=doctype)
        out = True
        # print('out = import_jasu(company=company, data_source=doctype)')
    if not out:
        print(help_string)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])
