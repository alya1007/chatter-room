using Grpc.Core;
using ChatService.Protos;
using ChatService.Models;
using ChatService.Data;
using MongoDB.Driver;
using System.Threading;

namespace ChatService.Services;
public class ChatManagementService : ChatServiceManager.ChatServiceManagerBase
{
    private readonly ChatServiceDbContext _dbContext;
    private readonly UserManagementClient _userManagementClient;
    public ChatManagementService(ChatServiceDbContext dbContext, UserManagementClient userManagementClient)
    {
        _dbContext = dbContext;
        _userManagementClient = userManagementClient;
    }

    public override async Task<SendPrivateMessageResponse> SendPrivateMessage(SendPrivateMessageRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.SenderId) ||
                string.IsNullOrWhiteSpace(request.ReceiverId) ||
                string.IsNullOrWhiteSpace(request.Message))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "All fields (SenderId, ReceiverId, Message) are required."));
            }

            await _userManagementClient.GetUserProfileAsync(request.SenderId);
            await _userManagementClient.GetUserProfileAsync(request.ReceiverId);

            var message = new ChatMessage
            {
                SenderId = request.SenderId,
                ReceiverId = request.ReceiverId,
                Message = request.Message,
                CreatedAt = DateTime.Now,
                UpdatedAt = DateTime.Now
            };

            await _dbContext.PrivateMessages.InsertOneAsync(message);
            return new SendPrivateMessageResponse { Message = $"User {message.SenderId} sent message to user {message.ReceiverId}: {message.Message}" };
        }
        catch (RpcException)
        {
            throw;
        }
        catch (System.Exception)
        {
            throw new RpcException(new Status(StatusCode.Internal, "An error occurred while sending the message."));
        }
    }

    public override async Task<GetPrivateChatHistoryResponse> GetPrivateChatHistory(GetPrivateChatHistoryRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.SenderId) || string.IsNullOrWhiteSpace(request.ReceiverId))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Both SenderId and ReceiverId are required."));
            }

            var filter = Builders<ChatMessage>.Filter.Where(x => (x.SenderId == request.SenderId && x.ReceiverId == request.ReceiverId) || (x.SenderId == request.ReceiverId && x.ReceiverId == request.SenderId));
            var messages = await _dbContext.PrivateMessages.Find(filter).ToListAsync();

            var response = new GetPrivateChatHistoryResponse();
            foreach (var message in messages)
            {
                response.Messages.Add(new ChatMessageProto
                {
                    SenderId = message.SenderId,
                    ReceiverId = message.ReceiverId,
                    Message = message.Message,
                    CreatedAt = Google.Protobuf.WellKnownTypes.Timestamp.FromDateTime(message.CreatedAt.ToUniversalTime()),
                    UpdatedAt = Google.Protobuf.WellKnownTypes.Timestamp.FromDateTime(message.UpdatedAt.ToUniversalTime())
                });

            }

            return response;
        }
        catch (RpcException)
        {
            throw;
        }
        catch (System.Exception)
        {
            throw new RpcException(new Status(StatusCode.Internal, "An error occurred while fetching the chat history."));
        }
    }

    public override async Task<CreateRoomResponse> CreateRoom(CreateRoomRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.RoomName) || string.IsNullOrWhiteSpace(request.CreatorId) || request.MembersIds.Count == 0)
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "RoomName, Owner and Members are required."));
            }

            await _userManagementClient.GetUserProfileAsync(request.CreatorId);
            foreach (var memberId in request.MembersIds)
            {
                await _userManagementClient.GetUserProfileAsync(memberId);
            }

            var room = new ChatRoom
            {
                Name = request.RoomName,
                Owner = request.CreatorId,
                Members = request.MembersIds,
                CreatedAt = DateTime.Now,
                UpdatedAt = DateTime.Now
            };

            await _dbContext.ChatRooms.InsertOneAsync(room);
            return new CreateRoomResponse { Message = $"Room {room.Name} created successfully" };
        }
        catch (RpcException)
        {
            throw;
        }
        catch (System.Exception e)
        {
            throw new RpcException(new Status(StatusCode.Internal, $"An error occurred while creating the room: {e.Message}"));
        }
    }

    public override async Task<AddUserToRoomResponse> AddUserToRoom(AddUserToRoomRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.RoomId) || string.IsNullOrWhiteSpace(request.UserId))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "RoomId and UserId are required."));
            }

            var room = await _dbContext.ChatRooms.Find(x => x.Id == request.RoomId).FirstOrDefaultAsync();
            if (room == null)
            {
                throw new RpcException(new Status(StatusCode.NotFound, "Room not found."));
            }

            room.Members.Add(request.UserId);
            room.UpdatedAt = DateTime.Now;

            var update = Builders<ChatRoom>.Update.Set(x => x.Members, room.Members).Set(x => x.UpdatedAt, room.UpdatedAt);
            await _dbContext.ChatRooms.UpdateOneAsync(x => x.Id == request.RoomId, update);

            return new AddUserToRoomResponse { Message = $"User {request.UserId} added to room {room.Name}" };
        }
        catch (RpcException)
        {
            throw;
        }
        catch (System.Exception)
        {
            throw new RpcException(new Status(StatusCode.Internal, "An error occurred while adding the user to the room."));
        }
    }

    public override async Task<GetRoomHistoryResponse> GetRoomHistory(GetRoomHistoryRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.RoomId))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "RoomId is required."));
            }

            var filter = Builders<RoomMessage>.Filter.Where(x => x.RoomId == request.RoomId);
            var messages = await _dbContext.RoomMessages.Find(filter).ToListAsync();

            var response = new GetRoomHistoryResponse();
            foreach (var message in messages)
            {
                response.Messages.Add(new RoomMessageProto
                {
                    Id = message.Id,
                    SenderId = message.SenderId,
                    RoomId = message.RoomId,
                    Message = message.Message,
                    CreatedAt = Google.Protobuf.WellKnownTypes.Timestamp.FromDateTime(message.CreatedAt.ToUniversalTime()),
                    UpdatedAt = Google.Protobuf.WellKnownTypes.Timestamp.FromDateTime(message.UpdatedAt.ToUniversalTime())
                });

            }

            return response;
        }
        catch (RpcException)
        {
            throw;
        }
        catch (System.Exception)
        {
            throw new RpcException(new Status(StatusCode.Internal, "An error occurred while fetching the chat history."));
        }
    }

    public override async Task<LeaveRoomResponse> LeaveRoom(LeaveRoomRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.RoomId) || string.IsNullOrWhiteSpace(request.UserId))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "RoomId and UserId are required."));
            }

            var room = await _dbContext.ChatRooms.Find(x => x.Id == request.RoomId).FirstOrDefaultAsync();
            if (room == null)
            {
                throw new RpcException(new Status(StatusCode.NotFound, "Room not found."));
            }

            room.Members.Remove(request.UserId);
            room.UpdatedAt = DateTime.Now;

            var update = Builders<ChatRoom>.Update.Set(x => x.Members, room.Members).Set(x => x.UpdatedAt, room.UpdatedAt);
            await _dbContext.ChatRooms.UpdateOneAsync(x => x.Id == request.RoomId, update);

            return new LeaveRoomResponse { Message = $"User {request.UserId} left room {room.Name}" };
        }
        catch (RpcException)
        {
            throw;
        }
        catch (System.Exception)
        {
            throw new RpcException(new Status(StatusCode.Internal, "An error occurred while leaving the room."));
        }
    }

    public override async Task<AddUserResponse> AddUser(AddUserRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.UserId))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Id is required."));
            }

            if (string.IsNullOrWhiteSpace(request.Username))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Username is required."));
            }

            var user = new UserModel
            {
                Id = request.UserId,
                Username = request.Username
            };

            await _dbContext.Users.InsertOneAsync(user);
            return new AddUserResponse { Message = $"User {user.Username} added successfully" };
        }
        catch (RpcException)
        {
            throw;
        }
        catch (System.Exception e)
        {
            throw new RpcException(new Status(StatusCode.Internal, $"An error occurred while adding the user: {e.Message}"));
        }
    }
}
