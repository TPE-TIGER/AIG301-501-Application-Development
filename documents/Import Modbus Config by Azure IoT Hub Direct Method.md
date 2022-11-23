# Import Modbus Config by Azure IoT Hub Direct Method

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-11-23 | Document created |

### Purpose

This document demonstrates how to use **tpFunc/Function** to create and expose a HTTP Restful endpoint to import Modbus Master configuration file. 

By this extension, you can invoke JSON based Restful API via Azure IoT Hub/Direct Method or AWS IoT Core/Job or MQTT Topic to import Modbus Master configuration file.

Note: **tpFunc** required ThingsPro Edge V2.2.1+

------

### Install and Setup

1. Login to your ThingsPro Edge SSH console with default path (/home/moxa).

2. Switch role to su

   ```
   sudo su
   ```

3. Create a folder, and download source codes

   ```
   mkdir modbus_import_csv
   cd modbus_import_csv
   wget https://raw.githubusercontent.com/TPE-TIGER/TPE2-Application-Development/main/samples/tpFunc/importModbusConfig/index.py
   wget https://raw.githubusercontent.com/TPE-TIGER/TPE2-Application-Development/main/samples/tpFunc/importModbusConfig/package.json
   cd ..
   
   ```

   These commands shall create **modbus_import_csv** folder, and contains package.json and index.py files.

   ```
   root@it-gw:/home/moxa/modbus_import_csv# ls -l
   total 8
   -rw-r--r-- 1 root root 2659 Nov 23 10:26 index.py
   -rw-r--r-- 1 root root  376 Nov 23 10:26 package.json
   ```

4. Add to tpFunc and Run

   ```
   cd /home/moxa
   sudo su
   tpfunc add modbus_import_csv
   ```

   Verify there is no error on creation

   ```
   root@it-gw:/home/moxa# tpfunc ls
   +-------------------+--------+------------+---------------------------+---------+-------+
   |       NAME        | ENABLE |    MODE    |        LASTUPTIME         |  STATE  | ERROR |
   +-------------------+--------+------------+---------------------------+---------+-------+
   | modbus_import_csv | true   | timeDriven | 2022-11-23T10:29:00+08:00 | running |       |
   +-------------------+--------+------------+---------------------------+---------+-------+
   ```

   

### How to use

1. ##### Invoke by general Restful API tools (such as postman)

   Restful API End Point：https://{your device IP}:8443/api/v1/tpfunc/modbus/import

   Method：PUT

   Request Payload：

   ```
   {
       "file": "https://xxxxxxxxxxxxxxxx/modbusmaster_221123090912.csv"
   }
   ```

2. ##### Invoke by Azure IoT Hub Direct Method

   Method Name：thingspro-api-v1

   Payload：

   ```
   {
       "path":"/tpfunc/modbus/import",
       "method":"PUT",
       "headers":[],
       "requestBody": {"file": "https://xxxxxxxxxxxxxxxx/modbusmaster_221123090912.csv"}
   }
   ```

3. ##### Responses

   | Output Message                                               | Desc                                    |
   | ------------------------------------------------------------ | --------------------------------------- |
   | {"status": "fail", "step": "1/3. download csv file from input URL: ", "content": "{}"} | Fail on download CSV file, and reasons  |
   | {"status": "fail", "step": "2/3. import csv content into Modbus Master", "content": "{}"} | Fail on import CSV content, and reasons |
   | {"status": "fail", "step": "3/3. apply Modbus Master configuration", "content": "{}"} | Fail on apply configuration and reasons |
   | {"status": "sucess", "step": "3/3. apply Modbus Master configuration", "content": "{}"} | Success                                 |

   

