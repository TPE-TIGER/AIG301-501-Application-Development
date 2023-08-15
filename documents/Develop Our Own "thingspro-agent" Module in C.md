# Develop Our Own "thingspro-agent" Module in C

Document Version: V1.0

##### Change Log

| Version | Date       | Content                        |
| ------- | ---------- | ------------------------------ |
| 1.0     | 2022-10-14 | Document created               |



### Purpose

This document guide you how to develop, build and deploy a "thingspro-agent"-like Azure IoT Module with C.

------

### 1. Develop Environment

| item                   | Note / Command                                               |
| ---------------------- | ------------------------------------------------------------ |
| Linux OS               | A x86 CPU virtual machine with Ubuntu Server 18.04 OS        |
| Install Docker         | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |

------

### 2. Develop Our Azure IoT Edge Module (C)

#### 2.1 Download Sample Module

```
$ wget https://tpe2.thingspro.io/tpe2/C/SampleModule.tar.gz

$ tar -xvf SampleModule.tar
```

#### 2.2 Folder Structure

| Name                | Type | Note                                                             |
| ------------------- | ---- | ---------------------------------------------------------------- |
| Dockerfile.amd64    | File | Generates the amd64 docker image for our Azure IoT Edge module.  |
| Dockerfile.armhf    | File | Generates the armhf docker image for our Azure IoT Edge module.  |
| SampleModule.c      | File | The main entry point where we implment our logic.                |
| TpeHelper.h         | File | Header file for TpeHelper.c.                                     |
| TpeHelper.c         | File | TPE API helper.                                                  |
| build.sh            | File | Compile command.                                                 |

#### 2.3 Build Docker Image

##### 2.3.1 change current directory to "SampleModule"

```
$ cd SampleModule
```

##### 2.3.2 build docker image with image name: <font color='green'><b>sample_module_c:1.0.0-`<ARCH>`</b></font>

```
$ docker build . -f Dockerfile.<ARCH> -t <DOCKER_HUB_USERNAME>/sample_module_c:1.0.0-<ARCH>
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
root@moxa:/home/moxa/repo/SampleModule-C# docker push <DOCKER_HUB_USERNAME>/sample_module_c:0.0.1-amd64
The push refers to repository [docker.io/<DOCKER_HUB_USERNAME>/sample_module_c]
02cdacc16326: Pushed 
b274ff9aca9d: Pushed 
992f38e1a81c: Layer already exists 
0.0.1-amd64: digest: sha256:d672c29ac4c7a08bf9e3c5d9a2c5fa35793a5a461b5f596c7b046564361febeb size: 950

```

### 3. Deploy to Azure IoT Edge

#### 3.1 Install and Configuration Azure IoT Edge

Please refer to the link below to register an IoT Edge device. AIG series preloads Azure IoT Edge, so the install IoT Edge section can be ignored.

https://docs.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-2020-11&tabs=azure-portal%2Cubuntu

#### 3.2 Deploy Sample Module

- Navigate to the target IoT Edge device to deploy our custom module by clicking "Set modules".

  - Modules

    - IoT Edge Module Name: sample

    - Image URI: <DOCKER_HUB_USERNAME>/sample_module_c:1.0.0-<ARCH>

    - Container Create Options

      ```
      {
        "HostConfig": {
          "Binds": [
              "/var/thingspro/data/mx-api-token:/run/mx-api-token"
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
  sample           running          Up a minute      <DOCKER_HUB_USERNAME>/sample_module_c:1.0.0-<ARCH>
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

  - Update desired properties from Azure portal.

    ```
    "desired": {
      "key": "value"
    }
    ```

  - The module will add the same json object into the reported properties.

    ```
    "reported": {
      "key": "value"
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