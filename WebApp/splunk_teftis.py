#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ALP CANER SATI, Haziran 2021

import requests
import time
import json
import pandas
import os
import shutil
import datetime
import time
import concurrent.futures

def query(file_name:str,query:str,dates:str):
    """Verilen query ve dates'lere göre Splunk'da eş zamanlı olarak sorgulatılır ve sonucunu file_name isminde zipli dosya olarak kaydeder. İçinde belirtilen date'lere göre log sonuçları .xlsx dosyaları vardır."""
    if os.path.exists(f"./results\\{file_name}"):
        shutil.rmtree(f"./results\\{file_name}")
        time.sleep(2)
        # os.rmdir(f"./results\\{file_name}")
        os.mkdir(f"./results\\{file_name}")
    else:
        os.mkdir(f"./results\\{file_name}")

    dates = dates.split(",")
    requests.packages.urllib3.disable_warnings()

    def task(i):
        api_token = "Bearer {}".format(json.load(open('config.json'))['api_token'])
        url = json.load(open('config.json'))['splunk_server']+"/services/search/jobs"
        header = {"Authorization": api_token} 
        query_new = f"search (earliest=\"{i}:00:00:00\" latest=\"{i}:24:00:00\") " + query
        api_data = {"search": query_new }
        api_parameters = {"count": 30000,"output_mode": "json"}
        res = requests.post(url=url, headers=header, verify=False, params=api_parameters, data=api_data)
        api_sid = json.loads(res.text)["sid"]
        url3 = json.load(open('config.json'))['splunk_server']+"/services/search/jobs/{}".format(api_sid)
        with requests.session() as r:
            dispatchState = -1     #".find" metodu yanlışsa -1 döndürür. 
            while (dispatchState == -1):
                re = r.get(url=url3, headers=header, verify=False)
                dispatchState = re.text.find('"dispatchState">DONE')
                time.sleep(2)
        url2 = json.load(open('config.json'))['splunk_server']+"/services/search/jobs/{}/results".format(api_sid)
        res_result = requests.get(url=url2, headers=header,verify=False,params=api_parameters)
        query_result_json = json.loads(res_result.text)["results"]
        query_result = pandas.DataFrame(query_result_json)
        i = datetime.datetime.strptime(i,"%m/%d/%Y").strftime("%m-%d-%Y")
        if query_result.empty:
            open("./results\\"+file_name+"\\NoResult_"+i+".txt","w",encoding="utf-8").write("Sonuç Yok!!!")
        else:
            query_result.to_excel("./results\\"+file_name+"\\log_"+i+".xlsx",index=False)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(task, dates)

    shutil.make_archive("./results\\"+file_name, 'zip', "./results\\"+file_name)
