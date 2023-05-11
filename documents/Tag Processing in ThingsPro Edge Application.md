# Tag Processing in ThingsPro Edge Application

Document Version: V1.0

##### Change Log

| Version | Date       | Content                        |
| ------- | ---------- | ------------------------------ |
| 1.0     | 2023-05-11 | Document created               |



### Purpose

This document guides you how to customize a TPE application, which subscribes tag data from ThingsPro Edge, calculates and then publishes the results back to ThingsPro Edge as virtual tags.

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
$ wget https://tpe2.azureedge.net/Python3/TagProcess.tar.gz

$ mkdir TagProcess
$ tar -zxvf TagProcess.tar.gz -C TagProcess
```

#### 2.2 Folder Structure

| Name                | Type    | Note                                                                                                          |
| ------------------- | ------- | ------------------------------------------------------------------------------------------------------------- |
| Dockerfile          | File    | Generates the docker image for our application.                                                               |
| docker-compose.yml  | File    | Use by ThingsPro Edge to launch this application.                                                             |
| metadata.yml        | File    | Use by ThingsPro Edge to understand this application.                                                         |
| nginx.conf          | File    | A Nginx file to declare this application exposes restful API path, and plug-into ThingsPro Edge API framework.|
| requirements.txt    | File    | A file that specifies the required python modules.                                                            |
| config.json         | File    | Describes the source tags and the target tags.                                                                |
| /app/sample.py      | File    | The main entry point where we implment our logic.                                                             |
| /app/tpeHelper.py   | File    | A helper class that interacts with ThingsPro Edge.                                                            |

> Note: For more detailed information about each files, please refer to <a href="Build%20and%20Run%20Hello%20World%20Application-python3.md">Build and Run "Hello World" Application</a>.

#### 2.3 Packing a ThingsPro Edge Application

##### 2.3.1 Launching a ThingsPro Application Builder Instane

```
$ cd TagProcess
$ docker run --rm -it -v $(pwd):/app/ -v $(which docker):/usr/bin/docker -v /var/run/docker.sock:/var/run/docker.sock moxa2019/thingspro-app-builder:1.0 bash
```

##### 2.3.2 Change directory to "app"

```
$ cd app
```

##### 2.3.3 Build docker image with image name: <font color='green'><b>tag_process_sample:1.0.0</b></font>. The image name must match the image name that's specified in docker-compose.yml.

```
$ docker build . -t tag_process_sample:1.0.0
```

##### 2.3.4 Packing Our Application

```
$ tdk pack
```

If the application packing went well, a file `tag_process_sample_1.0.0_armhf.mpkg` will be created in the same folder.

### 3. Deploying the Module

The easiest way to install a mpkg file is to tranfer the file to the target unit with `scp`, then install it with command `appman app install tag_process_sample_1.0.0_armhf.mpkg`.

### 4. Testing the Module

- Availability of the Source Tags

    Please make sure the source tags specified in config.json exists.

- Leverage Tag Management to Monitor the Result

   We can monitor the result tags by selecting them in the tag management tab on ThingsPro Edge's web page. Virtual tags can also be selected when configuring device to cloud telemetry messages.