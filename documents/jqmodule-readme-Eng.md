# jq_module Readme

Document Version: V1.1

##### Change Log

| Version | Date       | Content                                                 |
| ------- | ---------- | ------------------------------------------------------- |
| 1.1     | 2022-09-28 | 1. Add Direct Method. <br />2. Upgrade jq_module to 1.1 |

This document describes how to use jq_module to transfer input message to output.

### Overview

jq_module is an Azure IoT Edge module, leveraging jq functionality to transfer input JSON message to output topic.

- By Module Twin & Direct Method to retrieve current jq_module configuration

- By Module Twin & Direct Method to update jq_module configuration

- Configuration contains below content,

  ```
  {
      "setting": {
          "input_topic": "jq_input_message",                             # Specify input topic from EdgeHub
          "jq": "{'MAC':'00:9..........601),'DataID': 301002} ]}",	   # jq content
          "output_topic": "jq_output_message"                            # Specify output topic to EdgeHub
      }
  }
  ```

About Azure IoT Edge message routing, please refer to:

- https://docs.microsoft.com/en-us/azure/iot-edge/iot-edge-runtime?view=iotedge-1.4
- https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-1.4

------

### How to Use

#### 1. Installation

##### 1.1 By Azure Marketplace

You can install jq_module by Azure Marketplace.

##### 1.2 By Manual on Azure IoT Hub

Same with other Azure IoT Edge module installation steps, you can manual install jq_module from Azure IoT Hub.

- name: jq_module
- image URI: moxa2019/jqmodule:1.1

#### 2. Configuration

##### 2.1 By Module Twin

You are able to retrieve jq_module configuration from module reported properties and update configuration by module desired properties.

![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-twin.jpg)

- In general, you don't need to modify input_topic nor output_topic

- the value of jq maybe not a well JSON format content, in order to pass it to module, the value must be arrange as a **STRING**

  

##### 4.2 By Direct Method

Apart from Module Twin, the configuration also could be retrieved and update via Direct Method

| Method Name | Payload                                                      | Description                    |
| ----------- | ------------------------------------------------------------ | ------------------------------ |
| get_config  | {}                                                           | Retrieve current configuration |
| set_config  | {<br/>    "setting": {<br/>        "input_topic": "jq_input_message",                             <br/>        "jq": "{'MAC':'00:9..........601),'DataID': 301002} ]}",	   <br/>        "output_topic": "jq_output_message"                            <br/>    }<br/>} | Update configuration           |

- Updated configuration will be display on module reported properties as well

  

#### 5. Message Routing

You shall setup EdgeHub routing to pass messages into jq_module.

![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-routing.jpg)

**Route 1**	

| Purpose  | Allow other modules' message feed into jq_module             |                                                              |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Name     | to_jqmodule                                                  | just a name                                                  |
| Value    | FROM /messages/modules/* INTO BrokeredEndpoint("/modules/jq_module/inputs/jq_input_message") | - You can fine tune /modules/* to a specific module name<br />- **jq_module** must be same with module name<br />- **jq_input_message** must be same with "input_topic" key in configuration of jq_module |
| Priority | 1                                                            | default                                                      |
| TTL      | 7200                                                         | default                                                      |

**Route 2**

| Purpose  | Allow jq_module output send to Azure IoT Hub      |                                               |
| -------- | ------------------------------------------------- | --------------------------------------------- |
| Name     | to_Azure_IoT_Hub                                  | just a name                                   |
| Value    | FROM /messages/modules/jq_module/* INTO $upstream | - **jq_module** must be same with module name |
| Priority | 2                                                 | default                                       |
| TTL      | 7200                                              | default                                       |

#### 6. Verify Result by Azure IoT Explorer

![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-result.jpg)



#### 7. Trouble Shooting

- By jq_module log, you can trace coming input message, jq convert, and output message. 

  ![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-log.jpg)

​					







