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

##### **4.1.1 AIC Module Status Monitor**

<img src="https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic16.JPG" style="zoom:50%;" />

This page presents module overall status, and refresh every 10 seconds automatically.

| Status             | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| Connection Status  | connection status with edgeHub (local)                       |
| Telemetry Status   | telemetry sent to edgeHub (local)                            |
| Command/Properties | command from Azure IoT Central<br />desired properties from Azure IoT Central<br />reported properties to Azure IoT Central |

##### **4.1.2 Change Telemetry Behavior**

<img src="https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic17.JPG" style="zoom:50%;" />

This page allows you to...

| Field Name                        | Description                                                  |
| --------------------------------- | ------------------------------------------------------------ |
| Send Telemetry                    | Enable / Disable Telemetry. Enable by default.               |
| Telemetry Output Topic            | The topic name on edgeHub that module sent to                |
| Telemetry Map File                | Upload a customize tag map file to extend Telemetry schema. Refer to 4.1.4 |
| Azure IoT Central Application URL | To invoke your AIC Restful API for uploading file. Refer to 4.3.1 |
| Azure IoT Central API Token       | To invoke your AIC Restful API for uploading file. Refer to 4.3.1 |

##### **4.1.3 Resource**

<img src="https://thingspro.blob.core.windows.net/resource/document/aic/aig-edge-aic18.JPG" style="zoom:50%;" />

| Resource           | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| root DTDL          | Same with what you download at 1.2                           |
| aic_module_20 DTDL | If you upload a custom tag map file, you can download up to date aic_module_20 DTDL from here. |
| Telemetry Map File | The default tag map file or the customize version you upload |
| Read Me            | Link to this document                                        |

##### **4.1.4 Customize Telemetry Schema**

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

##### **4.3.1 Allow devices upload files to Azure IoT Central**

1. Attach Azure blob storage into Azure IoT Central
2. Create Azure IoT Central API Token
3. Apply Credential on AIG-301 AIC Module

##### **4.3.2 Setup Network Interface**



##### **4.3.3 Setup Serial Port**

##### **4.3.4 Export/Import Modbus Master Configuration**

##### **4.3.5 Export Device System Log**

##### **4.3.6 Export/Import Device Configuration**

##### **4.3.7 OTA Software Upgrade**

##### **4.3.8 Reboot Device**

##### **4.3.9 Enable/Disable Telemetry**

##### **4.3.10 Enable/Disable Device Services**







2. 