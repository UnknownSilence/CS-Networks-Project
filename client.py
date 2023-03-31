import socket
import threading
import select
import time
import sys
import os

# Constants
UDP_PORT = 10000
TCP_PORT = 0 # port to be obtained from the server
BUFFER_SIZE = 1024
ACTIVITY_TIMEOUT = 300 # 5 minutes

# Client state
client_id = "" # to be obtained from the user
client_key = "" # to be obtained from the server
cookie = "" # to be obtained from the server
session_id = "" # to be obtained from the server
connected = False
server_address = "" # to be obtained from the user

# Encryption function (XOR)
def xor_crypt_string(data, key):
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in zip(data, key))

# Function to receive messages from the server
def receive_message(sock):
    while connected:
        r, w, e = select.select([sock], [], [], 1)
        if r:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            if data:
                # Decrypt the message
                decrypted_data = xor_crypt_string(data, client_key)
                # Handle the message
                handle_message(decrypted_data)

# Function to handle incoming messages
def handle_message(data):
    global session_id
    global connected
    split_data = data.split(" ")
    message_type = split_data[0]
    if message_type == "AUTH_FAIL":
        print("Authentication failed")
        connected = False
    elif message_type == "AUTH_SUCCESS":
        # Get the cookie and TCP port number
        global cookie
        global TCP_PORT
        cookie = split_data[1]
        TCP_PORT = int(split_data[2])
        print("Connected to server")
        connected = True
    elif message_type == "CHAT_STARTED":
        # Get the session ID
        session_id = split_data[1]
        print("Chat started with " + split_data[2])
    elif message_type == "UNREACHABLE":
        print("The requested client is not reachable")
    elif message_type == "END_NOTIF":
        print("Chat ended")
        session_id = ""
    else:
        # Unknown message type
        print("Unknown message type")

# Function to send messages to the server
def send_message(sock, message):
    # Encrypt the message
    encrypted_message = xor_crypt_string(message, client_key)
    # Send the message
    sock.sendto(encrypted_message, (server_address, UDP_PORT))

# Function to send chat messages to the server
def send_chat_message(sock, message):
    # Encrypt the message
    encrypted_message = xor_crypt_string(message, client_key)
    # Send the message
    sock.send(encrypted_message)

# Function to handle chat sessions
def chat_session(sock):
    global session_id
    if session_id == "":
        print("You are not currently in a chat session")
        return
    while connected:
        r, w, e = select.select([sock, sys.stdin], [], [], 1)
        if r:
            if sock in r:
                # Receive message from server and decrypt it
                data = sock.recv(BUFFER_SIZE)
                decrypted_data = xor_crypt_string(data, client_key)
                # Print the message
                print(decrypted_data)
            else:
                # Get user input and send chat message to server
                message = sys.stdin.readline().strip()
                if message == "End Chat":
                    # End the chat session
                    send_message(sock, "END_REQUEST " + session_id)
                    session_id = ""