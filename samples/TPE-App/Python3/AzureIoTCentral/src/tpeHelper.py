import os, requests, json, asyncio
from azure.iot.device import Message
from thingspro.edge.tag_v1 import tag

class tpe_function():
    def __init__(self, telemetryList, aicDevice):
        _APPMAN_HOST_IP = os.getenv('APPMAN_HOST_IP', '127.0.0.1')
        _API_TOKEN_FILE = '/run/mx-api-token'
        self.tpeURL = 'http://' + _APPMAN_HOST_IP + ':59000/'
        self.headers = {}
        self.headers["Content-Type"] = 'application/json'
        f=open(_API_TOKEN_FILE, 'r')
        self.headers["mx-api-token"] = f.read()
        
        
        ### For local test
        #_APPMAN_HOST_IP = "192.168.8.203"        
        #self.tpeURL = 'https://' + _APPMAN_HOST_IP + ':8443/'
        #self.headers = {}
        #self.headers["Content-Type"] = 'application/json'        
        #self.headers["mx-api-token"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJRCI6MCwiVXNlcm5hbWUiOiJhZG1pbiIsIlBlcm1pc3Npb25zIjpbIlNZU19NWEFQSV9UT0tFTiJdLCJleHAiOjQ4MjM4MDE4NzV9.VtRF8L9HDYSY-fRMEP91LbhnK5jisMrfaHauLoue9BY"

        # Create tag subscirber, and subscribe tags we need
        self.telemetryList = telemetryList
        self.aicDevice = aicDevice
        self.MonitorEnable = False
        self.subscriber = tag.Subscriber()
        self.subscriber.subscribe_callback(self.tagDataCallback)

    def invoke_tpe_api(self, method, apiPath, postPayload):
        
        cmdURL = self.tpeURL + apiPath
        try:
            if method == 'patch':
                response = requests.patch(cmdURL, json=json.loads(json.dumps(postPayload)), headers=self.headers, verify=False)
            elif method == 'put':
                response = requests.put(cmdURL, json=json.loads(json.dumps(postPayload)), headers=self.headers, verify=False)
            elif method == 'get':
                response = requests.get(cmdURL, headers=self.headers, verify=False)
                
            return response
        except Exception as e:
            print('[error] ' + str(e))
            return None
    
    def cmd_reboot(self, data):   
        result = {}        

        cmdEP = 'api/v1/system/reboot'
        cmdPayload = {}
        cmdPayload["now"] = True
        cmdURL = self.tpeURL + cmdEP
        try:
            response = requests.put(cmdURL, json=json.loads(json.dumps(cmdPayload)), headers=self.headers, verify=False)
        except Exception as e:
            print('[error] ' + str(e))
            
        if response.status_code == 200 :
            result["status"] = "success"
            result["message"] = "reboot succeeded"
        else:
            result["status"] = "fail"
            result["message"] = "reboot fail"

        return result

    def cmd_reboot_response(self, result):
        response = result
        return response

    def cmd_turnOnMonitor(self, data):  
        print("[info] receive turnOnMonitor command")
        self.subscribeTags()
        self.MonitorEnable = True
        result = {}
        result["status"] = "success"
        result["message"] = "turn on monitor succeeded"
        return result

    def cmd_turnOnMonitor_response(self, result):
        response = result
        return response
    
    def cmd_turnOffMonitor(self, data):    
        # shutdown send telemetry task
        self.unsubscribeTags()
        self.MonitorEnable = False
        result = {}
        result["status"] = "success"
        result["message"] = "turn off monitor succeeded"
        return result

    def cmd_turnOffMonitor_response(self, result):
        response = result
        return response   
    
    def tagDataCallback(self, data={}):
        if self.MonitorEnable:
            for key, value in self.telemetryList.items():
                tag = json.loads(json.dumps(value, indent = 4))  
                if (data["prvdName"] == tag["prvdName"]) and (data["srcName"] == tag["srcName"]) and (data["tagName"] == tag["tagName"]):
                    telemetry_msg = {key: data['dataValue']}
                    break        
        
            msg = Message(json.dumps(telemetry_msg))
            msg.content_encoding = "utf-8"
            msg.content_type = "application/json"
            asyncio.run(self.aicDevice.send_message(msg))
            print("[telemetry] send : " + str(telemetry_msg))
    
    def subscribeTags(self):
        for key, value in self.telemetryList.items():
            print(key)
            tag = json.loads(json.dumps(value, indent = 4))  
            print(tag["prvdName"])
            self.subscriber.subscribe(tag["prvdName"], tag["srcName"], [tag["tagName"]]) 
            print("[info] subscribe DTDL tag: " + key + ", AIG tag=" + tag["prvdName"] + "," + tag["srcName"] + "," + tag["tagName"])
    
    def unsubscribeTags(self):
        
        # below code doesn't work
        for key, value in self.telemetryList.items():
            tag = json.loads(json.dumps(value, indent = 4))  
            self.subscriber.unsubscribe(tag["prvdName"], tag["srcName"]) 
            print("[info] unsubscribe DTDL tag: " + key + ", AIG tag=" + tag["prvdName"] + "," + tag["srcName"] + "," + tag["tagName"]) 