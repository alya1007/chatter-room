using MongoDB.Driver;
using ChatService.Models;

namespace ChatService.Data;
public class ChatServiceDbContext
{
    private readonly IMongoDatabase _database;
    public ChatServiceDbContext(string connectionString, string databaseName)
    {
        var client = new MongoClient(connectionString);
        _database = client.GetDatabase(databaseName);
    }

    public IMongoCollection<ChatMessage> PrivateMessages => _database.GetCollection<ChatMessage>("private_messages");
    public IMongoCollection<ChatRoom> ChatRooms => _database.GetCollection<ChatRoom>("rooms");
    public IMongoCollection<RoomMessage> RoomMessages => _database.GetCollection<RoomMessage>("room_messages");
}
