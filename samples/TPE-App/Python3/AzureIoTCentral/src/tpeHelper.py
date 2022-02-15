import asyncio, json
import requests
from azure.iot.device import Message
from thingspro.edge.tag_v1 import tag

class iotHubHandler:        
    async def cmd_reboot(self, data):   
        result = {}        

        cmdEP = 'api/v1/system/reboot'
        cmdPayload = {}
        cmdPayload["now"] = True
        cmdURL = self.tpeURL + cmdEP
        try:
            response = requests.put(cmdURL, json=json.loads(json.dumps(cmdPayload)), headers=self.headers, verify=False)
            code = response.status_code
        except:
            code = 500
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

    async def cmd_turnOnMonitor(self, data):         
        self.monitorCommandOn = True 
        result = {}
        result["status"] = "success"
        result["message"] = "turn on monitor succeeded"
        return result

    def cmd_turnOnMonitor_response(self, result):
        response = result
        return response
    
    async def cmd_turnOffMonitor(self, data):    
        # shutdown send telemetry task
        self.monitorCommandOn = False
        result = {}
        result["status"] = "success"
        result["message"] = "turn off monitor succeeded"
        return result

    def cmd_turnOffMonitor_response(self, result):
        response = result
        return response        

    def tagDataCallback(self, data={}):
        if self.monitorCommandOn :
            if data['tagName'] == 'cpuUsage':
                telemetry_msg = {"cpuLoad": data['dataValue']}
            else:
                telemetry_msg = {data['tagName']: data['dataValue']}            
            
            msg = Message(json.dumps(telemetry_msg))
            msg.content_encoding = "utf-8"
            msg.content_type = "application/json"
            asyncio.run(self.device_client.send_message(msg))
            print("send : " + str(telemetry_msg))
     
    # Take action for reciveing a desired properites
    def desired_property_action(self, name, value, version):
        prop_dict = {}
        data_dict = {}

        if value is None:
            data_dict = None
            prop_dict[name] = data_dict
            return prop_dict        

        if name == "general_hostName":
            # action to update hostname
            cmdEP = 'api/v1/device/general'
            cmdPayload = {}
            cmdPayload["hostName"] = value
            cmdURL = self.tpeURL + cmdEP
            try:
                response = requests.patch(cmdURL, json=json.loads(json.dumps(cmdPayload)), headers=self.headers, verify=False)
                code = response.status_code
            except:
                code = 500
            print("update general_hostName name:" + str(value))
            if response.status_code == 200 :
                data_dict["ac"] = 200
                data_dict["ad"] = "Successfully executed patch"
            else :
                data_dict["ac"] = response.status_code
                data_dict["ad"] = "general_hostname update fail"
            data_dict["av"] = version
            data_dict["value"] = value
        elif name == "service_ssh":
            # action to update ssh service
            if value:
                cmdEP = 'api/v1/system/services/sshserver/enable'                
            else:
                cmdEP = 'api/v1/system/services/sshserver/disable'
            
            cmdURL = self.tpeURL + cmdEP
            try:
                response = requests.put(cmdURL, headers=self.headers, verify=False)  
                code = response.status_code
            except:
                code = 500          
            print("update service_ssh service:" + str(value))
            if response.status_code == 200 :
                data_dict["ac"] = 200
                data_dict["ad"] = "Successfully executed patch"
            else :
                data_dict["ac"] = response.status_code
                data_dict["ad"] = "service_ssh update fail"
            data_dict["av"] = version
            data_dict["value"] = value
        elif name == "ethernet_lan2_ip":
            # action to update LAN2 IP
            cmdEP = 'api/v1/device/ethernets/2' 
            cmdPayload = {}
            cmdPayload["ip"] = value
            cmdURL = self.tpeURL + cmdEP
            try:
                response = requests.patch(cmdURL, json=json.loads(json.dumps(cmdPayload)), headers=self.headers, verify=False)            
                code = response.status_code
            except:
                code = 500
            print("update LAN2 IP:" + str(value))
            if response.status_code == 200 :
                data_dict["ac"] = 200
                data_dict["ad"] = "Successfully executed patch"
            else :
                data_dict["ac"] = response.status_code
                data_dict["ad"] = "LAN2 IP update fail"
            data_dict["av"] = version
            data_dict["value"] = value
        else:            
            # No such desired properites
            print("no such desired properties:" + str(name))
            data_dict["ac"] = 404
            data_dict["ad"] = "No such desired properity"
            data_dict["av"] = version
            data_dict["value"] = value
            
        prop_dict[name] = data_dict

        return prop_dict
    
    # Report read only properties to cloud
    async def send_all_reported_properties(self):
        prop_dict = {}        

        #action to retrieve reported properties (general)
        cmdEP = 'api/v1/device/general'
        cmdURL = self.tpeURL + cmdEP
        try:
            response = requests.get(cmdURL, headers=self.headers, verify=False)
            code = response.status_code
        except:
            code = 500
        else:
            if code == 200 :
                prop_dict["general_serialNumber"] = {
                        "ac": 200,
                        "ad": "device serial number",
                        "av": "1",
                        "value": response.json()["data"]["serialNumber"],
                    }            
                prop_dict["general_deviceModel"] = {
                        "ac": 200,
                        "ad": "device model",
                        "av": "1",
                        "value": response.json()["data"]["modelName"],
                    }
                prop_dict["general_hostName"] = {
                        "ac": 200,
                        "ad": "device model",
                        "av": "1",
                        "value": response.json()["data"]["hostName"],
                    }

        #action to retrieve reported properties (services)
        cmdEP = 'api/v1/system/services'
        cmdURL = self.tpeURL + cmdEP
        try:
            response = requests.get(cmdURL, headers=self.headers, verify=False)
            code = response.status_code
        except:
            code = 500
        else:
            if code == 200 :
                for service in response.json()["data"]["service"]:
                    if service["id"] == 'sshserver':
                        prop_dict["service_ssh"] = {
                                "ac": 200,
                                "ad": "ssh service",
                                "av": "1",
                                "value": service["enable"],
                            } 
                        break
        
        await self.device_client.patch_twin_reported_properties(prop_dict)


    