# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from protos import user_pb2 as protos_dot_user__pb2

GRPC_GENERATED_VERSION = '1.67.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in protos/user_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class UserServiceManagerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterUser = channel.unary_unary(
                '/UserServiceManager/RegisterUser',
                request_serializer=protos_dot_user__pb2.RegisterUserRequest.SerializeToString,
                response_deserializer=protos_dot_user__pb2.RegisterUserResponse.FromString,
                _registered_method=True)
        self.LoginUser = channel.unary_unary(
                '/UserServiceManager/LoginUser',
                request_serializer=protos_dot_user__pb2.LoginUserRequest.SerializeToString,
                response_deserializer=protos_dot_user__pb2.LoginUserResponse.FromString,
                _registered_method=True)
        self.GetUserProfile = channel.unary_unary(
                '/UserServiceManager/GetUserProfile',
                request_serializer=protos_dot_user__pb2.GetUserProfileRequest.SerializeToString,
                response_deserializer=protos_dot_user__pb2.GetUserProfileResponse.FromString,
                _registered_method=True)


class UserServiceManagerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RegisterUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LoginUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUserProfile(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserServiceManagerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RegisterUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterUser,
                    request_deserializer=protos_dot_user__pb2.RegisterUserRequest.FromString,
                    response_serializer=protos_dot_user__pb2.RegisterUserResponse.SerializeToString,
            ),
            'LoginUser': grpc.unary_unary_rpc_method_handler(
                    servicer.LoginUser,
                    request_deserializer=protos_dot_user__pb2.LoginUserRequest.FromString,
                    response_serializer=protos_dot_user__pb2.LoginUserResponse.SerializeToString,
            ),
            'GetUserProfile': grpc.unary_unary_rpc_method_handler(
                    servicer.GetUserProfile,
                    request_deserializer=protos_dot_user__pb2.GetUserProfileRequest.FromString,
                    response_serializer=protos_dot_user__pb2.GetUserProfileResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'UserServiceManager', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('UserServiceManager', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class UserServiceManager(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RegisterUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/UserServiceManager/RegisterUser',
            protos_dot_user__pb2.RegisterUserRequest.SerializeToString,
            protos_dot_user__pb2.RegisterUserResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def LoginUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/UserServiceManager/LoginUser',
            protos_dot_user__pb2.LoginUserRequest.SerializeToString,
            protos_dot_user__pb2.LoginUserResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetUserProfile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/UserServiceManager/GetUserProfile',
            protos_dot_user__pb2.GetUserProfileRequest.SerializeToString,
            protos_dot_user__pb2.GetUserProfileResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)