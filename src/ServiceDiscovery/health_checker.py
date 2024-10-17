import grpc # type: ignore
from grpc_health.v1 import health_pb2, health_pb2_grpc # type: ignore

def check_grpc_health(service_address: str):
    with grpc.insecure_channel(service_address) as channel:
        health_stub = health_pb2_grpc.HealthStub(channel)
        health_check_request = health_pb2.HealthCheckRequest()

        try:
            health_response = health_stub.Check(health_check_request)
            if health_response.status == health_pb2.HealthCheckResponse.SERVING:
                return True
            else:
                return False
        except grpc.RpcError as e:
            print(f"Failed to connect to gRPC service.")
