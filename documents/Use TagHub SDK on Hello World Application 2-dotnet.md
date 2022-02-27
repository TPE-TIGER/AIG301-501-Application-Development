# Use TagHub SDK on Hello World Application 2

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-27 | Document created |



### Purpose

This document guide you how to use **TagHub C SDK** on Hello World Application to **subscribe** Tag data for edge computing.

You shall complete pre-request steps:

- <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>.
- <a href="Invoke%20ThingsPro%20Edge%20API%20on%20Hello%20World%20Application-dotnet.md">Invoke ThingsPro Edge API on Hello World Application</a>
- <a href="Use%20TagHub%20SDK%20on%20Hello%20World%20Application%201-dotnet.md">Use TagHub SDK on Hello World Application 1</a>




------

### 1. Add backendProcess Class

We need to create a new dotnet core console project to subscribe and process tags on backend. You can find it on folder 'app2'.

##### 1.1 Create new folder 'app2'

- Change original folder 'app' to 'app1'
- Rename original project 'HelloWorldApp13' to 'HelloWorldApp13_1'
- Create new folder 'app2', and initial a new dotnet console project 'HelloWorldApp13_2'

##### 1.2 Copy TagSDK_Helper.cs and TagType.cs

```
// Initial tag SDK 
    public Publisher()
    {
        _tagClient = dx_tag_client_init("Publisher_app2");
    }
```

- Copy these two files from 'HelloWorldApp12' to 'HelloWorldApp13_2', but adjust Publisher constructions by given a new name 'Publisher_app2'.
- This adjustment is important to distinguish another Publisher object on 'HelloWorldApp13_1'.


##### 1.3 Create start() method

```
public void start()
    {
        // Waiting Web API
        waitWebAPI();

        // Create virtual tags before subscribe them
        createTag("virtual","hello-world","tag01","string");
        createTag("virtual","hello-world","tag02","int32");
        createTag("virtual","hello-world","tag03","int32");

        // Subscribe virtual tags, and declare call back function  
        _subscriber = new Subscriber(tagDataCallback);
        _subscriber.subscribe("virtual", "hello-world", "tag02");

        while (true)
            Thread.Sleep(1000);
    }
```

- We tell Tag Subscriber that we want to subscribe tag02, and call we defined method, tagDataCallback, when data coming.

- To prevent failure, we create virtual tags (via hello-world Restful API) again, including 3rd tag (tag03).


##### 1.4 Create tagDataCallback() method

```
public void tagDataCallback(Dictionary<string,object> tag)
    {
        var tagPath = tag["prvdName"] + "/" + tag["srcName"] + "/" + tag["tagName"];
        var timeStamp = tag["timeStamp"];
        var dataType = tag["dataType"];
        var dataValue = new Object();
        switch (dataType)
        {
            case "boolen":
                dataValue = (bool)tag["dataValue"];
                break;
            ....
            case "raw":
                byte[] dataValueByte = (byte [])tag["dataValue"];
                dataValue = BitConverter.ToString(dataValueByte);
                break;            
        }
        if ((string)tag["tagName"] == "tag02") {
            double F = C_to_F((Int32)dataValue);
            Dictionary<string, object> tag03 = new Dictionary<string, object>();
            tag03.Add("prvdName", "virtual");
            tag03.Add("srcName", "hello-world");
            tag03.Add("tagName", "tag03");
            tag03.Add("dataType", "int32");
            tag03.Add("dataValue", (Int32)F);
            int rc1 = _publisher.publish(tag03);   

            string tag01Value = "";
            if (F >= 100)
                tag01Value = "Over Heat";
            else
                tag01Value = "Normal";
            
            Dictionary<string, object> tag01 = new Dictionary<string, object>();
            tag01.Add("prvdName", "virtual");
            tag01.Add("srcName", "hello-world");
            tag01.Add("tagName", "tag01");
            tag01.Add("dataType", "string");
            tag01.Add("dataValue", tag01Value);
            int rc2 = _publisher.publish(tag01);     
        }        
        Console.WriteLine("tag: " + tagPath + ", dataValue: " + dataValue + "(" + dataType + "), ts: " + timeStamp);
    }
```

- We convert tag02 value (temperature) , from °*C* to °*F*   , and publish temperature °*F*   to tag03.
- If tag03 value >= 100, publish 'Over Hit' to tag01, else publish 'Normal' to tag01




### 2. Develop Your Application

#### 2.1 Download Hello World Application 1.3

```
$ wget https://tpe2.azureedge.net/dotnet-core-6/HelloWorldApp13.tar
```

#### 2.2 ThingsPro Edge Application 1.3 Structure

| Name               | Type   | Note                                                         |
| ------------------ | ------ | ------------------------------------------------------------ |
| Dockerfile         | File   | Updated for launch HelloWorldApp13_1.dll and HelloWorldApp13_2.dll |
| app1               | Folder | Same with 1.2, HelloWorldApp12                               |
| app2               | Folder | Create new console app at backend to subscribe and handle tags |
| docker-compose.yml | File   | Update version to 1.3                                        |
| metadata.yml       | File   | Update version to 1.3                                        |
| nginx.conf         | File   | Same with 1.0                                                |
| run.sh             | File   | Docker container launch shell script                         |

#### 2.3 Build ThingsPro Edge Applicaiton

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>, to build hello-world application V1.3

```
drwxrwxrwx 5 root root      4096 Feb 26 10:55 app1
drwxrwxrwx 5 root root      4096 Feb 26 13:08 app2
-rwxrwxrwx 1 root root        78 Feb 26 13:30 docker-compose.yml
-rwxrwxrwx 1 root root      2117 Feb 27 00:20 Dockerfile
-rw-r--r-- 1 root root 133396480 Feb 27 00:32 hello-world_1.3_armhf.mpkg
-rwxrwxrwx 1 root root       107 Feb 26 13:30 metadata.yml
-rwxrwxrwx 1 root root       281 Feb 12 05:59 nginx.conf
-rwxrwxrwx 1 root root        71 Feb 26 13:06 run.sh
```



### 3. Deploy Application on Moxa IIoT Gateway

##### 3.1 Deploy hello-world V1.3

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>, to deploy hello-world application V1.3

##### 3.2 Testing 

###### 3.3.1 Update virtual tags value by PUT /api/v1/hello-world/tag

```
curl -X PUT https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag02", "dataValue":20, "dataType":"int32"}'

curl -X PUT https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag02", "dataValue":4040, "dataType":"int32"}'
```

###### 3.2.2 Monitor these two virtual tags on ThingsPro Edge Web Admin

Add Tag03 into monitoring.

<p align="center" width="100%"><img src="https://thingspro.blob.core.windows.net/resource/document/tpe/tagMonitor3.JPG" width="100%" /></p>

ThingsPro Edge Web Admin / Tag Management offers a easy way to monitor Tag value changed.

This feature is available on ThingsPro Edge V2.2.1+.



##### 3.3 Done and Next Action

