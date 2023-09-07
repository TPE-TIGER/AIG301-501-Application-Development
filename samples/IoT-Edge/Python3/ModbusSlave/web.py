from aiohttp import web
from pymodbus.datastore import (
    ModbusSlaveContext,
    ModbusSequentialDataBlock
)
import os
import asyncio
import json
import struct
import requests
from modbusTCPSlave import ModbusTCPSlave
from tpeHelper import tagHelper, apiHelper


datablock = None
tagHelper1 = tagHelper()
config_path = './config.json'
config_js = None


def process_tag(data, userdata):
    global config_js
    data_js = json.loads(data)
    for i in config_js:
        if i['prvdName'] == data_js['prvdName'] and i['srcName'] == data_js['srcName'] and i['tagName'] == data_js['tagName']:
            js = {}
            js['address'] = i['address']
            js['dataType'] = data_js['dataType']
            js['dataValue'] = data_js['dataValue']
            response = requests.post('http://127.0.0.1:80/write', json=js)
#            write_register(js)
            break
    

def initialize():
    global datablock, tagHelper1
    datablock = ModbusSequentialDataBlock(0x00, [0x00] * 100)
    tagHelper1.set_callback(process_tag)


def load_config():
    global config_path, config_js
    tag_list = {}
    if (os.path.isfile(config_path) is True):
        with open(config_path) as f:
            config_js = json.load(f)

    # Tag validation
    for i in config_js:
        if 'prvdName' not in i or 'srcName' not in i or 'tagName' not in i or 'address' not in i:
            print('Error: Invalid Tag, Skipping:' + str(i))
            continue
        if i['prvdName'] not in tag_list:
            tag_list[i['prvdName']] = {}
        if i['srcName'] not in tag_list[i['prvdName']]:
            tag_list[i['prvdName']][i['srcName']] = []
        tag_list[i['prvdName']][i['srcName']].append(i['tagName'])

    # Configure TPE helper
    tagHelper1.stop_stream()
    tagHelper1.set_tags(tag_list)
    tagHelper1.start_stream()


async def config(request):
    global config_path
    if request.method.upper() == 'GET':
        if (os.path.isfile(config_path) is True):
            with open(config_path) as f:
                config = f.read()
            return web.Response(status=200, text=config)
        return web.Response(status=500, text='Error: Cannot Open Config File')

    elif request.method.upper() == 'POST':
        data = await request.text()
        # Payload validation
        try:
            config = json.loads(data)
        except Exception as e:
            print(e)
            return web.Response(status=400, text='Error: Invalid Payload Format, Expecting JSON')
        for i in config:
            if 'prvdName' not in i or 'srcName' not in i or 'tagName' not in i or 'address' not in i:
                print('Error: Invalid Tag, Skipping:' + str(i))
                return web.Response(status=400, text='Error: Invalid Payload')

        # Config update
        if (os.path.isfile(config_path) is True):
            with open(config_path, 'w') as f:
                f.write(data)

        # Apply config
        load_config()
        return web.Response(status=200, text=data)


async def write(request):
    data = await request.text()
    js = json.loads(data)
    result = write_register(js)
    return web.Response(status=result[0], text=result[1])


def write_register(js):
    global datablock
    number_types = ['int16', 'int32', 'int64', 'uint16', 'uint32', 'uint64', 'float', 'double']
    try:
        if js['dataType'] in number_types:
            match js['dataType']:
                case 'int16':
                    r1 = struct.pack('>h', js['dataValue'])
                case 'int32':
                    r1 = struct.pack('>i', js['dataValue'])
                case 'int64':
                    r1 = struct.pack('>q', js['dataValue'])
                case 'uint16':
                    r1 = struct.pack('>H', js['dataValue'])
                case 'uint32':
                    r1 = struct.pack('>I', js['dataValue'])
                case 'uint64':
                    r1 = struct.pack('>Q', js['dataValue'])
                case 'float':
                    r1 = struct.pack('>f', js['dataValue'])
                case 'double':
                    r1 = struct.pack('>d', js['dataValue'])
            r2 = struct.unpack('>' + 'H'*(len(r1)//2), r1)
        elif js['dataType'] == 'string':
            r1 = js['dataValue'].encode('ascii')
            if len(r1) % 2:
                r1 += bytes([0])
            r2 = struct.unpack('>' + 'H'*(len(r1)//2), r1)
        else:
            return web.Response(status=400, text='Error: Invalid Data Type.')
        value = list(r2)
        address = js['address']
        print('[Write] Address: ' + str(address) + ', Value: ' + str(value))
        if datablock.validate(address, len(value)):
            datablock.setValues(address, value)
            r = datablock.getValues(address, len(value))
            print('[Read] Address: ' + str(address) + ', Value: ' + str(r))
            return 200, 'OK'
        else:
            return 400, 'Error: Invalid Address'
    except Exception as e:
        print(e)
        return 400, 'Error: Invalid Payload'


async def main():
    global tagHelper1
    app = web.Application()
    app.add_routes([web.get('/config', config)])
    app.add_routes([web.post('/write', write)])
    app.add_routes([web.post('/config', config)])

    # Starting the modbus slave. Different command types share the same data block in this sample.
    modbus_server = ModbusTCPSlave(ModbusSlaveContext(di=datablock, co=datablock, hr=datablock, ir=datablock, zero_mode=False))
    loop = asyncio.get_event_loop()
    loop.create_task(modbus_server.run_async_server())

    load_config()

    # Starting the REST API backend.
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=80)
    await site.start()
    await asyncio.Event().wait()


if __name__ == '__main__':
    initialize()
    asyncio.get_event_loop().run_until_complete(main())
