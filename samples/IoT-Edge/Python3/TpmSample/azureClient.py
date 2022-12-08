import json, time
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import MethodResponse, Message
# import asyncio
# from tpeClient import tpeClient

class azureClient():
    azure_client = None
    module = None

    def __init__(self, module):
        # The client object is used to interact with your Edge hub.
        self.azure_client = IoTHubModuleClient.create_from_edge_environment()
        self.module = module

        try:
            # set the twin patch handler on the client
            self.azure_client.on_twin_desired_properties_patch_received = self.module.twin_patch_handler
            # set the message handler on the client
            self.azure_client.on_message_received = self.module.message_handler
            # set the method handler on the client
            self.azure_client.on_method_request_received = self.module.method_handler
        except:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Exception: Cannot initialize azureClient')
            self.azure_client.shutdown()
            raise

    # define behavior for handling method calls
    async def send_method_response(self, method_request, status, payload):
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Direct Method Response] Status = {0}. Payload = {1}'.format(status, payload))
        await self.azure_client.send_method_response(method_response)  # send response

    # define behavior for receiving a twin patch
    async def send_twin(self, report):
        await self.send_twin(report)

    # Disconnect when module is terminated by Edge
    async def terminate(self):
        await self.azure_client.disconnect()

    async def connect(self):
        await self.azure_client.connect()

    async def send_message(self, topic, message):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Sending D2C Message] Topic = {0}, Payload = {1}'.format(topic, message))
        msg = Message(json.dumps(message))
        msg.content_encoding = 'utf-8'
        msg.content_type = 'application/json'
        await self.azure_client.send_message_to_output(msg, topic)

    async def send_twin(self, report):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Sending Module Twin] Report = {}'.format(report))
        await self.azure_client.patch_twin_reported_properties(report)
