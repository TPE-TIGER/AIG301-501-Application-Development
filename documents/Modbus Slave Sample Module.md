# Sample Modbus Slave Module

Document Version: V1.0

##### Change Log

| Version | Date       | Content                                      |
| ------- | ---------- | -------------------------------------------- |
| 1.0     | 2023-09-06 | Document created                             |

### Purpose

This document guide you how to deploy and use a sample Modbus slave module on TPE devices.

---

### 1. Deploying the Module

#### 1.1 Important Notice:

1. If you are deploying IoT Edge modules through deployments previously, please modify the device twin to opt-out the unit before adding a new module.
2. This module exposes two internal ports, 80 for http and 502 for Modbus. Please map them to external ports and avoid port conflicts.

#### 1.2 Deploy the Module from Azure Portal

- Image URL: frankshli/tpe_modbus_slave:1.0.0-armhf

  > Note: This docker image url allows us to test the module's functionality without having to go through the whole build process. However, it's recommended to build and maintain your own image versions when going into production.

- Container Create Option:

    This is the place to map the internal 80 and 502 port to external ports. We are mapping 80 and 502 port to 50000 and 50002 correspondingly in the following example, users should adjust the external port number base on the actual use case.

    ```json
    {
        "ExposedPorts": {
            "502/tcp": {},
            "80/tcp": {}
        },
        "HostConfig": {
            "PortBindings": {
                "502/tcp": [
                    {
                        "HostPort": "50002"
                    }
                ],
                "80/tcp": [
                    {
                        "HostPort": "50000"
                    }
                ]
            }
        }
    }
    ```

---

### 2. Supported Functionalities

#### 2.1 Mapping tags to Modbus addresses

This module allows users to map tags to Modbus addresses and keeps the Modbus value in sync with the latest tag values.

#### 2.2 Configure through REST API

Users can retreive or modify the tag mapping settings through REST API calls.

- Retrieving the current settings

    ```
    curl -X GET http://127.0.0.1:50000/config | jq
    ```

- Modifying the tag mapping settings

    ```
    curl -X POST http://127.0.0.1:50000/config \
    -d '[{"address":0,"prvdName":"system","srcName":"status","tagName":"memoryUsage"},{"address":4,"prvdName":"system","srcName":"status","tagName":"cpuUsage"}]' | jq
    ```

    | Key       | Value                     |
    | --------- | ------------------------- |
    | address   | Modbus start address      |
    | prvdname  | Provider name of the tag* |
    | srcName   | Source name of the tag*   |
    | tagName   | Name of the tag*          |

    > *Note: Provider name, source name and tag name can be listed with API: ***/tags/list***
    > ```
    > curl -X GET https://127.0.0.1:8443/api/v1/tags/list \
    > -H "accept: application/json" \
    > -H "mx-api-token:$(cat /var/run/mx-api-token)" -k | jq
    > ```

#### 2.3 Update Modbus registers through REST API

Users can also update Modbus values directly through REST API calls.

```
curl -X POST http://127.0.0.1:50000/write -d '{"address":20, "dataType":"string","dataValue":"123"}'
```

| Key       | Value                     |
| --------- | ------------------------- |
| address   | Modbus starting address   |
| dataType  | Data type of the value*   |
| dataValue | Assigned value            |

> *Supported data types: 
> - int16
> - int32
> - int64
> - uint16
> - uint32
> - uint64
> - float
> - double

---

### 3. Sample Code

<a href="../samples/IoT-Edge/Python3/ModbusSlave">Modbus Slave Sample Code</a>