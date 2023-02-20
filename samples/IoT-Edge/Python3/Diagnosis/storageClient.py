import os, time
from azure.storage.blob import BlobServiceClient, ContentSettings  # pip install azure-storage-blob

class storageClient():
    azure_blob_storage_container = None
    blob_service_client = None

    def set_blob_connection_string(self, azure_blob_connection_string):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Blob] Connection string = ' + azure_blob_connection_string)
        try:
            self.blob_service_client =  BlobServiceClient.from_connection_string(azure_blob_connection_string)
        except:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Error: Cannot create blob client')
        return azure_blob_connection_string

    def set_blob_storage_container(self, azure_blob_storage_container):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Blob] Container = ' + azure_blob_storage_container)
        self.azure_blob_storage_container = azure_blob_storage_container
        return self.azure_blob_storage_container

    def upload_log_to_storage(self, filepath):
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Upload Log] Start. Container = ' + str(self.azure_blob_storage_container) + ', File = ' + filepath)
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.azure_blob_storage_container, blob=os.path.basename(filepath))
        except:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Upload Log] Blob storage or container does not exist.')
            return 1, 'Failed to connect to the target blob storage, please check the blob connection string and container name settings.'
        if not blob_client:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Upload Log] Failed to connect to the target container.')
            return 1, 'Failed to connect to the target blob storage, please check the blob connection string and container name settings.'

        content_settings = ContentSettings(content_type='application/zip')
        try:
            blob_client.upload_blob(open(filepath, 'rb'), overwrite=True, content_settings=content_settings, timeout=10)
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Upload Log] Complete, URL = ' + blob_client.url)
            os.remove(filepath)
            return 0, blob_client.url
        except Exception as e:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Upload Log] Failed.')
            print(e)
            return 2, 'Failed to upload log, please check the blob settings and network connectivity.'

