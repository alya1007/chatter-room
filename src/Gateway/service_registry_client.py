import grpc  # type: ignore
import protos.service_registry_pb2 as service_registry_pb2  # type: ignore
import protos.service_registry_pb2_grpc as service_registry_pb2_grpc  # type: ignore


class ServiceRegistryClient:
    def __init__(self, registry_url):
        self.channel = grpc.insecure_channel(registry_url)
        self.stub = service_registry_pb2_grpc.ServiceRegistryStub(self.channel)

    def discover_services(self, service_name):
        try:
            response = self.stub.DiscoverServices(
                service_registry_pb2.DiscoverServicesRequest(
                    service_name=service_name
                )
            )

            return response.service_urls
        except grpc.RpcError as e:
            raise Exception(e.details())

    def heartbeat(self, service_url):
        try:
            response = self.stub.Heartbeat(
                service_registry_pb2.HeartbeatRequest(
                    service_url=service_url
                )
            )
            return response.message
        except grpc.RpcError as e:
            raise Exception(e.details())

    def status(self):
        try:
            response = self.stub.StatusCheck(
                service_registry_pb2.StatusCheckResponse())
            status = {
                "status": response.status,
                "db_status": response.db_status,
                "uptime": response.uptime,
                "registered_services": response.registered_services
            }

            return status
        except grpc.RpcError as e:
            raise Exception(e.details())
