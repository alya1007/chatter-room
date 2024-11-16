import grpc  # type: ignore
from concurrent import futures
import datetime
from pymongo import MongoClient  # type: ignore
import os
import protos.service_registry_pb2 as service_registry_pb2  # type: ignore
import protos.service_registry_pb2_grpc as service_registry_pb2_grpc  # type: ignore
from dotenv import load_dotenv  # type: ignore
from health_checker import check_grpc_health
import time

# MongoDB setup
load_dotenv()
mongo_uri = os.getenv('CONNECTION_STRING')
client = MongoClient(mongo_uri)
db = client[os.getenv('DB_NAME')]
collection = db[os.getenv('COLLECTION_NAME')]


start_time = time.time()


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

        collection.update_one(
            {"service_url": service_url},
            {
                "$set": {
                    "service_name": service_name,
                    "registered_at": datetime.datetime.utcnow(),
                    "last_seen_at": datetime.datetime.utcnow(),
                }
            },
            upsert=True
        )

        return service_registry_pb2.RegisterServiceResponse(
            success=True,
            message=f"Service {service_name} registered successfully"
        )

    # Get the location of a service
    def DiscoverService(self, request, context):
        service_name = request.service_name

        # Find all instances of the service
        services_cursor = collection.find({'service_name': service_name})
        services_urls = []

        for service in services_cursor:
            services_urls.append(service['service_url'])

        if not services_urls:
            return service_registry_pb2.DiscoverServiceResponse()

        # TO DO: Implement load balancing
        # for now, return the first service found
        return service_registry_pb2.DiscoverServiceResponse(
            service_url=services_urls[0]
        )

    # Update service heartbeat
    def Heartbeat(self, request, context):
        service_url = request.service_url

        if not service_url:
            return service_registry_pb2.HeartbeatResponse(
                success=False,
                message="service_url is required"
            )

        healthy = check_grpc_health(service_url)

        if healthy:
            # Update the last seen time of the service if it's healthy
            collection.update_one({'service_url': service_url}, {
                '$set': {'last_seen_at': datetime.datetime.utcnow()}})
            return service_registry_pb2.HeartbeatResponse(
                success=True,
                message="Heartbeat received"
            )
        else:
            # search for the service in the database
            service = collection.find_one({'service_url': service_url})
            if not service:
                return service_registry_pb2.HeartbeatResponse(
                    success=False,
                    message="Service not found"
                )
            else:
                # Remove the service from the database if it's not healthy
                collection.delete_one({'service_url': service_url})
                return service_registry_pb2.HeartbeatResponse(
                    success=False,
                    message="Service is not healthy and has been removed"
                )

    def StatusCheck(self, request, context):
        # check the status of database connection
        db_response = client.server_info()
        db_status = "Connected" if db_response else "Not connected"

        # check number of services registered
        services_count = collection.count_documents({})

        return service_registry_pb2.StatusCheckResponse(
            status="Service registry is running",
            db_status=db_status,
            uptime=str(round(time.time() - start_time, 2)),
            registered_services=str(services_count)
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
