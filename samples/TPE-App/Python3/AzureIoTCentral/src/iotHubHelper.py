from azure.iot.device import MethodResponse

class iotHub_function():
    ################################################################################################       
    ## Be trigger by recieving a Direct Method, and route to handler
    ## Direct Method handler functions => tpeHelper.py
    ################################################################################################
    async def execute_command_listener(self, method_name, user_command_handler, create_user_response_handler):
        while True:            
            if method_name:
                command_name = method_name
            else:
                command_name = None

            command_request = await self.aicDevice.receive_method_request(command_name)             

            data = {}
            if command_request.payload:
                data = command_request.payload
            
            result = user_command_handler(data)

            response_status = 200
            response_payload = create_user_response_handler(result)

            command_response = MethodResponse.create_from_method_request(
                command_request, response_status, response_payload
            )

            try:
                await self.aicDevice.send_method_response(command_response)
            except Exception:
                print("responding to the {command} command failed".format(command=method_name))
    
    ################################################################################################       
    ## Be trigger by recieving a Desired Properites, and route to handler
    ## Desired Properties handler functions => tpeHelper.py
    ################################################################################################
    async def execute_property_listener(self):
        ignore_keys = ["__t", "$version"]
        while True:
            patch = await self.aicDevice.receive_twin_desired_properties_patch()  # blocking call

            version = patch["$version"]
            prop_dict = {}

            for prop_name, prop_value in patch.items():
                if prop_name in ignore_keys:
                    continue
                else:
                    prop_dict = self.desired_property_action(prop_name, prop_value, version)
                    await self.aicDevice.patch_twin_reported_properties(prop_dict)    
     
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

            print("[properties] update general_hostName name:" + str(value))
            response = self.tpeFunction.invoke_tpe_api('patch', cmdEP, cmdPayload)
            if response != None:
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
      
            print("[properties] update service_ssh service:" + str(value))
            response = self.tpeFunction.invoke_tpe_api('put', cmdEP, None)
            if response != None:
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

            print("[properties] update LAN2 IP:" + str(value))
            response = self.tpeFunction.invoke_tpe_api('patch', cmdEP, cmdPayload)
            if response != None:
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
            print("[properties] no such desired properties:" + str(name))
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
        response = self.tpeFunction.invoke_tpe_api('get', cmdEP, None)
        if response != None:        
            if response.status_code == 200 :
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
        response = self.tpeFunction.invoke_tpe_api('get', cmdEP, None)
        if response != None:        
            if response.status_code == 200 :
                for service in response.json()["data"]["service"]:
                    if service["id"] == 'sshserver':
                        prop_dict["service_ssh"] = {
                                "ac": 200,
                                "ad": "ssh service",
                                "av": "1",
                                "value": service["enable"],
                            } 
                        break
        
        await self.aicDevice.patch_twin_reported_properties(prop_dict)