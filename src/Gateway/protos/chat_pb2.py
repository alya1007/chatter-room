# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: protos/chat.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'protos/chat.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11protos/chat.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\xab\x01\n\x10\x43hatMessageProto\x12\x11\n\tsender_id\x18\x01 \x01(\t\x12\x13\n\x0breceiver_id\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\x12.\n\ncreated_at\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12.\n\nupdated_at\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xb3\x01\n\x10RoomMessageProto\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07room_id\x18\x02 \x01(\t\x12\x11\n\tsender_id\x18\x03 \x01(\t\x12\x0f\n\x07message\x18\x04 \x01(\t\x12.\n\ncreated_at\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12.\n\nupdated_at\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"T\n\x19SendPrivateMessageRequest\x12\x11\n\tsender_id\x18\x01 \x01(\t\x12\x13\n\x0breceiver_id\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\"-\n\x1aSendPrivateMessageResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"F\n\x1cGetPrivateChatHistoryRequest\x12\x11\n\tsender_id\x18\x01 \x01(\t\x12\x13\n\x0breceiver_id\x18\x02 \x01(\t\"D\n\x1dGetPrivateChatHistoryResponse\x12#\n\x08messages\x18\x01 \x03(\x0b\x32\x11.ChatMessageProto\"O\n\x11\x43reateRoomRequest\x12\x11\n\troom_name\x18\x01 \x01(\t\x12\x12\n\ncreator_id\x18\x02 \x01(\t\x12\x13\n\x0bmembers_ids\x18\x03 \x03(\t\"%\n\x12\x43reateRoomResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"8\n\x14\x41\x64\x64UserToRoomRequest\x12\x0f\n\x07room_id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\"(\n\x15\x41\x64\x64UserToRoomResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"(\n\x15GetRoomHistoryRequest\x12\x0f\n\x07room_id\x18\x01 \x01(\t\"=\n\x16GetRoomHistoryResponse\x12#\n\x08messages\x18\x01 \x03(\x0b\x32\x11.RoomMessageProto\"4\n\x10LeaveRoomRequest\x12\x0f\n\x07room_id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\"$\n\x11LeaveRoomResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"3\n\x0e\x41\x64\x64UserRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\"\"\n\x0f\x41\x64\x64UserResponse\x12\x0f\n\x07message\x18\x01 \x01(\t2\xd7\x03\n\x12\x43hatServiceManager\x12M\n\x12SendPrivateMessage\x12\x1a.SendPrivateMessageRequest\x1a\x1b.SendPrivateMessageResponse\x12V\n\x15GetPrivateChatHistory\x12\x1d.GetPrivateChatHistoryRequest\x1a\x1e.GetPrivateChatHistoryResponse\x12\x35\n\nCreateRoom\x12\x12.CreateRoomRequest\x1a\x13.CreateRoomResponse\x12>\n\rAddUserToRoom\x12\x15.AddUserToRoomRequest\x1a\x16.AddUserToRoomResponse\x12\x41\n\x0eGetRoomHistory\x12\x16.GetRoomHistoryRequest\x1a\x17.GetRoomHistoryResponse\x12\x32\n\tLeaveRoom\x12\x11.LeaveRoomRequest\x1a\x12.LeaveRoomResponse\x12,\n\x07\x41\x64\x64User\x12\x0f.AddUserRequest\x1a\x10.AddUserResponseB\x15\xaa\x02\x12\x43hatService.Protosb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.chat_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\022ChatService.Protos'
  _globals['_CHATMESSAGEPROTO']._serialized_start=55
  _globals['_CHATMESSAGEPROTO']._serialized_end=226
  _globals['_ROOMMESSAGEPROTO']._serialized_start=229
  _globals['_ROOMMESSAGEPROTO']._serialized_end=408
  _globals['_SENDPRIVATEMESSAGEREQUEST']._serialized_start=410
  _globals['_SENDPRIVATEMESSAGEREQUEST']._serialized_end=494
  _globals['_SENDPRIVATEMESSAGERESPONSE']._serialized_start=496
  _globals['_SENDPRIVATEMESSAGERESPONSE']._serialized_end=541
  _globals['_GETPRIVATECHATHISTORYREQUEST']._serialized_start=543
  _globals['_GETPRIVATECHATHISTORYREQUEST']._serialized_end=613
  _globals['_GETPRIVATECHATHISTORYRESPONSE']._serialized_start=615
  _globals['_GETPRIVATECHATHISTORYRESPONSE']._serialized_end=683
  _globals['_CREATEROOMREQUEST']._serialized_start=685
  _globals['_CREATEROOMREQUEST']._serialized_end=764
  _globals['_CREATEROOMRESPONSE']._serialized_start=766
  _globals['_CREATEROOMRESPONSE']._serialized_end=803
  _globals['_ADDUSERTOROOMREQUEST']._serialized_start=805
  _globals['_ADDUSERTOROOMREQUEST']._serialized_end=861
  _globals['_ADDUSERTOROOMRESPONSE']._serialized_start=863
  _globals['_ADDUSERTOROOMRESPONSE']._serialized_end=903
  _globals['_GETROOMHISTORYREQUEST']._serialized_start=905
  _globals['_GETROOMHISTORYREQUEST']._serialized_end=945
  _globals['_GETROOMHISTORYRESPONSE']._serialized_start=947
  _globals['_GETROOMHISTORYRESPONSE']._serialized_end=1008
  _globals['_LEAVEROOMREQUEST']._serialized_start=1010
  _globals['_LEAVEROOMREQUEST']._serialized_end=1062
  _globals['_LEAVEROOMRESPONSE']._serialized_start=1064
  _globals['_LEAVEROOMRESPONSE']._serialized_end=1100
  _globals['_ADDUSERREQUEST']._serialized_start=1102
  _globals['_ADDUSERREQUEST']._serialized_end=1153
  _globals['_ADDUSERRESPONSE']._serialized_start=1155
  _globals['_ADDUSERRESPONSE']._serialized_end=1189
  _globals['_CHATSERVICEMANAGER']._serialized_start=1192
  _globals['_CHATSERVICEMANAGER']._serialized_end=1663
# @@protoc_insertion_point(module_scope)
