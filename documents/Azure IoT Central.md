# Azure IoT Central Demo Application

Document Version: V2.0

##### Change Log

| Version | Date       | Content                                                      |
| ------- | ---------- | ------------------------------------------------------------ |
| 2.0     | 2022-12-06 | Allows user to import self-define telemetry source configuration |



### Purpose

This application demonstrates below features and possibility for your owned ThingsPro Edge Application:

- Web Admin GUI
- Web Restful API 
- Invoke ThingsPro Edge Restful API
- Connect to Azure IoT Central as Azure IoT Device for
  - Publish Telemetry to Cloud
  - Device Management from Cloud



### 1. How to Run ...

- A Moxa IIoT Gateway, AIG-301 or AIG-501

- Download application

  - AIG-301: https://tpe2.azureedge.net/aic_2.0-210_armhf.mpkg
  - AIG-501: https://tpe2.azureedge.net/aic_2.0-210_amd64.mpkg
  - Source : https://tpe2.azureedge.net/Python3/AzureIoTCentral-V2.0.tar

- Install application on AIG-301 or AIG-501 Linux console by below command：

  ```
  moxa@Moxa:~$ sudo appman app install aic_2.0-210_armhf.mpkg
  ```

- Verify installation completed and running well.

  ```
  moxa@Moxa:~$ sudo appman app ls
  +--------------+-------------+-----------------------+--------+
  |     NAME     |   VERSION   | STATE (DESIRED STATE) | HEALTH |
  +--------------+-------------+-----------------------+--------+
  | aic          | 2.0-210     | ready (ready)         | good   |
  | edge-web     | 1.9.17-5046 | ready (ready)         | good   |
  | tagservice   | 2.2.0-575   | ready (ready)         | good   |
  +--------------+-------------+-----------------------+--------+
  ```

- On the Azure IoT Central, you have to...

  - Create an Azure IoT Central account

  - Create an **IoT Device** Template, and import DTDL file, which required by this demo application.

    - AIG-301: <a href="https://thingspro.blob.core.windows.net/resource/document/aic/AIG-301-3.json">AIG-301 DTDL file</a>
    - AIG-501: <a href="https://thingspro.blob.core.windows.net/resource/document/aic/AIG-501-3.json">AIG-501 DTDL file</a>

  - <img src="https://thingspro.blob.core.windows.net/resource/document/aic/aic03.jpg" style="zoom:67%;" />

  - Create an IoT Device, assigned by AIG-301 DTDL,  retrieve connection meta data, and fill them into demo application configuration form which show on above.

    ![](https://thingspro.blob.core.windows.net/resource/document/aic/aic_2.0_02.JPG)

    

- Open Browser connect to your AIG-301 Admin Web + demo application configuration page

  ```
  https://{IIoT Gateway IP}:8443/api/v1/aic
  ```
  The "Home" page presentㄋ device connection status, telemetry sending tag, and command/properties processing result.
  <img src="https://thingspro.blob.core.windows.net/resource/document/aic/aic_home.jpg" style="zoom:67%;" />

  Click "Connection Setting" page, input device connection credential which you retrieved from Azure IoT Central.
  <img src="https://thingspro.blob.core.windows.net/resource/document/aic/aic_config.jpg" style="zoom:67%;" />
  - You have to import Telemetry Map File:
    - AIG-301: <a href="https://thingspro.blob.core.windows.net/resource/document/aic/TelemetryMap-AIG-301-3.json"> Map File </a>
    - AIG-501: <a href="https://thingspro.blob.core.windows.net/resource/document/aic/TelemetryMap-AIG-501-3.json"> Map File </a>
 

### 2. Functionality

This demo application contains 3 commands, 3 telemetries, and 5 properties, you also can find them on <a href="../samples/TPE-App/Python3/AzureIoTCentral/src/data/deviceTemplateV0.5.json">DTDL file</a>.

##### 2.1 Command

|      | command        | note                               |
| ---- | -------------- | ---------------------------------- |
| 1    | reboot         | To restart device                  |
| 2    | turnOnMonitor  | To turn on device monitor feature  |
| 3    | turnOffMonitor | To turn off device monitor feature |

##### 2.2 Telemetry

|      | name          | note                                                         |
| ---- | ------------- | ------------------------------------------------------------ |
| 1    | cpuUsage      | CPU loading data will send to Azure IoT Central after turn on Monitor |
| 2    | lan1NetworkTx | LAN 1 outbound traffic will send to Azure IoT Central after turn on Monitor |
| 3    | lan1NetworkRx | LAN 1 inbound traffic will send to Azure IoT Central after turn on Monitor |
| 4    | memoryUsed    | Memory usage data will send to Azure IoT Central after turn on Monitor |
| 5    | Temperature   | A tag from Modbus slave device will send to Azure IoT Central after turn on Monitor |
| 6    | Inverter      | A tag from Modbus slave device will send to Azure IoT Central after turn on Monitor |
| 7    | LUX           | A tag from Modbus slave device will send to Azure IoT Central after turn on Monitor |

##### 2.3 Telemetry Map File

You are welcome to add/remove/update telemetry schema by yourself without change any code. The purpose of Telemetry Map File is for you to define how these data come from. 

**Example 1** : cpuUsage tag

To publish cpuUsage tag to Azure IoT Central, you need to know cpuUsage is a AIG-301 system level tag, and the tag schema are:

| Key           | Value    |
| ------------- | -------- |
| Provider Name | system   |
| Source Name   | status   |
| Tag Name      | cpuUsage |

With that, you need to define these key-value for cpuUsage tag at Telemetry Map File.

**Example 2** : Inverter tag

Inverter tag is not out of box AIG-301 tag, which could be generated from external device, such as Modbus slave. You can enable AIG-301 Modbus Master application to pull these external tags from slave devices. The tag schema will depend on what your configuration on Modbus Master.

| Key           | Value                                                        |
| ------------- | ------------------------------------------------------------ |
| Provider Name | the value cloud be **modbus_tcp_master** or **modbus_serial_master** |
| Source Name   | the value is {**Device Name**} which you assigned on Modbus Master application |
| Tag Name      | the value is {**tag name**} which you input on Modbus Master application |

**Note**: the value of key "**@id**" shall same with value in DTDL file.

```
{    
    "@id": "dtmi:com:moxa:AIG501;3",
    "contents": [ 
        {
            "@type":"Telemetry",
            "name": "cpuUsage",
            "aigTag" : {
                "prvdName": "system",
                "srcName": "status",
                "tagName": "cpuUsage"
            }
        },
        ..............
        ..............
        {
            "@type": "Telemetry",
            "name": "Inverter",
            "aigTag" : {
                "prvdName": "modbus_tcp_master",
                "srcName": "MGate",
                "tagName": "Inverter"
            }
        }
    ]
}
```



##### 2.4 Property

|      | name                 | Note                                                         |
| ---- | -------------------- | ------------------------------------------------------------ |
| 1    | general_serialNumber | Read only, to display device serial number                   |
| 2    | general_deviceModel  | Read only, to display device model name                      |
| 3    | general_hostName     | Read/Write, to display and set device host name              |
| 4    | service_ssh          | Read/Write, to display and enable/disable ssh service of device |
| 5    | ethernet_lan2_ip     | Read/Write, to display and set LAN2 IP address               |

### 3. Azure IoT Central Device Authentication

This demo application supports below authentication type to Azure IoT Central

|      | Authentication type           | Note                                                 |
| ---- | ----------------------------- | ---------------------------------------------------- |
| 1    | Shared access signature (SAS) | Symmetric Key：From Azure IoT Central                |
| 2    | Certificates (X.509)          | X.509 Certificate：Generated by Root/Intermediate CA |



### 4. Azure IoT Central Known Issue

1. When update properties on IoT Central, IoT Central show all devices' status are completed, but it means the desired properties sent to Azure IoT Hub, rather than devices receive desired properties.

   <img src="https://thingspro.blob.core.windows.net/resource/document/aic/aic02.jpg" style="zoom: 50%;" />

   

2. Set ethernet_lan2_ip property will always fail on this demo application by design (due to incomplete payload), but this exception message doesn't display on Azure IoT Central, even demo app follows Azure Plug & Play (DTDL) conversation (refer to https://docs.microsoft.com/en-us/azure/iot-develop/concepts-convention)
