import signal, asyncio, json, time, os, glob
from tpeClient import tpeClient
from azureClient import azureClient
from storageClient import storageClient

class moduleInstance():
    # Event indicating client stop
    loop = None
    azure_client = None
    tpe_client = None
    storage_client = None
    upload_log = False
    set_log = False
    log_frequency_new = 0
    set_message = False
    message_frequency_new = 0
    message_frequency = 30
    log_frequency = 86400
    max_log_count = 0
    counter_message = 0
    counter_log = 0

    def __init__(self):
        self.print_settings()
        self.tpe_client = tpeClient()
        self.azure_client = azureClient(self)
        self.storage_client = storageClient()

        # Set the Edge termination handler
        self.loop = asyncio.get_event_loop()
        for signame in ('SIGINT', 'SIGTERM'):
            self.loop.add_signal_handler(getattr(signal, signame), lambda signame=signame: asyncio.create_task(self.module_termination_handler(signame)))

        # getting the initial twin
        asyncio.gather(self.azure_client.connect())

        # Run worker threads
        log_worker = self.loop.create_task(self.do_work_log())
        message_worker = self.loop.create_task(self.do_work_message())
        self.loop.run_forever()

    def print_settings(self):
        print('============================================================')
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Module Start')
        print('[Module Default Settings]')
        print('Enable Log Upload = ' + str(self.upload_log))
        print('Log Upload Frequency = ' + str(self.log_frequency))
        print('Maximum Local Log File Count = ' + str(self.max_log_count))
        print('Heartbeat Message Frequency = ' + str(self.message_frequency))
        print('============================================================')

    # Define a handler to cleanup when module is is terminated by Edge
    async def module_termination_handler(self, signal):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Module Stopped')
        await self.azure_client.terminate()
        self.loop.stop()

    async def do_work_message(self):
        while True:
            if self.set_message:
                if self.azure_client:
                    await self.azure_client.send_message('output', {'message': 'heartbeat'})
                self.counter_message = 0
                self.message_frequency = self.message_frequency_new
                self.set_message = False
            if self.counter_message == self.message_frequency - 1:
                if self.azure_client:
                    await self.azure_client.send_message('output', {'message': 'heartbeat'})
                self.counter_message = 0
            else:
                self.counter_message += 1
            await asyncio.sleep(1)

    async def do_work_log(self):
        while True:
            if self.set_log:
                if self.upload_log:
                    self.prepare_and_upload()
                self.counter_log = 0
                self.log_frequency = self.log_frequency_new
                self.set_log = False
            if self.counter_log == self.log_frequency - 1:
                if self.upload_log:
                    self.prepare_and_upload()
                self.counter_log = 0
            else:
                self.counter_log += 1
            await asyncio.sleep(1)

    def prepare_and_upload(self):
        result = self.prepare_log()
        if result['status'] >= 200 and result['status'] < 300:
            return self.upload_log_to_storage(result['message'])
        else:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Failed to prepare log, skipped.')
            return 1, 'Failed to prepare log, skipped.'

    def prepare_log(self):
        self.remove_log(self.max_log_count - 1) # Clean up a position for the new log file
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Prepare Log] Start')
        result = self.tpe_client.invoke_api('GET', '/system/log?download=true', None, True)
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Prepare Log] Complete, file path = ' + result['message'])
        return result

    def remove_log(self, keep_file_count):
        if keep_file_count <= 0 or keep_file_count == None:
            return
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Remove Log] Start')
        files = sorted(glob.glob('/host/log/*.zip'))
        count = len(files)
        for i in range(count - keep_file_count):
            os.remove(files[i])
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Remove Log] Complete')

    def set_blob_connection_string(self, azure_blob_connection_string):
        return self.storage_client.set_blob_connection_string(azure_blob_connection_string)

    def set_blob_storage_container(self, azure_blob_storage_container):
        return self.storage_client.set_blob_storage_container(azure_blob_storage_container)

    def set_log_frequency(self, log_frequency):
        self.set_log = True
        self.log_frequency_new = log_frequency
        return self.log_frequency_new

    def set_max_log_count(self, max_log_count):
        self.max_log_count = max_log_count
        self.remove_log(self.max_log_count)
        return self.max_log_count

    def set_message_frequency(self, message_frequency):
        self.set_message = True
        self.message_frequency_new = message_frequency
        return self.message_frequency_new

    def upload_log_to_storage(self, filepath):
        result = self.storage_client.upload_log_to_storage(filepath)
        return result

    def set_trigger(self, upload_log):
        self.upload_log = upload_log
        self.set_log = True

async def main():
    await module_client.run()

if __name__ == '__main__':
    module_client = moduleInstance()

