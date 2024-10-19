using UserService.Services;
using UserService.Data;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using System.Net.WebSockets;
using System.Text;
using System.Threading;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                      .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true);

string connectionString = builder.Configuration["CustomSettings:connectionString"] ?? "";
string databaseName = builder.Configuration["CustomSettings:databaseName"] ?? "";

string serviceDiscoveryAddress = builder.Configuration["Registry:serviceDiscoveryAddress"] ?? "";
string serviceName = builder.Configuration["Registry:serviceName"] ?? "";

var serviceRegistryClient = new ServiceRegistryClient(serviceDiscoveryAddress);

var serviceUrl = $"user-service:{builder.Configuration["Registry:port"]}";

await serviceRegistryClient.RegisterServiceAsync(serviceName, serviceUrl);

builder.Services.AddGrpc();

builder.Services.AddGrpcHealthChecks().AddCheck("Sample", () => HealthCheckResult.Healthy());

builder.Services.AddSingleton<UserServiceDbContext>(new UserServiceDbContext(connectionString, databaseName));

var app = builder.Build();

app.UseWebSockets();

WebSocketUserService.Initialize();

app.Map("/ws/alert", async context =>
{
    if (context.WebSockets.IsWebSocketRequest)
    {
        Console.WriteLine("WebSocket request received");
        var webSocket = await context.WebSockets.AcceptWebSocketAsync();
        await WebSocketUserService.HandleWebSocket(context, webSocket);
    }
    else
    {
        Console.WriteLine("Not a WebSocket request");
        context.Response.StatusCode = 410;
    }
});

app.MapGrpcService<UserManagementService>();
app.MapGrpcHealthChecksService()
    .AllowAnonymous();
app.MapGet("/", () => "This is the User Service.");

app.Run();
