import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'protos'))

import grpc  # type: ignore
from concurrent import futures
import datetime
from pymongo import MongoClient  # type: ignore
import os
import service_registry_pb2  # type: ignore
import service_registry_pb2_grpc  # type: ignore
from dotenv import load_dotenv  # type: ignore
from health_checker import check_grpc_health

# MongoDB setup
load_dotenv()
mongo_uri = os.getenv('CONNECTION_STRING')
client = MongoClient(mongo_uri)
db = client[os.getenv('DB_NAME')]
collection = db[os.getenv('COLLECTION_NAME')]


class ServiceRegistryServicer(service_registry_pb2_grpc.ServiceRegistryServicer):
    # Register a new service
    def RegisterService(self, request, context):
        service_name = request.service_name
        service_url = request.service_url

        if not service_name or not service_url:
            return service_registry_pb2.RegisterServiceResponse(
                success=False,
                message="service_name and service_url are required"
            )

        existing_url = collection.find_one({'service_url': service_url})
        if existing_url:
            return service_registry_pb2.RegisterServiceResponse(
                success=False,
                message="Service URL already exists"
            )

        # Insert the new service if it does not already exist
        collection.insert_one({
            'service_name': service_name,
            'service_url': service_url,
            'registered_at': datetime.datetime.utcnow(),
            'last_seen_at': datetime.datetime.utcnow()
        })

        return service_registry_pb2.RegisterServiceResponse(
            success=True,
            message=f"Service {service_name} registered successfully"
        )

    # Get the location of a service
    def DiscoverService(self, request, context):
        service_name = request.service_name

        # Find all instances of the service
        services_cursor = collection.find({'service_name': service_name})
        services = []

        for service in services_cursor:
            services.append(service_registry_pb2.Service(
                service_url=service['service_url'],
                # Convert to string for gRPC
                last_seen_at=service['last_seen_at'].isoformat()
            ))

        if not services:
            return service_registry_pb2.DiscoverServiceResponse()

        return service_registry_pb2.DiscoverServiceResponse(services=services)

    # Update service heartbeat
    def Heartbeat(self, request, context):
        service_url = request.service_url

        if not service_url:
            return service_registry_pb2.HeartbeatResponse(
                success=False,
                message="service_url is required"
            )

        healthy = check_grpc_health(service_url)

        # Update the last seen time of the service
        collection.update_one({'service_url': service_url}, {
                              '$set': {'last_seen_at': datetime.datetime.utcnow()}})

        if not healthy:
            return service_registry_pb2.HeartbeatResponse(
                success=False,
                message="Service is not healthy"
            )

        return service_registry_pb2.HeartbeatResponse(
            success=True,
            message="Heartbeat received"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_registry_pb2_grpc.add_ServiceRegistryServicer_to_server(
        ServiceRegistryServicer(), server)

    discovery_port = os.getenv('PORT')
    server.add_insecure_port(f'[::]:{discovery_port}')
    server.start()
    print(f"Service registry running on port {discovery_port}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
