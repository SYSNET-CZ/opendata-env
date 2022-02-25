#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         esmlouvy
# Purpose:      Import opendata from eSmouvy to EAP
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2020
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------

import getopt
import sys

import requests
from requests import RequestException

from elastic import EapSmlouva, ElasticFactory
from settings import ES_HOST, CONFIG

# URL_JSON = CONFIG['esmlouvy']['mzp']['json']
# URL_CSV = CONFIG['esmlouvy']['mzp']['csv']


def import_esmlouvy(host=ES_HOST):
    try:
        url = CONFIG['esmlouvy']['mzp']['json']
        # index += '-' + elasticsearch_dsl.date.today().isoformat().replace('-', '.')
        index = CONFIG['data_source']['mzp']['smlouva']['index']
        r = requests.get(url)
        json = r.json()
        count = json["total"]
        # success = json["success"]
        data = json["data"]
        n = 0
        if data is not None:
            factory = ElasticFactory(hosts=host)
            factory.clear_index(index=index)
            dot = 0
            for sml in data:
                sml_es = EapSmlouva()
                sml_es.load_data_esmlouvy(sml)
                doc_id = sml_es.id
                sml_es.meta.id = doc_id
                sml_es.save(using=factory.client, index=index)
                dot += 1
                n += 1
                if dot <= 100:
                    print(".", end="")
                else:
                    print(".")
                    dot = 0
            del factory
        print("Hotovo", 'pocet', count, 'nahrano', n, 'index', index)
        return True
    except RequestException as err:
        print("CHYBA: {0}".format(err))
        return False


def main(argv):
    url_json = CONFIG['esmlouvy']['mzp']['json']
    es_host = ES_HOST
    index = CONFIG['data_source']['mzp']['smlouva']['index']
    help_string = 'Usage: esmlouvy.py ' \
                  '--url-json=<esmlouvy json source> --es-host=<elasticsearch hostname:port> --index=<EAP index>'
    help_string += '\nUse esmlouvy.py -h for help'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['url-json=', 'es-host=', 'index='])

    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit()
        elif opt in ("-u", "--url-json"):
            url_json = arg
        elif opt in ("-e", "--es-host"):
            es_host = arg
        elif opt in ("-i", "--index"):
            index = arg

    print('url_json:', url_json, '|', 'es_host:', es_host, '|', 'index:', index)

    if not import_esmlouvy(host=es_host):
        print(help_string)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])
