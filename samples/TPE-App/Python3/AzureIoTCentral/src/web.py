# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import os, json, time, socket, os.path

app = Flask(__name__)

#_CONFIG_PATH = 'D:\\OneDrive\\Git\\AIC-src\\data\\'
_CONFIG_PATH = '/var/thingspro/aic/data/'
_CONFIG_FILE = _CONFIG_PATH + 'config.json'
_CONFIG_json = None

#設定 Flask
app.secret_key = 'my secret key'

# --------------Restful API--------------- #

# FormData. Contains JSON string on configData section & certificate, key file upload
#
#put /api/v1/aic/config
@app.route('/api/v1/aic/config', methods=['PUT'])
def api_put_config(): 
    data = ""
    with open(_CONFIG_FILE) as f:
        data = json.load(f)
    if 'configData' in request.form:
        configData = request.form["configData"]        
        inData = json.loads(configData)
        print(inData)
        if 'enable' in inData:
            data['enable'] = inData['enable']
        if 'provision' in inData:
            if 'dps_host' in inData['provision']:
                data['provision']['dps_host'] = inData['provision']['dps_host']
            if 'id_scope' in inData['provision']:
                data['provision']['id_scope'] = inData['provision']['id_scope']
            if 'type' in inData['provision']:
                data['provision']['type'] = inData['provision']['type']                          
                if 'symmetric_key' in inData['provision']:
                    data['provision']['symmetric_key'] = inData['provision']['symmetric_key']
                if 'registration_id' in inData['provision']:
                    data['provision']['registration_id'] = inData['provision']['registration_id']             
    
    if 'deviceCert' in request.files:
        deviceCer = request.files['deviceCert']
        certFile = _CONFIG_PATH + deviceCer.filename
        deviceCer.save(certFile)
        data['certificate']['cert_file'] = deviceCer.filename        
    
    if 'deviceKey' in request.files:
        deviceKey = request.files['deviceKey']
        keyFile = _CONFIG_PATH + deviceKey.filename
        deviceKey.save(keyFile)
        data['certificate']['key_file'] = deviceKey.filename  
    
    if 'telemetryMapFile' in request.files:
        telemetryMapFile = request.files['telemetryMapFile']
        fileName = _CONFIG_PATH + telemetryMapFile.filename
        telemetryMapFile.save(fileName)
        data['deviceModel']['telemetry_map_file'] = telemetryMapFile.filename      

    with open(_CONFIG_FILE, 'w') as outfile:
        json.dump(data, outfile)

    global _CONFIG_json
    _CONFIG_json = json.loads(json.dumps(data)) 
    return json.dumps(_CONFIG_json)

#put /api/v1/aic/control/start
@app.route('/api/v1/aic/control/start', methods=['PUT'])
def api_put_control_start(): 
    command = 'put start'
    data = forward_to_daemon(command)    
    return get_aic_status()

#put /api/v1/aic/control/stop
@app.route('/api/v1/aic/control/stop', methods=['PUT'])
def api_put_control_stop():
    command = 'put stop'
    data = forward_to_daemon(command)    
    return get_aic_status()

# --------------Index.html---------------- #

@app.route('/api/v1/aic')
def home():
    global _CONFIG_json    
    return render_template('index.html', configData=json.dumps(_CONFIG_json), aicConnectionStatus=get_aic_status()) 

# --------------Internal Functions---------------- #

def load_config():
    global _CONFIG_json

    if (os.path.isfile(_CONFIG_FILE) is not True) :
        with open(_CONFIG_FILE, 'w') as outfile:
            initConfig = {}
            provision = {}
            certificate = {}
            deviceModel = {}

            initConfig["enable"] = False

            provision["dps_host"] = "global.azure-devices-provisioning.net"
            provision["id_scope"] = ""
            provision["type"]  = "symmetric_key"
            provision["registration_id"]  = ""
            provision["symmetric_key"]  = ""
            initConfig["provision"] = provision

            certificate["cert_file"]  = ""
            certificate["key_file"]  = ""
            certificate["trusted_cert"]  = ""
            initConfig["certificate"] = certificate            
            
            deviceModel["telemetry_map_file"] = ""
            initConfig["deviceModel"] = deviceModel
            json.dump(initConfig, outfile)

    with open(_CONFIG_FILE) as f:
        _CONFIG_json = json.load(f)
        print("===  Load Config Data ====")

def get_aic_status():     
    command = 'get status'
    aicStatus = forward_to_daemon(command) 
    if aicStatus == "Exception on Daemon":
        aicStatus = {}
        aicStatus["connectionStatus"] = 'unknow'
        aicStatus["connectionTS"] = time.time()
        aicStatus = json.dumps(aicStatus)
    return aicStatus

def forward_to_daemon(commandString):
    # Create a TCP/IP socket
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    SERVER_ADDRESS = ('localhost', 10000)
    try:
        try:
            SOCKET.send(commandString.encode("utf-8"))
        except:
            # recreate the socket and reconnect
            SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            SOCKET.connect(SERVER_ADDRESS)
            SOCKET.sendall(commandString.encode("utf-8"))

        data = SOCKET.recv(128)
        SOCKET.close()
        return data.decode("utf-8")
    except:
        return 'Exception on Daemon'

# --------------Main Program---------------- #
if __name__ == '__main__':    
    load_config()
    app.run(host='0.0.0.0', port=5449, debug=True)


    
    