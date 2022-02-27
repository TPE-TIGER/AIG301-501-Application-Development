
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/api/v1/hello-world", () => 
{
    return "Hello World.";
});




app.Run("http://0.0.0.0:80");