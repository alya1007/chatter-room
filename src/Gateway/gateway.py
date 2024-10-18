import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'protos'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))


from flask_limiter.util import get_remote_address  # type: ignore
from flask_limiter import Limiter  # type: ignore
import health_checker  # type: ignore
import time
import status_codes_translator as code_t  # type: ignore
import chat_pb2  # type: ignore
import chat_pb2_grpc  # type: ignore
import user_pb2  # type: ignore
import user_pb2_grpc  # type: ignore
import grpc  # type: ignore
from flask import Flask, jsonify, request
import service_registry_client as src  # type: ignore
from dotenv import load_dotenv  # type: ignore


start_time = time.time()


load_dotenv()
service_discovery_address = os.getenv('SERVICE_DISCOVERY_ADDRESS')


app = Flask(__name__)


limiter = Limiter(get_remote_address, app=app, default_limits=[
                  "5 per minute"])


registry_client = src.ServiceRegistryClient(service_discovery_address)


services = {
    "user_service": registry_client.discover_service("user_service"),
    "chat_service": registry_client.discover_service("chat_service")
}


user_channel = grpc.insecure_channel(services["user_service"])
chat_channel = grpc.insecure_channel(services["chat_service"])

user_service_stub = user_pb2_grpc.UserServiceManagerStub(user_channel)
chat_service_stub = chat_pb2_grpc.ChatServiceManagerStub(chat_channel)


@app.route("/user-service/register", methods=["POST"])
def register_user():
    data = request.get_json()
    try:
        response = user_service_stub.RegisterUser(
            user_pb2.RegisterUserRequest(
                username=data["username"], password=data["password"], email=data["email"]),
            timeout=5.0
        )
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/user-service/login', methods=['POST'])
def login_user():
    data = request.get_json()
    try:
        response = user_service_stub.LoginUser(
            user_pb2.LoginUserRequest(email=data["email"], password=data["password"]), timeout=5.0)
        return jsonify({"token": response.token})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/user-service/user/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        response = user_service_stub.GetUserProfile(user_pb2.GetUserProfileRequest(
            user_id=user_id
        ), timeout=5.0)
        return jsonify({
            "username": response.username,
            "email": response.email
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/chat-service/private/send', methods=['POST'])
def send_private_message():
    data = request.get_json()
    try:
        response = chat_service_stub.SendPrivateMessage(
            chat_pb2.SendPrivateMessageRequest(sender_id=data["sender_id"], receiver_id=data["receiver_id"], message=data["message"]), timeout=5.0)
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/chat-service/private/<receiver_id>', methods=['POST'])
def get_private_chat_history(receiver_id):
    data = request.get_json()
    try:
        response = chat_service_stub.GetPrivateChatHistory(
            chat_pb2.GetPrivateChatHistoryRequest(sender_id=data["sender_id"], receiver_id=receiver_id), timeout=5.0)
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


@app.route('/chat-service/rooms/create', methods=['POST'])
def create_room():
    data = request.get_json()
    try:
        response = chat_service_stub.CreateRoom(
            chat_pb2.CreateRoomRequest(
                room_name=data["room_name"],
                creator_id=data["creator_id"],
                members_ids=data["members_ids"]
            ), timeout=5.0)
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/chat-service/rooms/<room_id>/add', methods=['PUT'])
def add_room_member(room_id):
    data = request.get_json()
    try:
        response = chat_service_stub.AddUserToRoom(
            chat_pb2.AddUserToRoomRequest(
                room_id=room_id,
                user_id=data["user_id"]
            ), timeout=5.0)
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/chat-service/rooms/<room_id>/send', methods=['POST'])
def send_room_message(room_id):
    data = request.get_json()
    try:
        response = chat_service_stub.SendRoomMessage(
            chat_pb2.SendRoomMessageRequest(
                room_id=room_id,
                sender_id=data["sender_id"],
                message=data["message"]
            ), timeout=5.0)
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/chat-service/rooms/<room_id>', methods=['GET'])
def get_room_chat_history(room_id):
    try:
        response = chat_service_stub.GetRoomHistory(
            chat_pb2.GetRoomHistoryRequest(
                room_id=room_id
            ), timeout=5.0)
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


@app.route('/chat-service/rooms/<room_id>/leave', methods=['PUT'])
def leave_room(room_id):
    data = request.get_json()
    try:
        response = chat_service_stub.LeaveRoom(
            chat_pb2.LeaveRoomRequest(
                room_id=room_id,
                user_id=data["user_id"]
            ), timeout=5.0)
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/status', methods=['GET'])
def gateway_status():
    uptime = time.time() - start_time

    status = {
        "gateway": "healthy",
        "uptime_seconds": round(uptime, 2),
        "user_service": registry_client.heartbeat(services["user_service"]),
        "chat_service": registry_client.heartbeat(services["chat_service"])
    }

    return jsonify(status), 200


@app.route('/discovery/status', methods=['GET'])
def discovery_status():
    return jsonify({"status": registry_client.status()})


@app.route('/user-service/status', methods=['GET'])
def user_service_status():
    return jsonify({"status": "healthy"}) if health_checker.check_grpc_health(services["user_service"]) else jsonify({"status": "unhealthy"})


@app.route('/chat-service/status', methods=['GET'])
def chat_service_status():
    return jsonify({"status": "healthy"}) if health_checker.check_grpc_health(services["chat_service"]) else jsonify({"status": "unhealthy"})


if __name__ == "__main__":
    app.run(port=5000)
