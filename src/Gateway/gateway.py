import json
from flask import jsonify, request
import grpc  # type: ignore
import protos.user_pb2_grpc as user_pb2_grpc  # type: ignore
import protos.user_pb2 as user_pb2  # type: ignore
import protos.chat_pb2_grpc as chat_pb2_grpc  # type: ignore
import protos.chat_pb2 as chat_pb2  # type: ignore
import utils.status_codes_translator as code_t  # type: ignore
import utils.retry_request as retry  # type: ignore
import time
import utils.health_checker as health_checker  # type: ignore
from init import Initializer  # type: ignore


start_time = time.time()


context = Initializer()
app = context.app


@app.route("/user-service/register", methods=["POST"])
def register_user():
    data = request.get_json()
    try:
        # Step 1: Register user in User Service
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: user_pb2_grpc.UserServiceManagerStub(channel).RegisterUser(
                request, timeout=timeout),
            request_data=user_pb2.RegisterUserRequest(
                username=data["username"], email=data["email"], password=data["password"]),
            load_balancer=context.user_service_load_balancer,
            circuit_breaker=context.user_service_circuit_breaker,
            logger=context.logger
        )
        response_user_id = response.user_id

    except grpc.RpcError as e:
        # register fails
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())

    except Exception as e:
        context.logger.error(f"User Service registration failed: {str(e)}")
        return {"status": "failure", "message": "Failed to register user in User Service"}

    try:
        # Step 2: Add user to Chat Service
        retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: chat_pb2_grpc.ChatServiceManagerStub(channel).AddUser(
                request, timeout=timeout),
            request_data=chat_pb2.AddUserRequest(
                user_id=response_user_id,
                username=data["username"]
            ),
            load_balancer=context.chat_service_load_balancer,
            circuit_breaker=context.chat_service_circuit_breaker,
            logger=context.logger
        )
    except (grpc.RpcError, Exception) as e:
        # roll back User Service
        context.logger.error(
            "Failed to add user to chat service: " + str(e))
        context.logger.info("Rolling back user creation")
        try:
            rollback_response = retry.retry_request_with_circuit_breaker(
                stub_method=lambda channel, request, timeout: user_pb2_grpc.UserServiceManagerStub(channel).DeleteUser(
                    request, timeout=timeout),
                request_data=user_pb2.DeleteUserRequest(
                    user_id=response_user_id
                ),
                load_balancer=context.user_service_load_balancer,
                circuit_breaker=context.user_service_circuit_breaker,
                logger=context.logger
            )
            context.logger.info("User rolled back successfully: " +
                                rollback_response.message)
        except (grpc.RpcError, Exception) as rollback_error:
            context.logger.error(
                "Failed to roll back user: " + str(rollback_error))
            return {"status": "failure", "message": "Failed to propagate user to Chat Service, and rollback also failed"}

        return {"status": "failure", "message": "Failed to propagate user to Chat Service"}

    # Step 3: If everything succeeds, return success
    return {"status": "success", "message": "User registered successfully"}


@ app.route('/user-service/login', methods=['POST'])
def login_user():
    data = request.get_json()
    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: user_pb2_grpc.UserServiceManagerStub(channel).LoginUser(
                request, timeout=timeout),
            request_data=user_pb2.LoginUserRequest(
                email=data["email"], password=data["password"]),
            load_balancer=context.user_service_load_balancer,
            circuit_breaker=context.user_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"token": response.token})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/user-service/users/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    cache_key = f"user_profile:{user_id}"

    cached_profile = context.redis_client.get(cache_key)
    if cached_profile:
        return json.loads(cached_profile)

    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: user_pb2_grpc.UserServiceManagerStub(channel).GetUserProfile(
                request, timeout=timeout),
            request_data=user_pb2.GetUserProfileRequest(
                user_id=user_id
            ),
            load_balancer=context.user_service_load_balancer,
            circuit_breaker=context.user_service_circuit_breaker,
            logger=context.logger
        )

        user_profile = {
            "username": response.username,
            "email": response.email
        }

        context.redis_client.setex(cache_key, 60, json.dumps(user_profile))
        return jsonify(user_profile)
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/user-service/users/delete', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: user_pb2_grpc.UserServiceManagerStub(channel).DeleteUser(
                request, timeout=timeout),
            request_data=user_pb2.DeleteUserRequest(
                user_id=data["user_id"]
            ),
            load_balancer=context.user_service_load_balancer,
            circuit_breaker=context.user_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/chat-service/private/send', methods=['POST'])
def send_private_message():
    data = request.get_json()
    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: chat_pb2_grpc.ChatServiceManagerStub(channel).SendPrivateMessage(
                request, timeout=timeout),
            request_data=chat_pb2.SendPrivateMessageRequest(
                sender_id=data["sender_id"], receiver_id=data["receiver_id"], message=data["message"]),
            load_balancer=context.chat_service_load_balancer,
            circuit_breaker=context.chat_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/chat-service/private/<receiver_id>', methods=['POST'])
def get_private_chat_history(receiver_id):
    data = request.get_json()
    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: chat_pb2_grpc.ChatServiceManagerStub(channel).GetPrivateChatHistory(
                request, timeout=timeout),
            request_data=chat_pb2.GetPrivateChatHistoryRequest(
                sender_id=data["sender_id"], receiver_id=receiver_id),
            load_balancer=context.chat_service_load_balancer,
            circuit_breaker=context.chat_service_circuit_breaker,
            logger=context.logger
        )
        messages = []
        for message in response.messages:
            messages.append({
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "message": message.message,
                "created_at": message.created_at.ToJsonString(),
                "updated_at": message.updated_at.ToJsonString()
            })
        return jsonify({"messages": messages})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/chat-service/rooms/create', methods=['POST'])
def create_room():
    data = request.get_json()
    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: chat_pb2_grpc.ChatServiceManagerStub(channel).CreateRoom(
                request, timeout=timeout),
            request_data=chat_pb2.CreateRoomRequest(
                room_name=data["room_name"],
                creator_id=data["creator_id"],
                members_ids=data["members_ids"]
            ),
            load_balancer=context.chat_service_load_balancer,
            circuit_breaker=context.chat_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/chat-service/rooms/<room_id>/add', methods=['PUT'])
def add_room_member(room_id):
    data = request.get_json()
    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: chat_pb2_grpc.ChatServiceManagerStub(channel).AddUserToRoom(
                request, timeout=timeout),
            request_data=chat_pb2.AddUserToRoomRequest(
                room_id=room_id,
                user_id=data["user_id"]
            ),
            load_balancer=context.chat_service_load_balancer,
            circuit_breaker=context.chat_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/chat-service/rooms/<room_id>', methods=['GET'])
def get_room_chat_history(room_id):
    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: chat_pb2_grpc.ChatServiceManagerStub(channel).GetRoomHistory(
                request, timeout=timeout),
            request_data=chat_pb2.GetRoomHistoryRequest(
                room_id=room_id
            ),
            load_balancer=context.chat_service_load_balancer,
            circuit_breaker=context.chat_service_circuit_breaker,
            logger=context.logger
        )
        messages = []
        for message in response.messages:
            messages.append({
                "id": message.id,
                "room_id": message.room_id,
                "sender_id": message.sender_id,
                "message": message.message,
                "created_at": message.created_at.ToJsonString(),
                "updated_at": message.updated_at.ToJsonString()
            })

        return jsonify({"messages": messages})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/chat-service/rooms/<room_id>/leave', methods=['PUT'])
def leave_room(room_id):
    data = request.get_json()
    try:
        response = retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: chat_pb2_grpc.ChatServiceManagerStub(channel).LeaveRoom(
                request, timeout=timeout),
            request_data=chat_pb2.LeaveRoomRequest(
                room_id=room_id,
                user_id=data["user_id"]
            ),
            load_balancer=context.chat_service_load_balancer,
            circuit_breaker=context.chat_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/status', methods=['GET'])
def gateway_status():
    uptime = time.time() - start_time

    status = {
        "gateway": "healthy",
        "uptime_seconds": round(uptime, 2)
    }

    return jsonify(status), 200


@ app.route('/discovery/status', methods=['GET'])
def discovery_status():
    return jsonify({"status": context.registry_client.status()})


@ app.route('/user-service/status', methods=['GET'])
def user_service_status():
    statuses = [user_service_address for user_service_address in context.user_service_addresses if health_checker.check_grpc_health(
        user_service_address)]
    return jsonify({"status": statuses}) if statuses else jsonify({"status": "unhealthy"})


@ app.route('/chat-service/status', methods=['GET'])
def chat_service_status():
    statuses = [chat_service_address for chat_service_address in context.chat_service_addresses if health_checker.check_grpc_health(
        chat_service_address)]
    return jsonify({"status": statuses}) if statuses else jsonify({"status": "unhealthy"})


@ app.route('/timeout', methods=['GET'])
def timeout():
    empty = user_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
    try:
        retry.retry_request_with_circuit_breaker(
            stub_method=lambda channel, request, timeout: user_pb2_grpc.UserServiceManagerStub(channel).Timeout(
                request, timeout=timeout),
            request_data=empty,
            load_balancer=context.user_service_load_balancer,
            circuit_breaker=context.user_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": "Test Timeout"})

    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
