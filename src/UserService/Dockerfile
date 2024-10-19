# Use .NET SDK 8.0 to build the project
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Copy the .csproj and restore dependencies as a distinct layer
COPY ["UserService.csproj", "./"]
RUN dotnet restore

# Copy everything else and build
COPY . ./
RUN dotnet publish -c Release -o out

# Use .NET 8.0 runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/out .

# Expose the port
EXPOSE 5002

# Start the service
ENTRYPOINT ["dotnet", "UserService.dll"]
