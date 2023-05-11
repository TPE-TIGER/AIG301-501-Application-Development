import json, time, os, multiprocessing
import requests

class apiHelper():

    def __init__(self, username=None, password=None, protocol=None, ip=None, port=None):
        # Compose URL prefix
        if protocol == None:
            _protocol = 'http'
        elif protocol != 'http' and protocol != 'https':
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Error: Unsupported protocol "' + protocol + '", using http instead.')
            _protocol = 'http'
        else:
            _protocol = protocol

        if ip == None:
            _ip = '172.31.8.1'
        else:
            _ip = ip

        if port == None:
            _port = '59000'
        else:
            _port = str(port)

        self._tpe_url_prefix = _protocol + '://' + _ip + ':' + _port + '/api/v1'

        # Setup credentials
        if username == None:
            self._username = 'admin'
        else:
            self._username = username

        if password == None:
            self._password = 'admin@123'
        else:
            self._password = password

        # Default headers
        self._headers = dict()
        self._headers['Content-Type'] = 'application/json'

        # Retrieve token
        self.renew_token()

    def renew_token(self):
        result = self.invoke_api('post', '/auth', {"acceptEULA": True, "name": self._username, "password": self._password})
        try:
            self._headers['Authorization'] = 'Bearer ' + json.loads(result['message'])['data']['token']
        except:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Authentication Failed: Please verify the login credentials.')
            if 'Authorization' in self._headers:
                self._headers.pop('Authorization')

    def invoke_api(self, method, endpoint, payload):
        result = {}
        cmd_url = self._tpe_url_prefix + endpoint
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
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Exception: ' + str(e))
            return str(e)

        if response.status_code >= 200 and response.status_code < 300 :
            result['message'] = response.text
        else:
            result['message'] = response.text
        result['status'] = response.status_code
        # print(response.status_code)
        # print(response.text)
        return result

class tagHelper(apiHelper):

    def __init__(self, username=None, password=None, protocol=None, ip=None, port=None):
        apiHelper.__init__(self, username=username, password=password, protocol=protocol, ip=ip, port=port)
        self._tag_list = None
        self._callback = None
        self._userdata = None
        self._process_pool = list()

    def do_work(self, endpoint, params):
        cmd_url = self._tpe_url_prefix + endpoint
        try:
            if 'onChanged' in params or 'streamInterval' in params:
                with requests.get(cmd_url, headers=self._headers, params=params, verify=False, stream=True) as response:
                    for line in response.iter_lines():
                        if self._callback and line and line.startswith(b'data:'):
                            self._callback(line.decode('utf-8')[5:], self._userdata)
            else:
                with requests.get(cmd_url, headers=self._headers, params=params, verify=False) as response:
                    self._callback(response.text[8:-1], self._userdata)
        except Exception as e:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Exception: ' + str(e))
            return

    def set_callback(self, callback):
        self._callback = callback

    def set_tags(self, tag_list):
        self._tag_list = tag_list

    def start_stream(self, interval=0, userdata=None):
        self._userdata = userdata
        for provider in self._tag_list:
            for source in self._tag_list[provider]:
                params = {}
                for tag in self._tag_list[provider][source]:
                    if not 'tags' in params:
                        params['tags'] = tag
                    else:
                        params['tags'] = params['tags'] + ',' + tag
                endpoint = '/tags/monitor/' + provider + '/' + source
                if interval == 0:
                    params['onChanged'] = 'true'
                elif interval != 0:
                    params['streamInterval'] = interval
                self._process_pool.append(multiprocessing.Process(target=self.do_work, args=(endpoint, params)))
        for process in self._process_pool:
            process.start()

    def stop_stream(self):
        for process in self._process_pool:
            process.terminate()
            process.join()
        self._process_pool.clear()

    def get_tag_values(self, userdata=None):
        self._userdata = userdata
        for provider in self._tag_list:
            for source in self._tag_list[provider]:
                params = {}
                for tag in self._tag_list[provider][source]:
                    if not 'tags' in params:
                        params['tags'] = tag
                    else:
                        params['tags'] = params['tags'] + ',' + tag
                endpoint = '/tags/monitor/' + provider + '/' + source
                self.do_work(endpoint, params)

    def set_tag_value(self, provider, source, tag, data_type, value):
        cmd_url = self._tpe_url_prefix + '/tags/publish'
        payload = {}
        payload['prvdName'] = provider
        payload['srcName'] = source
        payload['tagName'] = tag
        payload['dataType'] = data_type
        payload['dataValue'] = value
        try:
            with requests.post(cmd_url, headers=self._headers, data=json.dumps(payload)) as response:
                result = {}
                result['message'] = response.text
                result['status'] = response.status_code
        except Exception as e:
            print(time.strftime('%Y/%m/%d %H:%M:%S') + ' Exception: ' + str(e))
            return str(e)
