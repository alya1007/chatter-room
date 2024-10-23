# ChatterRoom

## Description

ChatterRoom is a realtime chat platform, build with a high emphasis on microservices architecture. It has two main functionalities: private chats and group chats.

## Application Suitability

Chat applications require a high level of responsiveness and low latency. This makes them a good candidate for microservices architecture. The microservices architecture allows for the application to be broken down into smaller, more manageable services, which can be scaled independently.

- **Scalability**: Microservices allow independent scaling of different parts of the application. In a chat application, a service such as, for example, a chats management service may require scaling more than other services. This service can be scaled horizontally to handle a large number of concurrent WebSocket connections.

- **Fault Tolerance**: Microservices can be designed to be fault-tolerant. In a chat application, if a service fails, the application can continue to function by routing requests to other services. In a chat application we can have multiple functionalities that are managed by different services, such as user management, chat management, and message management. If one of these services fails, the users can still use the other functionalities.

- **Security**: Security of personal data is a major concern in every messenger application. The users need to be sure that their chats are secure and private. Microservices architecture allows for the implementation of security measures at the service level.

- **Resource Allocation**: Microservices allow for the allocation of resources to the services that need them most. In a chat application, the chat management service may require more resources than other services. Microservices architecture allows for the allocation of resources to the chat management service as needed.

## Service Boundary

![System Architecture](./system_architecture.png)

- **User Service**: This service is responsible for managing user accounts. It provides functionalities such as user registration, login, and getting the profile of user.

- **Chat Service**: This service is responsible for managing chats. It provides functionalities such as writing to another user (creating a chat), creating a group chat, adding users to a group chat, and sending messages.

- **API Gateway**: Is responsible for routing requests to the appropriate service. It receives HTTP requests from the client and makes corresponding gRPC calls to the services.

- **Service Discovery**: Is responsible for service discovery. It allows services to find each other and communicate with each other. It also provides load balancing and fault tolerance. Each service registers itself with the service discovery service when it starts up. The service discovery service maintains a list of all the services that are currently running.

## Technology Stack and Communication Patterns

- **User Service**: C#
- **Chat Service**: C#
- **User Account Storage**: MongoDB
- **Chats Storage**: MongoDB
- **Chat Rooms Storage**: Redis
- **API Gateway**: Python
- **Communication Protocol**: HTTP, WebSocket, gRPC

## Data Management

### Database Separation

- **User Service**: Uses its own database to manage user data, ensuring that user information is isolated and secure. Suitable for storing user credentials, profiles, and preferences. The database has one collection: `users`.

- **Chat Service**: Maintains a separate database for chat data, including private messages and chat room content. This allows for scalability and performance optimizations specific to chat operations. Unit tests will be written to ensure the correctness of the data. This database has two collections: `private_messages`, `private_messages` and `rooms`.

- **Service Discovery**: For service discovery, a separate database is used to store service information, such as IP addresses and ports.

### Data Access

- Services communicate with the gateway using gRPC for efficient data transfer and service discovery, and use HTTP/WebSocket protocol for client communication.

- Each service exposes endpoints that the other services can consume to perform necessary operations while maintaining data encapsulation and service autonomy.

### Endpoints Definitions

#### WebSocket Endpoints

- **/ws/alert** - WebSocket endpoint on User Service for sending alerts to a user when a login attempt is made from a new device.

- **/ws/chat** - WebSocket endpoint on Chat Service for handling chat messages in rooms, including sending and receiving messages. Allows for real-time communication between users in a chat room, such that every user in the room receives messages in real-time.

#### HTTP Endpoints

##### User Service HTTP

- POST **/user-service/register**: Register a new user
- POST **/user-service/login**: Login a user
- GET **/user-service/users/{userId}**: Get user details
- GET **/user-service/status**: Status endpoint to check the health of the user service.

##### Chat Service HTTP

- POST **/chat-service/private/send**: Send a private message
- GET **/chat-service/private/{receiverId}**: Get private chat history with a user
- POST **/chat-service/rooms/create**: Create a new chat room
- PUT **/chat-service/rooms/{roomId}/add**: Add a user to a chat room
- GET **/chat-service/rooms/{roomId}**: Get chat room history
- PUT **/chat-service/rooms/{roomId}/leave**: Leave a chat room
- GET **/chat-service/status**: Status endpoint to check the health of the chat service.

##### API Gateway HTTP

- GET **/status**: Status endpoint to check the health of the API Gateway.
- GET **/timeout**: Endpoint to test the timeout functionality.

##### Service Discovery HTTP

- GET **/discovery/status**: Status endpoint to check the health of the service discovery service.

#### gRPC Endpoints

##### User Service gRPC

- **RegisterUser**: Register a new user.
  - **Request**: `RegisterUserRequest { string username, string email, string password }`
  - **Response**: `RegisterUserResponse { string message }`
- **LoginUser**: Login a user.
  - **Request**: `LoginUserRequest { string email, string password }`
  - **Response**: `LoginUserResponse { string token }`
- **GetUserProfile**: Retrieve user details.
  - **Request**: `GetUserProfileRequest { string user_id }`
  - **Response**: `GetUserProfileResponse { string username, string email }`

##### Chat Service gRPC

- **SendPrivateMessage**: Send a private message between users.
  - **Request**: `PrivateMessageRequest { string sender_id, string receiver_id, string message }`
  - **Response**: `PrivateMessageResponse { string message }`
- **GetPrivateChatHistory**: Retrieve the history of messages between two users.
  - **Request**: `PrivateHistoryRequest { string user_id, string receiver_id }`
  - **Response**: `PrivateHistoryResponse { repeated ChatMessageProto messages }`
- **GetRoomHistory**: Retrieve the message history for a room.
  - **Request**: `RoomHistoryRequest { string room_id }`
  - **Response**: `RoomHistoryResponse { repeated RoomMessageProto messages }`
- **CreateRoom**: Create a new chat room.
  - **Request**: `CreateRoomRequest { string room_name, string creator_id, repeated string members_ids }`
  - **Response**: `CreateRoomResponse { string message }`
- **AddUserToRoom**: Add a user to a chat room.
  - **Request**: `AddUserToRoomRequest { string room_id, string user_id }`
  - **Response**: `AddUserToRoomResponse { string message }`
- **LeaveRoom**: Leave a chat room.
  - **Request**: `LeaveRoomRequest { string room_id, string user_id }`
  - **Response**: `LeaveRoomResponse { string message }`

For each of the requests it will be necessary to implement a task timeout, to avoid blocking the service in case of a failure. If a user sends a message and the request to the chat service takes too long (perhaps because the chat service is down), a timeout is set. After this timeout, the client or API Gateway will cancel the request and return an error to the user.

### Concurrent Tasks Limit

#### At the API Gateway Level

- Rate-limiting mechanism to control the number of incoming requests, ensuring that only a certain number of requests are allowed through at a given time.
- Concurrency limit per endpoint, so each service (e.g., Chat Service, User Service) can handle only a specific number of concurrent tasks.

## Deployment and Scaling

The application will be deployed using Docker containers. Each service will be deployed as a separate container. Also, databases will be deployed as separate containers.
