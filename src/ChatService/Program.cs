using ChatService.Services;
using ChatService.Data;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using System.Net.WebSockets;
using System.Text;
using System.Threading;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true).AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true);

string connectionString = builder.Configuration["CustomSettings:connectionString"] ?? "";
string databaseName = builder.Configuration["CustomSettings:databaseName"] ?? "";

string serviceDiscoveryAddress = builder.Configuration["Registry:serviceDiscoveryAddress"] ?? "";
string serviceName = builder.Configuration["Registry:serviceName"] ?? "";
string userServiceName = builder.Configuration["Registry:userServiceName"] ?? "";

var serviceRegistryClient = new ServiceRegistryClient(serviceDiscoveryAddress);

var serviceUrl = $"chat-service:{builder.Configuration["Registry:port"]}";

await serviceRegistryClient.RegisterServiceAsync(serviceName, serviceUrl);

string userServiceUrl = await serviceRegistryClient.DiscoverServiceAsync(userServiceName);
string userServiceFullUrl = $"http://{userServiceUrl}";

builder.Services.AddGrpc();

builder.Services.AddGrpcHealthChecks().AddCheck("Sample", () => HealthCheckResult.Healthy());

builder.Services.AddSingleton<ChatServiceDbContext>(new ChatServiceDbContext(connectionString, databaseName));

builder.Services.AddSingleton<UserManagementClient>(new UserManagementClient(userServiceFullUrl));

var app = builder.Build();


app.UseWebSockets();

WebSocketChatService.Initialize(new ChatServiceDbContext(connectionString, databaseName));

app.Map("/ws/chat", async context =>
{
    if (context.WebSockets.IsWebSocketRequest)
    {
        Console.WriteLine("WebSocket request received");
        var webSocket = await context.WebSockets.AcceptWebSocketAsync();
        await WebSocketChatService.HandleWebSocket(context, webSocket);
    }
    else
    {
        Console.WriteLine("Not a WebSocket request");
        context.Response.StatusCode = 410;
    }
});

app.MapGrpcService<ChatManagementService>();
app.MapGrpcHealthChecksService()
    .AllowAnonymous();
app.MapGet("/", () => "This is the Chat Service.");

app.Run();
