#!/usr/bin/env python

# minimal example using Kerberos auth
import sys
import os
import re
import pyodbc
import pandas as pd
import json
import requests
from requests.sessions import Session
import time
import datetime
import dask.dataframe as dd
from dask.multiprocessing import get
from pandarallel import pandarallel
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, local


thread_local = local()

q = []


def loopData(df):
    loopstart = time.time()
    for index, row in df.iterrows():
        qty = row['qty']
        sku = row['sku']
        # print(qty)
        # print(sku)
        if qty == 0:
            # print('qty is 0')
            payload = '''{
              "product": {
                "sku": null,
                "extension_attributes": {
                  "stock_item": {
                    "qty": null,
                    "is_in_stock": false
                  }
                }
              }
            }'''
            # print('payload template set')
            y = json.loads(payload)
            y['product']['sku'] = sku
            y['product']['extension_attributes']['stock_item']['qty'] = qty
            # print(y)
            q.append(y)
        if qty > 0:
            # print('qty is not 0')
            payload = '''{
              "product": {
                "sku": null,
                "extension_attributes": {
                  "stock_item": {
                    "qty": null,
                    "is_in_stock": true
                  }
                }
              }
            }'''
            # print('payload template set')
            y = json.loads(payload)
            y['product']['sku'] = sku
            y['product']['extension_attributes']['stock_item']['qty'] = qty
            # print(y)
            q.append(y)


def get_session() -> Session:
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session


def sendData(y):
    start = time.time()
    session = get_session()
    with session as session:
        response = session.post(api_url, headers=headers, json=y)

        if response.status_code == 200:
            pass
        if response.status_code == 400:
            pass
        if response.status_code != 200 and response.status_code != 400:
            # print('FFFFFF')
            while response.status_code != 200 and response.status_code != 400:
                # print('retrying...')
                time.sleep(2)
                response = session.post(api_url, headers=headers, json=y)
                # print(response.status_code)
        end = time.time()

        log = pd.Series([response.status_code, howLong(start, end)])
        pd.concat([logdf, log])
        global count
        global total
        count = count + 1
        # print(count/total)


def morehands() -> None:
    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(sendData, q)


def howLong(start, end):
    final = end - start
    return final


def localpull():
    # driver='{ODBC Driver 13 for SQL Server}'
    server = "WIN-PBL82ADEL98.HDLUSA.LAN,49816,49816"
    database = "HDL"
    driver_name = ''
    driver_names = [x for x in pyodbc.drivers()]
    if driver_names:
        driver_name = driver_names[0]
    if driver_name:
        conn_str = 'DRIVER={}; ...'.format(driver_name)
        # then continue with ...
        # pyodbc.connect(conn_str)
        # ... etc.
        # print(conn_str)
        try:
            cnxn = pyodbc.connect(driver=driver_name, server=server, database=database, trusted_connection='yes')
            cursor = cnxn.cursor()
        except pyodbc.Error as ex:
            msg = ex.args[1]
            if re.search('No Kerberos', msg):
                print('You must login using kinit before using this script.')
                exit(1)
            else:
                raise

        # Sample select query
        # print('running query...')

        query = """select * from openquery ([HDL-WAREHOUSE],'select MASTER_STOCKNO,MASTER_QOH from wlib.dbo.master')"""

        cursor.execute(query)
        row = cursor.fetchall()
        final = pd.read_sql(query, cnxn)
        cnxn.close()
        # print('success')
        # print('processing...')
        final.rename(columns={"MASTER_STOCKNO": "sku", "MASTER_QOH": "qty"}, inplace=True)
        # print(final)
        # print('done')
        return final
    else:
        print('(No suitable driver found. Cannot connect.)')
    # trusted_connection uses kerberos ticket and ignores UID and PASSWORD in connection string
    # https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/using-integrated-authentication?view=sql-server-ver15


final = localpull()
api_url = 'https://www.wwhardware.com/rest/V1/products'

count = 0
headers = {'Authorization': 'Bearer 2qlm7ls28dzzv1afeoieda7ood5j6137'}
logdf = pd.DataFrame(columns=['response code', 'time'])

start = time.time()
loopData(final)
total = len(q)
morehands()

end = time.time()


now = datetime.datetime.now()
f = open(f"{now} out.txt", "w")
f.write(f'last uploaded {len(q)} products in {end - start} seconds on {now}')
f.close()
logdf.to_csv(f'/home/ftp/logs/{now} log.csv')



print(f'last uploaded {len(q)} products in {end - start} seconds on {now}')

# https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/using-integrated-authentication?view=sql-server-ver15

