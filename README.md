# AIG301/501 Application Development

### TPE Application v.s. tpFunc Function v.s. AIE Module

There are 3 ways for customers to develop, run your own application on AIG301/501 device. All these ways allow your application to integrate and leverage ThingsPro Edge's capabilities and features by Restful API and SDK.

The application could be edge computing program (to calculate, manipulate, analysis data on edge), data acquisition (to fetch data by proprietary protocols), scheduling task (to arrange routine operation tasks), or data publish program (to transfer data to specific IT system).

Below table gives you ideas how to select suitable application development way to fit your requirements.

|                        | TPE Application                                              | tpFunc Function                                       | AIE Module                                                   |
| ---------------------- | ------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------ |
| Framework              | Docker container managed by ThingsPro Edge                   | Python program managed by tpFunc                      | Docker container managed by Azure IoT Edge                   |
| Language               | All programing language                                      | Python 3                                              | All programing language                                      |
| TagHub SDK             | Python, C and Go Lang SDK                                    | Python SDK                                            | Python, C and Go Lang SDK                                    |
| Access TPE API         | OK                                                           | OK                                                    | OK                                                           |
| LAN Access             | OK                                                           | OK                                                    | OK                                                           |
| WAN Access             | OK                                                           | OK                                                    | OK                                                           |
| Storage Access         | OK                                                           | X                                                     | OK                                                           |
| Serial Port Access     | OK (*)                                                       | X                                                     | OK (*)                                                       |
| BLE Access             | OK (*)                                                       | X                                                     | OK (*)                                                       |
| Expose Restful API     | OK                                                           | OK                                                    | OK                                                           |
| Expose Web GUI         | OK                                                           | X                                                     | OK                                                           |
| Knowledge Require      | - Docker container Application design<br />- Linux Driver & Utility<br />- ThingsPro Edge Application build and deployment | Python coding tpFunc deployment                       | - Docker container Application<br />design<br />- Linux Driver & Utility<br />- Azure IoT Edge |
| Program Design Pattern | By your own                                                  | - Time Driven<br />- Data Driven<br />- Web API Style | By your own                                                  |
| Other Limitations      |                                                              | - all source code must keep at 1 file                 |                                                              |

(*) Need to mount physical resources into Docker container

## ThingsPro Edge Application

- <a href="documents/What%20is%20ThingsPro%20Edge%20Appliation.md">What is ThingsPro Edge Application</a>
#### Python3 Sample App
1. <a href="documents/Build%20and%20Run%20Hello%20World%20Application-python3.md">Build and Run "Hello World" Application</a>
2. <a href="documents/Invoke%20ThingsPro%20Edge%20API%20on%20Hello%20World%20Application-python3.md">Invoke ThingsPro Edge API on "Hello World" Application</a>
3. <a href="documents/Use%20TagHub%20SDK%20on%20Hello%20World%20Application%201-python3.md">Use TagHub SDK on Hello World Application 1</a> (publish tag)
4. <a href="documents/Use%20TagHub%20SDK%20on%20Hello%20World%20Application%202-python3.md">Use TagHub SDK on Hello World Application 2</a> (subscribe tag)
5. <a href="documents/Bind%20Hello%20World%20Application%20on%20Host%20Port%20-%20Way%201.md">Bind Hello World Application on Host Port - Way 1</a>
6. <a href="documents/Bind%20Hello%20World%20Application%20on%20Host%20Port%20-%20Way%202.md">Bind Hello World Application on Host Port - Way 2</a>
7. <a href="documents/Azure%20IoT%20Central.md">(Example) Azure IoT Central Demo Application</a>
8. <a href="documents/OPC%20UA%20Client%20Sample%20Application-python3.md">(Example) OPC UA Client Application</a>
9. <a href="documents/File%20Upload:%20from%20FTP%20to%20AWS%20S3.md">(Example) File Download/Upload Sample Application</a>

#### Dotnet Core C# Sample App
1. <a href="documents/Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>
2. <a href="documents/Invoke%20ThingsPro%20Edge%20API%20on%20Hello%20World%20Application-dotnet.md">Invoke ThingsPro Edge API on "Hello World" Application</a>
3. <a href="documents/Use%20TagHub%20SDK%20on%20Hello%20World%20Application%201-dotnet.md">Use TagHub SDK on Hello World Application 1</a> (publish tag)
4. <a href="documents/Use%20TagHub%20SDK%20on%20Hello%20World%20Application%202-dotnet.md">Use TagHub SDK on Hello World Application 2</a> (subscribe tag)

#### C Sample App
1. <a href="documents/Develop%20Our%20Own%20ThingsPro%20Edge%20Application%20in%20C.md">Develop Our Own ThingsPro Edge Application in C</a>

## tpFunc Function
1. <a href="https://github.com/TPE-TIGER/tpe-function-sdk">What is tpFunc and tpFunc funciton</a>
2. <a href="documents/Scheduled%20Operation%20Task%201.md">(Example) Scheduled Operation Task 1</a> (by confg)
3. <a href="documents/Scheduled%20Operation%20Task%202.md">(Example) Scheduled Operation Task 2</a> (by code)
4. <a href="documents/Enable%20onChange%20Feature%20on%20TagHub.md">(Example) Enable onChange Feature on TagHub</a> 
5. <a href="documents//Import%20Modbus%20Config%20by%20Azure%20IoT%20Hub%20Direct%20Method.md">(Example) Import Modbus Configuration File by Azure IoT Hub Direct Method</a>
6. <a href="documents/tpFunc-Virtual-Tags-by-Hopping-Window.md">(Example) Virtual Tags by Hopping Window</a>

## Azure IoT Edge Module
1. <a href="documents/Develop%20Our%20Own%20&quot;thingspro-agent&quot;%20Module%20in%20Python3.md">Develop Our Own "thingspro-agent" Module in Python3</a>
2. <a href="documents/Develop%20Module%20on%20.Net%20Core%206%20%2B%20ARM32%20%2B%20Debian64.md">Develop Module on .Net Core 6 (ARM32, Debian64)</a>
3. <a href="documents/jqmodule-readme-Eng.md">jq Module Readme</a>
4. <a href="documents/Develop%20Our%20Own%20&quot;thingspro-agent&quot;%20Module%20in%20C.md">Develop Our Own "thingspro-agent" Module in C</a>
5. <a href="documents/Leveraging%20TPM%20in%20IoT%20Edge%20Module.md">Leveraging TPM in IoT Edge Module</a>
6. <a href="documents/Leveraging%20DIO%20in%20IoT%20Edge%20Module.md">Leveraging DIO in IoT Edge Module</a>
