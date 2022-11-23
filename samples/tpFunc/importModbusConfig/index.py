#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, requests, time, json
from thingspro.edge.http_v1 import http

_tpeURL = 'http://' + os.getenv('APPMAN_HOST_IP', '127.0.0.1') + ':59000/api/v1'
_headers = {}
_headers["Content-Type"] = 'application/json'
f=open('/run/mx-api-token', 'r')
_headers["mx-api-token"] = f.read()

def post_csv_file(data_bytes):
    url = _tpeURL + "/modbusmaster/control/config/masters/import"
    _headers["Content-Type"] = None
    files = {'mastersFile': ('modbus_file.csv', data_bytes, 'text/x-spam')}
    try:
        response = requests.post(url, headers=_headers, files=files, verify=False)
    except Exception as e:
        print(e)
        return 500, e
    
    return response.status_code, response.content

def apply_modbus_change():
    url = _tpeURL + "/modbusmaster/control/config/apply"
    _headers["Content-Type"] = 'application/json'
    try:
        response = requests.put(url, headers=_headers, verify=False)
    except Exception as e:
        print(e)
        return 500, e
    
    return response.status_code, response.content

def download_csv_file(url):
    try:
        response = requests.get(url, verify=False)
    except Exception as e:
        print(e)
        return 500, e
    
    return response.status_code, response.content

""" 
PUT method by callback function 
    {
       "file": "https://abc.com/file.csv"
    }
    
"""
def modbus_import(resource, headers, message):
    output = {}
    jsonMsg = json.loads(message)
    
    status, content = download_csv_file(jsonMsg["file"])
    if (status > 300) :
        output["status"] = "fail"
        output["step"] = "1/3. download csv file from input URL: " + jsonMsg["file"]
        output["content"] = content.decode("utf-8")
        return http.Response(code=200, data=output)
    
    status, content = post_csv_file(content)
    if (status > 300) :
        output["status"] = "fail"
        output["step"] = "2/3. import csv content into Modbus Master"
        output["content"] = content.decode("utf-8")
        return http.Response(code=200, data=output)
    
    status, content = apply_modbus_change()
    if (status >= 200) and (status < 300) :
        output["status"] = "sucess"
    else:
        output["status"] = "fail"
    output["step"] = "3/3. apply Modbus Master configuraiton"
    output["content"] = content.decode("utf-8")
    return http.Response(code=200, data=output)

if __name__ == "__main__":
    # callback function
    http.Server.PUT("/modbus/import", modbus_import)
    # infinite loop
    while True:
        time.sleep(1)