using System.Text;

public class TPE_Helper
{    
    private HttpClient _client;
    private string _tpeURL;
    public TPE_Helper()
    {
        this._client = new HttpClient();        
        this._client.DefaultRequestHeaders.Add("mx-api-token", File.ReadAllText("/run/mx-api-token"));
        this._tpeURL = "http://" + Environment.GetEnvironmentVariable("APPMAN_HOST_IP") + ":59000/api/v1";
    }
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
}