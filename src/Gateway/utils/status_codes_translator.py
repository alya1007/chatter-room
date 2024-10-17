import grpc # type: ignore


grpc_to_http_status_codes = {
    grpc.StatusCode.INVALID_ARGUMENT: 400,
    grpc.StatusCode.NOT_FOUND: 404,
    grpc.StatusCode.ALREADY_EXISTS: 409,
    grpc.StatusCode.PERMISSION_DENIED: 403,
    grpc.StatusCode.UNAUTHENTICATED: 401,
    grpc.StatusCode.UNIMPLEMENTED: 501,
    grpc.StatusCode.DEADLINE_EXCEEDED: 408,
    grpc.StatusCode.INTERNAL: 500
}


def grpc_status_to_http(status: grpc.StatusCode) -> int:
    return grpc_to_http_status_codes.get(status, 500)


