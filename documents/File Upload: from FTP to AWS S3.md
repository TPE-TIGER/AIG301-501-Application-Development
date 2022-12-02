# File Upload: from FTP to AWS S3

Document Version: V1.0

##### Change Log

| Version | Date       | Content                        |
| ------- | ---------- | ------------------------------ |
| 1.0     | 2022-12-03 | Document created               |



### Purpose

This document guide you how to develop, build and install a ThingsPro Edge Application, which periodically downloads file from an FTP server and upload it to a designated AWS S3 bucket.

------

### 1. Develop Environment

| item                   | Note / Command                                               |
| ---------------------- | ------------------------------------------------------------ |
| Linux OS               | A x86 CPU virtual machine with Ubuntu Server 18.04 OS        |
| Install Docker         | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |

------

### 2. Develop Our ThingsPro Edge App (Python 3)

#### 2.1 Download Sample Code

```
$ wget https://tpe2.azureedge.net/Python3/FtpToS3.tar.gz
$ mkdir FtpToS3
$ tar -zxvf FtpToS3.tar.gz -C FtpToS3
```

#### 2.2 Folder Structure

| Name                | Type    | Note                                                             |
| ------------------- | ------- | ---------------------------------------------------------------- |
| Dockerfile.         | File    | Generates the docker image for our ThingsPro Edge application.   |
| docker-compose.yml  | File    | A file for ThingsPro Edge to launch the application.             |
| metadata.yml        | File    | A file that describes this application to ThingsPro Edge.        |
| nginx.conf          | File    | A nginx file that declares the exposed restful API paths.        |
| requirements.txt    | File    | A file that specifies the required python modules.               |
| ftp-to-s3.cron      | File    | Cron job file.                                                   |
| app                 | Folder  | Folder that contains our source code.                            |

#### 2.3 Build Docker Image

##### 2.3.1 Change Current Directory to "FtpToS3"

```
$ cd FtpToS3
```

##### 2.3.2 Build Docker Image

```
$ docker build -t ftp-to-s3:1.0.0-armhf .
```

##### 2.3.3 Pack as a ThingsPro Edge Application

```
$ docker run --rm -it -v $(pwd):/app/ -v $(which docker):/usr/bin/docker -v /var/run/docker.sock:/var/run/docker.sock moxa2019/thingspro-app-builder:1.0 /bin/bash -c 'cd app && tdk pack'
```

> Note: ftp-to-s3_1.0.0_armhf.mpkg will be generated after packing the application, this is the installtion file for our ThingsPro Edge application.

> Note: If the docker image's name or tag has been changed, then it's required to modify docker-compose.yml prior to packing the application.

### 3. Installing the ThingsPro Edge Application

- Copy the installation file to your Moxa IIoT Gateway (WinSCP)

- Install the application through command line

```
root@Moxa:/home/moxa# appman app install ftp-to-s3_1.0.0_armhf.mpkg
```

- Verify the installation

```
root@Moxa:/home/moxa# appman app ls
+--------------+--------------+-----------------------+--------+
|     NAME     |   VERSION    | STATE (DESIRED STATE) | HEALTH |
+--------------+--------------+-----------------------+--------+
|...           | ...          | ...                   | ...    |
| ftp-to-s3    | 1.0.0        | ready (ready)         | good   |
|...           | ...          | ...                   | ...    |
+--------------+--------------+-----------------------+--------+
```

### 4. Testing the ThingsPro Edge Application

#### 4.1 Get the current settings from the gateway's command line

```
root@Moxa:/home/moxa# curl https://127.0.0.1:8443/api/v1/ftp-to-s3 -H "mx-api-token:$(cat /var/run/mx-api-token)" -k
{"aws":{"key":"<MY_SECRET_ACCESS_KEY>","key_id":"<MY_ACCESS_KEY_ID>","s3_bucket":"<MY_S3_BUCKET_NAME>"},"file":{"cache":"<LOCAL_CACHED_FILENAME>","destination":"<S3_FILENAME>","source":"<FTP_FILENAME>"},"ftp":{"ip":"<FTP_SERVER_IP>","password":"<FTP_PASSWORD>","username":"<FTP_USERNAME>"}}
```

#### 4.2 Configure the application

```
curl -X POST https://127.0.0.1:8443/api/v1/ftp-to-s3 -H "mx-api-token:$(cat /var/run/mx-api-token)" -H "Content-Type: application/json" -d '{"aws":{"key":"****","key_id":"*****","s3_bucket":"*****"},"file":{"cache":"*****","destination":"*****","source":"*****"},"ftp":{"ip":"*****","password":"*****","username":"*****"}}' -k
{"aws":{"key":"****","key_id":"*****","s3_bucket":"*****"},"file":{"cache":"*****","destination":"*****","source":"*****"},"ftp":{"ip":"*****","password":"*****","username":"*****"}}
```