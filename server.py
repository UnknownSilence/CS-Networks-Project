import socket
import threading

# Server configuration
host = 'localhost'
port = 8000

# Socket creation
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))
server_socket.listen()

# Clients and their usernames
clients = {}
usernames = []

# Function to broadcast messages to all connected clients
def broadcast(message):
    for client_socket in clients:
        client_socket.send(message)

# Function to handle each client's connection
def handle_client(client_socket, username):
    # Welcome message to new client
    client_socket.send(f"Welcome {username}! You are now connected to the chat room.\n".encode())

    # Notify all other clients that a new client has joined
    broadcast(f"{username} has joined the chat room!\n".encode())

    while True:
        # Receive message from client
        message = client_socket.recv(1024)

        # Broadcast message to all other clients
        broadcast(f"{username}: {message.decode()}".encode())

    # Close client socket when they disconnect
    client_socket.close()

# Function to start the server
def start_server():
    print(f"Server listening on {host}:{port}...\n")

    while True:
        # Accept client connections
        client_socket, client_address = server_socket.accept()

        # Prompt client for their username
        client_socket.send("Please enter your username: ".encode())
        username = client_socket.recv(1024).decode().strip()

        # Add client to list of connected clients
        clients[client_socket] = username
        usernames.append(username)

        # Handle each client's connection in a new thread
        thread = threading.Thread(target=handle_client, args=(client_socket, username))
        thread.start()

# Start the server
start_server()
