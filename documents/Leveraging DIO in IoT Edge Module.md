# Leveraging DIO in IoT Edge Module

Document Version: V1.0

##### Change Log

| Version | Date       | Content                        |
| ------- | ---------- | ------------------------------ |
| 1.0     | 2022-11-24 | Document created               |



### Purpose

This document guide you how to develop, build and deploy an Azure IoT Module with Python 3, which is able to leverage the DI/DO port on a moxa unit.

------

### 1. Develop Environment

| item                   | Note / Command                                               |
| ---------------------- | ------------------------------------------------------------ |
| Linux OS               | A x86 CPU virtual machine with Ubuntu Server 18.04 OS        |
| Install Docker         | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |

------

### 2. Develop Our Azure IoT Edge Module (Python 3)

#### 2.1 Sample Module Source Code

```
$ wget https://tpe2.azureedge.net/Python3/DioSample.tar.gz

$ mkdir DioSample
$ tar -zxvf DioSample.tar.gz -C DioSample
```

#### 2.2 Folder Structure

| Name                | Type    | Note                                                             |
| ------------------- | ------- | ---------------------------------------------------------------- |
| Dockerfile.armhf    | File    | Generates the armhf docker image for our Azure IoT Edge module.  |
| web.py              | File    | The main entry point where we implment our logic.                |
| dioHelper.py        | File    | A helper class that interacts with DIO ports.                    |
| requirements.txt    | File    | A file that specifies the required python modules.               |

#### 2.3 Build Docker Image

##### 2.3.1 change current directory to "DioSample"

```
$ cd DioSample
```

##### 2.3.2 build docker image with image name: <font color='green'><b>dio_sample_module:1.0.0-armhf</b></font>

```
$ docker build . -f Dockerfile.armhf -t <DOCKER_HUB_USERNAME>/dio_sample_module:1.0.0-armhf
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
root@moxa:/home/moxa/SampleModule# docker push <DOCKER_HUB_USERNAME>/dio_sample_module:1.0.0-armhf
The push refers to repository [docker.io/<DOCKER_HUB_USERNAME>/dio_sample_module]
45f342a2921c: Pushed 
ded8d3983254: Pushed 
397bd42d47d7: Pushed 
be579af62b39: Pushed 
6eb10ccab083: Pushed 
61c7ea1dc217: Pushed
6ad53ffe0785: Pushed
a61d5286e920: Pushed
95cabbd8d010: Pushed
56be6d3609f9: Pushed
3f3c058f4c82: Pushed
d1be827c1d28: Pushed
ff4025bea81b: Pushed
1.0.0-armhf: digest: sha256:4f4f5adecdda8298d23804763bdb7ef148eeaef50ce095e4c91dcaadf036d9ec size: 3040
```

### 3. Deploy to Azure IoT Edge

#### 3.1 Install and Configuration Azure IoT Edge

Please refer to the link below to register an IoT Edge device. AIG series preloads Azure IoT Edge, so the install IoT Edge section can be ignored.

https://docs.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-2020-11&tabs=azure-portal%2Cubuntu

#### 3.2 Deploy Sample Module

- Navigate to the target IoT Edge device to deploy our custom module by clicking "Set modules".

  - Modules

    - IoT Edge Module Name: sample

    - Image URI: <DOCKER_HUB_USERNAME>/dio_sample_module:1.0.0-armhf

    - Container Create Options

    ```
    {
        "HostConfig": {
            "Binds": [
                "/sys/class/gpio:/sys/class/gpio",
                "/sys/devices/platform/soc:/sys/devices/platform/soc",
                "/etc/moxa-configs/moxa-dio-control.json:/etc/moxa-configs/moxa-dio-control.json"
            ],
            "PortBindings": {
                "80/tcp": [
                    {
                        "HostPort": "50000"
                    }
                ]
            }
        },
        "ExposedPorts": {
            "80/tcp": {}
        }
    }
    ```

#### 3.3 Testing the Module

- Verify Module Status

  ```
  root@Moxa:/home/moxa# iotedge list
  NAME             STATUS           DESCRIPTION      CONFIG
  edgeAgent        running          Up an hour       mcr.microsoft.com/azureiotedge-agent:1.1
  edgeHub          running          Up an hour       mcr.microsoft.com/azureiotedge-hub:1.1
  thingspro-agent  running          Up an hour       moxa2019/thingspro-agent:2.X.X-<ARCH>
  sample           running          Up a minute      <DOCKER_HUB_USERNAME>/dio_sample_module:1.0.0-armhf
  ```

- Check Module Log 

    - With TPE installed

        ```
        root@Moxa:/home/moxa# journalctl CONTAINER_NAME=sample -f
        ```

    - Without TPE

        ```
        root@Moxa:/home/moxa# iotedge logs sample -f
        ```

- Get Current DI/DO State

    |               | Value                                     |
    | ------------- | ----------------------------------------- |
    | API endpoint  | http://<IP>:50000/api/v1/[di, do]/<PORT>  |
    | Method        | GET                                       |
    | Response      | [DIN, DOUT] port <PORT> state: [0, 1]     |

    Example:

    ```
    root@Moxa:/home/moxa# curl -X GET http://127.0.0.1:50000/api/v1/di/0 -d '{"value": 0}'
    DIN port 0 state: 0
    root@Moxa:/home/moxa# curl -X GET http://127.0.0.1:50000/api/v1/do/0 -d '{"value": 0}'
    DOUT port 0 state: 0
    ```

- Set DO State

    |               | Value                                     |
    | ------------- | ----------------------------------------- |
    | API endpoint  | http://<IP>:50000/api/v1/do/<PORT>        |
    | Method        | POST                                      |
    | Response      | DOUT port <PORT> state: [0, 1]            |

    Example:

    ```
    root@Moxa:/home/moxa# curl -X POST http://127.0.0.1:50000/api/v1/do/0 -d '{"value": 0}'
    DOUT port 0 state: 0
    ```