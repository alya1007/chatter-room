using Grpc.Core;
using MongoDB.Driver;
using UserService.Data;
using UserService.Protos;
using UserService.Models;

namespace UserService.Services
{
    public class UserManagementService : UserServiceManager.UserServiceManagerBase
    {
        private readonly UserServiceDbContext _dbContext;

        public UserManagementService(UserServiceDbContext dbContext)
        {
            _dbContext = dbContext;
        }

        public override async Task<RegisterUserResponse> RegisterUser(RegisterUserRequest request, ServerCallContext context)
        {
            var user = new User
            {
                Username = request.Username,
                Password = request.Password, // to do: hash password
                Email = request.Email
            };

            await _dbContext.Users.InsertOneAsync(user);

            return new RegisterUserResponse { UserId = user.Id };
        }

        public override async Task<LoginUserResponse> LoginUser(LoginUserRequest request, ServerCallContext context)
        {
            var user = await _dbContext.Users
                .Find(u => u.Username == request.Username && u.Password == request.Password)
                .FirstOrDefaultAsync();
            if (user == null)
            {
                throw new RpcException(new Status(StatusCode.NotFound, "Invalid credentials"));
            }

            string token = $"token-{user.Id}"; // to do: generate JWT token

            return new LoginUserResponse { Token = token };
        }

        public override async Task<GetUserProfileResponse> GetUserProfile(GetUserProfileRequest request, ServerCallContext context)
        {
            var user = await _dbContext.Users.Find(u => u.Id == request.UserId).FirstOrDefaultAsync();
            if (user == null)
            {
                throw new RpcException(new Status(StatusCode.NotFound, "User not found"));
            }

            return new GetUserProfileResponse { Username = user.Username, Email = user.Email };
        }


    }
}