import os, threading, signal, asyncio, json, time
from azureClient import azureClient
from tpmHelper import tpmHelper

class moduleInstance():
    # Event indicating client stop
    stop_event = threading.Event()
    azure_client = None
    credential_path = './data/credentials'
    tpm_helper = None

    def __init__(self):
        self.tpm_helper = tpmHelper()
        self.azure_client = azureClient(self)

    # Define a handler to cleanup when module is is terminated by Edge
    async def module_termination_handler(self, signal):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Stop Signal Receieved')
        await self.azure_client.terminate()
        self.stop_event.set()

    # define behavior for receiving a message
    async def message_handler(self, message):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Message Received] Topic = {0}, Payload = {1}, Properties = {2}'.format(message.input_name, message.data.decode('utf-8'), message.custom_properties))

    # define behavior for handling method calls
    async def method_handler(self, method_request):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Direct Method Received] Method Name = {0}, Payload = {1}'.format(method_request.name, method_request.payload))

        payload = {}
        if method_request.name == 'encrypt':
            result = self.tpm_helper.encrypt(None, method_request.payload['data'])
            payload['result'] = result
            status = 200
        elif method_request.name == 'decrypt':
            result = self.tpm_helper.decrypt(None, method_request.payload['data'])
            payload['result'] = result
            status = 200
        else:
            payload['message'] = 'unsupported method name'
            status = 500

        await self.azure_client.send_method_response(method_request, status, payload)

    # define behavior for receiving a twin patch
    async def twin_patch_handler(self, patch):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Twin Received] Desired = {0}'.format(patch))

        report = {}
        await self.azure_client.send_twin(report)

    async def run(self):
        # getting the initial twin
        await self.azure_client.connect()

        while not self.stop_event.is_set():
            await asyncio.sleep(1)

        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Module Stopped')

if __name__ == '__main__':
    module_client = moduleInstance()

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), lambda signame=signame: asyncio.create_task(module_client.module_termination_handler(signame)))
    loop.run_until_complete(module_client.run())

