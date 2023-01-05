# Azure IoT Central Demo Application - IoT Edge

Document Version: V1.0

##### Change Log

| Version | Date       | Content |
| ------- | ---------- | ------- |
| 1.0     | 2022-12-28 | Created |

### Purpose

This document provides detail information on how to connect your AIG-301/AIG-501 to Azure IoT Central through Azure IoT Edge.

### Terminology 

- AIC：Azure IoT Central
- AIE：Azure IoT Edge
- AIG：Advanced IIoT Gateway
- DTDL：Digital Twin Definition Language

### Preparation and whole picture

- This document & all necessary files on GitHub/TPE-Tiger
- AIG-301 or AIG-501 device
  - Please upgrade devices to up to date version by <a href="https://github.com/TPE-TIGER/TPE2-Technical-Document/blob/main/documents/AIG%20Software%20Upgrade.md">this document</a>. 
- Azure Cloud subscription and an Azure IoT Central account

![](https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic00.JPG)



### Step 1. Download AIG (AIE) manifest file & DTDL files

| Name                       | URL  | Notes                   |
| -------------------------- | ---- | ----------------------- |
| AIG (AIE) manifest         |      | For AIG-301 and AIG-501 |
| AIG-301 root DTDL          |      | AIG-301 only            |
| AIG-301 aic_module_20 DTDL |      | AIG-301 only            |
| AIG-501 root DTDL          |      | AIG-501 only            |
| AIG-501 aic_module_20 DTDL |      | AIG-501 only            |

#### 1.1 manifest file

This is standard Azure IoT Edge manifest, which declares 3 modules required by this demonstration.

- edgeAgent version 1.2.7. Please don't change version to others. AIG-301 and AIG-501 support version 1.2.* only.
- edgeHub version 1.2.7. Please don't change version to others. AIG-301 and AIG-501 support version 1.2.* only.
- aic_module_20 version 2.0. This is a custom module, which offers device capabilities based on DTDL specification. 

#### 1.2 DTDL files

- **root DTDL** is base element of Azure IoT Edge device. We don't need to declares any extra capability on root DTDL.

- **aic_module_20 DTDL** contains 17 commands, 2 telemetries and 7 properties for this demonstration. We will explain them at following section of this document.



### Step 2. Import mainfest file and DTDL files

#### 2.1 Create a Custom app

On Azure IoT Central, create a **Custom app**. (It is OK to create your app by Azure IoT Central build-in application type.)

Input Application name, pricing plan and all necessary data. Submit, then you shall able to have your Azure IoT Central application in a minute.

![](https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic09.JPG)

#### 2.2 Import manifest file

From Azure IoT Central menu, select **Edge manifests**, import AIG (AIE) manifest file, that you download at 1.1.

#### 2.3 Import DTDL files

From Azure IoT Central menu, select **Device templates**, create a new gateway device by given device template name, **AIG-301**, for example.

Upload **AIG-301 root DTDL**, which you download at 1.2.

You shall able to see the result like below:

![](https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic10.JPG)

Click **module_aic_20**, click **Edit DTDL**

![](https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic11.JPG)

Overwrite all the content by **AIG-301 aic_module_20 DTDL**, that download at 1.2.

Save and close Edit DTDL. 

Click Publish button to active this device template.

![](https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic13.JPG)

#### 2.4 Create Devices

It is time to create first device on Azure IoT Central.

From Azure IoT Central menu, select **Devices**, and create a new device by following data:

| Field Name           | Value                | Notes                                             |
| -------------------- | -------------------- | ------------------------------------------------- |
| Device name          | AIG-301 Demo Device  | Friendly name                                     |
| Device ID            | tbaib1114961         | mus be lower case of device ID of physical device |
| Device template      | AIG-301              | the device template you create at 2.3             |
| Simulate this device | No                   | We will use physical device                       |
| Edge manifest        | AIG-301_501 Manifest | the Edge manifest you create at 2.2               |

### Step 3. Connect 

In order to connect AIG-301 physical device with Azure IoT Central, both of them shall know some specific information from each other, for example:

- AIG-301 physical device shall know what is the address of Azure IoT Central, and what credential data shall send over.
- Azure IoT Central shall know what is device ID and corresponding credential.

####  3.1 Setup Credential![](https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic14.JPG)

Open AIG-301 Admin Web, click **Azure IoT Edge**, **Provision Settings**, select **DPS** as Source, and **TPM** as attestation method.

Open Azure IoT Central Admin Web, click **Devices**, select **AIG-301 Demo Device**, click **Connect** button, select **Individual enrollment** as Authentication type, and **TPM** as Authentication method.

By above diagram indicate, copy ID scope from Azure IoT Central to AIG-301, copy Endorsement Key from AIG-301 to Azure IoT Central, and make sure Registration ID equals to Device ID.

#### 3.2 Make Connection

On Azure IoT Central Admin Web, click **Save** button.

On AIG-301 Admin Web, click **Save** button. 

With few minutes waiting, you shall able to see Azure IoT Edge running status by deployed 3 modules which we declares on manifest of Azure IoT Central.

![](https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic15.JPG)



### Step 4. Communication and Management 

#### 4.1 AIC Module Web UI

AIC Module Web: **http://{device IP}:5449/aic**

**4.1.1 AIC Module Status Monitor**

<img src="https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic16.JPG" style="zoom:50%;" />

This page presents module overall status, and refresh every 10 seconds automatically.

| Status             | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| Connection Status  | connection status with edgeHub (local)                       |
| Telemetry Status   | telemetry sent to edgeHub (local)                            |
| Command/Properties | command from Azure IoT Central<br />desired properties from Azure IoT Central<br />reported properties to Azure IoT Central |

**4.1.2 Change Telemetry Behavior**

<img src="https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic17.JPG" style="zoom:50%;" />

This page allows you to...

| Field Name                        | Description                                                  |
| --------------------------------- | ------------------------------------------------------------ |
| Send Telemetry                    | Enable / Disable Telemetry. Enable by default.               |
| Telemetry Output Topic            | The topic name on edgeHub that module sent to                |
| Telemetry Map File                | Upload a customize tag map file to extend Telemetry schema. Refer to 4.1.4 |
| Azure IoT Central Application URL | To invoke your AIC Restful API for uploading file. Refer to 4.3.1 |
| Azure IoT Central API Token       | To invoke your AIC Restful API for uploading file. Refer to 4.3.1 |

**4.1.3 Resource**

<img src="https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic18.JPG" style="zoom:50%;" />

| Resource           | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| root DTDL          | Same with what you download at 1.2                           |
| aic_module_20 DTDL | If you upload a custom tag map file, you can download up to date aic_module_20 DTDL from here. |
| Telemetry Map File | The default tag map file or the customize version you upload |
| Read Me            | Link to this document                                        |

**4.1.4 Customize Telemetry Schema**

To send out other than default tags from AIG-301 device to Azure IoT Central, you shall tell AIC Module what it is.

1. Download default Telemetry Map File from **Resource** page

   ```
   {
       "contents": [
           {
               "@type": "Telemetry",
               "name": "cpuUsage",
               "aigTag": {
                   "prvdName": "system",
                   "srcName": "status",
                   "tagName": "cpuUsage",
                   "schema": "double"
               }
           },
           {
               "@type": "Telemetry",
               "name": "memoryUsage",
               "aigTag": {
                   "prvdName": "system",
                   "srcName": "status",
                   "tagName": "memoryUsage",
                   "schema": "double"
               }
           }
       ]
   }
   ```

2. Edit Telemetry Map File

   You can add/update/delete tag definition by below specification: 

   | Field Name      | Value                 | Description                                                  |
   | --------------- | --------------------- | ------------------------------------------------------------ |
   | @type           | **Telemetry**         | Every JSON element must come with fixed value: Telemetry     |
   | name            | {tag name}            | Telemetry name send to Azure IoT Hub, the value must unique across all JSON elements |
   | aigTag/prodName | {tag provider name}   | Note 1                                                       |
   | aigTag/srcName  | {tag source name}     | Note 1                                                       |
   | aigTag/tagName  | {tag name}            | Note 1                                                       |
   | aigTag/schema   | {tag value data type} | value cloud be: integer, double, boolean, date, dateTime, float, long, string, time |

   Note 1: You can retrieve these value at AIG-301 Admin Web / **Tag Management** page.

3. Upload Telemetry Map File

   Refer to 4.1.2, to upload updated Telemetry Map File

4. Download update to date **aic_module_20 DTDL**

   Refer to 4.1.3, download updated aic_module_20 DTDL

5. Replace **aic_module_20 DTDL** at Azure IoT Central

   Refer to 2.3.



#### 4.2 Information Domain - Build Dashboard from Telemetry



#### 4.3 Operation Domain - Manage AIG-301 on Cloud

**4.3.1 Allow devices upload files to Azure IoT Central**

**4.3.2 Setup Network Interface**

**4.3.3 Setup Serial Port**

**4.3.4 Export/Import Modbus Master Configuration**

**4.3.5 Export Device System Log**

**4.3.6 Export/Import Device Configuration**

**4.3.7 OTA Software Upgrade**

**4.3.8 Reboot Device**

**4.3.9 Enable/Disable Telemetry**

**4.3.10 Enable/Disable Device Services**







### 2. Understand AIG-301/AIG-501 Device Template

aic_module_20 contains **12 Commands**, **2 Telemetry Tags**, and **8 Properties**. 

##### 2.1 **Commands**

| No   | Command Name               | Description                                                  |
| ---- | -------------------------- | ------------------------------------------------------------ |
| 1    | interface_cellular_auto    | to setup device cellular with auto detection mode            |
| 2    | interface_cellular_manual  | to setup device cellular by input values                     |
| 3    | interface_ethernet_auto    | to setup device ethernet with DHCP mode                      |
| 4    | interface_ethernet_manual  | to setup device ethernet with static IP                      |
| 5    | interface_GPS_auto         | to setup device location by GPS's signal                     |
| 6    | interface_GPS_manual       | to setup device location by input values                     |
| 7    | interface_serials          | to setup serial port, including rs232, baudRate, dataBit, stopBit ... |
| 8    | applications_control       | to start/stop/restart/uninstall applications (such as Modbus Master, OPC UA...) |
| 9    | modbusmaster_config_import | to import modbus master configuration (csv file) from an URL |
| 10   | modbusmaster_config_export | to export modbus master configuration (csv file) to Azure IoT Central |
| 11   | telemetry_control          | to start/stop telemetry which sending from device to Azure IoT Central |
| 12   | software_upgrade           | to install/upgrade software of device                        |
| 13   | system_reboot              | to reboot device                                             |
| 14   | thingspro_api_v1           | to invoke AIG-301/AIG-50 support Restful API from Azure IoT Central |

##### 2.2 **Telemetry Tags** 

| No   | Tag Name    | Description         |
| ---- | ----------- | ------------------- |
| 1    | cpuUsage    | device CPU usage    |
| 2    | memoryUsage | device Memory usage |

You can extend Telemetry without change any code. Please refer to ....

##### 2.3 **Properties**

| No   | Property Key   | Description                                             |
| ---- | -------------- | ------------------------------------------------------- |
| 1    | http_server    | to enable/disable http server and setup port            |
| 2    | https_server   | to enable/disable https server and setup port           |
| 3    | ssh_server     | to enable/disable ssh server and setup port             |
| 4    | discovery      | to enable/disable device provision service and behavior |
| 5    | serial_console | to enable/disable local console port                    |
| 6    | time           | to setup timezone and network time server               |
| 7    | general        | to change hostname and description of device            |



- 

- The connected status shall present on Azure IoT Central as well.

  <img src="https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic08.JPG" style="zoom:67%;" />

  
  


### 4. Operation

##### 4.1 aic_module_20 admin web

|      | command        | note                               |
| ---- | -------------- | ---------------------------------- |
| 1    | reboot         | To restart device                  |
| 2    | turnOnMonitor  | To turn on device monitor feature  |
| 3    | turnOffMonitor | To turn off device monitor feature |

##### 4.2 Change device physical interface setting from Azure IoT Central

|      | name          | note                                                         |
| ---- | ------------- | ------------------------------------------------------------ |
| 1    | cpuUsage      | CPU loading data will send to Azure IoT Central after turn on Monitor |
| 2    | lan1NetworkTx | LAN 1 outbound traffic will send to Azure IoT Central after turn on Monitor |
| 3    | lan1NetworkRx | LAN 1 inbound traffic will send to Azure IoT Central after turn on Monitor |
| 4    | memoryUsed    | Memory usage data will send to Azure IoT Central after turn on Monitor |
| 5    | Temperature   | A tag from Modbus slave device will send to Azure IoT Central after turn on Monitor |
| 6    | Inverter      | A tag from Modbus slave device will send to Azure IoT Central after turn on Monitor |
| 7    | LUX           | A tag from Modbus slave device will send to Azure IoT Central after turn on Monitor |

##### 4.3 2.3 Telemetry Map File

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