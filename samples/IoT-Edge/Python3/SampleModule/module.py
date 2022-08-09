import os, threading, signal, asyncio, json
from tpeClient import tpeClient
from azureClient import azureClient

# Event indicating client stop
stop_event = threading.Event()
azure_client = None
tpe_client = None
config= {}

def load_config():
    global config
    if (os.path.isfile('module_config.json') is True):
        with open('module_config.json') as f:
            config = json.load(f)

async def run():
    global azure_client

    # getting the initial twin
    await azure_client.connect()
    
    global tpe_client
    await tpe_client.run()

    # Do whatever needed in the loop
    global stop_event
    while not stop_event.is_set():
        await asyncio.sleep(1000)

def tag_callback(data):
    # print(data)
    global azure_client
    if azure_client and 'dataValue' in data:
        # Process data
        data['dataValue'] = data['dataValue'] * 2.0
        # Send message
        asyncio.run(azure_client.send_message(config['topic'], data))

async def main():
    load_config()

    global tpe_client
    tpe_client = tpeClient()
    tpe_client.set_tag_callback(tag_callback)

    global azure_client
    azure_client = azureClient(tpe_client)
    # Set the Edge termination handler
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), lambda signame=signame: asyncio.create_task(azure_client.module_termination_handler(signame)))
    global stop_event
    azure_client.set_stop(stop_event)
    tpe_client.set_stop(stop_event)

    await run()

if __name__ == '__main__':
    asyncio.run(main())
