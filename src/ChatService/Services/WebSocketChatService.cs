using ChatService.Data;
using MongoDB.Driver;
using System;
using System.Net.WebSockets;
using System.Text;
using ChatService.Models;

public class WebSocketChatService
{
    private static Dictionary<string, WebSocket> _clients = new Dictionary<string, WebSocket>();
    private static Dictionary<string, List<string>> _rooms = new Dictionary<string, List<string>>();
    private static ChatServiceDbContext? _dbContext;

    public static void Initialize(ChatServiceDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public static async Task HandleWebSocket(HttpContext context, WebSocket webSocket)
    {
        string userId = context.Request.Query["userId"];
        string roomId = context.Request.Query["roomId"];

        if (!_clients.ContainsKey(userId))
        {
            _clients.Add(userId, webSocket);
        }

        if (!_rooms.ContainsKey(roomId))
        {
            _rooms[roomId] = new List<string>();
        }
        if (!_rooms[roomId].Contains(userId))
        {
            _rooms[roomId].Add(userId);
        }

        await ReceiveMessagesAsync(userId, roomId, webSocket);
    }

    private static async Task ReceiveMessagesAsync(string userId, string roomId, WebSocket webSocket)
    {
        var buffer = new byte[1024 * 4];
        while (webSocket.State == WebSocketState.Open)
        {
            var result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);

            if (result.MessageType == WebSocketMessageType.Text)
            {
                var message = Encoding.UTF8.GetString(buffer, 0, result.Count);

                // Store the message directly in the database
                await StoreMessageInDatabase(userId, roomId, message);

                // Broadcast the message to others in the room
                await BroadcastMessage(userId, roomId, message);
            }
            else if (result.MessageType == WebSocketMessageType.Close)
            {
                _clients.Remove(userId);
                _rooms[roomId].Remove(userId);
                await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
            }
        }
    }

    private static async Task StoreMessageInDatabase(string userId, string roomId, string message)
    {
        var roomMessage = new RoomMessage
        {
            SenderId = userId,
            RoomId = roomId,
            Message = message,
            CreatedAt = DateTime.Now,
            UpdatedAt = DateTime.Now
        };

        await _dbContext.RoomMessages.InsertOneAsync(roomMessage);
    }

    private static async Task BroadcastMessage(string senderId, string roomId, string message)
    {
        var buffer = Encoding.UTF8.GetBytes(message);

        foreach (var userId in _rooms[roomId])
        {
            if (_clients.ContainsKey(userId) && userId != senderId)
            {
                var clientSocket = _clients[userId];
                if (clientSocket.State == WebSocketState.Open)
                {
                    await clientSocket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
                }
            }
        }
    }
}
