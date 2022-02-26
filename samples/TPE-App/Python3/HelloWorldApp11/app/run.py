# -*- coding: utf-8 -*-
import os, requests
from flask import Flask 

app = Flask(__name__)

#Define Flask Key
app.secret_key = 'my secret key'

#Define ThingsPro Edge API Environment
_tpeURL = 'http://' + os.getenv('APPMAN_HOST_IP', '127.0.0.1') + ':59000/api/v1'
_headers = {}
_headers["Content-Type"] = 'application/json'
f=open('/run/mx-api-token', 'r')
_headers["mx-api-token"] = f.read()
f.close()

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

#get /api/v1/hello-world/tpe-apps
@app.route('/api/v1/hello-world/tpe-apps', methods=['GET'])
def get_tpe_apps():
    result = call_API('get', '/apps', None)
    return result["message"]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
