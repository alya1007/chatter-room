import time


class CircuitBreaker:
    def __init__(self, timeout_limit, logger):
        self.failures = {}
        self.cooldown_period = timeout_limit * 3.5
        self.logger = logger

    def record_failure(self, service_url):

        current_time = time.time()

        if service_url not in self.failures:
            self.failures[service_url] = current_time
            self.logger.info("Service ", service_url, " marked as unavailable")
        else:
            self.logger.info("Service ", service_url, " still unavailable")

        return self.failures[service_url]

    def is_service_available(self, service_url):
        if service_url not in self.failures:
            return True

        last_failure_time = self.failures[service_url]
        current_time = time.time()

        if current_time - last_failure_time > self.cooldown_period:
            self.logger.info("Service ", service_url, " is available again")
            del self.failures[service_url]  # reset the failure count
            return True

        self.logger.info("Service ", service_url, " still unavailable")
        return False
