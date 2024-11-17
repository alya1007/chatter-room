import grpc  # type: ignore


def retry_request_with_circuit_breaker(
    stub_method, request_data, service_address, circuit_breaker, logger, max_retries=3
):
    retries = 0

    while retries < max_retries:
        try:
            response = stub_method(request_data, timeout=5.0)
            return response  # Success on first try or retry
        except grpc.RpcError as e:
            recoverable_errors = [
                grpc.StatusCode.DEADLINE_EXCEEDED,
                grpc.StatusCode.UNAVAILABLE,
            ]

            if e.code() not in recoverable_errors:
                raise e

            logger.error("Attempt " + str(retries + 1) + "failed for " +
                         service_address + ": " + e.details() + "(gRPC Code: " + str(e.code()) + ")")

            # Record the failure in the Circuit Breaker
            circuit_opened = not circuit_breaker.record_failure(
                service_address)

            if circuit_opened:
                logger.error(service_address +
                             "is now unavailable due to repeated failures.")
                raise Exception(f"{service_address} is now unavailable.")

            retries += 1

            if retries >= max_retries:
                logger.error("All " + str(max_retries) + "retries failed for " + service_address +
                             ". Last error: " + e.details() + "(gRPC Code: " + str(e.code()) + ")")
                raise e  # Re-raise the original exception
