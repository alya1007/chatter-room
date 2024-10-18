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
            response = self.stub.StatusCheck(service_registry_pb2.StatusCheckResponse())
            status = {
                "status": response.status,
                "db_status": response.db_status,
                "uptime": response.uptime,
                "registered_services": response.registered_services
            }

            return status
        except grpc.RpcError as e:
            raise Exception(e.details())
