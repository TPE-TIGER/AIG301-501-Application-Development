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
        global azure_client
        self.azure_client = IoTHubModuleClient.create_from_edge_environment()
        self.module = module

        try:
            # set the twin patch handler on the client
            self.azure_client.on_twin_desired_properties_patch_received = self.twin_patch_handler
            # set the message handler on the client
            self.azure_client.on_message_received = self.message_handler
            # set the method handler on the client
            self.azure_client.on_method_request_received = self.method_handler
        except:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Exception: azureClient init()')
            self.azure_client.shutdown()
            raise

    # define behavior for receiving a message
    async def message_handler(self, message):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Message Received] Topic = {0}, Payload = {1}, Properties = {2}'.format(message.input_name, message.data.decode('utf-8'), message.custom_properties))

    # define behavior for handling method calls
    async def method_handler(self, method_request):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Direct Method Received] Method Name = {0}, Payload = {1}'.format(method_request.name, method_request.payload))

        result = self.module.prepare_and_upload()
        if result:
            payload = {'message': 'File Upload Done', 'URL': result}
            status = 200
        else:
            payload = {'message': 'Failed to upload syslog, do you have azure_blob_connection_string and azure_blob_storage_container configured?'}  # set response payload
            status = 500  # set return status code

        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Direct Method Response] Status = {0}. Payload = {1}'.format(status, payload))
        await self.azure_client.send_method_response(method_response)  # send response

    # define behavior for receiving a twin patch
    async def twin_patch_handler(self, patch):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Twin Received] Desired = {0}'.format(patch))

        report = {}

        if 'upload_log' in patch:
            if patch['upload_log'] is not None:
                self.module.set_trigger(patch['upload_log'])
                report['upload_log'] = patch['upload_log']
            
        if 'azure_blob_connection_string' in patch:
            if patch['azure_blob_connection_string']:
                result = self.module.set_blob_connection_string(patch['azure_blob_connection_string'])
                report['azure_blob_connection_string'] = result

        if 'azure_blob_storage_container' in patch:
            if patch['azure_blob_storage_container']:
                result = self.module.set_blob_storage_container(patch['azure_blob_storage_container'])
                report['azure_blob_storage_container'] = result

        if 'log_frequency' in patch:
            if patch['log_frequency']:
                result = self.module.set_log_frequency(patch['log_frequency'])
                report['log_frequency'] = result

        if 'message_frequency' in patch:
            if patch['message_frequency']:
                result = self.module.set_message_frequency(patch['message_frequency'])
                report['message_frequency'] = result

        if report:
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
