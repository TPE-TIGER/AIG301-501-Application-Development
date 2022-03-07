# OPC UA Client Sample Application-python3

Document Version: V1.0

### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-03-04 | Document created |

### Purpose

This document guides you how to implement an OPC UA client application, which subscribes data from OPC UA server and publishes it to ThingsPro Edge as virtual tags.

---

### Usage

- A Moxa IIoT Gateway running with ThingsPro Edge V2.2.0+
- Download application

    - Binary : 
    - Source : 

- Install application via command console.

  ```
  moxa@Moxa:~$ sudo appman app install opc_ua_client_sample_1_armhf.mpkg
  ```

- Verify the installation. We can temporarily the state and health at this moment.

  ```
  moxa@Moxa:~$ sudo appman app ls
    +----------------------+--------------+-----------------------+--------+
    |         NAME         |   VERSION    | STATE (DESIRED STATE) | HEALTH |
    +----------------------+--------------+-----------------------+--------+
    | ...                  | ...          | ...                   | ...    |
    | opc_ua_client_sample |            1 | ready (ready)         | good   |
    +----------------------+--------------+-----------------------+--------+
  ```

- Run an OPC UA server.

- Configure the application.

    - File path: /var/thingspro/apps/opc_ua_client_sample/data/setting/config.json

        | Key | Value |
        | --- | ---|
        | OPC_server| OPC UA server endpoint URL |
        | TPE_prvd_name | provider name of tag |
        | TPE_src_name | source name of tag |
        | node_id | OPC UA node ID. <br />Please follow the format of **ns=\<namespaceIndex\>;\<identifiertype\>=\<identifier\>** |
        | TPE_tag_name | tag name |

- Restart the opc_ua_client_sample application via command console.

    ```
    moxa@Moxa:~$ sudo appman app restart opc_ua_client_sample
    ```

- Validate the result.

    Once the application starts running, it connects to the destination OPC UA server and subscribes the tags specified in the configuration file, then publishes the updated values to ThingsPro Edge. This can be validated by leveraging the tag management feature on ThinsPro Edge's web GUI.

    The tags can later be selected by cloud applications, to get the updated values published to cloud services.

### Known Issue
The latest ThingsPro Edge SDK (tpfunc) does not run on Python 3.5. There is a known bug which subscribe callback doesn't work on this version.
