import asyncio
import json, time, socket, os, os.path
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse
from azure.iot.device import X509
from thingspro.edge.tag_v1 import tag
import tpeHelper 

#_CONFIG_FILE = 'D:\\OneDrive\\Git\\AIC-src\\data\\config.json'

_CONFIG_PATH = '/var/thingspro/aic/data/'
_CONFIG_FILE = _CONFIG_PATH + 'config.json'
_APPMAN_HOST_IP = os.getenv('APPMAN_HOST_IP', '127.0.0.1')
_API_TOKEN_FILE = '/run/mx-api-token'

class azureIoTCentral(tpeHelper.iotHubHandler):
    def __init__(self, port=10000):
        self.tpeURL = 'http://' + _APPMAN_HOST_IP + ':59000/'
        self.headers = {}
        self.headers["Content-Type"] = 'application/json'
        f=open(_API_TOKEN_FILE, 'r')
        self.headers["mx-api-token"] = f.read()
        #self.headers["mx-api-token"] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJRCI6MCwiVXNlcm5hbWUiOiJhZG1pbiIsIlBlcm1pc3Npb25zIjpbIlNZU19NWEFQSV9UT0tFTiJdLCJleHAiOjQ3ODMzMTEwOTh9.gJM9DMHmVRhuu-OIlfRTGu4SDhuGMNtjnUYpYhKzQ74'

        self.provisioning_device_client = None
        self.device_client = None
        self.registration_result = None
        self.connection_status = 'Disconnect'
        self.connection_ts = None
        self.monitorCommandOn = False

        # Create tag subscirber, and subscribe tags we need
        self.subscriber = tag.Subscriber()
        self.subscriber.subscribe_callback(self.tagDataCallback)
        self.subscriber.subscribe('system', 'status', ['cpuUsage'])
        self.subscriber.subscribe('system', 'network', ['lan1NetworkRx', 'lan1NetworkTx'])

        if (os.path.isfile(_CONFIG_FILE) is not True) :
            with open(_CONFIG_FILE, 'w') as outfile:
                initConfig = {}
                provision = {}
                certificate = {}

                initConfig["enable"] = False
                initConfig["pnpModelId"] = "dtmi:com:moxa:TPE;1"

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
                json.dump(initConfig, outfile)

        self.load_config_file()        

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', port)
        print('starting up on {} port {}'.format(*server_address))
        self.sock.bind(server_address)   
        self.sock.listen(1)   
    
    def load_config_file(self):
        data = ""        
        with open(_CONFIG_FILE) as f:
            data = json.load(f)
            self.enable = data['enable']
            self.pnpModelId = data['pnpModelId']
            self.provision_dps_host = data['provision']['dps_host']
            self.provision_id_scope = data['provision']['id_scope']
            self.provision_type = data['provision']['type']
            self.provision_registration_id = data['provision']['registration_id']
            self.provision_symmetric_key = data['provision']['symmetric_key']

            self.cert_cert_file = data['certificate']['cert_file']
            self.cert_key_file = data['certificate']['key_file']
            self.cert_trusted_cert = data['certificate']['trusted_cert']  
    
    ################################################################################################       
    ## Be trigger by recieving a Direct Method, and route to handler
    ## Diect Method handler functions => tpeHelper.py
    ################################################################################################
    async def execute_command_listener(self, method_name, user_command_handler, create_user_response_handler):
        while True:
            if method_name:
                command_name = method_name
            else:
                command_name = None

            command_request = await self.device_client.receive_method_request(command_name)             

            data = {}
            if command_request.payload:
                data = command_request.payload
            
            result = await user_command_handler(data)

            response_status = 200
            response_payload = create_user_response_handler(result)

            command_response = MethodResponse.create_from_method_request(
                command_request, response_status, response_payload
            )

            try:
                await self.device_client.send_method_response(command_response)
            except Exception:
                print("responding to the {command} command failed".format(command=method_name))

    ################################################################################################       
    ## Be trigger by recieving a Desired Properites, and route to handler
    ## Desired Properties handler functions => tpeHelper.py
    ################################################################################################
    async def execute_property_listener(self):
        ignore_keys = ["__t", "$version"]
        while True:
            patch = await self.device_client.receive_twin_desired_properties_patch()  # blocking call

            version = patch["$version"]
            prop_dict = {}

            for prop_name, prop_value in patch.items():
                if prop_name in ignore_keys:
                    continue
                else:
                    prop_dict = self.desired_property_action(prop_name, prop_value, version)
                    await self.device_client.patch_twin_reported_properties(prop_dict)

            

    ################################################################################################       
    ## This is long run code
    ## Start Connection to Azure IoT Central till 1) receive stop command or 2) exception
    ## X509 code is OK to connect to Self-DPS, but not for Azure IoT Central : Get un-catch exception on self.provisioning_device_client.register()
    ################################################################################################
    async def start(self):
        print("on start...")
        if self.provision_type == 'symmetric_key':
            self.provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
                provisioning_host=self.provision_dps_host,
                id_scope=self.provision_id_scope,
                registration_id=self.provision_registration_id,                
                symmetric_key=self.provision_symmetric_key,
            )        
        elif self.provision_type == 'X509':
            x509 = X509(
                cert_file=_CONFIG_PATH + self.cert_cert_file,
                key_file=_CONFIG_PATH + self.cert_key_file,
            )
            self.provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
                provisioning_host=self.provision_dps_host,
                registration_id=self.provision_registration_id,
                id_scope=self.provision_id_scope,
                x509=x509,
            )
        
        
        registration_result = await self.provisioning_device_client.register()
        if registration_result.status == "assigned":
            if self.provision_type == 'symmetric_key':
                self.device_client = IoTHubDeviceClient.create_from_symmetric_key(
                    symmetric_key=self.provision_symmetric_key,
                    hostname=registration_result.registration_state.assigned_hub,
                    device_id=registration_result.registration_state.device_id,
                    product_info=self.pnpModelId,
                )
            elif self.provision_type == 'X509':
                self.device_client = IoTHubDeviceClient.create_from_x509_certificate(
                    x509=x509,
                    hostname=registration_result.registration_state.assigned_hub,
                    device_id=registration_result.registration_state.device_id,
                    product_info=self.pnpModelId,
                )

            try:
                # Connect the client.
                await self.device_client.connect()
            except:
                print('Fail on connect to Azure IoT Central')
                self.connection_status = 'Fail'
                self.connection_ts = time.time()
                return
            else:
                print('Connected to Azure IoT Central')
                self.connection_status = 'Connected'
                self.connection_ts = time.time()

            # Declare Direct Method & Desired Properties & Telemetry Handler
            listeners = asyncio.gather(
                self.execute_command_listener(
                method_name="reboot",
                user_command_handler=self.cmd_reboot,
                create_user_response_handler=self.cmd_reboot_response,
                ),
                self.execute_command_listener(
                method_name="turnOnMonitor",
                user_command_handler=self.cmd_turnOnMonitor,
                create_user_response_handler=self.cmd_turnOnMonitor_response,
                ),
                self.execute_command_listener(
                method_name="turnOffMonitor",
                user_command_handler=self.cmd_turnOffMonitor,
                create_user_response_handler=self.cmd_turnOffMonitor_response,
                ),
                self.execute_property_listener(),
            )            

            # send out read only properties
            await self.send_all_reported_properties()            

            # keep device client running till receive stop signal
            loop = asyncio.get_running_loop()
            loop_finished = loop.run_in_executor(None, self.handle_received_command)
            await loop_finished    

            # shutdown direct methods & properties call back listener
            if not listeners.done():
                listeners.set_result("DONE")
            listeners.cancel()

            # Finally, shut down the client
            await self.device_client.shutdown()

            print('Disconnect & Shutdown Client')  
            self.connection_status = 'Disconnected'  
            self.connection_ts = time.time() 
        else:
            print('Fail on connect to Azure IoT Central')
            self.connection_status = 'Fail'
            self.connection_ts = time.time()
            return
        return            

    ################################################################################################################
    ## Waiting and handle coming commands : start / stop / status
    ## Be called by 1) main entry program, run(); 2) client connected long run loop
    ## Exit conditions:
    ##      1) When iot Central disconnect, exit when received every single command
    ##      2) When iot Central connected, exit when received 'stop' command
    ################################################################################################################
    def handle_received_command(self):
        in_connecting = False
        command = None
        while True:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = self.sock.accept()

            try:
                print('connection from ', client_address)
                while True:
                    # Receive client data hardcode Max 128 bytes
                    command = connection.recv(128).decode("utf-8")
                    print(command)
                    if command == 'start':
                        if self.enable is not True:
                            self.load_config_file()  
                            in_connecting = True
                        
                        self.enable = True
                        connection.sendall(b'OK')  
                        break
                    elif command == 'stop':
                        self.enable = False
                        connection.sendall(b'OK')  
                        break
                    elif command == 'status':
                        data = {}
                        data['connectionStatus'] = self.connection_status
                        data['connectionTS'] = self.connection_ts
                        dataString = json.dumps(data)
                        connection.sendall(dataString.encode())  
                        break

            finally:
                # Clean up the connection                
                print('close session')
                connection.close()
            
            # Receive command to start connection, and now is stop
            if in_connecting:
                break
            
            # Keep in long loop for connected status
            if self.enable :
                continue
            else :
                break
        return

    def run(self):
        try:
            while True:
                if self.enable:
                    asyncio.run(self.start())
                else:
                    self.handle_received_command()
                    
                time.sleep(1)                           # Flush every second    
        except:
            print('program get exception')
            self.sock.close()
        else:        
            print('program is going to die')
            self.sock.close()


if __name__ == '__main__':  
    # Launch Azure IoT Central Client
    iotCentral = azureIoTCentral()
    iotCentral.run()