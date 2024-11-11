class RoundRobinLoadBalancer:
    def __init__(self, servers, circuit_breaker):
        self.servers = servers
        self.circuit_breaker = circuit_breaker
        self.current_server = 0

    def get_server(self):
        for _ in range(len(self.servers)):
            instance = self.servers[self.current_server]
            self.current_server = (self.current_server + 1) % len(self.servers)
            if self.circuit_breaker.is_service_available(instance):
                return instance
        raise Exception("No available instances")
