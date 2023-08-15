# Use TagHub SDK on Hello World Application 1

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-25 | Document created |



### Purpose

This document guide you how to call **TagHub C Lib SDK** via C# (dotnet core 6) on Hello World Application to **publish** Tag data.

You shall complete pre-request steps:

- <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>.
- <a href="Invoke%20ThingsPro%20Edge%20API%20on%20Hello%20World%20Application-dotnet.md">Invoke ThingsPro Edge API on Hello World Application</a>




------

### 1. Modify C# Code

##### 1.1 Add TagSDK_Helper.cs and TagType.cs

```
public unsafe class Publisher : TagType
{    
    // Load C Lib and declare 3 APIs
    const string DLL_Path = "/usr/lib/arm-linux-gnueabihf/libmx-dx.so";
    [DllImport(DLL_Path)]
    private static extern UIntPtr dx_tag_client_init([In, MarshalAs(UnmanagedType.LPStr)] string moduleName);
    
    .....
    
    // publish mehtod to build C Lib data structure
    public unsafe int publish(Dictionary<string,object> tag)
    {
        string prvdName, srcName, tagName, valueTypeString;
        TAG_VALUE_TYPE valueType;
        TAG_VALUE tagValue = new TAG_VALUE();
        
        ....
        
        return (int)publish(prvdName, srcName, tagName, valueType, tagValue);
    } 
```

- TagSDK_Helper container Publisher class which imports TagHub C Lib SDK, and expose method: publish allows developer to update a tag's value.
- TagType.cs contains required data structures which mapping with TagHub C Lib headers.

##### 1.2 Define Tag Publisher on Program.cs

```
Publisher _publisher = new Publisher();
```

- We will use _publisher to update Tag value on Program.cs


##### 1.3 Define a method on Program.cs to Create a Virtual Tag via ThingsPro Edge Restful API

```
app.MapPost("/api/v1/hello-world/tag", (TagObj tagObj) =>
{
    if ((tagObj.prvdName != null) && (tagObj.srcName != null) && (tagObj.tagName != null) && (tagObj.dataType != null))
    {
        try
        {            var result = tpeHelper.call_API("get", "/tags/list?provider=" + tagObj.prvdName, "");
            var jsonObj = JsonDocument.Parse(result);
            foreach (JsonElement elem in jsonObj.RootElement.GetProperty("data").EnumerateArray())
            {
                if ((elem.GetProperty("srcName").ToString() == tagObj.srcName) && (elem.GetProperty("tagName").ToString() == tagObj.tagName))
                    return "OK";
            }
            // Create Tag
            tagObj.access = "rw";
            string postTag = JsonSerializer.Serialize(tagObj);
            result = tpeHelper.call_API("post", "/tags/virtual", postTag);
            return "OK";
        }
        catch (Exception e)
        {
            return e.ToString();
        }
    }
    else
    {
        return "Bad payload.";
    }
});
```

- Before update writable tags, this method allows us to create virtual tags by Restful API.


##### 1.4 Define a method on Program.cs to Update a Virtual Tag Value via TagHub C Lib SDK

```
app.MapPut("/api/v1/hello-world/tag", (TagObj tagObj) =>
{
    if ((tagObj.prvdName != null) && (tagObj.srcName != null) && (tagObj.tagName != null) && (tagObj.dataType != null) && (tagObj.dataValue != null))
    {
        Dictionary<string, object> tagDict = new Dictionary<string, object>();
        try
        {
            tagDict.Add("prvdName", tagObj.prvdName);
            tagDict.Add("srcName", tagObj.srcName);
            tagDict.Add("tagName", tagObj.tagName);
            tagDict.Add("dataType", tagObj.dataType);
            System.Text.Json.JsonElement valueJObject = (System.Text.Json.JsonElement)tagObj.dataValue;
            switch (tagObj.dataType)
            {
                case "boolen":
                    tagDict.Add("dataValue", valueJObject.GetBoolean());
                    break;
               	......
            }
            var rc = _publisher.publish(tagDict);
            return rc.ToString();
        }
        catch (Exception e)
        {
            return e.ToString();
        }
    }
    else
    {
        return "Bad payload.";
    }
});
```

- _publisher.publish() will update **Tag**'s value.




### 2. Develop Your Application

#### 2.1 Download Hello World Application 1.2

```
$ wget https://tpe2.thingspro.io/tpe2/dotnet-core-6/HelloWorldApp12.tar
```

#### 2.2 ThingsPro Edge Application 1.2 Structure

| Name               | Type   | Note                                       |
| ------------------ | ------ | ------------------------------------------ |
| Dockerfile         | File   | Add TagHub C Lib SDK and required packages |
| app                | Folder | Update with TagHub C Lib SDK code          |
| docker-compose.yml | File   | Update version to 1.2                      |
| metadata.yml       | File   | Update version to 1.2                      |
| nginx.conf         | File   | Same with 1.0                              |

#### 2.3 Build ThingsPro Edge Applicaiton

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>, to build hello-world application V1.2

```
drwxrwxrwx 5 root root      4096 Feb 23 15:44 app
-rwxrwxrwx 1 root root       877 Feb 24 16:59 build-step.txt
-rwxrwxrwx 1 root root        78 Feb 25 01:06 docker-compose.yml
-rwxrwxrwx 1 root root      1881 Feb 25 00:54 Dockerfile
-rw-r--r-- 1 root root 133355520 Feb 25 01:13 hello-world_1.2_armhf.mpkg
-rwxrwxrwx 1 root root       107 Feb 23 15:18 metadata.yml
-rwxrwxrwx 1 root root       281 Feb 12 05:59 nginx.conf
```



### 3. Deploy Application on Moxa IIoT Gateway

##### 3.1 Deploy hello-world V1.2

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>, to deploy hello-world application V1.2

##### 3.2 Testing 

###### 3.2.1 Create two new virtual tags by **POST /api/v1/hello-world/tag**

```
curl -X POST https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag01", "dataType":"string"}'

curl -X POST https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag02", "dataType":"int32"}'
```

###### 3.3.2 Update virtual tags value by PUT /api/v1/hello-world/tag

```
curl -X PUT https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag01", "dataValue":"Hello World", "dataType":"string"}'

curl -X PUT https://127.0.0.1:8443/api/v1/hello-world/tag -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -H "Content-Type:application/json" -k -d '{"prvdName":"virtual","srcName":"hello-world","tagName":"tag02", "dataValue":4040, "dataType":"int32"}'
```

###### 3.2.3 Monitor these two virtual tags on ThingsPro Edge Web Admin

<p align="center" width="100%"><img src="https://thingspro.blob.core.windows.net/resource/document/tpe/tagMonitor2.JPG" width="100%" /></p>



ThingsPro Edge Web Admin / Tag Management offers a easy way to monitor Tag value changed.

This feature is available on ThingsPro Edge V2.2.1+.



##### 3.3 Done and Next Action

- <a href="Use%20TagHub%20SDK%20on%20Hello%20World%20Application%202-dotnet.md">Use TagHub SDK on Hello World Application 2</a>

