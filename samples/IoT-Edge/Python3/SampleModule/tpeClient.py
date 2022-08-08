import json, os.path
import requests
from thingspro.edge.tag_v1 import tag

class tpeClient:

    _CONFIG_FILE = 'tag_config.json'
    _APPMAN_HOST_IP = os.getenv('APPMAN_HOST_IP', '172.31.8.1')
    _API_TOKEN_FILE = '/var/run/mx-api-token'
    _headers = {}
    _config = {}

    def __init__(self):
        self._tpe_url_prefix = 'http://' + self._APPMAN_HOST_IP + ':59000/api/v1'
        self._headers['Content-Type'] = 'application/json'
        with open(self._API_TOKEN_FILE) as f:
            self._headers['mx-api-token'] = f.read()

        # Load config
        self.load_config()
        # Subscribe tags
        self.subscriber = tag.Subscriber()
        for tpe_tag in self._config['Tags']:
            self.subscriber.subscribe(tpe_tag['provider'], tpe_tag['source'], [tpe_tag['tag']])

    def load_config(self):
        if (os.path.isfile(self._CONFIG_FILE) is True):
            with open(self._CONFIG_FILE) as f:
                self._config = json.load(f)

    def set_subscriber_callback(self, func):
        self.subscriber.subscribe_callback(func)

    def invoke_api(self, method, end_point, payload):
        result = {}
        cmd_url = self._tpe_url_prefix + end_point
        try:
            if method.lower() == 'put':
                response = requests.put(cmd_url, json=payload, headers=self._headers, verify=False)
            elif method.lower() == 'post':
                response = requests.post(cmd_url, json=payload, headers=self._headers, verify=False)
            elif method.lower() == 'delete':
                response = requests.delete(cmd_url, json=payload, headers=self._headers, verify=False)
            elif method.lower() == 'patch':
                response = requests.patch(cmd_url, json=payload, headers=self._headers, verify=False)
            elif method.lower() == 'get':
                response = requests.get(cmd_url, json=payload, headers=self._headers, verify=False)
        except Exception as e:
            print('Exception: ' + str(e))
            return str(e)

        if (response.status_code >= 200) and (response.status_code < 300) :
            result['status'] = 'success'
            result['message'] = response.text
        else:
            result['status'] = 'fail'
            result['message'] = response.text
        print(response.status_code)
        print(response.text)
        return result

# if __name__ == '__main__':
#     tpe_client = tpeClient()
#     tpe_client.invoke_api('PUT', '/system/sshserver', {"enable": True})
