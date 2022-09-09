import threading, signal, asyncio
from azureClient import azureClient

# Event indicating client stop
stop_event = threading.Event()
azure_client = None

async def run():
    global azure_client

    # getting the initial twin
    await azure_client.connect()

    # Do whatever needed in the loop
    global stop_event
    while not stop_event.is_set():
        await asyncio.sleep(1)

async def main():   

    global azure_client
    azure_client = azureClient()
    # Set the Edge termination handler
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), lambda signame=signame: asyncio.create_task(azure_client.module_termination_handler(signame)))
    global stop_event
    azure_client.set_stop(stop_event)

    await run()

if __name__ == '__main__':
    asyncio.run(main())