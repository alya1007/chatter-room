using UserService.Services;
using UserService.Data;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using Microsoft.AspNetCore.Server.Kestrel.Core;

var builder = WebApplication.CreateBuilder(args);

int grpcPort = int.Parse(Environment.GetEnvironmentVariable("GRPC_PORT") ?? "10000");
int webSocketPort = int.Parse(Environment.GetEnvironmentVariable("WEBSOCKET_PORT") ?? "10001");

builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(grpcPort, listenOptions =>
    {
        listenOptions.Protocols = HttpProtocols.Http2;
    });
    options.ListenAnyIP(webSocketPort, listenOptions =>
    {
        listenOptions.Protocols = HttpProtocols.Http1;
    });
});

string connectionString = Environment.GetEnvironmentVariable("USER_CONNECTION_STRING") ?? "";
string databaseName = Environment.GetEnvironmentVariable("USER_DATABASE_NAME") ?? "";
string serviceDiscoveryAddress = Environment.GetEnvironmentVariable("SERVICE_DISCOVERY_ADDRESS") ?? "";
string serviceName = Environment.GetEnvironmentVariable("SERVICE_NAME") ?? "";

var serviceRegistryClient = new ServiceRegistryClient(serviceDiscoveryAddress);

var serviceUrl = $"user-service:{Environment.GetEnvironmentVariable("PORT")}";

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
