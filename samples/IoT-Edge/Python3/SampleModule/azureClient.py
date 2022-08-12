import json
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import MethodResponse, Message
# import asyncio
# from tpeClient import tpeClient

class azureClient():
    azure_client = None
    tpe_client = None
    stop_event = None

    def __init__(self, tpe):
        # The client object is used to interact with your Edge hub.
        global azure_client
        self.azure_client = IoTHubModuleClient.create_from_edge_environment()
        self.tpe_client = tpe

        try:
            # set the twin patch handler on the client
            self.azure_client.on_twin_desired_properties_patch_received = self.twin_patch_handler
            # set the message handler on the client
            self.azure_client.on_message_received = self.message_handler
            # set the method handler on the client
            self.azure_client.on_method_request_received = self.method_handler
        except:
            print('Exception: azureClient init()')
            self.azure_client.shutdown()
            raise

    # define behavior for receiving a message
    async def message_handler(self, message):
        print('[Message Received]\nTopic = {0}\nPayload = {1}\nProperties = {2}'.format(message.input_name, message.data.decode('utf-8'), message.custom_properties))

    # define behavior for handling method calls
    async def method_handler(self, method_request):
        print('[Direct Method Received]\nMethod Name = {0}\nPayload = (1)'.format(method_request.name, method_request.payload))

        # Sample command name: thingspro_api_v1
        # Sample payload:
        # {
        #   "path": "/system/sshserver",
        #   "method": "PUT",
        #   "request_body": {"enable": true, "port": 22}
        # }

        if method_request.name == 'thingspro_api_v1':
            if isinstance(method_request.payload, dict):
                if 'method' in method_request.payload and 'path' in method_request.payload and 'request_body' in method_request.payload:
                    # Invoke TPE API
                    result = self.tpe_client.invoke_api(method_request.payload['method'], method_request.payload['path'], method_request.payload['request_body'])
                    if result['status'] == 'success':
                        payload = {'message': result['message']}  # set response payload
                        status = 200  # set return status code
                        report = {"sshserver": json.loads(result['message'])['data']}
                        print('Reported = {0}'.format(report))
                        await self.azure_client.patch_twin_reported_properties(report)
                    else:
                        payload = {'message': 'Error: Configuration failed.'}  # set response payload
                        status = 400  # set return status code
                else:
                    payload = {'message': 'Error: Malformed payload.'}
                    status = 400
            else:
                payload = {'message': 'Error: Wrong payload type, expecting a JSON object.'}  # set response payload
                status = 400  # set return status code
        else:
            payload = {'message': 'Error: The method name is not supported.'}  # set response payload
            status = 404  # set return status code

        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        print('[Direct Method Response]\nStatus = {0}\nPayload = {1}'.format(status, payload))
        await self.azure_client.send_method_response(method_response)  # send response

    # define behavior for receiving a twin patch
    async def twin_patch_handler(self, patch):
        print('[Twin Received]\nDesired = {0}'.format(patch))

        # Sample desired format:
        # {
        #   'sshserver': {
        #       'enable': true,
        #       'port': 22
        #   }
        # }

        if 'sshserver' in patch:
            result = self.tpe_client.invoke_api('PUT', '/system/sshserver', patch['sshserver'])
            # Send reported twin if configuration succeeded
            if result['status'] == 'success':
                report = {"sshserver": json.loads(result['message'])['data'], "data": None}
                print('Reported = {0}'.format(report))
                await self.azure_client.patch_twin_reported_properties(report)

    # Define a handler to cleanup when module is is terminated by Edge
    async def module_termination_handler(self, signal):
        global module_client
        print('IoTHubClient sample stopped by Edge')
        self.stop_event.set()
        await self.azure_client.disconnect()

    async def connect(self):
        await self.azure_client.connect()

    async def send_message(self, topic, message):
        print('[Sending D2C Message]\nTopic = {0}\nPayload = {1}'.format(topic, message))
        msg = Message(json.dumps(message))
        msg.content_encoding = 'utf-8'
        msg.content_type = 'application/json'
        await self.azure_client.send_message_to_output(msg, topic)

    def set_stop(self, stop):
        self.stop_event = stop

#async def main():
#    tpe_client = tpeClient()
#    azure_client = azureClient(tpe_client)
#    await azure_client.connect()
#    while True:
#        await asyncio.sleep(1000)
#
#if __name__ == '__main__':
#    asyncio.run(main())
