import json, os, pyjq, asyncio
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import MethodResponse, Message

class azureClient():
    azure_client = None
    stop_event = None

    def __init__(self):
        # The client object is used to interact with your Edge hub.
        global azure_client
        self.config = {}
        self.azure_client = IoTHubModuleClient.create_from_edge_environment()

        try:
            # load config
            self.load_config()
            # set the callback method when receiving desired properties
            self.azure_client.on_twin_desired_properties_patch_received = self.twin_patch_handler
            # set the callback method when receiving a routing message from edgeHub
            self.azure_client.on_message_received = self.message_handler
            # set the callback method when receiving a direct method
            self.azure_client.on_method_request_received = self.method_handler            
        except:
            print('Exception: azureClient init()')
            self.azure_client.shutdown()
            raise
    def load_config(self):
        if (os.path.isfile('module_config.json') is True):
            with open('module_config.json') as f:
                self.config = json.load(f)
    
    def save_config(self):
        # Serializing json
        json_object = json.dumps(self.config, indent=4)
        
        # Writing to sample.json
        with open('module_config.json', 'w') as outfile:
            outfile.write(json_object)

    # Callback method for receiving a routing message from edgeHub
    async def message_handler(self, message):
        print('[Message Received]\nTopic = {0}\nPayload = {1}\nProperties = {2}'.format(message.input_name, message.data.decode('utf-8'), message.custom_properties))
        
        # If comming topic is NOT define in config file, then return
        if self.config["setting"]["input_topic"] != "*":
            if message.input_name != self.config["setting"]["input_topic"]:
                print("\nInput topic not match, exit.")
                return
        
        # Run JQ to convert message and Send result to EdgeHub
        incomming_message = json.loads(message.data.decode('utf-8'))
        jqFiler = self.config["setting"]["jq"].replace("'","\"")
        print("\nRun jq convert payload.....")
        output_message = pyjq.all(jqFiler, incomming_message)
        print("Run jq convert payload Done\n")
        await self.send_message(self.config["setting"]["output_topic"], output_message)


    # Callback method for receiving a direct method
    async def method_handler(self, method_request):
        
        print('[Direct Method Received]\nMethod Name = {0}'.format(method_request.name))        
        if method_request.payload != None:
            print('Payload = {0}'.format(method_request.payload))
        
        if method_request.name == 'get_config':  
            payload = self.config  # set response payload
            status = 200  # set return status code
        elif method_request.name == 'set_config':
            if "setting" in method_request.payload:
                if "input_topic" in method_request.payload["setting"]:
                    self.config["setting"]["input_topic"] = method_request.payload["setting"]["input_topic"]                    
                if "jq" in method_request.payload["setting"]:
                    self.config["setting"]["jq"] = method_request.payload["setting"]["jq"]                    
                if "output_topic" in method_request.payload["setting"]:
                    self.config["setting"]["output_topic"] = method_request.payload["setting"]["output_topic"]
            
            self.save_config()
            payload = self.config  # set response payload
            status = 200  # set return status code
            
            # Update Module Twin
            await self.update_reported_properties(self.config)
        else:
            payload = {'message': 'Error: The method name is not supported.'}  # set response payload
            status = 404  # set return status code        
        
        # Send response back to direct method
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        print('[Direct Method Response]\nStatus = {0}\nPayload = {1}'.format(status, payload))
        await self.azure_client.send_method_response(method_response)  # send response        

    # Callback method for receiving desired properties
    async def twin_patch_handler(self, patch):
        new_value_flag = False
        print('[Twin Received]\nDesired = {0}'.format(patch))  
        if "setting" in patch:
            if "input_topic" in patch["setting"]:
                self.config["setting"]["input_topic"] = patch["setting"]["input_topic"]
                new_value_flag = True
            if "jq" in patch["setting"]:
                self.config["setting"]["jq"] = patch["setting"]["jq"]
                new_value_flag = True                  
            if "output_topic" in patch["setting"]:
                self.config["setting"]["output_topic"] = patch["setting"]["output_topic"]
                new_value_flag = True

        if new_value_flag:
            self.save_config()        
            # Update Module Twin            
            await self.update_reported_properties(self.config)
        else:
            print('No new value to report.')
    
    # Send out reported properties. 4K issue
    async def update_reported_properties(self, properties):
        reported_properties = {}
        reported_properties["setting"] = {}
        if len(properties["setting"]["jq"]) > 3200:
            reported_properties["setting"]["jq"] = "over size, please retrieve the value by Direct Method: get_config."
        else:
            reported_properties["setting"]["jq"] = properties["setting"]["jq"]
        
        reported_properties["setting"]["input_topic"] = properties["setting"]["input_topic"]
        reported_properties["setting"]["output_topic"] = properties["setting"]["output_topic"]
        
        print('[Twin Publish]\nReported = {0}'.format(reported_properties))
        await self.azure_client.patch_twin_reported_properties(reported_properties)
                
    # Define a handler to cleanup when module is is terminated by Edge
    async def module_termination_handler(self, signal):
        global module_client
        print('IoTHubClient sample stopped by Edge')
        self.stop_event.set()
        await self.azure_client.disconnect()

    async def connect(self):
        await self.azure_client.connect()
        
        # send reported properties to Azure IoT Hub at startup
        await self.update_reported_properties(self.config)

    async def send_message(self, topic, message):
        print('[Sending D2C Message]\nTopic = {0}\nPayload = {1}'.format(topic, message))
        msg = Message(json.dumps(message))
        msg.content_encoding = 'utf-8'
        msg.content_type = 'application/json'
        await self.azure_client.send_message_to_output(msg, topic)

    def set_stop(self, stop):
        self.stop_event = stop
