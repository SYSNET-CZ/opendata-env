#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         parky
# Purpose:      Import opendata from web to EAP
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2020
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------

"""
Správa Krkonošského národního parku - https://opendata.krnap.cz/
Správa Národního parku České Švýcarsko - https://opendata.nppodyji.cz/
Správa Národního parku Podyjí - https://opendata.nppodyji.cz/
Správa Národního parku Šumava - https://opendata.npsumava.cz/
"""
import csv
import os
import shutil
from urllib.error import URLError

import urllib3
from urllib3.exceptions import HTTPError

URL_CSV_KRNAP_SMLOUVY = "https://opendata.krnap.cz/smlouvy.php?export=csv"
URL_CSV_KRNAP_FAKTURY = "https://opendata.krnap.cz/faktury.php?export=csv"
TEMP_FILE_NAME = "data.csv"


def download_csv_file(url, file_name=TEMP_FILE_NAME):
    try:
        http = urllib3.PoolManager()
        if os.path.exists(file_name):
            os.remove(file_name)
        with http.request('GET', url, preload_content=False) as resp, open(file_name, 'wb') as out_file:
            print(resp.status)
            if resp.status == 200:
                shutil.copyfileobj(resp, out_file)
            else:
                print(resp.status)
                file_name = ""
        resp.release_conn()  # not 100% sure this is required though
        return file_name
    except (HTTPError, URLError) as e:
        print(str(e))
        return ""


def re_encode(file_name):
    for line in file_name:
        yield line.decode('windows-1250').encode('utf-8')


# InvoiceID;ContractID;Description;ContractorID;ContractorCompany;ValueWithoutVAT;DatePayment
def read_csv_file(file_name):
    with open(file_name, mode="r", encoding="windows-1250") as csvfile:
        # reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        reader = csv.DictReader(csvfile, dialect='excel', delimiter=';', quotechar='"')
        for row in reader:
            print(row)
