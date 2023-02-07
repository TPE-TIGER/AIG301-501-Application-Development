# Virtual Tags by Hopping Window 

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2023-02-07 | Document created |

### Purpose

This document demonstrates how to use **tpFunc/Function** to create virtual tags which calculate via hopping window pattern.

Note: **tpFunc** required ThingsPro Edge V2.2.1+

Note: for more information about hopping window, please refer to <a href="https://learn.microsoft.com/en-us/stream-analytics-query/hopping-window-azure-stream-analytics">this article</a>.

------

### How to use

1. Download **tpFunc/Hopping Window** function: <a href='https://github.com/TPE-TIGER/TPE2-Application-Development/blob/main/samples/tpFunc/hopping_window/hopping_window.tar.gz'>hopping_window.tar.gz</a>. 

2. Open ThingsPro Edge Admin Web, click **Function Management**, and import hopping_window.tar.gz file.

   ![](https://thingspro.blob.core.windows.net/resource/document/tpe/tpFunc_hopping_window.JPG)

   The function creates two new tags (cpuUsage_avg, memoryUsage_avg) which calculate cpuUsage and memoryUsage value by specified hopping window.

   You can monitor these two new tags on ThingsPro Edge Admin Web by click **Tag Management** and select these two tags.

   ![](https://thingspro.blob.core.windows.net/resource/document/tpe/tpFunc_hopping_window_02.JPG)

   

### How to change to my desired Tags

1. ##### Modify package.json

    <a href='https://github.com/TPE-TIGER/TPE2-Application-Development/blob/main/samples/tpFunc/hopping_window/hopping_window.tar.gz'>hopping_window.tar.gz</a> contains package.json and index.py, what you need to do is to declare Tags schema at package.json file.

   Below is default content of **params** in package.json file.

   ```
   "params": {
       "hoppingWindowsSec": 60,
       "calMethod": "average",
       "tags": [
         {
           "sourceTag": {
             "prvdName": "system",
             "srcName": "status",
             "tagName": "cpuUsage"
           },
           "virtualTag": {
             "prvdName": "tpFunc",
             "srcName": "hoppingWindowCal",
             "tagName": "cpuUsage_avg",
             "dataType": "double"
           }
         },
         {
           "sourceTag": {
             "prvdName": "system",
             "srcName": "status",
             "tagName": "memoryUsage"
           },
           "virtualTag": {
             "prvdName": "tpFunc",
             "srcName": "hoppingWindowCal",
             "tagName": "memoryUsage_avg",
             "dataType": "double"
           }
         }
       ]
     }
   ```

   | Key               | Description                                                  |
   | ----------------- | ------------------------------------------------------------ |
   | hoppingWindowsSec | Hopping Window length in seconds                             |
   | calMethod         | "average": Average value of all valid records<br />"counter": Valid record numbers |
   | tags/sourceTag    | The origin tag you desired                                 |
   | tags/virtualTag   | The new tag you desired, the tag value will be output of hopping window |

   Note: **tags** support array type.

2. ##### Pack and Import your Function

   - Pack package.json and index.py as .tar.gz file, and import it via **Function Management** Admin Web.
   - You need to delete old Function (hoppingWindowCal), if them come with same function name.

