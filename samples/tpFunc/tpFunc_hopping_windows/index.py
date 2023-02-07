import os, time, requests
from thingspro.edge.tag_v1 import tag as tpeTAG
from thingspro.edge.func_v1 import package

_tpeURL = 'http://' + os.getenv('APPMAN_HOST_IP', '127.0.0.1') + ':59000/api/v1'
_headers = {}
_headers["Content-Type"] = 'application/json'
f=open('/run/mx-api-token', 'r')
_headers["mx-api-token"] = f.read()

_hoppingWindowTags = {}

config = package.Configuration()
_params = config.parameters()
_hoppingWindowsSec = _params["hoppingWindowsSec"] * 1000000

def call_API(method, endPoint, payload):    
    global _tpeURL
    global _headers
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

def cal(objectName, tagTS, method):
    global _hoppingWindowTags
    global _hoppingWindowsSec
    print(tagTS)
    for item in _hoppingWindowTags[objectName]:
        if ((item["ts"] + _hoppingWindowsSec) < tagTS):
            _hoppingWindowTags[objectName].remove(item)
            print("remove expired item")
    
    if method.lower() == "count":
        return len(_hoppingWindowTags[objectName])
    else:
        value = 0
        for item in _hoppingWindowTags[objectName]:
            value = value + item["value"]
        return value/len(_hoppingWindowTags[objectName])

def createHoppingWindowObject():
    global _params
    global _hoppingWindowTags
    for tag in _params["tags"]:
        objectName = tag["sourceTag"]["prvdName"] + "_" + tag["sourceTag"]["srcName"] + "_" + tag["sourceTag"]["tagName"]
        _hoppingWindowTags[objectName] = []

def createVirtualTag():
    global _params
    for tag in _params["tags"]:
        vTag = {
            "prvdName": tag["virtualTag"]["prvdName"],
            "srcName": tag["virtualTag"]["srcName"],
            "tagName": tag["virtualTag"]["tagName"],
            "dataType": tag["virtualTag"]["dataType"],
            "dataUnit": "unit",
            "access": "r"
            }
        result = call_API("POST", "/tags/virtual", vTag)
        print(result["message"])

def subscribeSourceTag():
    global _subscriber
    for tag in _params["tags"]:
        _subscriber.subscribe(tag["sourceTag"]["prvdName"], tag["sourceTag"]["srcName"], [tag["sourceTag"]["tagName"]])
        print("subscribe:" + tag["sourceTag"]["prvdName"] + "/" + tag["sourceTag"]["srcName"] + "/" + tag["sourceTag"]["tagName"])

def onReceivingTag(data={}):
    global _params
    global _hoppingWindowTags
    global _publisher
    
    objectName = data["prvdName"] + "_" + data["srcName"] + "_" + data["tagName"]
    item = {}
    item["value"] = data["dataValue"]
    item["ts"] = data["ts"]
    print("in:"  + str(data["dataValue"]))
    _hoppingWindowTags[objectName].append(item) 
    dataValue = cal(objectName, data["ts"], _params["calMethod"])
    
    for tag in _params["tags"]:
        if (tag["sourceTag"]["prvdName"] == data["prvdName"]) and (tag["sourceTag"]["srcName"] == data["srcName"]) and (tag["sourceTag"]["tagName"] == data["tagName"]):
            newTag = {
                    'prvdName': tag["virtualTag"]["prvdName"],
                    'srcName': tag["virtualTag"]["srcName"],
                    'tagName': tag["virtualTag"]["tagName"],            
                    'dataValue': dataValue,
                    'dataType' : tag["virtualTag"]["dataType"],
                    'ts': data["ts"]
                    }    
            _publisher.publish(newTag)
            print("updated " + tag["virtualTag"]["prvdName"] + "/" + tag["virtualTag"]["srcName"] + "/" +  tag["virtualTag"]["tagName"] + " by new vlaue: " + str(dataValue))
            return

if __name__ == "__main__":
    global _subscriber
    global _publisher
    
    # create in-memory data for watching tags
    createHoppingWindowObject()
    
    # create virtual tags
    createVirtualTag()
    
    # create subscriber client instance
    _subscriber = tpeTAG.Subscriber()
    _subscriber.subscribe_callback(onReceivingTag)
    subscribeSourceTag()
    
    # create publisher client instance
    _publisher = tpeTAG.Publisher()
    
    # infinite loop
    while True:
        time.sleep(1)
    
    