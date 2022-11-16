# jqmodule

Document Version: V1.2

本文件說明如何使用 jqmodule 於 AIG-301 設備，以及如何修改、打包 jqmodule。

### 說明

jqmodule 是一個運行於 Azure IoT Edge 上的 module，主要目的在於透過 jq 能力，轉換 input message 成用戶定義的 output message。

用戶可以：

- 透過 Module Twin & Direct Method 取得目前的 Configuration 內容

- 透過 Module Twin & Direct Method 設定/修改 Configuration 內容

- Configuration 是一個 JSON 內容，如下

  ```
  {
      "setting": {
          "input_topic": "jq_input_message",                             # 指定由 EdgeHub 傳入的 topic
          "jq": "{'MAC':'00:9..........601),'DataID': 301002} ]}",	   # jq 內容
          "output_topic": "jq_output_message"                            # 指定輸出到 EdgeHub 的 topic
      }
  }
  ```

關於 Azure IoT Edge 訊息路由 (Routing) 的運作方式，請參考 Azure 線上文件：

- https://docs.microsoft.com/en-us/azure/iot-edge/iot-edge-runtime?view=iotedge-1.4
- https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-1.4

------

### 如何使用 (於 AIG-301)

#### 1. 設定 Modbus Master

在 AIG-301 上，設定 Modbus Master，確認 Modbus Master 可以正確採集資料。

#### 2. 設定 Azure IoT Edge

- 安裝 thingspro-agent module：你應該已經安裝了，若還沒安裝，請依據 <a href="https://github.com/TPE-TIGER/TPE2-Technical-Document/blob/main/documents/thingspro-agent%20Release%20&%20Configuration.md">這個網頁</a>，依據 ThingsPro Edge 版本，安裝正確的 thingspro-agent。
- 在 AIG-301 上，設定 Azure IoT Edge 的 Telemetry Message，依據目前的設定配置，包括第 1 道 jq。
- 你可以使用 <a href="https://github.com/Azure/azure-iot-explorer/releases">Azure IoT Explorer</a> 來確認 AIG-301 是否正確的透過 Azure IoT Edge 上傳資料到 Azure IoT Hub。

#### 3. 安裝 jqmodule

如同安裝 thingspro-agent module 的方法，你需要安裝 jqmodule：

- name: jqmodule
- image URI: moxa2019/jqmodule:1.1
- 其他欄位不需要設定

#### 4. 設定 jqmodule

##### 4.1 經由 Module Twin 檢視/編輯 設定

jqmodule 啟動後，會將目前 Configuration 透過 Module Reported Properties 回報到 Azure IoT Hub，你可以從 Azure IoT Hub 的 Module Twin 讀取/檢查設定；若需要修改，可以直接透過 Module Desired Properties 來完成作業。

![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-twin.jpg)

- 一般而言，你不需要去更改 input_topic 以及 output_topic
- 基本上你需要為每一台設備，設定符合該設備的 jq，如 MAC, gwSN .....
- 由於 Module Twin 只支援 JSON 內容，但 jq 內容包含了類似變數語法，使得 jq 內容不是一個合規的 JSON，因此，jq 後面帶的必須是一個字串。(請小心、注意字串的正確與完整性)
- Module Twin 最大的資料承載量為 4 KB，如果需要設定的資料量超過此上限，請改用 Direct Method

##### 4.2 經由 Direct Method 檢視/編輯 設定

除了透過 Module Twin 來設定外，也可以透過 Direct Method 來讀取/修改這些設定   

| Method Name | Payload                                                      | 說明           |
| ----------- | ------------------------------------------------------------ | -------------- |
| get_config  | {}                                                           | 讀取目前設定值 |
| set_config  | {<br/>    "setting": {<br/>        "input_topic": "jq_input_message",                             <br/>        "jq": "{'MAC':'00:9..........601),'DataID': 301002} ]}",	   <br/>        "output_topic": "jq_output_message"                            <br/>    }<br/>} | 修改設定值     |

- Direct Method 最大的資料承載量為 128 KB
- 透過 Direct Method 修改後的設定仍然會顯示到 Module Twin 裡
- 若資料量大於 Module Twin 支援的上限 (4 KB)，Module Twin 的 jq 欄位會顯示 ："over size, please retrieve the value by Direct Method: get_config."

#### 5. 設定 Routing，讓 thingspro-agent 的訊息可以傳入 jqmodule

你需要回到 Azure IoT Hub，找到該設備，在 Set modules / Routes 表單裡，設定訊息路由：

![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-routing.jpg)

​		**Route 1 (路由 1)**			

| 目的     | 讓 thingspro-agent 的訊息傳入 jqmodule                       |                                                              |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Name     | to_jqmodule                                                  | 只是名稱，可以更改成其他 Text                                |
| Value    | FROM /messages/modules/thingspro-agent/* INTO BrokeredEndpoint("/modules/jqmodule/inputs/jq_input_message") | Text 必須與實際設定符合，包括：<br />- thingspro-agent、jqmodule 必須是正確的 module name<br />- jq_input_message 必須與 Configuration 的設定一致 |
| Priority | 1                                                            | 預設值即可                                                   |
| TTL      | 7200                                                         | 預設值即可                                                   |

​		**Route 2 (路由 2)**

| 目的     | 讓 jqmodule 的訊息傳到 Azure IoT Hub             |                                                              |
| -------- | ------------------------------------------------ | ------------------------------------------------------------ |
| Name     | to_Azure_IoT_Hub                                 | 只是名稱，可以更改成其他 Text                                |
| Value    | FROM /messages/modules/jqmodule/* INTO $upstream | Text 必須與實際設定符合，包括：<br />- jqmodule 必須是正確的 module name<br />- $upstream 表示 Azure IoT Hub |
| Priority | 2                                                | 預設值即可                                                   |
| TTL      | 7200                                             | 預設值即可                                                   |

#### 6. 完成上述步驟後，你可以使用 Azure IoT Explorer 檢視 message 是否正確轉換成功。

![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-result.jpg)



#### 7. 常見問題診斷與排除

- Azure IoT Edge 的 edgeAgent 或是 edgeHub 出現 fail 狀態

  - ThingsPro Edge 2.2.0、2.2.1、2.3.1 有相匹配的 thingspro-agent 版本以及 create option，請務必依據各版本正確設定

  - ThingsPro Edge 2.2.0、2.2.1、2.3.1 對於 edgeAgent 與 edgeHub 要求的匹配版本如下，請依建議設定

    | ThingsPro Edge Version | edgeAgent / edgeHub version |
    | ---------------------- | --------------------------- |
    | ThingsPro Edge 2.2.0   | 1.0.9                      |
    | ThingsPro Edge 2.2.1   | 1.1.4                      |
    | ThingsPro Edge 2.3.0+  | 1.2                         |

- Azure IoT Explorer 收不到 message

  - 可以從 Azure IoT Hub 設定 edgeHub 環境變數 RuntimeLogLevel = debug，進入 debug 模式

    <img src="https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-edgeHub-debug-mode.jpg" style="zoom:67%;" />

  - 登入到 AIG-301 shell，以 root (su) 身分檢視 edgeHub log，判斷 thingspro-agent 是否有送出 message 到 edgeHub，以及 message 是否有被轉送到 jqmodule；若是無此 log，請檢查 Routing 的設定是否正確

    ```
    journalctl CONTAINER_NAME=edgeHub -f
    ```

    ![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-input-message.jpg)

    ![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-forward-message.jpg)

  - 若是 message 已轉入 jqmodule，你可以檢視 jqmodule log，log 包括接收到的 message、執行 jq 轉換、轉換後的內容

    ```
    journalctl CONTAINER_NAME=jqmodule -f
    ```

    ![](https://thingspro.blob.core.windows.net/resource/document/tpe/jqmodule-log.jpg)

​					

------

### 如何修改、打包 (armhf docker image)

##### 1. Develop Environment

你可以使用 x86 Ubuntu Server 18.04 (64bit) 來開發以及產生 Docker Image (armhf)

| item                   | Note / Command                                               |
| ---------------------- | ------------------------------------------------------------ |
| Linux OS               | A x86 CPU virtual machine with Ubuntu Server 18.04 OS (64bit) |
| Install Docker         | https://docs.docker.com/install/linux/docker-ce/ubuntu/      |
| Install ARM32 emulator | A tool to convert x86/x64 docker image to ARM CPU. <br />>apt-get update<br />>apt-get install -y qemu-user-static |
| jqmodule source code   | https://github.com/TPE-TIGER/TPE2-Application-Development/tree/main/samples/IoT-Edge/jqmodule |

##### 2. Source Code 檔案說明

| Name               | Type | Note                                                         |
| ------------------ | ---- | ------------------------------------------------------------ |
| Dockerfile         | File | Build this jqmodule<br />Convert this jqmodule from x86/x64 to ARM32 docker image by ARM32 emulator. |
| module_config.json | File | Persist configuration                                        |
| module.py          | File | jqmodule startup python code                                 |
| azureClient.py     | File | The major python3 code to handle twin, message and jq process. |
| requirements.tx    | File | The required Python package list of jqmodule.                |

##### 3. Modify Code

Basically, you just need to change code at azureClient.py to fit your extra requirement.

##### 4. Build armhf Docker Image

On Ubuntu Server 18.04 (x86) development envrionment, build docker image by command:

```
$ docker build -t {my_docker_hub}/{my_jqmodule}:{my_version} .
```

You shall change **{value}** by your valid data.

##### 5. Publish docker image 

Publish docker image to somewhere that Azure IoT Hub able to access

```
$ docker push {my_docker_hub}/{my_jqmodule}:{my_version}
```



