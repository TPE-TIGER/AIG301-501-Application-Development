# Develop Our Own "thingspro-agent" Module

Document Version: V1.1

##### Change Log

| Version | Date       | Content                        |
| ------- | ---------- | ------------------------------ |
| 1.0     | 2022-08-10 | Document created               |



### Purpose

This document guide you how to develop, build and deploy a "thingspro-agent"-like Azure IoT Module with Python 3.

------

### 1. Develop Environment

| item                   | Note / Command                                               |
| ---------------------- | ------------------------------------------------------------ |
| Linux OS               | A x86 CPU virtual machine with Ubuntu Server 18.04 OS        |
| Install Docker         | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |
|                        |                                                              |

------

### 2. Develop Our Azure IoT Edge Module (Python 3)

#### 2.1 Download Sample Module

```
$ wget https://tpe2.azureedge.net/Python3/SampleModule.tar.gz

$ tar -xvf SampleModule.tar
```

#### 2.2 Folder Structure

| Name                | Type | Note                                                             |
| ------------------- | ---- | ---------------------------------------------------------------- |
| Dockerfile.amd64    | File | Generates the amd64 docker image for our Azure IoT Edge module.  |
| Dockerfile.armhf    | File | Generates the armhf docker image for our Azure IoT Edge module.  |
| module.py           | File | The main entry point where we implment our logic.                |
| azureClient.py      | File | A helper class for Azure IoT Edge module.                        |
| tpeClient.py        | File | A helper class to interact with ThingsPro Edge.                  |
| module_config.json  | File | A configuration file for our Azure IoT Edge module.              |
| tag_config.py       | File | A configuration file where we store TPE related settings.        |

#### 2.3 Build Docker Image

##### 2.3.1 change current directory to "SampleModule"

```
$ cd SampleModule
```

##### 2.3.2 build docker image with app name: <font color='green'><b>sample_module:1.0.0-`<ARCH>`</b></font>

```
$ docker build . -f Dockerfile.<ARCH> -t <DOCKER_HUB_USERNAME>/sample_module:1.0.0-<ARCH>
```

| Argument              | Description                                                                                       |
| --------------------- |-------------------------------------------------------------------------------------------------- |
| DOCKER_HUB_USERNAME   | A docker hub account where we can upload our docker image.                                        |
| ARCH                  | The CPU architecture. Could be **amd64** or **armhf** depending on the model of our target device.|

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
root@moxa:/home/moxa/SampleModule# docker push <DOCKER_HUB_USERNAME>/sample_module:1.0.0-<ARCH>
The push refers to repository [docker.io/<DOCKER_HUB_USERNAME>/sample_module]
201544413655: Pushed 
b5d65982330f: Pushed 
9b6d44d4adfe: Pushed 
a77667094402: Pushed 
5c6db9375f22: Pushed 
95cabbd8d010: Pushed 
56be6d3609f9: Pushed 
3f3c058f4c82: Pushed 
d1be827c1d28: Pushed 
ff4025bea81b: Pushed 
1.0.0-<ARCH>: digest: sha256:143a874c24dcc7d773bea17899db7df49235b3b90fb690cdcab8b54fa814c4fe size: 2415
```

### 3. Deploy to Azure IoT Edge

#### 3.1 Install and Configuration Azure IoT Edge

Please refer to the link below to register an IoT Edge device. AIG series preloads Azure IoT Edge, so the install IoT Edge section can be ignored.

https://docs.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-2020-11&tabs=azure-portal%2Cubuntu

#### 3.2 Deploy Sample Module

- Navigate to the target IoT Edge device to deploy our custom module by clicking "Set modules".

  - Modules

    - IoT Edge Module Name: sample

    - Image URI: <DOCKER_HUB_USERNAME>/sample_module:1.0.0-<ARCH>

    - Container Create Options

      ```
      {
        "HostConfig": {
          "Binds": [
              "/var/thingspro/data/mx-api-token:/run/mx-api-token",
              "/var/thingspro/apps/tagservice/data/dx-engine:/run/taghub"
          ]
        }
      }
      ```

  - Routes

    We'll need to add two message routes. The first one routes all the messages to Azure IoT Hub, and the second one routes messages sent by thingspro-agent to topic "test" of our sample module.

      | Name    | Value                                                                                         | Priority  | Time To Live (Secs) |
      | ------- | --------------------------------------------------------------------------------------------- | --------- | ------------------- |
      | default | FROM /messages/* INTO $upstream                                                               | 0         | 7200                |
      | sample  | FROM /messages/modules/thingspro-agent/* INTO BrokeredEndpoint("/modules/sample/inputs/test") | 0         | 7200                |

#### 3.3 Testing the Module

- Verify Module Status

  ```
  root@Moxa:/home/moxa# iotedge list
  NAME             STATUS           DESCRIPTION      CONFIG
  edgeAgent        running          Up an hour       mcr.microsoft.com/azureiotedge-agent:1.1
  edgeHub          running          Up an hour       mcr.microsoft.com/azureiotedge-hub:1.1
  thingspro-agent  running          Up an hour       moxa2019/thingspro-agent:2.X.X-<ARCH>
  sample           running          Up a minute      <DOCKER_HUB_USERNAME>/sample_module:1.0.0-<ARCH>
  ```

- Check Module log 

  - With TPE installed

    ```
    root@Moxa:/home/moxa# journalctl CONTAINER_NAME=sample -f
    ```

  - Without TPE

    ```
    root@Moxa:/home/moxa# iotedge logs sample -f
    ```

  - Module Twin

    - Configure the device through desired twin.

      ```
      "desired": {
        "sshserver:" {
          "enable": true,
          "port": 22
        }
      }
      ```

    - Get the latest device status from reported twin.

      ```
      "reported": {
        "sshserver:" {
          "enable": true,
          "port": 22
        }
      }
      ```

  - Direct Method

    - Method Name: `thingspro_api_v1`
    - Payload:
      This method allows us to invoke all the TPE APIs, please refer to https://thingspro-edge.moxa.online/latest/core/index.html

      ```
      {
        "method": "put",
        "path": "/system/sshserver",
        "request_body": {
          "enable": true
        }
      }
      ```

  - Device to Cloud Message

    Once valid tags are specified in tag_config.json, the module sends out messages to edgeHub whenever new tag values are published. edgeHub routes the message to IoT Hub if the message routing is properly set.

  - Cloud to Device Message

    The module acceps messages from edgeHub. We will have to set the message routing in order to tell edgeHub to route messages to our module.
