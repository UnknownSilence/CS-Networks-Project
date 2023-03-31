import socket
import threading

# Server configuration
host = 'localhost'
port = 8000

# Socket creation
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# Function to receive messages from the server
def receive():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(message)
        except:
            # If there is an error, close the socket and exit the program
            print("An error occurred!")
            client_socket.close()
            break

# Function to send messages to the server
def send():
    while True:
        message = input()
        client_socket.send(message.encode())

# Prompt user for their username
username = input("Please enter your username: ")

# Send username to server
client_socket.send(username.encode())

# Start threads for sending and receiving messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()
