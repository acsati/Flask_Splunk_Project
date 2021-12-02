#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ALP CANER SATI, Ekim 2021

import requests
import os
import time
import json
import pandas

def check_metricslog(sources:str, source_type:str):
    """Splunk'da metricslog'larını check edip sonucu .xlsx uzantılı file olarak kaydeder."""
    sources = [i.strip() for i in sources.splitlines()]
    if source_type == "Source IP":  
        komut1 = f"""| makeresults | eval sourceIp=split("{",".join(sources)}",",") 
| mvexpand sourceIp 
| table sourceIp 
| join sourceIp type=left 
    [ search index=_internal phonehome connection clientip IN ({",".join(sources)}) earliest=-1h 
    | eval hostname=upper(mvindex(split(uri_path,"_"),4)) 
    | where isnotnull(hostname) 
    | stats values(clientip) AS sourceIp by hostname] 
| join type=left hostname 
    [| tstats count where index=_internal earliest=-1d latest=now by host 
    | rename host AS hostname, count AS metrics_log 
    | eval hostname=upper(hostname), metrics_log="Geliyor" ] 
| join type=left sourceIp 
    [ search index="_internal" source="*metrics.lo*" group=tcpin_connections fwdType=uf earliest=-1h 
    | fields hostname, sourceIp 
    | eval hostname=upper(hostname), metrics_log="Geliyor" ]
| fillnull value="Gelmiyor" metrics_log
| fillnull value="-" hostname"""
    else:
        sources = [i.upper() for i in sources]
        komut1 = f"""search index="_internal" source="*metrics.lo*" group=tcpin_connections fwdType=uf hostname IN ({",".join(sources)}) earliest=-1h latest=now | dedup hostname | eval metrics_log="Geliyor" | table hostname,sourceIp,metrics_log"""

    requests.packages.urllib3.disable_warnings()
    api_token = "Bearer {}".format(json.load(open('config.json'))['api_token'])
    url = json.load(open('config.json'))['splunk_server']+"/services/search/jobs"
    header = {
        "Authorization": api_token
    }
    api_data = {"search": komut1 }
    api_parameters = {
        "count": 100000,
        "output_mode": "json"
    }
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

    komut1_result_json = json.loads(res_result.text)["results"]
    komut1_result_dict = {"hostname": [komut1_result_json[i]["hostname"].casefold() for i in range(len(komut1_result_json))], "sourceIp": [komut1_result_json[i]["sourceIp"] for i in range(len(komut1_result_json))], "metrics_log": [komut1_result_json[i]["metrics_log"] for i in range(len(komut1_result_json))]}
    komut1_result = pandas.DataFrame(komut1_result_dict)

    if source_type == "Source IP":
        # Splunk'da görünmeyenler
        no_access = komut1_result[komut1_result["metrics_log"]=="Gelmiyor"].loc[:,["hostname","sourceIp"]]
        no_access["hostname"] = no_access["hostname"].apply(lambda x: x.upper())

        # Splunk'da görünenler
        komut1_result = komut1_result[komut1_result["metrics_log"]=="Geliyor"].loc[:,["hostname","sourceIp"]]
        komut1_result["hostname"] = komut1_result["hostname"].apply(lambda x: x.upper())

        with pandas.ExcelWriter('./results\\internal_log_result.xlsx') as writer:
            no_access.to_excel(writer, sheet_name="Metric Log'u Gelmeyenler", index=False)
            komut1_result.to_excel(writer,sheet_name="Metric Log'u Gelenler", index=False)
    else:
        # Splunk'da görünmeyenler
        no_access = [i.upper() for i in sources if (not i.casefold() in komut1_result["hostname"].to_list())]

        # Splunk'da görünenler
        komut1_result = komut1_result[komut1_result["metrics_log"]=="Geliyor"].loc[:,["hostname","sourceIp"]]
        komut1_result["hostname"] = komut1_result["hostname"].apply(lambda x: x.upper())

        with pandas.ExcelWriter('./results\\internal_log_result.xlsx') as writer:
            pandas.DataFrame({"Metric Log'u Gelmeyenler":no_access}).to_excel(writer, sheet_name="Metric Log'u Gelmeyenler", index=False)
            komut1_result.to_excel(writer,sheet_name="Metric Log'u Gelenler", index=False)

def check_wineventlog(hostnames:str):
    """Splunk'da winevenlog'larını check edip sonucu .xlsx uzantılı file olarak kaydeder."""
    hostnames = [i.strip() for i in hostnames.splitlines()]
    komut2 = f"""search index=wineventlog host IN ({",".join(hostnames)}) earliest=-24h latest=now | dedup host | table host"""

    requests.packages.urllib3.disable_warnings()
    api_token = "Bearer {}".format(json.load(open('config.json'))['api_token'])
    url = json.load(open('config.json'))['splunk_server']+"/services/search/jobs"
    header = {
        "Authorization": api_token
    }
    api_data = {"search": komut2 }
    api_parameters = {
        "count": 100000,
        "output_mode": "json"
    }
    res = requests.post(url=url, headers=header, verify=False, params=api_parameters, data=api_data)
    api_sid = json.loads(res.text)["sid"]

    url3 = json.load(open('config.json'))['splunk_server']+"/services/search/jobs/{}".format(api_sid)
    header1 = {
        "Authorization": api_token,
        'Content-Type': "text"
    }
    with requests.session() as r:
        dispatchState = -1     #".find" metodu yanlışsa -1 döndürür. 
        while (dispatchState == -1):
            re = r.get(url=url3, headers=header, verify=False)
            dispatchState = re.text.find('"dispatchState">DONE')
            time.sleep(2)
    url2 = json.load(open('config.json'))['splunk_server']+"/services/search/jobs/{}/results".format(api_sid)
    res_result = requests.get(url=url2, headers=header,verify=False,params=api_parameters)

    # Splunk'a Winevent logu gelenler
    winevent_gelenler = [i["host"] for i in json.loads(res_result.text)["results"]]

    # Splunk'a Winevent logu gelmeyenler
    komut2_result = [i["host"].casefold() for i in json.loads(res_result.text)["results"]]
    winevent_gelmeyenler = [i.upper() for i in hostnames if not i.casefold() in komut2_result]

    with pandas.ExcelWriter('./results\\winevent_log_result.xlsx') as writer:
        pandas.DataFrame({"Winevent Log'u Gelmeyenler":winevent_gelmeyenler}).to_excel(writer,sheet_name="Winevent Log'u Gelmeyenler", index=False)
        pandas.DataFrame({"Winevent Log'u Gelenler":winevent_gelenler}).to_excel(writer, sheet_name="Winevent Log'u Gelenler", index=False)
        
