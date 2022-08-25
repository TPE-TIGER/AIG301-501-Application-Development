# Develop Our Own ThingsPro Edge Application in C

Document Version: V1.0

##### Change Log

| Version | Date       | Content                        |
| ------- | ---------- | ------------------------------ |
| 1.0     | 2022-08-24 | Document created               |

### Purpose

This document guide you how to develop, build and deploy a customized ThingsPro Edge application.

------

### 1. Develop Environment

| item                   | Note / Command                                               |
| ---------------------- | ------------------------------------------------------------ |
| Linux OS               | A x86 CPU virtual machine with Ubuntu Server 18.04 OS        |
| Install Docker         | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |

------

### 2. Develop Our Own ThingsPro Edge Application

#### 2.1 Download Sample Application

```
$ wget https://tpe2.azureedge.net/C/SampleApplication.tar.gz

$ tar -xvf SampleApplication.tar.gz
```

#### 2.2 Folder Structure

| Name                | Type | Note                                                                                         |
| ------------------- | ---- | -------------------------------------------------------------------------------------------- |
| Dockerfile          | File | Generates the amd64 docker image for our Azure IoT Edge module                               |
| app/app.c           | File | The main entry point where we implment our logic                                             |
| docker-compose.yml  | File | This file should contain the name of the application's docker image                          |
| metadata.yml        | File | The application's general information should be specified in this file                       |
| nginx.conf          | File | The configuration for reverse proxy, do not modify it unless we know exactly what we're doing|
| run.sh              | File | The entry point for our ThingsPro Edge application                                           |

#### 2.3 Build Our Docker Image

##### 2.3.1 change current directory to "SampleApplication"

```
$ cd SampleApplication
```

##### 2.3.2 run the ThingsPro Edge application packer

```
$ docker run --rm -it -v $(pwd):/app/ -v $(which docker):/usr/bin/docker -v /var/run/docker.sock:/var/run/docker.sock moxa2019/thingspro-app-builder:1.0 bash
```

##### 2.3.3 build the docker image

```
$ cd /app
$ docker build . -t hello:1.0.0
```

> **Important**: The image name and version we're using here must be identical to the one specified in docker-compose.yml

```
$ docker images
REPOSITORY                            TAG                   IMAGE ID       CREATED         SIZE
hello                                 1.0.0                 f15f16d5e2ee   2 minutes ago   89.6MB
moxa2019/thingspro-app-builder        1.0                   af2529d9b9ae   2 years ago     777MB
```


#### 2.4 Pack Our ThingsPro Edge Application

```
$ tdk pack
INFO[0000] [Save files]
INFO[0000] Copy docker-compose.yml
INFO[0000] Copy metadata.yml
INFO[0000] Copy nginx.conf
INFO[0000] [Save images]
INFO[0000] hello:1.0.0
INFO[0007] [pack]
INFO[0007] Success!
INFO[0007] hello_1.0.0_armhf.mpkg 32.88 MB
```

> Note: the application name and version showing in ThingsPro Edge is defined in metadata.yml

### 3. Deploy the ThingsPro Edge Application


#### 3.1 Transfer mpkg File to the Target Unit

The mpkg file can be transferred to the target unit via scp. SSH server must be enabled on the target unit in advance.

```
$ scp hello_1.0.0_armhf.mpkg <USERNAME>@<TARGET_IP>:<REMOTE_DIR>
```

#### 3.2 Install Our ThingsPro Edge Application

```
$ appman app install hello_1.0.0_armhf.mpkg
```

#### 3.3 Validate the Result of Our Installation Task

Application installation will take some time. Please wait until the application's state turns to "ready".

```
$ watch appman app ls
+--------------+--------------+-----------------------+--------+
|     NAME     |   VERSION    | STATE (DESIRED STATE) | HEALTH |
+--------------+--------------+-----------------------+--------+
| ...          | ...          | ...                   | ...    |
| hello        | 1.0.0        | ready (ready)         | good   |
| ...          | ...          | ...                   | ...    |
+--------------+--------------+-----------------------+--------+
```

### 4. Capabilities of the Sample Application

#### 4.1 API Backend

This sample application exposes an endpoint /hello, which simply replies "Hello!" to the caller. This can be verified by accessing https://<GATEWAY_IP>:8443/api/v1/hello with web browser.

#### 4.2 Subscribing to Tags

This sample application subscribes to all the tags available in ThingsPro Edge and prints out log whenever new value arrives.

#### 4.3 Publishing New Tag Values

This sample application registers a new virtual tag (provider: application; source: hello; name: output1) and publishes a new tag value every 10 seconds. The tag value keeps incrementing and zeros out every day. 

Because the sample application is subscibing to all tags, the updated tag value will also be received by the sample application itself and we should be able to see it from the container log. Another way to monitor the latest virtual tag value is through "Tag Management" on the web GUI.

#### 4.4 Container Log

The container log is the easiest place to track the application's status.

```
$ journalctl APPNAME=hello -f
```

