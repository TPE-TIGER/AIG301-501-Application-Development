# Invoke ThingsPro Edge API on Hello World Application

Document Version: V1.1

##### Change Log

| Version | Date       | Content                 |
| ------- | ---------- | ----------------------- |
| 1.0     | 2022-02-10 | Document created        |
| 1.1     | 2022-02-16 | Add .Net core C# sample |



### Purpose

This document guide you how to invoke ThingsPro Edge API on Hello World Application.

You shall complete pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application.md">Build and Run "Hello World" Application</a>.




------

### 1. Modify Code (Python)

##### 1.1 Add Python packages

```
import os, requests
```

##### 1.2 Define ThingsPro Edge API Environment

```
#Define ThingsPro Edge API Environment
_tpeURL = 'http://' + os.getenv('APPMAN_HOST_IP', '127.0.0.1') + ':59000/api/v1'
_headers = {}
_headers["Content-Type"] = 'application/json'
f=open('/run/mx-api-token', 'r')
_headers["mx-api-token"] = f.read()
```

- ThingsPro Edge Application be assigned below environment variables. At this sample code, we use 'APPMAN_HOST_IP', which points to ThingsPro Edge API service.

  | Name           | Value      | Desc                                   |
  | -------------- | ---------- | -------------------------------------- |
  | APPMAN_HOST_IP | 172.31.8.1 | ThingsPro Edge API service IP address. |

- Your application shall read API token from '/run/mx-api-token', and pass it on HTTP headers, when invoke ThingsPro Edge Restful API.

##### 1.3 Define a method to Invoke ThingsPro Edge Restful API

```
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
```

##### 1.4 Add new Restful API endPoint: /api/v1/hello-world/tpe-apps

```
#get /api/v1/hello-world/tpe-apps
@app.route('/api/v1/hello-world/tpe-apps', methods=['GET'])
def get_tpe_apps():
    result = call_API('get', '/apps', None)
    return result["message"]
```

This new Restful API will invoke ThingsPro Edge Restful API: /api/v1/apps, and return result back.



### 2. Build Your Application

#### 2.1 Download Hello World Application 1.1

```
$ wget https://tpe2.azureedge.net/Python3/HelloWorldApp11.tar
```

#### 2.2 ThingsPro Edge Application 1.1 Structure

| Name               | Type   | Note                        |
| ------------------ | ------ | --------------------------- |
| Dockerfile         | File   | Same with 1.0               |
| app                | Folder | Update with Invoke API code |
| docker-compose.yml | File   | Update version to 1.1       |
| metadata.yml       | File   | Update version to 1.1       |
| nginx.conf         | File   | Same with 1.0               |
| requirements.tx    | File   | Update required packages    |

#### 2.3 Build ThingsPro Edge Applicaiton

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application.md">Build and Run "Hello World" Application</a>, to build hello-world application V1.1

```
drwxrwxrwx 2 root root     4096 Feb 12 06:29 app
-rwxrwxrwx 1 root root       56 Feb 12 06:44 docker-compose.yml
-rwxrwxrwx 1 root root      852 Nov  9  2019 Dockerfile
-rw-r--r-- 1 root root 28456960 Feb 12 07:51 hello-world_1.1_armhf.mpkg
-rwxrwxrwx 1 root root      107 Feb 12 06:39 metadata.yml
-rwxrwxrwx 1 root root      281 Feb 12 05:59 nginx.conf
-rwxrwxrwx 1 root root       22 Feb 12 07:47 requirements.txt
```



### 3. Deploy Application on Moxa IIoT Gateway

##### 3.1 Deploy hello-world V1.1

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application.md">Build and Run "Hello World" Application</a>, to deploy hello-world application V1.1

##### 3.2 Testing new Restful API: /api/v1/hello-world/tpe-apps

```
$ curl -X GET https://127.0.0.1:8443/api/v1/hello-world/tpe-apps -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -k

{"count":9,"data":[{"arch":"armhf","attributes":null,"availableVersions":[],"category":"","cpu_percent":0,"description":"","desiredState":"ready","displayName":"Hello World App","hardwares":[],"health":"good","icon":"","id":"hello-world","imageSize":95196160,"license":{"paid":true,"type":"free"},"mem_limit":0,"menuID":"app-hello-world","name":"hello-world","ports":{"filter":null,"forward":null},"state":"ready","version":"1.1"},{"arch":"armhf","attributes":

....

Server","desiredState":"ready","displayName":"OPCUA Server","hardwares":[],"health":"good","icon":"","id":"opcuaserver","imageSize":58061824,"license":{"paid":true,"type":"propetual"},"mem_limit":0,"menuID":"app-opcuaserver","name":"opcuaserver","ports":{"filter":null,"forward":null},"state":"ready","version":"2.1.0-644"}]}
```

##### 3.4 Done and Next Action

- <a href="Use%20TagHub%20SDK%20on%20Hello%20World%20Application%201.md">Use TagHub SDK on Hello World Application 1</a>



### Appendix

For .Net Core C# developer, download the sample code:

```
$ wget https://tpe2.azureedge.net/dotnet-core-6/HelloWorldApp11.tar
```

