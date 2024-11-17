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


def get_user_service_stub():
    user_service_address = context.user_service_load_balancer.get_server()
    context.logger.info("Request to user service: ", user_service_address)
    user_channel = grpc.insecure_channel(user_service_address)
    return user_pb2_grpc.UserServiceManagerStub(user_channel), user_service_address


def get_chat_service_stub():
    chat_service_address = context.chat_service_load_balancer.get_server()
    context.logger.info("Request to chat service: ", chat_service_address)
    chat_channel = grpc.insecure_channel(chat_service_address)
    return chat_pb2_grpc.ChatServiceManagerStub(chat_channel), chat_service_address


@app.route("/user-service/register", methods=["POST"])
def register_user():
    data = request.get_json()
    try:
        user_service_stub, user_service_address = get_user_service_stub()
        response = retry.retry_request_with_circuit_breaker(
            stub_method=user_service_stub.RegisterUser,
            request_data=user_pb2.RegisterUserRequest(
                username=data["username"], email=data["email"], password=data["password"]),
            service_address=user_service_address,
            circuit_breaker=context.user_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/user-service/login', methods=['POST'])
def login_user():
    data = request.get_json()
    try:
        user_service_stub, user_service_address = get_user_service_stub()
        response = retry.retry_request_with_circuit_breaker(
            stub_method=user_service_stub.LoginUser,
            request_data=user_pb2.LoginUserRequest(
                email=data["email"], password=data["password"]),
            service_address=user_service_address,
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
        user_service_stub, user_service_address = get_user_service_stub()

        response = retry.retry_request_with_circuit_breaker(
            stub_method=user_service_stub.GetUserProfile,
            request_data=user_pb2.GetUserProfileRequest(
                user_id=user_id
            ),
            service_address=user_service_address,
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


@ app.route('/chat-service/private/send', methods=['POST'])
def send_private_message():
    data = request.get_json()
    try:
        chat_service_stub, chat_service_address = get_chat_service_stub()
        response = retry.retry_request_with_circuit_breaker(
            stub_method=chat_service_stub.SendPrivateMessage,
            request_data=chat_pb2.SendPrivateMessageRequest(
                sender_id=data["sender_id"], receiver_id=data["receiver_id"], message=data["message"]),
            service_address=chat_service_address,
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
        chat_service_stub, chat_service_address = get_chat_service_stub()
        response = retry.retry_request_with_circuit_breaker(
            stub_method=chat_service_stub.GetPrivateChatHistory,
            request_data=chat_pb2.GetPrivateChatHistoryRequest(
                sender_id=data["sender_id"], receiver_id=receiver_id),
            service_address=chat_service_address,
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
        chat_service_stub, chat_service_address = get_chat_service_stub()
        response = retry.retry_request_with_circuit_breaker(
            stub_method=chat_service_stub.CreateRoom,
            request_data=chat_pb2.CreateRoomRequest(
                room_name=data["room_name"],
                creator_id=data["creator_id"],
                members_ids=data["members_ids"]
            ),
            service_address=chat_service_address,
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
        chat_service_stub, chat_service_address = get_chat_service_stub()
        response = retry.retry_request_with_circuit_breaker(
            stub_method=chat_service_stub.AddUserToRoom,
            request_data=chat_pb2.AddUserToRoomRequest(
                room_id=room_id,
                user_id=data["user_id"]
            ),
            service_address=chat_service_address,
            circuit_breaker=context.chat_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@ app.route('/chat-service/rooms/<room_id>', methods=['GET'])
def get_room_chat_history(room_id):
    try:
        chat_service_stub, chat_service_address = get_chat_service_stub()
        response = retry.retry_request_with_circuit_breaker(
            stub_method=chat_service_stub.GetRoomHistory,
            request_data=chat_pb2.GetRoomHistoryRequest(
                room_id=room_id
            ),
            service_address=chat_service_address,
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
        chat_service_stub, chat_service_address = get_chat_service_stub()
        response = retry.retry_request_with_circuit_breaker(
            stub_method=chat_service_stub.LeaveRoom,
            request_data=chat_pb2.LeaveRoomRequest(
                room_id=room_id,
                user_id=data["user_id"]
            ),
            service_address=chat_service_address,
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
        user_service_stub, user_service_address = get_user_service_stub()
        retry.retry_request_with_circuit_breaker(
            stub_method=user_service_stub.Timeout,
            request_data=empty,
            service_address=user_service_address,
            circuit_breaker=context.user_service_circuit_breaker,
            logger=context.logger
        )
        return jsonify({"message": "Test Timeout"})

    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
