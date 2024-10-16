import grpc  # type: ignore
from flask import Flask, jsonify, request

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'protos'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))


import user_pb2_grpc  # type: ignore
import user_pb2  # type: ignore
import chat_pb2_grpc  # type: ignore
import chat_pb2  # type: ignore


import status_codes_translator as code_t # type: ignore

app = Flask(__name__)


services = {
    "user_service": "localhost:5002",
    "chat_service": "localhost:5001"
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
            user_pb2.RegisterUserRequest(username=data["username"], password=data["password"], email=data["email"]))
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())


@app.route('/user-service/login', methods=['POST'])
def login_user():
    data = request.get_json()
    try:
        response = user_service_stub.LoginUser(
            user_pb2.LoginUserRequest(email=data["email"], password=data["password"]))
        return jsonify({"token": response.token})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())

@app.route('/user-service/user/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        response = user_service_stub.GetUserProfile(user_pb2.GetUserProfileRequest(
            user_id=user_id
        ))
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
            chat_pb2.SendPrivateMessageRequest(sender_id=data["sender_id"], receiver_id=data["receiver_id"], message=data["message"]))
        return jsonify({"message": response.message})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), code_t.grpc_status_to_http(e.code())
    


@app.route('/chat-service/private/history', methods=['POST'])
def get_private_chat_history():
    data = request.get_json()
    try:
        response = chat_service_stub.GetPrivateChatHistory(
            chat_pb2.GetPrivateChatHistoryRequest(sender_id=data["sender_id"], receiver_id=data["receiver_id"]))
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


if __name__ == "__main__":
    app.run(port=5000)
