# Build and Run "Hello World" Application

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-10 | Document created |



### Purpose

This document guide you how to develop, build and deploy a simple ThingsPro Edge Application, Hello World.

------

### 1. Develop Environment

| item                          | Note / Command                                               |
| ----------------------------- | ------------------------------------------------------------ |
| Linux OS                      | A x86 CPU virtual machine with Ubuntu Server 18.04 OS        |
| Install Docker                | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator        | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |
| Install ThingsPro Develop Kit | A tool to pack docker image to be ThingsPro Edge Application. <br />>docker pull moxa2019/thingspro-app-builder:1.0 |



------

### 2. Develop Your Application

#### 2.1 Download Hello World Application

```
$ wget https://tpe2.azureedge.net/HelloWorldApp10.tar

$ tar -xvf HelloWorldApp10.tar
```

#### 2.2 ThingsPro Edge Application Structure

| Name               | Type   | Note                                                         |
| ------------------ | ------ | ------------------------------------------------------------ |
| Dockerfile         | File   | Build this application<br />Convert this application to ARM32 docker image by ARM32 emulator. |
| app                | Folder | Source code of this application.                             |
| docker-compose.yml | File   | Use by ThingsPro Edge to launch this application.            |
| metadata.yml       | File   | Use by ThingsPro Edge to understand this application.        |
| nginx.conf         | File   | A Nginx file to declare this application exposes restful API path, and plug-into ThingsPro Edge API framework. |
| requirements.tx    | File   | The required Python package list of this application.        |

#### 2.3 Build Docker Image

##### 2.3.1 change current directory to "HelloWorldApp10"

```
$ cd HelloWorldApp10
```

##### 2.3.2 launch ThingsPro App Builder docker container

Using below command to launch "ThingsPro Develop Kit", and entry "ThingsPro App Builder" shell

```
$ docker run --rm -it -v $(pwd):/app/ -v $(which docker):/usr/bin/docker -v /var/run/docker.sock:/var/run/docker.sock moxa2019/thingspro-app-builder:1.0 bash
```

##### 2.3.3 change directory to "app" folder

The "ThingsPro App Builder" will mount host's current folder at /app. 

```
$ cd /app
```

##### 2.3.4 build docker image with app name: <font color='green'><b>hello-world:1.0</b></font>

At /app folder, build your docker image with application name and tag.

```
$ docker build -t hello-world:1.0 .
```

Ignore all <font color='red'>mount: permission denied</font> message and all warning messages.

#### 2.4 Pack Docker Image as ThingsPro Edge Application

##### 2.4.1 Edit docker-compose.yml 

Make sure app image matched with <font color='green'><b>hello-world:1.0</b></font> 

```
version: '2'
services:
  app:
    image: hello-world:1.0
```

| Item  | Note              |
| ----- | ----------------- |
| image | Docker image path |

##### 2.4.2 Edit metadata.yaml

Make sure app name matched with <font color='green'><b>hello-world</b></font>

Make sure version matched with <font color='green'><b>1.0</b></font>

```
kind: app
version: v1
spec:
  name: hello-world
  displayname: Hello World App
  version: 1.0
  arch: armhf
```

##### 2.4.3 Edit nginx.conf

```
location ^~ /api/v1/hello-world {
   auth_request /api/v1/auth;
   auth_request_set $auth_status $upstream_status;
   proxy_set_header X-Real-IP $remote_addr;
   proxy_set_header X-Forwarded-For $remote_addr;
   proxy_set_header Host $host;
   proxy_pass http://helloworld_app_1;
}
```

| No   | Item                                | Note                                                         |
| ---- | ----------------------------------- | ------------------------------------------------------------ |
| 1    | ^~ /api/v1/hello-world              | Match application Restful API end point start with ..        |
| 2    | auth_request /api/v1/auth;          | If the application would like to co-op ThingsPro Edge API authentication<br />: keep this line<br />: else remove this line. |
| 3    | proxy_pass http://helloworld_app_1; | ThingsPro Edge redirects matched end point to your docker container.<br />Please watch out the naming convention at below Note. |

Note: ThingsPro Edge launch docker image as container, and label container by a name, the naming rules are:

1. fetch 'name' field from metadata.yaml. (**hello-world**)
2. remove all the character other than [a-z] and [0-9]. (**helloworld**)
3. append '_app_1'. (**helloworld_app_1**)

##### 2.4.4 Pack as ThingsPro Edge Application

```
$ tdk pack
```

##### 2.4.5 Build Complete

**helloworld_1_armhf.mpkg** success generated.

```
drwxrwxrwx 2 root root     4096 Feb 12 05:39 app
-rwxrwxrwx 1 root root       56 Feb 12 05:42 docker-compose.yml
-rwxrwxrwx 1 root root      852 Nov  9  2019 Dockerfile
-rw-r--r-- 1 root root 27095040 Feb 12 06:02 hello-world_1_armhf.mpkg
-rwxrwxrwx 1 root root      107 Feb 12 05:42 metadata.yml
-rwxrwxrwx 1 root root      285 Feb 12 05:43 nginx.conf
-rwxrwxrwx 1 root root       12 Nov  9  2019 requirements.txt

```



### 3. Deploy Application on Moxa IIoT Gateway

##### 3.1 Copy **helloworld_1_armhf.mpkg** to Moxa IIoT Gateway

##### 3.2 Install mpkg by ThingsPro Edge App Manager

Install it via App Manager

```
$ appman app install helloworld_1_armhf.mpkg

{
  "data": {
    "arch": "armhf",
    "attributes": null,
    "availableVersions": [],
    "category": "",
    "cpu_percent": 0,
    "description": "",
    "desiredState": "ready",
    "displayName": "Hello World App",
    "hardwares": [],
    "health": "wait",
    "icon": "",
    "id": "hello-world",
    "imageSize": 90668032,
    "mem_limit": 0,
    "name": "hello-world",
    "ports": {
      "filter": null,
      "forward": null
    },
    "state": "init",
    "version": "1"
  }
}
```

By follow command to verify it's DESIRED STATUS: <font color='green'><b>ready (ready)</b></font>, and HEALTH: <font color='green'><b>good</b></font>.

```
$ appman app ls

+--------------+--------------+-----------------------+--------+
|     NAME     |   VERSION    | STATE (DESIRED STATE) | HEALTH |
+--------------+--------------+-----------------------+--------+
| cloud        | 2.2.1-1499   | ready (ready)         | good   |
| device       | 2.2.1-3736   | ready (ready)         | good   |
| dlmclient    | 2.2.1-1485   | ready (ready)         | good   |
| edge-web     | 1.23.37-5380 | ready (ready)         | good   |
| function     | 1.0.0-166    | ready (ready)         | good   |
| hello-world  |            1 | ready (ready)         | good   |
| modbusmaster | 1.4.0-659    | ready (ready)         | good   |
| opcuaserver  | 2.1.0-644    | ready (ready)         | good   |
| tagservice   | 2.2.1-601    | ready (ready)         | good   |
+--------------+--------------+-----------------------+--------+
```

##### 3.3 Test Your Application 

You can use Linux command, curl, or PostMan to test your Restful API.

```
$ curl -X GET https://127.0.0.1:8443/api/v1/hello-world -k

{"error":{"code":401,"message":"authentication required"}}
```

With authentication integrated with ThingsPro Edge, you will get <font color='red'><b>401 Authorization Required</b></font> return.



By passing API token, you shall able to get expected response from Restful API.

```
$ curl -X GET https://127.0.0.1:8443/api/v1/hello-world -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -k

Hello World.
```

##### 3.4 Done and Next Action

- <a href="Invoke%20ThingsPro%20Edge%20API%20on%20Hello%20World%20Application.md">Invoke ThingsPro Edge API on "Hello World" Application</a>

