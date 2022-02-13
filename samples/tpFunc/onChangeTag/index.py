#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
ThingsPro Edge Function data driven function template
"""

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
