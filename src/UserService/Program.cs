using UserService.Services;
using UserService.Data;
using Microsoft.Extensions.Diagnostics.HealthChecks;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                      .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true);

string connectionString = builder.Configuration["CustomSettings:connectionString"] ?? "";
string databaseName = builder.Configuration["CustomSettings:databaseName"] ?? "";

builder.Services.AddGrpc();

builder.Services.AddGrpcHealthChecks().AddCheck("Server", () => HealthCheckResult.Healthy());

builder.Services.AddSingleton<UserServiceDbContext>(new UserServiceDbContext(connectionString, databaseName));

var app = builder.Build();

app.MapGrpcService<UserManagementService>();
app.MapGrpcHealthChecksService()
    .AllowAnonymous();
app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");

app.Run();
