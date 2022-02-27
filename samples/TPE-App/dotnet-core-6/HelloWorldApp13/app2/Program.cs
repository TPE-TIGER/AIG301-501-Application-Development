using System.Text;
using System.Text.Json;
class backendProcess
{   
    public string _webAPIURL = "http://127.0.0.1/api/v1"; 
    public Subscriber? _subscriber;
    public Publisher _publisher = new Publisher();
    void waitWebAPI()
    {
        while (true)
        {          
            HttpClient httpClient = new HttpClient();
            // Invoke this applications' self Restful API till ready        
            HttpRequestMessage request = new HttpRequestMessage();
            request.Method = HttpMethod.Get;   
            request.RequestUri = new Uri(_webAPIURL + "/hello-world");
            request.Content = new StringContent("", Encoding.UTF8, "application/json");
            request.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");
            httpClient.DefaultRequestHeaders.ConnectionClose = true;
        
            try {
                var response = httpClient.Send(request);
                StreamReader reader = new StreamReader(response.Content.ReadAsStream());
                string content = reader.ReadToEnd();
                if (content == "Hello World.") {
                    httpClient.Dispose();
                    return; 
                } else {
                    httpClient.Dispose();
                    Console.WriteLine("Waiting API");
                    Thread.Sleep(10000);
                }
            } catch (Exception e) {
                httpClient.Dispose();
                Console.WriteLine("Waiting API");
                Thread.Sleep(10000);
            }
        }
    }
    void createTag(string prvdName, string srcName, string tagName, string dataType)
    {
        HttpClient httpClient = new HttpClient();
        Dictionary<string, string> tagObj = new Dictionary<string, string>();
        tagObj.Add("prvdName", prvdName);
        tagObj.Add("srcName", srcName);
        tagObj.Add("tagName", tagName);
        tagObj.Add("dataType", dataType);
        string postTag = JsonSerializer.Serialize(tagObj);
        // Invoke this application's self Restful API to create Tag
        HttpRequestMessage request = new HttpRequestMessage();
        request.Method = HttpMethod.Post;   
        request.RequestUri = new Uri(_webAPIURL + "/hello-world/tag");
        request.Content = new StringContent(postTag, Encoding.UTF8, "application/json");
        request.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");
        var response = httpClient.Send(request);
        StreamReader reader = new StreamReader(response.Content.ReadAsStream());
        Console.WriteLine(reader.ReadToEnd());
    }
    double C_to_F(Int32 inputC)
    {
        var F= ((inputC*9)/5) + 32;
        return F;
    } 
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
            case "int8":
                dataValue = (SByte)tag["dataValue"];
                break;
            case "int16":
                dataValue = (Int16)tag["dataValue"];
                break;
            case "int32":
                dataValue = (Int32)tag["dataValue"];
                break;
            case "int64":
                dataValue = (Int64)tag["dataValue"];
                break;
            case "uint8":
                dataValue = (Byte)tag["dataValue"];
                break;
            case "uint16":
                dataValue = (UInt16)tag["dataValue"];
                break;
            case "uint32":
                dataValue = (UInt32)tag["dataValue"];
                break;
            case "uint64":
                dataValue = (UInt64)tag["dataValue"];
                break;
            case "float":
                dataValue = (float)tag["dataValue"];
                break;
            case "double":
                dataValue = (double)tag["dataValue"];
                break;
            case "string":
                dataValue = (string)tag["dataValue"];
                break;
            case "byte-array":
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
    public static void Main()
    {
        // Launch Azure IoT Central Client
        backendProcess bgprocess = new backendProcess();
        bgprocess.start();        
    }
}