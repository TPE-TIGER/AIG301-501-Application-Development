#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, requests, json
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

def Enable_AID():
    result = {}
    config = get_AID_configuration()    
    if config != None:
        if config["provisioning"]["enable"]:
            result["status"] = "success"
            result["message"] = "Do nothing, the enable already true"
        else:
            config["provisioning"]["enable"] = True
            result = call_API("PUT", "/azure-device", config)
    else:
        result["status"] = "fail"
        result["message"] = "Can't read AID configuration"
    return result

def Disable_AID():
    result = {}
    config = get_AID_configuration()    
    if config != None:
        if config["provisioning"]["enable"]:
            config["provisioning"]["enable"] = False
            result = call_API("PUT", "/azure-device", config)
        else:
            result["status"] = "success"
            result["message"] = "Do nothing, the enable already false"
    else:
        result["status"] = "fail"
        result["message"] = "Can't read AID configuration"
    return result

def get_AID_configuration():
    result = call_API("GET", "/azure-device", None)
    if result["status"] == "success":
        config = json.loads(result["message"])
        return config["data"]
    else:
        print(result["message"])
        return None
    

if __name__ == "__main__":
    config = package.Configuration()
    params = config.parameters()
    
    timeLine = params["timeLine"]
    
    now = datetime.now()
    timeFrame = now.strftime("%H")
    print("Run " + timeFrame + " ================")
    
    if timeFrame in timeLine:
        commandList = timeLine[timeFrame]        
        for cmdName in commandList:   
            print("Invoke : " + cmdName)   
            result = eval(cmdName)
            print(result["status"])
            print(result["message"])
    
    print("Shutdown ================")
    print("")