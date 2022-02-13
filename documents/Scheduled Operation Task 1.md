# Scheduled Operation Task 1

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-10 | Document created |



### Purpose

This document demostrates how to use **tpFunc/Function** to perform a hourly based task by invoking ThingsPro Edge Restful API.

Note: **tpFunc** required ThingsPro Edge V2.2.1+


------

### Install and Setup

1. Login to your ThingsPro Edge SSH console with default path (/home/moxa).

2. Switch role to su

   ```
   sudo su
   ```

3. Download schedule1.tar and unpack it

   ```
   wget https://tpe2.azureedge.net/scheduler1.tar
   
   tar -xvf scheduler1.tar
   ```

   This command shall create **scheduler1** folder, and contains package.json and index.py files.

   ```
   root@Moxa:/home/moxa/scheduler1# ls -l
   total 5
   -rwxrwxrwx 1 root root 2219 Feb 13 11:56 index.py
   -rwxrwxrwx 1 root root 1311 Feb 13 12:10 package.json
   ```

4. Understand package.json

   ```
   {
     "name": "scheduler1",
     "enabled": true,
     "trigger": {
       "driven": "timeDriven",
       "timeDriven": {
         "mode": "cronJob",
         "intervalSec": 1,
         "cronJob": "0 * * * *"
       }
     },
     "expose": {},
     "executable": {
       "language": "python"
     },
     "params": {
       "timeLine": {      
         "08": ["01_Enable_SSH"],
         "18": ["02_Disable_SSH"]
       },
       "commands": {
         "01_Enable_SSH": {
           "displayName": "Enable SSH Service",
           "enable": true,
           "method": "PUT",
           "endPoint": "/system/sshserver",
           "payload": {
             "enable": true,
             "port": 22
           }
         },
         "02_Disable_SSH": {
           "displayName": "Disable SSH Service",
           "enable": true,
           "method": "PUT",
           "endPoint": "/system/sshserver",
           "payload": {
             "enable": false,
             "port": 22
           }
         }
       }
     }
   }
   ```

   1. First of all, you need to define all the ThingsPro Edge APIs (operation tasks) you would like to invoked under **params / commands** JSON section.

      Command Name: **02_Disable_SSH**

      | Key         | Value               | Desc                                                         |
      | ----------- | ------------------- | ------------------------------------------------------------ |
      | displayName | Disable SSH Service | Function will display the task status by displayName         |
      | enable      | true                | enable/disable this task, even it be arranged into schedule. |
      | method      | PUT                 | The method for this Restful API end point.                   |
      | endPoint    | /system/sshserver   | The Restful API end point to be call.                        |
      | payload     | {.....}             | The payload will submit to this Restful API                  |

   2. Second, you need to define when to invoke which Commands you defined, under **params / timeLine** JSON section.

      - You don't need to declare full time range. Just the hours with commands.
      - You can declare multiple commands for an hour with JSON string array.

5. Understand index.py

   ```
   if __name__ == "__main__":
       config = package.Configuration()
       params = config.parameters()
       
       timeLine = params["timeLine"]
       commands = params["commands"]
       
       now = datetime.now()
       timeFrame = now.strftime("%H")
       print("Run " + timeFrame + " ================")
       
       if timeFrame in timeLine:
           commandList = timeLine[timeFrame]        
           for cmdIdx in commandList:
               cmd = commands[cmdIdx]
               if (cmd["enable"]):
                   print("Call API : " + cmd["displayName"])
                   result = call_API(cmd["method"], cmd["endPoint"], cmd["payload"])
                   print(result["status"])
                   print(result["message"])
       
       print("Shutdown ================")
       print("")
   ```

   1. index.py will be launch by tpFunc every hour.
   2. index.py will check the current time, and pick up matched commands from timeLine.
   3. index.py will invoke ThingsPro Edge API by command, and output result on log of tpFunc.




### Add to tpFunc and Run

1. Add it to tpFunc

   ```
   cd /home/moxa
   sudo su
   tpfunc add scheduler1
   ```

2. Verify there is no error on creation

   ```
   root@Moxa:/home/moxa# tpfunc ls
   +------------+--------+------------+------------+----------+-------+
   |    NAME    | ENABLE |    MODE    | LASTUPTIME |  STATE   | ERROR |
   +------------+--------+------------+------------+----------+-------+
   | scheduler1 | true   | timeDriven |            | inactive |       |
   +------------+--------+------------+------------+----------+-------+
   ```

3. Verify there is no error when it be launch and review the log

   ```
   root@Moxa:/home/moxa# tpfunc ls
   +------------+--------+------------+---------------------------+---------+-------+
   |    NAME    | ENABLE |    MODE    |        LASTUPTIME         |  STATE  | ERROR |
   +------------+--------+------------+---------------------------+---------+-------+
   | scheduler1 | true   | timeDriven | 2022-02-13T13:00:00+08:00 | running |       |
   +------------+--------+------------+---------------------------+---------+-------+
   
   root@Moxa:/home/moxa# tpfunc log scheduler1
   [2022-02-13T13:00:03+08:00] Run 13 ================
   [2022-02-13T13:00:03+08:00] Shutdown ================
   [2022-02-13T13:00:03+08:00]
   ```



### Next Action

If your operation tasks are complex than a simple Restful API:

- <a href="Scheduled%20Operation%20Task%202.md">(Example) Scheduled Operation Task 2</a>
