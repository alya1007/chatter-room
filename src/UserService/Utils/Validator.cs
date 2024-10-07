using System.ComponentModel.DataAnnotations;
using Grpc.Core;

namespace UserService.Utils;
public static class CustomValidator
{
    public static void Validate(object model)
    {
        var context = new ValidationContext(model, serviceProvider: null, items: null);
        var results = new List<ValidationResult>();

        bool isValid = Validator.TryValidateObject(model, context, results, validateAllProperties: true);
        if (!isValid)
        {
            var errors = string.Join(", ", results.Select(r => r.ErrorMessage));
            throw new RpcException(new Status(StatusCode.InvalidArgument, $"Validation failed: {errors}"));
        }
    }
}