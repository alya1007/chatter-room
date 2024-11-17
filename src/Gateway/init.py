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


class Initializer:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        load_dotenv()
        self.discovery_address = os.getenv("DISCOVERY_ADDRESS")
        self.redis_host = os.getenv("REDIS_HOST")
        self.redis_port = os.getenv("REDIS_PORT")
        self.user_service_name = os.getenv("USER_SERVICE_NAME")
        self.chat_service_name = os.getenv("CHAT_SERVICE_NAME")
        self.redis_client = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, db=0, decode_responses=True)
        self.app = Flask(__name__)
        self.limiter = Limiter(get_remote_address, app=self.app, default_limits=[
            "500 per minute"])
        self.registry_client = src.ServiceRegistryClient(
            self.discovery_address)
        self.user_service_addresses = self.registry_client.discover_services(
            self.user_service_name)
        self.chat_service_addresses = self.registry_client.discover_services(
            self.chat_service_name)
        self.user_service_circuit_breaker = cb.CircuitBreaker(
            3, 5, self.logger)
        self.chat_service_circuit_breaker = cb.CircuitBreaker(
            3, 5, self.logger)
        self.user_service_load_balancer = lb.RoundRobinLoadBalancer(
            self.user_service_addresses, self.user_service_circuit_breaker)
        self.chat_service_load_balancer = lb.RoundRobinLoadBalancer(
            self.chat_service_addresses, self.chat_service_circuit_breaker)
