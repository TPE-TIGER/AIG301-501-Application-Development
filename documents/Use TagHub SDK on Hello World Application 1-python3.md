# Use TagHub SDK on Hello World Application 1

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-10 | Document created |



### Purpose

This document guide you how to use **TagHub Python SDK** on Hello World Application to **publish** Tag data.

You shall complete pre-request steps:

- <a href="Build%20and%20Run%20Hello%20World%20Application-python3.md">Build and Run "Hello World" Application</a>.
- <a href="Invoke%20ThingsPro%20Edge%20API%20on%20Hello%20World%20Application-python3.md">Invoke ThingsPro Edge API on Hello World Application</a>




------

### 1. Modify Python Code

##### 1.1 Add Python packages

```
import os, requests, time, json
from thingspro.edge.tag_v1 import tag
```

- thingspro.edge.tag_v1 is TagHub Python SDK.

##### 1.2 Define Tag Publisher

```
_publisher = tag.Publisher()
```

- We will use _publisher to update Tag value.


##### 1.3 Define a method to Create a Virtual Tag via ThingsPro Edge Restful API

```
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
```

- Before update writable tags, this method allow us to create virtual tags by Restful API.


##### 1.4 Define a method to Update a Virtual Tag Value via TagHub Python SDK

```
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
                'dataValue': newTagValue['value'],
                'dataType': newTagValue['dataType'],
                'ts': timestamp        
            }    
            _publisher.publish(tagValue)  
            return 'OK'
        except Exception as e:
            return str(e)    
    else:
        return "Bad payload."
```

- _publisher.publish() will update **Tag**'s value.




### 2. Develop Your Application

#### 2.1 Download Hello World Application 1.2

```
$ wget https://tpe2.thingspro.io/tpe2/Python3/HelloWorldApp12.tar
```

#### 2.2 ThingsPro Edge Application 1.2 Structure

| Name               | Type   | Note                                    |
| ------------------ | ------ | --------------------------------------- |
| Dockerfile         | File   | Same with 1.0                           |
| app                | Folder | Update with TagHub SDK code             |
| docker-compose.yml | File   | Update version to 1.2                   |
| metadata.yml       | File   | Update version to 1.2                   |
| nginx.conf         | File   | Same with 1.0                           |
| requirements.tx    | File   | Update required packages for TagHub SDK |

#### 2.3 Build ThingsPro Edge Applicaiton

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-python3.md">Build and Run "Hello World" Application</a>, to build hello-world application V1.2

```
drwxrwxrwx 2 root root      4096 Feb 12 15:28 app
-rwxrwxrwx 1 root root        56 Feb 12 08:46 docker-compose.yml
-rwxrwxrwx 1 root root       851 Feb 12 15:35 Dockerfile
-rw-r--r-- 1 root root 136970240 Feb 12 16:11 hello-world_1.2_armhf.mpkg
-rwxrwxrwx 1 root root       107 Feb 12 08:46 metadata.yml
-rwxrwxrwx 1 root root       281 Feb 12 08:46 nginx.conf
-rwxrwxrwx 1 root root        73 Feb 12 13:07 requirements.txt
```



### 3. Deploy Application on Moxa IIoT Gateway

##### 3.1 Deploy hello-world V1.2

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-python3.md">Build and Run "Hello World" Application</a>, to deploy hello-world application V1.2

##### 3.2 Testing 

###### 3.2.1 Create two new virtual tags by **POST /api/v1/hello-world/tag**

```
curl -X POST https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag01", "dataType":"string"}'

curl -X POST https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag02", "dataType":"int32"}'
```

###### 3.3.2 Update virtual tags value by PUT /api/v1/hello-world/tag

```
curl -X PUT https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag01", "dataValue":"Hello World", "dataType":"string"}'

curl -X PUT https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag02", "dataValue":4040, "dataType":"int32"}'
```

###### 3.2.3 Monitor these two virtual tags on ThingsPro Edge Web Admin

<p align="center" width="100%"><img src="https://thingspro.blob.core.windows.net/resource/document/tpe/tagMonitor2.JPG" width="100%" /></p>



ThingsPro Edge Web Admin / Tag Management offers a easy way to monitor Tag value changed.

This feature is available on ThingsPro Edge V2.2.1+.



##### 3.3 Done and Next Action

- <a href="Use%20TagHub%20SDK%20on%20Hello%20World%20Application%202-python3.md">Use TagHub SDK on Hello World Application 2</a>

