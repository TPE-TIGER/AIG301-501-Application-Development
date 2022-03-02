# Develop Module on .Net Core 6 (ARM32, Debian64)

Document Version: V1.1

##### Change Log

| Version | Date       | Content                        |
| ------- | ---------- | ------------------------------ |
| 1.1     | 2022-03-02 | Fixed steps<br />Add Debian 64 |



### Purpose

This document guide you how to develop, build and deploy an Azure IoT Module by .Net Core 6 on Moxa ARM32 device.

------

### 1. Develop Environment

| item                   | Note / Command                                               |
| ---------------------- | ------------------------------------------------------------ |
| Linux OS               | A x86 CPU virtual machine with Ubuntu Server 18.04 OS        |
| Install Docker         | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |
|                        |                                                              |



------

### 2. Develop Your Application (dotnet core 6)

#### 2.1 Download Sample Module

```
$ wget https://tpe2.azureedge.net/dotnet-core-6/SampleModule.tar

$ tar -xvf SampleModule.tar
```

#### 2.2 ThingsPro Edge Application Structure

| Name                | Type | Note                                                         |
| ------------------- | ---- | ------------------------------------------------------------ |
| Dockerfile          | File | Build this application by .Net core 6 SDK<br />Generate arm32v7 docker image contains .Net core 6 runtim |
| Dockerfile_x64      | File | Build this application by .Net core 6 SDK<br />Generate debian x64 docker image contains .Net core 6 runtim |
| Program.cs          | File | Copy from https://github.com/Azure/dotnet-template-azure-iot-edge-module/blob/master/content/dotnet-template-azure-iot-edge-module/CSharp/Program.cs |
| SampleModule.csproj | File | C# Project file                                              |

#### 2.3 Build Docker Image

##### 2.3.1 change current directory to "SampleModule"

```
$ cd SampleModule
```

##### 2.3.2 build docker image with app name: <font color='green'><b>sample-module:1.0</b></font>

```
$ docker build -t sample-module:1.0 .
```

#### 2.4 Push Docker image to public site

##### 2.4.1 Push to Container Registry

We use moxa2019/sample-module:1.0 as example. You shall change to your own container registry.

```
root@moxa:/home/moxa/SampleModule# docker push moxa2019/sample-module:1.0
The push refers to repository [docker.io/moxa2019/sample-module]
81a43ec1ac3f: Pushed
1c075810b5b3: Pushed
e2f16cb69977: Pushed
a1ba5803ab66: Pushed
a7ad0170d594: Pushed
e6bfcf3835b1: Pushed
1.0: digest: sha256:2367b5318320d71c3b23cef67fc6af9d42bbb795fb8a742ce63711971613c7e3 size: 1578
```



### 3. Deploy to Azure IoT Edge

##### 3.1 Install and Configuration Azure IoT Edge

You shall setup your Azure IoT Edge ready on device and Azure cloud.

https://docs.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-2020-11&tabs=azure-portal%2Cubuntu

##### 3.2 Deploy Sample Module

- On Azure IoT Hub, select the IoT Edge device, add a custom module as

  - IoT Edge Module Name: SampleModule

  - Image URI: moxa2019/sample-module:1.0

  - Container Create Options (This configuration only required for arm32 cpu )

    ```
    {
        "HostConfig": {
            "Privileged": true
        }
    }
    ```


- Verify status on device

  ```
  root@Moxa:/home/moxa# iotedge list
  NAME             STATUS           DESCRIPTION      CONFIG
  SampleModule     running          Up a minute      moxa2019/sample-module:1.0
  edgeAgent        running          Up an hour       mcr.microsoft.com/azureiotedge-agent:1.1
  edgeHub          running          Up an hour       mcr.microsoft.com/azureiotedge-hub:1.1
  ```

- Check Sample Module log 

  ```
  root@Moxa:/home/moxa# iotedge logs SampleModule
  
  -- Logs begin at Wed 2022-02-16 22:47:23 CST. --
  Feb 17 00:43:41 Moxa e9b2b018ac7b[675]: IoT Hub module client initialized. (.NET Core 6 + Moxa)
  ```

  

- Check Sample Module log when ThingsPro Edge installed

  ```
  root@Moxa:/home/moxa# journalctl CONTAINER_NAME=SampleModule -f
  
  -- Logs begin at Wed 2022-03-02 18:45:55 CST. --
  Mar 02 23:36:04 AIG501 ef1082c7e8bf[1905]: IoT Hub module client initialized. (.NET Core 6 + Moxa)
  ```

  

