# Use TagHub SDK on Hello World Application 2

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-10 | Document created |



### Purpose

This document guide you how to use **TagHub Python SDK** on Hello World Application to **subscribe** Tag data for edge computing.

You shall complete pre-request steps:

- <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>.
- <a href="Invoke%20ThingsPro%20Edge%20API%20on%20Hello%20World%20Application-dotnet.md">Invoke ThingsPro Edge API on Hello World Application</a>
- <a href="Use%20TagHub%20SDK%20on%20Hello%20World%20Application%201-dotnet.md">Use TagHub SDK on Hello World Application 1</a>




------

### 1. Add backend.py Python Code

We need to add one python script, running at backend to subscribe Tags and do some edge computing tasks.

##### 1.1 Create backend.py and add Python packages

```
import time, requests
from thingspro.edge.tag_v1 import tag
```

- thingspro.edge.tag_v1 is TagHub Python SDK.

##### 1.2 Add Class: backendProcess and assign initial variables

```
class backendProcess():
    def __init__(self):
        self.subscriber = tag.Subscriber()
        self.publisher = tag.Publisher()
        self.webAPIURL = 'http://127.0.0.1/api/v1'
        self.headers = {}
        self.headers["Content-Type"] = 'application/json'
```

- We will use self.subscriber to subscribe Tag.
- The backend process will leverage hello-world's Restful API to create virtual tags.


##### 1.3 Create start() method

```
def start(self):
        # Waiting Web API
        self.waitWebAPI()
        
        # Create virtual tags before subscribe them
        self.createTag('virtual', 'hello-world', 'tag01', 'string')
        self.createTag('virtual', 'hello-world', 'tag02', 'int32')
        self.createTag('virtual', 'hello-world', 'tag03', 'int32')        
        
        # Subscribe virtual tags, and declare call back function        
        self.subscriber.subscribe_callback(self.tagDataCallback)        
        self.subscriber.subscribe('virtual', 'hello-world', ['tag01', 'tag02'])
        
        while True:
            time.sleep(1)
```

- We tell Tag Subscriber that we want to subscribe tag01 and tag02, and call we defined method, self.tagDataCallback, when data coming.

- To prevent failure, we create virtual tags (via hello-world Restful API) again, including 3rd tag (tag03).


##### 1.4 Create tagDataCallback() method

```
def tagDataCallback(self, data={}):
        timestamp=int(time.time()*1000000)  
        if data["tagName"] == 'tag02':
            F = self.C_to_F(data['dataValue'])
            tag03 = {
                    'prvdName': 'virtual',
                    'srcName': 'hello-world',
                    'tagName': 'tag03',            
                    'dataValue': int(F),
                    'dataType': 'int32',
                    'ts': timestamp        
                }  
            self.publisher.publish(tag03)
            
            if (F >= 100):     
                tag01Value = 'Over Hit'
            else:
                tag01Value = 'Normal'                     
            tag01 = {
                'prvdName': 'virtual',
                'srcName': 'hello-world',
                'tagName': 'tag01',            
                'dataValue': tag01Value,
                'dataType': 'string',
                'ts': timestamp        
            }             
            self.publisher.publish(tag01)
```

- We convert tag02 value (temperature) , from °*C* to °*F*   , and publish temperature °*F*   to tag03.
- If tag03 value >= 100, publish 'Over Hit' to tag01, else publish 'Normal' to tag01




### 2. Develop Your Application

#### 2.1 Download Hello World Application 1.3

```
$ wget https://tpe2.azureedge.net/Python3/HelloWorldApp13.tar
```

#### 2.2 ThingsPro Edge Application 1.2 Structure

| Name               | Type   | Note                                        |
| ------------------ | ------ | ------------------------------------------- |
| Dockerfile         | File   | Updated for launch backend.py and web.py    |
| app                | Folder | Add backend.py<br />Rename run.py to web.py |
| docker-compose.yml | File   | Update version to 1.3                       |
| metadata.yml       | File   | Update version to 1.3                       |
| nginx.conf         | File   | Same with 1.0                               |
| requirements.tx    | File   | Same with 1.2                               |

#### 2.3 Build ThingsPro Edge Applicaiton

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>, to build hello-world application V1.3

```
-rwxrwxrwx 1 root root       861 Feb 12 14:07 Dockerfile
drwxrwxrwx 2 root root      4096 Feb 12 15:12 app
-rwxrwxrwx 1 root root        56 Feb 12 16:54 docker-compose.yml
-rw-r--r-- 1 root root 136980480 Feb 13 02:06 hello-world_1.3_armhf.mpkg
-rwxrwxrwx 1 root root       107 Feb 12 16:54 metadata.yml
-rwxrwxrwx 1 root root       281 Feb 12 08:46 nginx.conf
-rwxrwxrwx 1 root root        73 Feb 12 13:07 requirements.txt
```



### 3. Deploy Application on Moxa IIoT Gateway

##### 3.1 Deploy hello-world V1.3

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>, to deploy hello-world application V1.3

##### 3.2 Testing 

###### 3.3.1 Update virtual tags value by PUT /api/v1/hello-world/tag

```
curl -X PUT https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag02", "dataValue":20, "dataType":"int32"}'

curl -X PUT https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag02", "dataValue":4040, "dataType":"int32"}'
```

###### 3.2.2 Monitor these two virtual tags on ThingsPro Edge Web Admin

Add Tag03 into monitoring.

<p align="center" width="100%"><img src="https://thingspro.blob.core.windows.net/resource/document/tpe/tagMonitor3.JPG" width="100%" /></p>

ThingsPro Edge Web Admin / Tag Management offers a easy way to monitor Tag value changed.

This feature is available on ThingsPro Edge V2.2.1+.



##### 3.3 Done and Next Action

