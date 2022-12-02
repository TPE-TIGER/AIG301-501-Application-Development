from flask import Flask, request
from flask_expects_json import expects_json
import json

app = Flask(__name__)
_config_path = '/app/cfg/config.json'

@app.route('/api/v1/ftp-to-s3', methods=['GET'])
def get_cfg():
    try:
        with open(_config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        ret = {}
        ret['message'] = str(e)
        return json.dumps(ret), 500

@app.route('/api/v1/ftp-to-s3', methods=['POST'])
@expects_json({
    'type': 'object',
    'properties': {
        'ftp': {
            'type': 'object',
            'properties': {
                'ip': {'type': 'string'},
                'username': {'type': 'string'},
                'password': {'type': 'string'}
            },
            'required': ['ip', 'username', 'password']
        },
        'aws': {
            'type': 'object',
            'properties': {
                'key_id': {'type': 'string'},
                'key': {'type': 'string'},
                's3_bucket': {'type': 'string'}
            },
            'required': ['key_id', 'key', 's3_bucket']
        },
        'file': {
            'type': 'object',
            'properties': {
                'source': {'type': 'string'},
                'cache': {'type': 'string'},
                'destination': {'type': 'string'}
            },
            'required': ['source', 'cache', 'destination']
        },
    },
    'required': ['ftp', 'aws', 'file']
})
def set_cfg():
    try:
        with open(_config_path, 'w') as f:
            json.dump(request.get_json(), f)
            return request.get_json()
    except Exception as e:
        ret = {}
        ret['message'] = str(e)
        return json.dumps(ret), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

