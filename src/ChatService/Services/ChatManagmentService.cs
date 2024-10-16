using Grpc.Core;
using ChatService.Protos;
using ChatService.Models;
using ChatService.Data;
using MongoDB.Driver;

namespace ChatService.Services;
public class ChatManagementService : ChatServiceManager.ChatServiceManagerBase
{
    private readonly ChatServiceDbContext _dbContext;
    public ChatManagementService(ChatServiceDbContext dbContext)
    {
        _dbContext = dbContext;
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
}
