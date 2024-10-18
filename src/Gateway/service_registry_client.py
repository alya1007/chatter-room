import grpc  # type: ignore
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), 'protos'))
import service_registry_pb2_grpc  # type: ignore
import service_registry_pb2  # type: ignore


class ServiceRegistryClient:
    def __init__(self, registry_url):
        self.channel = grpc.insecure_channel(registry_url)
        self.stub = service_registry_pb2_grpc.ServiceRegistryStub(self.channel)

    def discover_service(self, service_name):
        try:
            response = self.stub.DiscoverService(
                service_registry_pb2.DiscoverServiceRequest(
                    service_name=service_name
                )
            )

            return response.service_url
        except grpc.RpcError as e:
            raise Exception(e.details())
