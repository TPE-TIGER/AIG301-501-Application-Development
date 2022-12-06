import asyncio, time, json, os
from iotHubHelper import iotHub_function
from tpeHelper import tpe_function
from azure.iot.device import X509
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.aio import IoTHubDeviceClient


_CONFIG_PATH = '/var/thingspro/aic/data/'
_CONFIG_FILE = _CONFIG_PATH + 'config.json'

class aic_client(iotHub_function):
    def __init__(self):        
        self.connection_status = 'Disconnect'
        self.connection_ts = None
        self.telemetryList = {}
        self.aicDevice = None
        self.tpeFunction = None       
        
    def run(self, aicProcessInQ, aicProcessOutQ):
        try:
            if (os.path.isfile(_CONFIG_FILE) is not True):
                self.create_test_config_file()
                print("[info] create default config file")
            
            config = self.load_config_file()
            print("[info] load config file")
            
            pnpModelId, self.telemetryList = self.load_telemetry_map_file(config)               
            print("[info] load telemetry map file")
            
            asyncio.run(self.apply_config(config, pnpModelId))
            print("[info] apply config")
            
            if self.aicDevice == None:
                print('[info] fail on connect to Azure IoT Central on apply config')
                data = "disconnect#" + str(time.time())
                aicProcessOutQ.put(data, block=False)
                return
            
            print("[info] start tpeFunction process")
            self.tpeFunction = tpe_function(self.telemetryList, self.aicDevice) 
            
            print("[info] connecting to Azure IoT Central...")
            asyncio.run(self.connect(aicProcessInQ, aicProcessOutQ))            
            
        except Exception as e:
            print('[error] ' + str(e))
            data = "disconnect#" + str(time.time())
            aicProcessOutQ.put(data, block=False)
    
    async def connect(self, aicProcessInQ, aicProcessOutQ):
        # Connect the client.
        await self.aicDevice.connect()        
        print('[info] connected to Azure IoT Central')
        data = "connected#" + str(time.time())
        aicProcessOutQ.put(data, block=False)



        # Declare Direct Method & Desired Properties & Telemetry Handler
        listeners = asyncio.gather(
            self.execute_command_listener(
            method_name="reboot",
            user_command_handler=self.tpeFunction.cmd_reboot,
            create_user_response_handler=self.tpeFunction.cmd_reboot_response,
            ),
            self.execute_command_listener(
            method_name="turnOnMonitor",
            user_command_handler=self.tpeFunction.cmd_turnOnMonitor,
            create_user_response_handler=self.tpeFunction.cmd_turnOnMonitor_response,
            ),
            self.execute_command_listener(
            method_name="turnOffMonitor",
            user_command_handler=self.tpeFunction.cmd_turnOffMonitor,
            create_user_response_handler=self.tpeFunction.cmd_turnOffMonitor_response,
            ),
            self.execute_property_listener(),
        )  
        
        # send out read only properties
        await self.send_all_reported_properties()     
        
        # keep device client running till receive stop signal
        loop = asyncio.get_running_loop()
        loop_finished = loop.run_in_executor(None, self.loop_till_stop, aicProcessInQ)
        await loop_finished
        
        # shutdown direct methods & properties call back listener
        if not listeners.done():
            listeners.set_result("DONE")
        listeners.cancel()
        
        # Finally, shut down the client
        await self.aicDevice.disconnect()

        print('[info] disconnect & shutdown aic client')
        data = "disconnect#" + str(time.time())
        aicProcessOutQ.put(data, block=False)
            
        return 
    
    def loop_till_stop(self, aicProcessInQ):        
        while True:
            command = aicProcessInQ.get(block=True)
            if command == 'shutdown':
                break
    
    
    async def apply_config(self, config, pnpModelId):
        if config["provision_type"] == 'symmetric_key':
            provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
                provisioning_host=config["provision_dps_host"],
                id_scope=config["provision_id_scope"],
                registration_id=config["provision_registration_id"],                
                symmetric_key=config["provision_symmetric_key"],
            )        
        elif config["provision_type"] == 'X509':
            x509 = X509(
                cert_file=_CONFIG_PATH + config["cert_cert_file"],
                key_file=_CONFIG_PATH + config["cert_key_file"],
            )
            provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
                provisioning_host=config["provision_dps_host"],
                registration_id=config["provision_registration_id"],
                id_scope=self.provision_id_scope,
                x509=x509,
            )        
        
        registration_result = await provisioning_device_client.register()
        if registration_result.status == "assigned":
            if config["provision_type"] == 'symmetric_key':
                self.aicDevice = IoTHubDeviceClient.create_from_symmetric_key(
                    symmetric_key=config["provision_symmetric_key"],
                    hostname=registration_result.registration_state.assigned_hub,
                    device_id=registration_result.registration_state.device_id,
                    product_info=pnpModelId,
                )
            elif config["provision_type"] == 'X509':
                self.aicDevice = IoTHubDeviceClient.create_from_x509_certificate(
                    x509=x509,
                    hostname=registration_result.registration_state.assigned_hub,
                    device_id=registration_result.registration_state.device_id,
                    product_info=pnpModelId,
                )   
    
    def create_test_config_file(self):
        with open(_CONFIG_FILE, 'w') as outfile:
            initConfig = {}
            provision = {}
            certificate = {}
            deviceModel = {}

            initConfig["enable"] = False

            provision["dps_host"] = "global.azure-devices-provisioning.net"
            provision["id_scope"] = "0ne0087B16C"
            provision["type"]  = "symmetric_key"
            provision["registration_id"]  = "TBAIB1114961"
            provision["symmetric_key"]  = "5B613ngUIka4DulOn5rK8LveRngdx48VVwbnKeCYZ/U="
            initConfig["provision"] = provision

            certificate["cert_file"]  = ""
            certificate["key_file"]  = ""
            certificate["trusted_cert"]  = ""
            initConfig["certificate"] = certificate                
            
            deviceModel["telemetry_map_file"] = "TelemetryMap-AIG-301-3.json"
            initConfig["deviceModel"] = deviceModel
            json.dump(initConfig, outfile)
    
    def create_default_config_file(self):
        with open(_CONFIG_FILE, 'w') as outfile:
            initConfig = {}
            provision = {}
            certificate = {}
            deviceModel = {}

            initConfig["enable"] = False

            provision["dps_host"] = "global.azure-devices-provisioning.net"
            provision["id_scope"] = ""
            provision["type"]  = "symmetric_key"
            provision["registration_id"]  = ""
            provision["symmetric_key"]  = ""
            initConfig["provision"] = provision

            certificate["cert_file"]  = ""
            certificate["key_file"]  = ""
            certificate["trusted_cert"]  = ""
            initConfig["certificate"] = certificate                
            
            deviceModel["telemetry_map_file"] = ""
            initConfig["deviceModel"] = deviceModel
            json.dump(initConfig, outfile)
    
    def load_config_file(self):
        config = {}
        data = ""        
        with open(_CONFIG_FILE) as f:
            data = json.load(f)
            config["enable"] = data['enable']
            config["provision_dps_host"] = data['provision']['dps_host']
            config["provision_id_scope"] = data['provision']['id_scope']
            config["provision_type"] = data['provision']['type']
            config["provision_registration_id"] = data['provision']['registration_id']
            config["provision_symmetric_key"] = data['provision']['symmetric_key']

            config["cert_cert_file"] = data['certificate']['cert_file']
            config["cert_key_file"] = data['certificate']['key_file']
            config["cert_trusted_cert"] = data['certificate']['trusted_cert']  
            
            config["telemetry_map_file"] = data['deviceModel']['telemetry_map_file']
            return config
    
    def load_telemetry_map_file(self, config):
        print("[info] load telemetry map file")
        fileName = _CONFIG_PATH + config["telemetry_map_file"]
        f = open(fileName)
        map = json.load(f)
        pnpModelId = map["@id"]
        print("[info] retrieve pnpModelId from map file: " + pnpModelId)
        
        telemetryList = {}
        for item in map["contents"]:
            if item["@type"] == "Telemetry":
                telemetryList[item["name"]] = item["aigTag"]
                print("[info] retrieve telemetry from map file: " + item["name"] + ":" + str(item["aigTag"]))
        
        return pnpModelId, telemetryList