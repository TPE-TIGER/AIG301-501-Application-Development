import sys
from xml.etree.ElementTree import TreeBuilder
import logging
import time
import os
import requests
import json
import datetime

from thingspro.edge.tag_v1 import tag
from opcua import Client
from opcua import ua
from opcua.ua.uatypes import VariantType
from datetime import timezone

_config_file = open('/app/cfg/config.json')
_config = json.load(_config_file)
_config_file.close()

class TPE_Handler(object):

    """
    TPE Application Class which handles tag creation and tag update
    """

    def call_API(self, method, endPoint, payload):
        result = {}
        cmdURL = self._tpeURL + endPoint
        try:
            if method.lower() == 'put':
                response = requests.put(cmdURL, json=payload, headers=self._headers, verify=False)
            elif method.lower() == 'post':
                response = requests.post(cmdURL, json=payload, headers=self._headers, verify=False)
            elif method.lower() == 'delete':
                response = requests.delete(cmdURL, json=payload, headers=self._headers, verify=False)
            elif method.lower() == 'patch':
                response = requests.patch(cmdURL, json=payload, headers=self._headers, verify=False)
            elif method.lower() == 'get':
                response = requests.get(cmdURL, json=payload, headers=self._headers, verify=False)
        except Exception as e:
            print('Exception: ' + str(e))
            return str(e)

        if (response.status_code >= 200) and (response.status_code < 300) :
            result['status'] = 'success'
            result['message'] = response.text
        else:
            result['status'] = 'fail'
            result['message'] = response.text

        return result

    def create_tag(self, tag):
        try:
            # Check tag's existance
            result = self.call_API('get', '/tags/list?provider='+self._prvd_name, None)
            messageJson = json.loads(result['message'])
            if 'data' in messageJson:
                tagList = messageJson['data']
                for i in tagList:
                    if (i['srcName'] == self._src_name) and (i['tagName'] == tag['TPE_tag_name']):
                        print('Existed tag: ' + self._src_name + ': ' + tag['TPE_tag_name'])
                        return

            # Payload for tag creation
            postTag = {
                'prvdName': self._prvd_name,
                'srcName': self._src_name,
                'tagName': tag['TPE_tag_name'],
                'dataType': tag['TPE_data_type'],
                'access': 'rw'
            }

            # Create tag
            result = self.call_API('post', '/tags/virtual', postTag)
            return 'OK'
        except Exception as e:
            print('Exception: ' + str(e))
            return str(e)

    def publish_tag(self, tag, val, timestamp):
        try:
            tagValue = {
                'prvdName': self._prvd_name,
                'srcName': self._src_name,
                'tagName': tag['TPE_tag_name'],
                'dataValue': val,
                'dataType': tag['TPE_data_type'],
                'ts': int(timestamp.replace(tzinfo=timezone.utc).timestamp() * 1000000)
            }
            print('Publish tag: ' + str(tagValue))
            self._publisher.publish(tagValue)
            return 'OK'
        except Exception as e:
            print('Exception: ' + str(e))
            return str(e)

    def __init__(self):
        self._prvd_name = _config['TPE_prvd_name']
        self._src_name = _config['TPE_src_name']

        # Define Tag Publisher
        self._publisher = tag.Publisher()

        # Define ThingsPro Edge API Environment
        self._tpeURL = 'http://' + os.getenv('APPMAN_HOST_IP', '127.0.0.1') + ':59000/api/v1'
        self._headers = {}
        self._headers['Content-Type'] = 'application/json'
        f=open('/run/mx-api-token', 'r')
        self._headers['mx-api-token'] = f.read()
        f.close()

        # Create TPE virtual tags
        for i in _config['nodes']:
            self.create_tag(i)

class OPC_Client_Sub(object):

    """
    Subscription Handler. This class should publish updates to TPE when notified.
    """

    def datachange_notification(self, node, val, data):
        for i in _config['nodes']:
            # Compare the incoming node ID with the original node ID specified in the json config file, to get it's corresponding tag name in TPE
            if i['node_id'] == str(node):
                self._tpe.publish_tag(i, val, data.monitored_item.Value.ServerTimestamp)

    def event_notification(self, event):
        print('Python: New event', event)

    def __init__(self):
        self._tpe = TPE_Handler()

def variant_type_to_tpe_type(vtype):
    return {
        VariantType.Boolean: 'boolean',
        VariantType.Int16: 'int16',
        VariantType.UInt16: 'uint16',
        VariantType.Int32: 'int32',
        VariantType.UInt32: 'uint32',
        VariantType.Int64: 'int64',
        VariantType.UInt64: 'uint64',
        VariantType.Float: 'float',
        VariantType.Double: 'double',
        VariantType.String: 'string',
        VariantType.ByteString: 'byte-array',
    }.get(vtype, 'raw')

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    # Create OPC Client Object
    client = Client(_config['OPC_server'])
    try:
        # Connect to server
        client.connect()
        client.load_type_definitions()  # load definition of server specific structures/extension objects

        for i in _config['nodes']:
            node = client.get_node(i['node_id'])
            i['node'] = node
            i['TPE_data_type'] = variant_type_to_tpe_type(node.get_data_type_as_variant_type())

        # Create subscription
        sub_handler = OPC_Client_Sub()
        sub = client.create_subscription(1000, sub_handler)
        for i in _config['nodes']:
            node = client.get_node(i['node_id'])
            sub.subscribe_data_change(node)
            time.sleep(0.1)

        while True:
            time.sleep(1)

    finally:
        print('Exiting...')
        sub.delete()
        client.disconnect()