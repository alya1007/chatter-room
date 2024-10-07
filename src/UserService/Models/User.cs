using System.ComponentModel.DataAnnotations;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace UserService.Models
{
    public class User
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string? Id { get; set; }

        public required string Username { get; set; }
        public required string Password { get; set; }
        [EmailAddress]
        public required string Email { get; set; }
        [BsonDateTimeOptions(Kind = DateTimeKind.Local)]
        public required DateTime CreatedAt { get; set; }
        [BsonDateTimeOptions(Kind = DateTimeKind.Local)]
        public required DateTime UpdatedAt { get; set; }

    }
}