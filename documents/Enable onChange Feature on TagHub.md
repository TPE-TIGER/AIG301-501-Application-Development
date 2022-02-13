# Enable onChange Feature on TagHub

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-10 | Document created |



### Purpose

This document demonstrates how to use **tpFunc/Function** to extend current TagHub with onChange tag featrues.

Note: **tpFunc** required ThingsPro Edge V2.2.1+


------

### Install and Setup

1. Login to your ThingsPro Edge SSH console with default path (/home/moxa).

2. Switch role to su

   ```
   sudo su
   ```

3. Download onChangeTag.tar and unpack it

   ```
   wget https://tpe2.azureedge.net/onChangeTag.tar
   
   tar -xvf onChangeTag.tar
   ```

   This command shall create **onChangeTag.** folder, and contains package.json and index.py files.

   ```
   root@Moxa:/home/moxa/onChangeTag# ls -l
   total 3
   -rwxrwxrwx 1 root root 1195 Feb 13 14:23 index.py
   -rwxrwxrwx 1 root root  645 Feb 13 14:23 package.json
   ```

4. Understand package.json

   ```
   {
     "name": "onChangeTag",
     "enabled": true,
     "trigger": {
       "driven": "dataDriven",
       "dataDriven": {
         "tags": {
           "system": {
             "status": [
               "cpuUsage"
             ]
           }
         },
         "events": {}
       },
       "timeDriven": {
         "mode": "boot",
         "intervalSec": 1,
         "cronJob": ""
       }
     },
     "expose": {
       "tags": [
         {
           "prvdName": "virtual",
           "srcName": "onChange",
           "tagName": "cpuUsage",
           "dataType": "double",
           "access": "rw"
         }
       ]
     },
     "executable": {
       "language": "python"
     },
     "params": {}
   }
   ```

   - This function configured with data-driven pattern, and declare below tags to subscribe
     - tag(**system/status/cpuUsage**)
   - It is free to add others tags under subscribe list. Once the value of subscribed tags be updated, tpFunc will call the method, **onChangeTag()** , which defined in index.py.
   - For each subscribe tags, it is make sense to define associated "onChange" Tag, such as
     - tag(**system/status/cpuUsage**) associated with tag(**virtual/onChange/cpuUsage**) 
   - Please aware that "onChange" tag shall has same dataType with it's origin, and with "read/write" access attribute.

5. Understand index.py

   ```
   from thingspro.edge.tag_v1 import tag as tpeTAG
   
   cacheValue = {}
   cacheValue["cpuUsage"] = None
   
   def onChangeTag(_type, data):    
       publisher = tpeTAG.Publisher()
       
       if (_type == "tag"):
           if (data["prvdName"]=="system") and (data["srcName"] == "status") and (data["tagName"] == "cpuUsage"):
               if (cacheValue["cpuUsage"] == None) or (cacheValue["cpuUsage"] != data["dataValue"]):   
                   print("Cache value of virtual/onChange/cpuUsage : " + str(cacheValue["cpuUsage"]))             
                   newTag = {
                       'prvdName': "virtual",
                       'srcName': "onChange",
                       'tagName': "cpuUsage",            
                       'dataValue': data["dataValue"],
                       'dataType' : "double",
                       'ts': data["ts"]
                       }    
                   publisher.publish(newTag)                
                   print("updated virtual/onChange/cpuUsage by new vlaue: " + str(data["dataValue"]))
                   cacheValue["cpuUsage"] = data["dataValue"]
   ```

   - cacheValue is python dict object, which be used to store onChange Tags value in RAM.

   - onChangeTag() method, shall be with same named as 'function name' in package.json.

   - onChangeTag() compares incoming Tag value with cacheValue, and publish Tag value to onChange Tag if them are different, like below diagram.

     

     <p align="center" width="100%"><img src="https://thingspro.blob.core.windows.net/resource/document/onChangeTag/p1.jpg" width="800" /></p>


### Add to tpFunc and Run

1. Add it to tpFunc

   ```
   cd /home/moxa
   sudo su
   tpfunc add onChangeTag
   ```

2. Verify there is no error on creation

   ```
   root@Moxa:/home/moxa# tpfunc ls
   +-------------+--------+------------+---------------------------+---------+-------+
   |    NAME     | ENABLE |    MODE    |        LASTUPTIME         |  STATE  | ERROR |
   +-------------+--------+------------+---------------------------+---------+-------+
   | onChangeTag | true   | dataDriven | 2022-02-13T14:51:54+08:00 | running |       |
   +-------------+--------+------------+---------------------------+---------+-------+
   ```

   

### Tips

When onChangeTag function running, other applications or functions could subscribe these onChange Tags, when needed, to reduce complexity of these applications implementation.

<p align="center" width="100%"><img src="https://thingspro.blob.core.windows.net/resource/document/onChangeTag/p2.jpg" width="800" /></p>

