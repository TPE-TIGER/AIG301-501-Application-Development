# -*- coding: utf-8 -*-
import os, requests, time, json
from flask import Flask, request
from thingspro.edge.tag_v1 import tag

app = Flask(__name__)

#Define Tag Publisher
_publisher = tag.Publisher()

#Define Flask Key
app.secret_key = 'my secret key'

#Define ThingsPro Edge API Environment
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

# --------------------------------------------------------- #

#get /api/v1/hello-world
@app.route('/api/v1/hello-world', methods=['GET'])
def hello_world():
    return 'Hello World.'

#post /api/v1/hello-world/tag
@app.route('/api/v1/hello-world/tag', methods=['POST'])
def post_tag():
    newTag = request.json
    
    if ('prvdName' in newTag) and ('srcName' in newTag) and ('tagName' in newTag) and ('dataType' in newTag):    
        try:
            result = call_API('get', '/tags/list?provider='+newTag['prvdName'], None)
            messageJson = json.loads(result["message"])
            if "data" in messageJson:
                tagList = messageJson["data"]            
                for tag in tagList:
                    if (tag['srcName'] == newTag['srcName']) and (tag['tagName'] == newTag['tagName']):
                        return "OK"         # Tag already there, return
            
            # Create Tag
            postTag = {
                'prvdName': newTag['prvdName'],
                'srcName': newTag['srcName'],
                'tagName': newTag['tagName'],            
                'dataType': newTag['dataType'],
                'access': 'rw'
            }    
            result = call_API('post', '/tags/virtual', postTag)
            return 'OK'
        except Exception as e:
            return str(e) 
    else:
        return "Bad payload."

#put /api/v1/hello-world/tag
@app.route('/api/v1/hello-world/tag', methods=['PUT'])
def put_tag():
    newTagValue = request.json
    if ('prvdName' in newTagValue) and ('srcName' in newTagValue) and ('tagName' in newTagValue) and ('dataValue' in newTagValue) and ('dataType' in newTagValue):
        timestamp=int(time.time()*1000000)
        try:
            tagValue = {
                'prvdName': newTagValue['prvdName'],
                'srcName': newTagValue['srcName'],
                'tagName': newTagValue['tagName'],            
                'dataValue': newTagValue['dataValue'],
                'dataType': newTagValue['dataType'],
                'ts': timestamp        
            }    
            _publisher.publish(tagValue)  
            return 'OK'
        except Exception as e:
            return str(e)    
    else:
        return "Bad payload."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
