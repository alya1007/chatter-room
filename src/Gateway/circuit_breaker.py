import time


class CircuitBreaker:
    def __init__(self, threshold, timeout_limit, logger):
        self.failures = {}
        self.threshold = threshold
        self.cooldown_period = timeout_limit * 3.5
        self.logger = logger

    def record_failure(self, service_url):

        current_time = time.time()

        if service_url not in self.failures:
            self.failures[service_url] = [0, current_time]

        self.failures[service_url][0] += 1
        self.failures[service_url][1] = current_time

        if self.failures[service_url][0] >= self.threshold:
            self.logger.error("Service ", service_url, " triggered CB")

            return False  # Circuit is now open

        return True

    def is_service_available(self, service_url):
        if service_url not in self.failures:
            return True

        failure_count, last_failure_time = self.failures[service_url]

        if failure_count >= self.threshold:
            if time.time() - last_failure_time > self.cooldown_period:
                self.logger.info("Cd period for ", service_url, " expired")
                self.reset_service(service_url)
                return True
            return False  # service is still marked as unavailable

        return True  # service is available

    def reset_service(self, service_url):
        if service_url in self.failures:
            del self.failures[service_url]
