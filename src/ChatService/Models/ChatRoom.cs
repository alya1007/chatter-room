using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ChatService.Models;

public class ChatRoom
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }
    [BsonRepresentation(BsonType.ObjectId)]
    public required string Owner { get; set; }

    public required string Name { get; set; }

    public required List<string> Members { get; set; }


    [BsonDateTimeOptions(Kind = DateTimeKind.Local)]
    public required DateTime CreatedAt { get; set; }


    [BsonDateTimeOptions(Kind = DateTimeKind.Local)]
    public required DateTime UpdatedAt { get; set; }
}