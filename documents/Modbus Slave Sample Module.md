# Sample Modbus Slave Module

Document Version: V1.0

##### Change Log

| Version | Date       | Content                                      |
| ------- | ---------- | -------------------------------------------- |
| 1.0     | 2023-09-06 | Document created                             |

### Purpose

This document guide you how to deploy and use a sample Modbus slave module on TPE devices.

---

### 1. Develop Environment

| item                   | Note / Command                                               |
| ---------------------- | ------------------------------------------------------------ |
| Linux OS               | A x86 CPU virtual machine with Ubuntu Server 18.04 OS        |
| Install Docker         | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |

------

### 2. Develop Our Azure IoT Edge Module (Python 3)

#### 2.1 Download Sample Module

```
$ wget https://tpe2.thingspro.io/tpe2/Python3/ModbusSlave.tar.gz

$ mkdir ModbusSlave
$ tar -zxvf ModbusSlave.tar.gz -C ModbusSlave
```

#### 2.2 Folder Structure

| Name              | Type    | Note                                                                                |
| ----------------- | ------- | ----------------------------------------------------------------------------------- |
| Dockerfile.armhf  | File    | Generates the armhf docker image for our Azure IoT Edge module.                     |
| web.py            | File    | The main entry point where we implment our logic.                                   |
| modbusTCPSlave.py | File    | A sample Modbus Slave from pymodbus. Ref: https://github.com/pymodbus-dev/pymodbus  |
| tpeHelper.py      | File    | A helper class that interacts with ThingsPro Edge.                                  |
| requirements.txt  | File    | A file that specifies the required python modules.                                  |
| config.json       | File    | Configuration file that stores the latest tag-address mapping.                      |


#### 2.3 Build Docker Image

##### 2.3.1 change current directory

```
$ cd ModbusSlave
```

##### 2.3.2 build docker image with image name: <font color='green'><b>tpe_modbus_slave:1.0.0-armhf</b></font>

```
$ docker build . -f Dockerfile.armhf -t <DOCKER_HUB_USERNAME>/tpe_modbus_slave:1.0.0-armhf
```

| Argument              | Description                                                                                       |
| --------------------- |-------------------------------------------------------------------------------------------------- |
| DOCKER_HUB_USERNAME   | A docker hub account where we can upload our docker image.                                        |

#### 2.4 Push Docker image to public site

##### 2.4.1 Login Our Docker Hub Account

We'll first need to login our docker account. Please specify <LOGIN_SERVER> if we're using our own private docker registry, such as Azure Container Registry. 

```
root@Moxa:/home/moxa/sampleModule# docker login (<LOGIN_SERVER>)
Username: <DOCKER_HUB_USERNAME>
Password: <DOCKER_HUB_PASSWORD>
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```

##### 2.4.2 Push to Container Registry

Push the generated image to our container registry.

```
root@moxa:/home/moxa/SampleModule# docker push <DOCKER_HUB_USERNAME>/tpe_modbus_slave:1.0.0-armhf
The push refers to repository [docker.io/<DOCKER_HUB_USERNAME>/tpe_modbus_slave]
914d630f9ace: Pushed
7ff24f69e41a: Pushed
8901f0ffdb01: Pushed
fdb8ea09efbe: Pushed
464f5ff06834: Pushed
fd58077533c6: Pushed
d235bb066270: Pushed 
a61d5286e920: Pushed
95cabbd8d010: Pushed
56be6d3609f9: Pushed
3f3c058f4c82: Pushed
d1be827c1d28: Pushed
ff4025bea81b: Pushed
1.0.0-armhf: digest: sha256:59b843866b8a3186d8dc69976f90dab01aec3f083a2a8e81cc72703528b86b86 size: 3043
```

------

### 3. Deploying the Module

#### 3.1 Important Notice:

1. If you are deploying IoT Edge modules through deployments previously, please modify the device twin to opt-out the unit before adding a new module.
2. This module exposes two internal ports, 80 for http and 502 for Modbus. Please map them to external ports and avoid port conflicts.

#### 3.2 Deploy the Module from Azure Portal

- Image URL: frankshli/tpe_modbus_slave:1.0.0-armhf

  > Note: This docker image url allows us to test the module's functionality without having to go through the whole build process. However, it's recommended to build and maintain your own image versions when going into production.

- Container Create Option:

    This is the place to map the internal 80 and 502 port to external ports. We are mapping 80 and 502 port to 50000 and 50002 correspondingly in the following example, users should adjust the external port number base on the actual use case.

    ```json
    {
        "ExposedPorts": {
            "502/tcp": {},
            "80/tcp": {}
        },
        "HostConfig": {
            "PortBindings": {
                "502/tcp": [
                    {
                        "HostPort": "50002"
                    }
                ],
                "80/tcp": [
                    {
                        "HostPort": "50000"
                    }
                ]
            }
        }
    }
    ```

------

### 4. Supported Functionalities

#### 4.1 Mapping tags to Modbus addresses

This module allows users to map tags to Modbus addresses and keeps the Modbus value in sync with the latest tag values.

#### 4.2 Configure through REST API

Users can retreive or modify the tag mapping settings through REST API calls.

- Retrieving the current settings

    ```
    curl -X GET http://127.0.0.1:50000/config | jq
    ```

- Modifying the tag mapping settings

    ```
    curl -X POST http://127.0.0.1:50000/config \
    -d '[{"address":0,"prvdName":"system","srcName":"status","tagName":"memoryUsage"},{"address":4,"prvdName":"system","srcName":"status","tagName":"cpuUsage"}]' | jq
    ```

    | Key       | Value                     |
    | --------- | ------------------------- |
    | address   | Modbus start address      |
    | prvdname  | Provider name of the tag* |
    | srcName   | Source name of the tag*   |
    | tagName   | Name of the tag*          |

    > *Note: Provider name, source name and tag name can be listed with API: ***/tags/list***
    > ```
    > curl -X GET https://127.0.0.1:8443/api/v1/tags/list \
    > -H "accept: application/json" \
    > -H "mx-api-token:$(cat /var/run/mx-api-token)" -k | jq
    > ```

#### 4.3 Update Modbus registers through REST API

Users can also update Modbus values directly through REST API calls.

```
curl -X POST http://127.0.0.1:50000/write -d '{"address":20, "dataType":"string","dataValue":"123"}'
```

| Key       | Value                     |
| --------- | ------------------------- |
| address   | Modbus starting address   |
| dataType  | Data type of the value*   |
| dataValue | Assigned value            |

> *Supported data types: 
> - int16
> - int32
> - int64
> - uint16
> - uint32
> - uint64
> - float
> - double

------

### 5. View Sample Code on GitHub

<a href="../samples/IoT-Edge/Python3/ModbusSlave">Modbus Slave Sample Code</a>