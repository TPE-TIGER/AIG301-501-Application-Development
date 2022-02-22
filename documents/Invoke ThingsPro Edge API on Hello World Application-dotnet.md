# Invoke ThingsPro Edge API on Hello World Application

Document Version: V1.0

##### Change Log

| Version | Date       | Content          |
| ------- | ---------- | ---------------- |
| 1.0     | 2022-02-16 | Document created |



### Purpose

This document guide you how to invoke ThingsPro Edge API on Hello World Application.

You shall complete pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>.




------

### 1. Modify Code

##### 1.1 Add TPE_Helper.cs

TPE_Helper.cs contains a TPE_Helper class, which allow to invoke TPE's Restful API easily.

##### 1.2 Construct of TPE_Helper

```
public TPE_Helper()
    {
        this._client = new HttpClient();        
        this._client.DefaultRequestHeaders.Add("mx-api-token", File.ReadAllText("/run/mx-api-token"));
        this._tpeURL = "http://" + Environment.GetEnvironmentVariable("APPMAN_HOST_IP") + ":59000/api/v1";
    }
```

- ThingsPro Edge Application be assigned below environment variables. At this sample code, we use 'APPMAN_HOST_IP', which points to ThingsPro Edge API service.

  | Name           | Value      | Desc                                   |
  | -------------- | ---------- | -------------------------------------- |
  | APPMAN_HOST_IP | 172.31.8.1 | ThingsPro Edge API service IP address. |

- Your application shall read API token from '/run/mx-api-token', and pass it on HTTP headers, when invoke ThingsPro Edge Restful API.

##### 1.3 Define a method to Invoke ThingsPro Edge Restful API

```
public string call_API(string method, string endPoint, string payload)
    {  
        try {
            HttpRequestMessage request = new HttpRequestMessage();
            if (method.ToLower() == "put") {
                request.Method = HttpMethod.Put;
            } else if (method.ToLower() == "post") {
                request.Method = HttpMethod.Post;
            } else if (method.ToLower() == "delete") {
                request.Method = HttpMethod.Delete;
            } else if (method.ToLower() == "patch") {
                request.Method = HttpMethod.Patch;
            } else if (method.ToLower() == "get") {
                request.Method = HttpMethod.Get;             
            }
            request.RequestUri = new Uri(this._tpeURL + endPoint);
            request.Content = new StringContent(payload, Encoding.UTF8, "application/json");
            request.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");
            var response = this._client.Send(request);
            StreamReader reader = new StreamReader(response.Content.ReadAsStream());
               
            return reader.ReadToEnd();

        } catch {
            return "fail";
        }
    }
```

##### 1.4 Add new Restful API endPoint: /api/v1/hello-world/tpe-apps

```
app.MapGet("/api/v1/hello-world/tpe-apps", () => 
{
    return tpeHelper.call_API("get", "/apps", "");
});
```

This new Restful API will invoke ThingsPro Edge Restful API: /api/v1/apps, and return result back.



------

### 2. Build Your Application

#### 2.1 Download Hello World Application 1.1

```
$ wget https://tpe2.azureedge.net/dotnet-core-6/HelloWorldApp11.tar
```

#### 2.2 ThingsPro Edge Application 1.1 Structure

| Name               | Type   | Note                        |
| ------------------ | ------ | --------------------------- |
| Dockerfile         | File   | Same with 1.0               |
| app                | Folder | Update with Invoke API code |
| docker-compose.yml | File   | Update version to 1.1       |
| metadata.yml       | File   | Update version to 1.1       |
| nginx.conf         | File   | Same with 1.0               |

#### 2.3 Build ThingsPro Edge Applicaiton

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>, to build hello-world application V1.1

```
drwxrwxrwx 2 root root     4096 Feb 12 06:29 app
-rwxrwxrwx 1 root root       56 Feb 12 06:44 docker-compose.yml
-rwxrwxrwx 1 root root      852 Nov  9  2019 Dockerfile
-rw-r--r-- 1 root root 28456960 Feb 12 07:51 hello-world_1.1_armhf.mpkg
-rwxrwxrwx 1 root root      107 Feb 12 06:39 metadata.yml
-rwxrwxrwx 1 root root      281 Feb 12 05:59 nginx.conf
-rwxrwxrwx 1 root root       22 Feb 12 07:47 requirements.txt
```



### 3. Deploy Application on Moxa IIoT Gateway

##### 3.1 Deploy hello-world V1.1

Follow pre-request step: <a href="Build%20and%20Run%20Hello%20World%20Application-dotnet.md">Build and Run "Hello World" Application</a>, to deploy hello-world application V1.1

##### 3.2 Testing new Restful API: /api/v1/hello-world/tpe-apps

```
$ curl -X GET https://127.0.0.1:8443/api/v1/hello-world/tpe-apps -H "mx-api-token:$(cat /var/thingspro/data/mx-api-token)" -k

{"count":9,"data":[{"arch":"armhf","attributes":null,"availableVersions":[],"category":"","cpu_percent":0,"description":"","desiredState":"ready","displayName":"Hello World App","hardwares":[],"health":"good","icon":"","id":"hello-world","imageSize":95196160,"license":{"paid":true,"type":"free"},"mem_limit":0,"menuID":"app-hello-world","name":"hello-world","ports":{"filter":null,"forward":null},"state":"ready","version":"1.1"},{"arch":"armhf","attributes":

....

Server","desiredState":"ready","displayName":"OPCUA Server","hardwares":[],"health":"good","icon":"","id":"opcuaserver","imageSize":58061824,"license":{"paid":true,"type":"propetual"},"mem_limit":0,"menuID":"app-opcuaserver","name":"opcuaserver","ports":{"filter":null,"forward":null},"state":"ready","version":"2.1.0-644"}]}
```

##### 3.4 Done and Next Action

- <a href="Use%20TagHub%20SDK%20on%20Hello%20World%20Application%201-dotnet.md">Use TagHub SDK on Hello World Application 1</a>
