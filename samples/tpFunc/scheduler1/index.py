#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, requests
from datetime import datetime
from thingspro.edge.func_v1 import package

_tpeURL = 'http://' + os.getenv('APPMAN_HOST_IP', '127.0.0.1') + ':59000/api/v1'
_headers = {}
_headers["Content-Type"] = 'application/json'
f=open('/run/mx-api-token', 'r')
_headers["mx-api-token"] = f.read()

def call_API(method, endPoint, payload):    
    result = {}
    cmdURL = _tpeURL + endPoint
    try:
        if method.lower() == 'put':
            response = requests.put(cmdURL, json=payload, headers=_headers, verify=False)
        elif method.lower() == 'post':
            response = requests.post(cmdURL, json=payload, headers=_headers, verify=False)
        elif method.lower() == 'delete':
            response = requests.delete(cmdURL, json=payload, headers=_headers, verify=False)
        elif method.lower() == 'patch':
            response = requests.patch(cmdURL, json=payload, headers=_headers, verify=False)
        elif method.lower() == 'get':
            response = requests.get(cmdURL, json=payload, headers=_headers, verify=False)
    except Exception as e:
        print(e)
    if (response.status_code >= 200) and (response.status_code < 300) :
        result["status"] = "success"
        result["message"] = response.text
    else:
        result["status"] = "fail"
        result["message"] = response.text

    return result
    

if __name__ == "__main__":
    config = package.Configuration()
    params = config.parameters()
    
    timeLine = params["timeLine"]
    commands = params["commands"]
    
    now = datetime.now()
    timeFrame = now.strftime("%H")
    print("Run " + timeFrame + " ================")
    
    if timeFrame in timeLine:
        commandList = timeLine[timeFrame]        
        for cmdIdx in commandList:
            cmd = commands[cmdIdx]
            if (cmd["enable"]):
                print("Call API : " + cmd["displayName"])
                result = call_API(cmd["method"], cmd["endPoint"], cmd["payload"])
                print(result["status"])
                print(result["message"])
    
    print("Shutdown ================")
    print("")