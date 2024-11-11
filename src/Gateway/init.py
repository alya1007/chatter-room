import redis  # type: ignore
from dotenv import load_dotenv  # type: ignore
import service_registry_client as src  # type: ignore
import load_balancer as lb  # type: ignore
import circuit_breaker as cb  # type: ignore
from flask import Flask
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore
import logging
import os


def initialize():

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    load_dotenv()

    discovery_address = os.getenv("DISCOVERY_ADDRESS")

    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")

    user_service_name = os.getenv("USER_SERVICE_NAME")
    chat_service_name = os.getenv("CHAT_SERVICE_NAME")

    redis_client = redis.StrictRedis(
        host=redis_host, port=redis_port, db=0, decode_responses=True)

    app = Flask(__name__)

    limiter = Limiter(get_remote_address, app=app, default_limits=[
        "5 per minute"])

    registry_client = src.ServiceRegistryClient(discovery_address)

    user_service_addresses = registry_client.discover_services(
        user_service_name)
    chat_service_addresses = registry_client.discover_services(
        chat_service_name)

    user_service_circuit_breaker = cb.CircuitBreaker(3, 5, logger)
    chat_service_circuit_breaker = cb.CircuitBreaker(3, 5, logger)

    user_service_load_balancer = lb.RoundRobinLoadBalancer(
        user_service_addresses, user_service_circuit_breaker)
    chat_service_load_balancer = lb.RoundRobinLoadBalancer(
        chat_service_addresses, chat_service_circuit_breaker)

    print("discovery_address: ", discovery_address)

    return app, redis_client, user_service_load_balancer, chat_service_load_balancer, chat_service_circuit_breaker, user_service_circuit_breaker, limiter, logger, registry_client, user_service_addresses, chat_service_addresses
