using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace UserService.Models
{
    public class User
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public required string Id { get; set; }

        public required string Username { get; set; }
        public required string Password { get; set; }
        public required string Email { get; set; }

    }
}