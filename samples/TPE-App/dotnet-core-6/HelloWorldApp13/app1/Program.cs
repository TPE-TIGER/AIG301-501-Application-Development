using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
var tpeHelper = new TPE_Helper();

Publisher _publisher = new Publisher();

app.MapGet("/api/v1/hello-world", () =>
{
    return "Hello World.";
});

app.MapGet("/api/v1/hello-world/tpe-apps", () =>
{
    return tpeHelper.call_API("get", "/apps", "");
});

app.MapPost("/api/v1/hello-world/tag", (TagObj tagObj) =>
{
    if ((tagObj.prvdName != null) && (tagObj.srcName != null) && (tagObj.tagName != null) && (tagObj.dataType != null))
    {
        try
        {
            var result = tpeHelper.call_API("get", "/tags/list?provider=" + tagObj.prvdName, "");
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
                case "int8":
                    tagDict.Add("dataValue", valueJObject.GetSByte());
                    break;
                case "int16":
                    tagDict.Add("dataValue", valueJObject.GetInt16());
                    break;
                case "int32":
                    tagDict.Add("dataValue", valueJObject.GetInt32());
                    break;
                case "int64":
                    tagDict.Add("dataValue", valueJObject.GetInt64());
                    break;
                case "uint8":
                    tagDict.Add("dataValue", valueJObject.GetByte());
                    break;
                case "uint16":
                    tagDict.Add("dataValue", valueJObject.GetUInt16());
                    break;
                case "uint32":
                    tagDict.Add("dataValue", valueJObject.GetUInt32());
                    break;
                case "uint64":
                    tagDict.Add("dataValue", valueJObject.GetUInt64());
                    break;
                case "float":
                    tagDict.Add("dataValue", valueJObject.GetDecimal());
                    break;
                case "double":
                    tagDict.Add("dataValue", valueJObject.GetDouble());
                    break;
                case "string":
                    tagDict.Add("dataValue", valueJObject.GetString());
                    break;                
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

app.Run("http://0.0.0.0:80");

class TagObj
{
    public string? prvdName { get; set; }
    public string? srcName { get; set; }
    public string? tagName { get; set; }
    public string? dataType { get; set; }
    public Object? dataValue { get; set; }
    public string? access { get; set; }
}
