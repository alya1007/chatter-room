using MongoDB.Driver;
using UserService.Models;

namespace UserService.Data
{
    public class UserServiceDbContext
    {
        private readonly IMongoDatabase _database;
        public UserServiceDbContext(string connectionString, string databaseName)
        {
            var client = new MongoClient(connectionString);
            _database = client.GetDatabase(databaseName);
        }

        public IMongoCollection<User> Users => _database.GetCollection<User>("Users");
    }
}