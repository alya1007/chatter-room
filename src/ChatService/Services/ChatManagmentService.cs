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
}
