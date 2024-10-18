using Grpc.Core;
using Grpc.Net.Client;
using UserService.Protos;


namespace UserService.Services;

public class ServiceRegistryClient
{
    private readonly ServiceRegistry.ServiceRegistryClient _client;

    public ServiceRegistryClient(string serviceDiscoveryAddress)
    {
        var channel = GrpcChannel.ForAddress(serviceDiscoveryAddress, new GrpcChannelOptions
        {
            Credentials = ChannelCredentials.Insecure
        });
        _client = new ServiceRegistry.ServiceRegistryClient(channel);
    }

    public async Task RegisterServiceAsync(string serviceName, string serviceUrl)
    {
        try
        {
            var request = new RegisterServiceRequest
            {
                ServiceName = serviceName,
                ServiceUrl = serviceUrl
            };
            await _client.RegisterServiceAsync(request);
        }
        catch (RpcException e)
        {
            throw new Exception($"Failed to register service {serviceName}. {e.Message}");
        }
    }

    public async Task<string> DiscoverServiceAsync(string serviceName)
    {
        try
        {
            var request = new DiscoverServiceRequest
            {
                ServiceName = serviceName
            };
            var response = await _client.DiscoverServiceAsync(request);
            return response.ServiceUrl;
        }
        catch (RpcException e)
        {
            throw new Exception($"Failed to discover service {serviceName}. {e.Message}");
        }
    }

}