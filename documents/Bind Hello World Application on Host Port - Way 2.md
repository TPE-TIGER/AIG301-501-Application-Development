# Bind "Hello World" Application Bind on Host Port - Way 2

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2023-03-29 | Document created |

### Purpose

This document guide you how to bind self-developed ThingsPro Edge Application on Host Port 443.

------

### Pre-requirement

Please follow this document <a href="https://github.com/TPE-TIGER/AIG301-501-Application-Development/blob/main/documents/Build%20and%20Run%20Hello%20World%20Application-python3.md">(Build and Run "Hello World" Application)</a> to complete "Hello World" application. Make sure it works on the device.

------

### 1. Adjust docker-compose.yml

```
version: '2'
services:
  app:
    image: helloworld:1.0.1

```

- change image uri to be 'helloworld:1.0.1'
- Refer to Notes 

### 2. Adjust metadata.yml

```
kind: app
version: v1
spec:
  name: helloworld
  displayname: Hello World App
  version: 1.0.1
  arch: armhf
  ports:
    forward:
      - 443:80/tcp
```

- change name to be 'helloworld'
- change version to be '1.0.1'
- add **ports** section to define a port forwarding from host:443 to "Hello World":80

### 3. Build "Hello World" Application

- Download <a href="https://github.com/TPE-TIGER/AIG301-501-Application-Development/blob/main/samples/TPE-App/Python3/HelloWorldApp101/HelloWorldApp101.zip">helloworld:1.0.1 sample code</a>
- Follow this document <a href="https://github.com/TPE-TIGER/AIG301-501-Application-Development/blob/main/documents/Build%20and%20Run%20Hello%20World%20Application-python3.md">(Build and Run "Hello World" Application)</a> to build "Hello World" application version 1.0.1

```
docker build -t helloworld:1.0.1 .
```

- Pack it as .mpkg and install it on your device

### 4. Verify

- Login to ThingsPro Edge Admin Web by https://{device ip address}:8443/

- From main menu, select **Security** / **Firewall**, on **System Default** page, there shall be one **Forward** entry for routing Gateway port 443 to 'helloworld' application.

- Open browser or Postman with http://{device ip address}:443/api/v1/hello-world

  

### 5. Notes

- There is one known issue on deal application **name** which break forward function. To avoid this bug, you shall remove dash( - ) and under line ( _ ) from your application name.

  | Example Name |      | Remark                     |
  | ------------ | ---- | -------------------------- |
  | hello-world  | X    | Dash doesn't support       |
  | hello_world  | X    | Under line doesn't support |
  | helloworld   | Good |                            |

  

