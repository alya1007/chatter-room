using Grpc.Core;
using Grpc.Net.Client;
using ChatService.Protos;


namespace ChatService.Services;

public class UserManagementClient
{
    private readonly UserServiceManager.UserServiceManagerClient _client;

    public UserManagementClient(string userServiceAddress)
    {
        var channel = GrpcChannel.ForAddress(userServiceAddress, new GrpcChannelOptions
        {
            Credentials = ChannelCredentials.Insecure
        });
        _client = new UserServiceManager.UserServiceManagerClient(channel);
    }

    public async Task GetUserProfileAsync(string userId)
    {
        try
        {
            var request = new GetUserProfileRequest { UserId = userId };
            await _client.GetUserProfileAsync(request);
        }
        catch (RpcException e)
        {
            throw new RpcException(new Status(StatusCode.NotFound, $"User {userId} not found"));
        }
    }

}