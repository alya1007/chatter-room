using Grpc.Core;
using Grpc.Net.Client;
using ChatService.Protos;


namespace ChatService.Services;

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
            var request = new RegisterServiceRequest { ServiceName = serviceName, ServiceUrl = serviceUrl };
            await _client.RegisterServiceAsync(request);
        }
        catch (RpcException e)
        {
            throw new Exception($"Failed to register service {serviceName} with URL {serviceUrl}. {e.Message}");
        }
    }

    public async Task<string> DiscoverServicesAsync(string serviceName)
    {
        try
        {
            var request = new DiscoverServicesRequest
            {
                ServiceName = serviceName
            };
            var response = await _client.DiscoverServicesAsync(request);
            return response.ServiceUrls[0];
        }
        catch (RpcException e)
        {
            throw new Exception($"Failed to discover services of {serviceName}. {e.Message}");
        }
    }

}