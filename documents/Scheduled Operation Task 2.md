# Scheduled Operation Task 2

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-10 | Document created |



### Purpose

This document demonstrates how to use **tpFunc/Function** to perform a hourly based task by invoking ThingsPro Edge Restful API with your business logic.

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
   wget https://tpe2.thingspro.io/tpe2/Python3/scheduler2.tar
   
   tar -xvf scheduler2.tar
   ```

   This command shall create **scheduler1*2 folder, and contains package.json and index.py files.

   ```
   root@Moxa:/home/moxa/scheduler2# ls -l
   total 5
   -rwxrwxrwx 1 root root 3366 Feb 13 14:00 index.py
   -rwxrwxrwx 1 root root  766 Feb 13 14:14 package.json
   ```

4. Understand package.json

   ```
   {
     "name": "scheduler2",
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
         "08": ["Enable_AID()"],
         "18": ["Disable_AID()"],
       }
     }
   }
   ```
   
   - You need to define when to invoke which Commands, under **params / timeLine** JSON section.
   
      - You don't need to declare full time range. Just the hours with commands.
      - You can declare multiple commands for an hour with JSON string array.
   
5. Understand index.py - **Main section**

   ```
   if __name__ == "__main__":
       config = package.Configuration()
       params = config.parameters()
       
       timeLine = params["timeLine"]
       
       now = datetime.now()
       timeFrame = now.strftime("%H")
       print("Run " + timeFrame + " ================")
       
       if timeFrame in timeLine:
           commandList = timeLine[timeFrame]        
           for cmdName in commandList:   
               print("Invoke : " + cmdName)   
               result = eval(cmdName)
               print(result["status"])
               print(result["message"])
       
       print("Shutdown ================")
       print("")
   ```
   
   - index.py will be launch by tpFunc every hour.
   - index.py will check the current time, and pick up matched commands from timeLine.
- index.py will call python's method by matched name of commands,  .

6. Implement all the Commands, for example **Enable_AID() method**

   ```
   def Enable_AID():
       result = {}
       config = get_AID_configuration()    
       if config != None:
           if config["provisioning"]["enable"]:
               result["status"] = "success"
               result["message"] = "Do nothing, the enable already true"
           else:
               config["provisioning"]["enable"] = True
               result = call_API("PUT", "/azure-device", config)
       else:
           result["status"] = "fail"
           result["message"] = "Can't read AID configuration"
       return result
   ```

   - This method will be called by main process, according to the declaration on package.json
   - You can implement it by business logic.

   


### Add to tpFunc and Run

1. Add it to tpFunc

   ```
   cd /home/moxa
   sudo su
   tpfunc add scheduler2
   ```

2. Verify there is no error on creation

   ```
   root@Moxa:/home/moxa# tpfunc ls
   +------------+--------+------------+------------+----------+-------+
   |    NAME    | ENABLE |    MODE    | LASTUPTIME |  STATE   | ERROR |
   +------------+--------+------------+------------+----------+-------+
   | scheduler2 | true   | timeDriven |            | inactive |       |
   +------------+--------+------------+------------+----------+-------+
   ```

3. Verify there is no error when it be launch and review the log

   ```
   root@Moxa:/home/moxa# tpfunc ls
   +------------+--------+------------+---------------------------+---------+-------+
   |    NAME    | ENABLE |    MODE    |        LASTUPTIME         |  STATE  | ERROR |
   +------------+--------+------------+---------------------------+---------+-------+
   | scheduler2 | true   | timeDriven | 2022-02-13T13:00:00+08:00 | running |       |
   +------------+--------+------------+---------------------------+---------+-------+
   
   root@Moxa:/home/moxa# tpfunc log scheduler2
   [2022-02-13T13:00:03+08:00] Run 13 ================
   [2022-02-13T13:00:03+08:00] Shutdown ================
   [2022-02-13T13:00:03+08:00]
   ```
