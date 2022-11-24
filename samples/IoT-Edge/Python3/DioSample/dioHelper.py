import json
import subprocess

config_path = '/etc/moxa-configs/moxa-dio-control.json'

class dioHelper():
    config = {}
    dinPortNum = 0
    doutPortNum = 0

    def __init__(self):
        with open(config_path) as f:
            self.config = json.load(f)
            self.dinPortNum = self.config['NUM_OF_DIN_PORTS']
            self.doutPortNum = self.config['NUM_OF_DOUT_PORTS']

    def get(self, dioType, port):
        command = ''
        if dioType == 'in':
            command = 'mx-dio-ctl -i ' + str(port)
        elif dioType == 'out':
            command = 'mx-dio-ctl -o ' + str(port)
        return self.exec(command)

    def set(self, dioType, port, value):
        command = 'mx-dio-ctl -o ' + str(port) + ' -s ' + str(value)
        return self.exec(command)

    def exec(self, command):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = p.communicate()

        if p.returncode != 0:
            ret = 'Error[{0}]: Command failed, out = {1}, error = {2}'.format(p.returncode, out, err)
            return ret, 500
        return out
