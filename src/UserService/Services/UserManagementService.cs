using Grpc.Core;
using MongoDB.Driver;
using UserService.Data;
using UserService.Protos;
using UserService.Models;
using UserService.Utils;
using Google.Protobuf.WellKnownTypes;

namespace UserService.Services;
public class UserManagementService : UserServiceManager.UserServiceManagerBase
{
    private readonly UserServiceDbContext _dbContext;

    public UserManagementService(UserServiceDbContext dbContext)
    {
        _dbContext = dbContext;

        var indexKeys = Builders<User>.IndexKeys.Ascending(u => u.Email);
        var indexOptions = new CreateIndexOptions { Unique = true };
        var indexModel = new CreateIndexModel<User>(indexKeys, indexOptions);
        _dbContext.Users.Indexes.CreateOne(indexModel);
    }

    public override async Task<RegisterUserResponse> RegisterUser(RegisterUserRequest request, ServerCallContext context)
    {
        try
        {
            var user = new User
            {
                Username = request.Username,
                Email = request.Email,
                Password = request.Password,
                CreatedAt = DateTime.Now,
                UpdatedAt = DateTime.Now
            };

            CustomValidator.Validate(user);

            await _dbContext.Users.InsertOneAsync(user);

            return new RegisterUserResponse { Message = $"User {user.Username} registered successfully" };
        }
        catch (MongoWriteException ex) when (ex.WriteError.Category == ServerErrorCategory.DuplicateKey)
        {
            throw new RpcException(new Status(StatusCode.AlreadyExists, "A user with this email already exists."));
        }
        catch (RpcException)
        {
            throw;
        }
        catch (Exception)
        {
            throw new RpcException(new Status(StatusCode.Internal, "An error occurred while registering the user"));
        }

    }

    public override async Task<LoginUserResponse> LoginUser(LoginUserRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Email) || string.IsNullOrWhiteSpace(request.Password))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Email and Password are required."));
            }

            var user = await _dbContext.Users
                .Find(u => u.Email == request.Email && u.Password == request.Password)
                .FirstOrDefaultAsync();
            if (user == null)
            {
                throw new RpcException(new Status(StatusCode.NotFound, "Invalid credentials"));
            }

            string token = JwtGenerator.GenerateJwt(user.Email, user.Username, user.Id!);

            await WebSocketUserService.SendNotification(user.Id!, "A new device has logged in to your account.");

            return new LoginUserResponse { Token = token };
        }
        catch (RpcException)
        {
            throw;
        }
        catch (Exception)
        {
            throw new RpcException(new Status(StatusCode.Internal, "An error occurred while logging in"));
        }
    }

    public override async Task<GetUserProfileResponse> GetUserProfile(GetUserProfileRequest request, ServerCallContext context)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.UserId))
            {
                throw new RpcException(new Status(StatusCode.InvalidArgument, "User ID is required."));
            }

            var user = await _dbContext.Users.Find(u => u.Id == request.UserId).FirstOrDefaultAsync();
            if (user == null)
            {
                throw new RpcException(new Status(StatusCode.NotFound, "User not found"));
            }

            return new GetUserProfileResponse { Username = user.Username, Email = user.Email };
        }
        catch (RpcException)
        {
            throw;
        }
        catch (Exception e)
        {
            throw new RpcException(new Status(StatusCode.Internal, $"An error occurred while fetching user profile: {e.Message}"));
        }
    }

    public override Task<Empty> Timeout(Empty request, ServerCallContext context)
    {
        Task.Delay(10000).Wait();
        return Task.FromResult(new Empty());
    }
}
