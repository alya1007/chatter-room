using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace ChatService.Models;
public class RoomMessage
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }
    [BsonRepresentation(BsonType.ObjectId)]
    public required string SenderId { get; set; }
    [BsonRepresentation(BsonType.ObjectId)]
    public required string RoomId { get; set; }
    public required string Message { get; set; }
    [BsonDateTimeOptions(Kind = DateTimeKind.Local)]
    public required DateTime CreatedAt { get; set; }
    [BsonDateTimeOptions(Kind = DateTimeKind.Local)]
    public required DateTime UpdatedAt { get; set; }

}
