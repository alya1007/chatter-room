using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;

namespace UserService.Utils
{
    public static class JwtGenerator
    {
        private static readonly IConfiguration _configuration;
        private static readonly string _secretKey;

        static JwtGenerator()
        {
            var builder = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                .AddJsonFile($"appsettings.{Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT")}.json", optional: true);

            _configuration = builder.Build();
            _secretKey = _configuration["JWT:jwtSecret"] ?? "";
        }
        public static string GenerateJwt(string email, string username, string id)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(_secretKey))
                {
                    throw new Exception("JWT key is missing");
                }
                var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_secretKey));
                var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

                var token = new JwtSecurityToken(
                    claims: [
                        new Claim(JwtRegisteredClaimNames.Email, email),
                        new Claim(JwtRegisteredClaimNames.Sub, id),
                        new Claim("username", username)
                    ],
                    expires: DateTime.Now.AddMinutes(30),
                    signingCredentials: creds
                );
                return new JwtSecurityTokenHandler().WriteToken(token);
            }
            catch (Exception ex)
            {
                throw new Exception("An error occurred while generating JWT token", ex);
            }
        }
    }
}