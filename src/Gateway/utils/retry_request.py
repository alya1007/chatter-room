import grpc  # type: ignore


def retry_request_with_circuit_breaker(
    stub_method, request_data, load_balancer, circuit_breaker, logger, max_retries=3, max_reroutes=1
):
    failed_servers = set()
    reroutes = 0

    while True:
        service_address = load_balancer.get_server()
        circuit_breaker.is_service_available(service_address)

        if service_address in failed_servers:
            logger.info("Skipping " + service_address +
                        " because it is marked as unavailable.")
            continue  # Skip servers already marked as unavailable

        retries = 0

        while retries < max_retries:
            try:
                # Attempt the request
                circuit_breaker.is_service_available(service_address)
                channel = grpc.insecure_channel(service_address)
                response = stub_method(channel, request_data, timeout=5.0)
                logger.info(f"Request made to: {service_address}")
                return response  # Success on first try or retry
            except grpc.RpcError as e:
                recoverable_errors = [
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.INTERNAL,
                ]

                if e.code() not in recoverable_errors:
                    raise e
                logger.error("Attempt: " + str(retries + 1) +
                             " - failed on " + service_address + " with error: " + str(e.details()))
                retries += 1

                # Mark server as failed if max retries are reached
                if retries >= max_retries:
                    logger.error("Server " + service_address +
                                 " marked as unavailable after repeated failures.")
                    circuit_breaker.record_failure(service_address)
                    failed_servers.add(service_address)

        reroutes += 1
        # If reroutes exceeded the limit, break
        if reroutes > max_reroutes:
            break

    # If we reach here, reroutes exceeded the limit
    logger.error(
        "Maximum reroutes exceeded. All servers failed after retries.")
    raise Exception(
        "Maximum reroutes exceeded. All servers failed after retries.")
