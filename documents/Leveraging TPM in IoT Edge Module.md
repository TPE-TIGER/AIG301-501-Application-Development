# Leveraging TPM in IoT EdgeModule

Document Version: V1.0

##### Change Log

| Version | Date       | Content                        |
| ------- | ---------- | ------------------------------ |
| 1.0     | 2022-10-28 | Document created               |



### Purpose

This document guide you how to develop, build and deploy an Azure IoT Module with Python 3, which leverages TPM's capability to protect its sensitive information.

------

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
$ wget https://tpe2.azureedge.net/Python3/TpmSample.tar.gz

$ mkdir TpmSample
$ tar -zxvf TpmSample.tar.gz -C TpmSample
```

#### 2.2 Folder Structure

| Name                | Type    | Note                                                             |
| ------------------- | ------- | ---------------------------------------------------------------- |
| Dockerfile.armhf    | File    | Generates the armhf docker image for our Azure IoT Edge module.  |
| web.py              | File    | The main entry point where we implment our logic.                |
| tpmHelper.py        | File    | A helper class that interacts with TPM.                          |
| requirements.txt    | File    | A file that specifies the required python modules.               |
| templates           | Folder  | A folder that contains all the requried html files.              |


#### 2.3 Build Docker Image

##### 2.3.1 change current directory to "TpmSample"

```
$ cd TpmSample
```

##### 2.3.2 build docker image with image name: <font color='green'><b>tpm_sample_module:1.0.0-armhf</b></font>

```
$ docker build . -f Dockerfile.armhf -t <DOCKER_HUB_USERNAME>/tpm_sample_module:1.0.0-armhf
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
root@moxa:/home/moxa/SampleModule# docker push <DOCKER_HUB_USERNAME>/tpm_sample_module:1.0.0-armhf
The push refers to repository [docker.io/<DOCKER_HUB_USERNAME>/tpm_sample_module]
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

### 3. Deploy to Azure IoT Edge

#### 3.1 Install and Configuration Azure IoT Edge

Please refer to the link below to register an IoT Edge device. AIG series preloads Azure IoT Edge, so the install IoT Edge section can be ignored.

https://docs.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-2020-11&tabs=azure-portal%2Cubuntu

#### 3.2 Deploy Sample Module

- Navigate to the target IoT Edge device to deploy our custom module by clicking "Set modules".

  - Modules

    - IoT Edge Module Name: sample

    - Image URI: <DOCKER_HUB_USERNAME>/tpm_sample_module:1.0.0-armhf

    - Container Create Options

    ```
    {
        "ExposedPorts": {
            "443/tcp": {}
        },
        "HostConfig": {
            "Privileged": true,
            "Binds": [
                "/usr/bin:/usr/bin",
                "/usr/lib/arm-linux-gnueabihf:/usr/lib/arm-linux-gnueabihf"
            ],
            "PortBindings": {
                "443/tcp": [
                    {
                        "HostPort": "50000"
                    }
                ]
            }
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
  sample           running          Up a minute      <DOCKER_HUB_USERNAME>/tpe_sample_module:1.0.0-armhf
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

- Encrypt Sensitive Data

    The goal of this sample module is to demonstrate a way of having secrets saved locally, without having to worry about the secrets being leaked by copying the files to another unit that also has TPM integrated. This sample module allows user to create login credentials from web GUI, the credentials will be encryped by TPM and saved locally in the file `/app/data/credentials` inside the module container instance.

    - Access the login web page (http://<MY_IP>:50000)

    - Click the "Manage Accounts" button to add new users

    - Once users are added, we can view the content of `/app/data/credentials` with the following command. It is expected that the file content is not human-readable.

        ```
        root@Moxa:/home/moxa# docker exec -it sample cat /app/data/credentials
        ```

    - Validate that the credentials can be restored by the module by restarting the module and accessing http://<My_IP>:50000 after the module finishes its initialization (~1 minute).

        ```
        root@Moxa:/home/moxa# iotedge restart sample
        ```

    - Validate that the file cannot be loaded by another unit.

        - Copy `/app/data/credentials`, `/app/child.pub` `/app/child.priv` from the module.
    
            ```
            root@Moxa:/home/moxa# docker cp sample:/app/data/credentials .
            root@Moxa:/home/moxa# docker cp sample:/app/child.pub .
            root@Moxa:/home/moxa# docker cp sample:/app/child.priv .
            ```

        - Transfer the files to another unit.

            ```
            root@Moxa:/home/moxa# scp ./child.p* ./credentials moxa@<MY_IP_DEV_2>:/tmp
            ```

        - Replace the files with the copied files and restart the sample module.

            ```
            root@Moxa:/tmp# docker cp ./credentials sample:/app/data/credentials
            root@Moxa:/tmp# docker cp ./child.pub sample:/app/child.pub
            root@Moxa:/tmp# docker cp ./child.priv sample:/app/child.priv

            root@Moxa:/tmp# iotedge restart sample
            ```