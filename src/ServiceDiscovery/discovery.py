from flask import Flask, request, jsonify
from pymongo import MongoClient  # type: ignore
from dotenv import load_dotenv  # type: ignore
import datetime
import os
from health_checker import check_grpc_health


app = Flask(__name__)


# MongoDB setup
load_dotenv()
mongo_uri = os.getenv('CONNECTION_STRING')
client = MongoClient(mongo_uri)
db = client[os.getenv('DB_NAME')]
collection = db[os.getenv('COLLECTION_NAME')]


discovery_port = os.getenv('PORT')


# Register a new service
@app.route('/register', methods=['POST'])
def register_service():
    data = request.json
    service_name = data.get('service_name')
    service_url = data.get('service_url')

    if not service_name or not service_url:
        return jsonify({'error': 'service_name and service_url are required'}), 400
    
    existing_url = collection.find_one({'service_url': service_url})
    if existing_url:
        return jsonify({'error': 'Service URL already exists'}), 400

    # Insert the new service if it does not already exist
    collection.insert_one({
        'service_name': service_name,
        'service_url': service_url,
        'registered_at': datetime.datetime.utcnow(),
        'last_seen_at': datetime.datetime.utcnow()
    })
    
    return jsonify({'message': f'Service {service_name} registered successfully'}), 200


# Get the location of a service
@app.route('/discover/<service_name>', methods=['GET'])
def discover_service(service_name):
    # find all instances of the service
    services_cursor = collection.find({'service_name': service_name})
    
    services = []

    for service in services_cursor:
        services.append({
            'service_url': service['service_url'],
            'last_seen_at': service['last_seen_at']
        })

    if not services:
        return jsonify({'error': 'Service not found'}), 404
    
    return jsonify({'services': services}), 200


# Update service heartbeat (for health check)
@app.route('/heartbeat', methods=['PUT'])
def heartbeat():
    data = request.json
    service_url = data.get('service_url')

    if not service_url:
        return jsonify({'error': 'service_url is required'}), 400

    healthy = check_grpc_health(service_url)
    
    # Update the last seen time of the service
    collection.update_one({'service_url': service_url}, {'$set': {'last_seen_at': datetime.datetime.utcnow()}})

    if not healthy:
        return jsonify({'error': 'Service is not healthy'}), 400
    

    return jsonify({'message': 'Heartbeat received'}), 200


if __name__ == '__main__':
    app.run(port=discovery_port)
