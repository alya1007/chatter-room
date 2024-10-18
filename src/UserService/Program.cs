using UserService.Services;
using UserService.Data;
using Microsoft.Extensions.Diagnostics.HealthChecks;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                      .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true);

string connectionString = builder.Configuration["CustomSettings:connectionString"] ?? "";
string databaseName = builder.Configuration["CustomSettings:databaseName"] ?? "";

string serviceDiscoveryAddress = builder.Configuration["Registry:serviceDiscoveryAddress"] ?? "";
string serviceName = builder.Configuration["Registry:serviceName"] ?? "";

builder.Configuration.AddJsonFile(Path.Combine(Directory.GetCurrentDirectory(), "Properties", "launchSettings.json"));

string fullServiceUrl = builder.Configuration["profiles:http:applicationUrl"] ?? "";
string pattern = @"localhost.*";
string serviceUrl = System.Text.RegularExpressions.Regex.Match(fullServiceUrl, pattern).ToString();

var serviceRegistryClient = new ServiceRegistryClient(serviceDiscoveryAddress);

await serviceRegistryClient.RegisterServiceAsync(serviceName, serviceUrl);

builder.Services.AddGrpc();

builder.Services.AddGrpcHealthChecks().AddCheck("Sample", () => HealthCheckResult.Healthy());

builder.Services.AddSingleton<UserServiceDbContext>(new UserServiceDbContext(connectionString, databaseName));

var app = builder.Build();

app.MapGrpcService<UserManagementService>();
app.MapGrpcHealthChecksService()
    .AllowAnonymous();
app.MapGet("/", () => "This is the User Service.");

app.Run();
