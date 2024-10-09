from flask import Flask, request, jsonify
import requests
import pybreaker  # type: ignore
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = Flask(__name__)

# Task Timeout
REQUEST_TIMEOUT = 5

# Circuit Breaker
circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)

# Service Discovery
services = {
    "user_service": "http://localhost:5001",
    "chat_service": "http://localhost:5002"
}

# Concurrent tasks limit
executor = ThreadPoolExecutor(max_workers=10)

# Circuit breaker for user service


@circuit_breaker
def call_user_service(path, method="GET", data=None):
    url = f"{services['user_service'][0]}/{path}"
    response = requests.request(
        method, url, json=data, timeout=REQUEST_TIMEOUT)
    return response.json(), response.status_code

# Gateway status endpoint


@app.route("/status")
def status():
    return jsonify({"status": "ok"}), 200

# User Service Status Endpoint (Proxy)


@app.route('/user-service/status', methods=['GET'])
def user_service_status():
    try:
        response = call_user_service("status")
        return jsonify(response)
    except pybreaker.CircuitBreakerError:
        return jsonify({"error": "User service unavailable (circuit open)"}), 503

# Timeouts for Other Requests


@app.route('/user-service/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        response = call_user_service("register", method="POST", data=data)
        return jsonify(response)
    except request.Timeout:
        return jsonify({"error": "User service request timeout"}), 504
    except pybreaker.CircuitBreakerError:
        return jsonify({"error": "User service unavailable (circuit open)"}), 503

# Limiting concurrent tasks using asyncio


@app.route('/chat/send', methods=['POST'])
async def send_message():
    async with asyncio.Semaphore(10):  # Limit concurrent requests to 10
        data = request.get_json()
        response = requests.post(
            f"{services['chat_service'][0]}/send", json=data, timeout=REQUEST_TIMEOUT)
        return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=5000)
