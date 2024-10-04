using UserService.Services;
using UserService.Data;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddGrpc();

builder.Services.AddSingleton<UserServiceDbContext>(new UserServiceDbContext("mongodb://localhost:27017", "UserServiceDb"));

var app = builder.Build();

app.MapGrpcService<UserManagementService>();
app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");

app.Run();
