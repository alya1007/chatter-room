using System.Net.WebSockets;
using System.Text;
using UserService.Data;
namespace UserService.Services;

public class WebSocketUserService
{
    private static Dictionary<string, WebSocket> _clients = new Dictionary<string, WebSocket>();

    public static void Initialize()
    {
    }

    public static async Task HandleWebSocket(HttpContext context, WebSocket webSocket)
    {
        string userId = context.Request.Query["userId"];

        if (!_clients.ContainsKey(userId))
        {
            _clients.Add(userId, webSocket);
        }

        await ReceiveMessagesAsync(userId, webSocket);
    }

    private static async Task ReceiveMessagesAsync(string userId, WebSocket webSocket)
    {
        var buffer = new byte[1024 * 4];
        while (webSocket.State == WebSocketState.Open)
        {
            var result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);

            if (result.MessageType == WebSocketMessageType.Text)
            {
                var message = Encoding.UTF8.GetString(buffer, 0, result.Count);

                // You can choose to handle incoming messages or broadcast notifications.
                await BroadcastMessage(userId, message);
            }
            else if (result.MessageType == WebSocketMessageType.Close)
            {
                _clients.Remove(userId);
                await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
            }
        }
    }

    private static async Task BroadcastMessage(string userId, string message)
    {
        var buffer = Encoding.UTF8.GetBytes(message);

        foreach (var client in _clients)
        {
            if (client.Key != userId && client.Value.State == WebSocketState.Open)
            {
                await client.Value.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
            }
        }
    }

    public static async Task SendNotification(string userId, string notification)
    {
        if (_clients.ContainsKey(userId) && _clients[userId].State == WebSocketState.Open)
        {
            var buffer = Encoding.UTF8.GetBytes(notification);
            await _clients[userId].SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
        }
    }
}

