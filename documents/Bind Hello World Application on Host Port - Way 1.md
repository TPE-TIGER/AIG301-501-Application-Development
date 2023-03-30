# Bind "Hello World" Application Bind on Host Port - Way 1

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

### 1. Find IP Address of Hello World Container

- Find docker container name of "Hello World" application 

```
root@Moxa:/home/moxa# docker ps
CONTAINER ID        IMAGE       COMMAND     CREATED    STATUS               NAMES
3f561849b4dd        hello..     "pyth..     12 m...    Up 1es               helloworld_app_1

```

- Find container IP address

```
root@Moxa:/home/moxa# docker inspect helloworld_app_1 | grep IPv4Address
                        "IPv4Address": "172.31.9.14"
```



### 2. Add Port Forwarding to Hello World Application

- Login to ThingsPro Edge Admin Web by https://{device ip address}:8443/

- From main menu, select **Security** / **Firewall**, on **Allowed List**, add one RULE

  | Field Name       | Value       | Remark                                            |
  | ---------------- | ----------- | ------------------------------------------------- |
  | Action           | Forward     |                                                   |
  | Protocol         | TCP         |                                                   |
  | Gateway Port     | 443         | The port on Host                                  |
  | Destination IP   | 172.31.9.14 | The IP we found it at step 1                      |
  | Destination Port | 80          | The port that "Hello World" application listen on |

- Click **Save** button



### 3. Verify 

- Open browser or Postman with http://{device ip address}:443/api/v1/hello-world



### 4. Notes

- The IP address of "Hello World" containers may change after device reboot each time.

