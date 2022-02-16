
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
var tpeHelper = new TPE_Helper();

app.MapGet("/api/v1/hello-world", () => 
{
    return "Hello World";
});

app.MapGet("/api/v1/hello-world/tpe-apps", () => 
{
    return tpeHelper.call_API("get", "/apps", "");
});

app.Run("http://0.0.0.0:80");
