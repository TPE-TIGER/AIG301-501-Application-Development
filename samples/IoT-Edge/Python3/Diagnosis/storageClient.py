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
        print(time.strftime('%Y/%m/%d %H:%M:%S') + ' [Upload Log] Upload start. Container = ' + str(self.azure_blob_storage_container) + ', File = ' + filepath)
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.azure_blob_storage_container, blob=os.path.basename(filepath))
        except:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Error: Blob or container does not exist')
            return None
        content_settings = ContentSettings(content_type='application/zip')
        blob_client.upload_blob(open(filepath, 'rb'), overwrite=True, content_settings=content_settings)
        os.remove(filepath)
        return blob_client.url
