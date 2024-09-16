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

- **User Service**: This service is responsible for managing user accounts. It provides functionalities such as user registration, login, and user profile management.

- **Chat Service**: This service is responsible for managing chats. It provides functionalities such as writing to another user (creating a chat), creating a group chat, adding users to a group chat, and sending messages.

## Technology Stack and Communication Patterns

- **User Service**: Node.js (TypeScript)
- **Chat Service**: Node.js (TypeScript)
- **User Account Storage**: MongoDB
- **Chats Storage**: MongoDB
- **Chat Rooms Storage**: Redis
- **Message Broker**: RabbitMQ
- **API Gateway**: Python (Flask)
- **Communication Protocol**: HTTP, WebSocket, gRPC

## Data Management

### Database Separation

- **User Service**: Uses its own database to manage user data, ensuring that user information is isolated and secure. Suitable for storing user credentials, profiles, and preferences.

- **Chat Service**: Maintains a separate database for chat data, including private messages and chat room content. This allows for scalability and performance optimizations specific to chat operations.

### Data Access

- Services communicate with the gateway using gRPC for efficient data transfer and service discovery, and use HTTP/WebSocket protocol for client communication.

- Each service exposes endpoints that the other services can consume to perform necessary operations while maintaining data encapsulation and service autonomy.

### Endpoints Definitions

#### WebSocket Endpoints

- **/ws/chat**: Establishes a WebSocket connection for chat operations, including sending and receiving messages, creating chat rooms, and managing chat participants.

Each WebSocket endpoint would:

- Handle **onOpen** for establishing the connection.
- Handle **onMessage** for real-time message sending.
- Handle **onClose** for ending the session.

#### HTTP Endpoints

##### User Service HTTP

- POST **/users/create**: Create a new user.
- GET **/users/{userId}**: Retrieve user details.
- POST **/users/authenticate**: Authenticate a user and provide JWT (if applicable).

##### Chat Service HTTP

- POST **/chats/private/{recipientId}**: Send a private message to another user.
  - Request body: `{ "message": "<messageContent>" }`
- GET **/chats/private/{recipientId}/history**: Retrieve private message history with a user.
  - Response: `[ { "senderId": "<userId>", "message": "<messageContent>", "timestamp": "<time>" } ]`
- POST **/chats/room/{roomId}**: Send a message to a room.
  - Request body: `{ "message": "<messageContent>" }`
- GET **/chats/room/{roomId}/history**: Retrieve room message history.
  - Response: `[ { "userId": "<userId>", "message": "<messageContent>", "timestamp": "<time>" } ]`
- POST **/rooms/create**: Create a new chat room.
  - Request body: `{ "name": "<roomName>" }`
- POST **/rooms/{roomId}/join**: Join a chat room.
- POST **/rooms/{roomId}/leave**: Leave a chat room.

#### gRPC Endpoints

##### User Service gRPC

- **CreateUser**: Create a new user.
  - **Request**: `CreateUserRequest { string username, string email, string password }`
  - **Response**: `CreateUserResponse { int32 userId }`
- **AuthenticateUser**: Authenticate a user and return a token.
  - **Request**: `AuthenticateRequest { string username, string password }`
  - **Response**: `AuthenticateResponse { string token }`
- **GetUser**: Retrieve user details.
  - **Request**: `GetUserRequest { int32 userId }`
  - **Response**: `GetUserResponse { string username, string email }`

##### Chat Service gRPC

- **SendPrivateMessage**: Send a private message between users.
  - **Request**: `PrivateMessageRequest { int32 fromUserId, int32 toUserId, string message }`
  - **Response**: `PrivateMessageResponse { bool success }`
- **GetPrivateChatHistory**: Retrieve the history of messages between two users.
  - **Request**: `PrivateHistoryRequest { int32 fromUserId, int32 toUserId }`
  - **Response**: `PrivateHistoryResponse { repeated Message messages }`
- **SendRoomMessage**: Send a message to a room.
  - **Request**: `RoomMessageRequest { int32 userId, int32 roomId, string message }`
  - **Response**: `RoomMessageResponse { bool success }`
- **GetRoomHistory**: Retrieve the message history for a room.
  - **Request**: `RoomHistoryRequest { int32 roomId }`
  - **Response**: `RoomHistoryResponse { repeated Message messages }`
- **CreateRoom**: Create a new chat room.
  - **Request**: `CreateRoomRequest { string roomName }`
  - **Response**: `CreateRoomResponse { int32 roomId }`
- **JoinRoom**: Allow a user to join a specific chat room.
  - **Request**: `JoinRoomRequest { int32 userId, int32 roomId }`
  - **Response**: `JoinRoomResponse { bool success }`

## Deployment and Scaling

The application will be deployed using Docker containers. Each service will be deployed as a separate container. Also, databases will be deployed as separate containers.
