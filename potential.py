
# SNIPPET 1
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
import socket
import threading
import hashlib

# Define server host and port
HOST = 'localhost'
PORT = 12345

# Define dictionary to store client IDs and keys
clients = {}

# Define dictionary to store client chat history
chat_history = {}

# Define function to authenticate clients
def authenticate_client(client_id, rand, response):
    secret_key = clients[client_id]
    xres = hashlib.sha256((rand + secret_key).encode()).hexdigest()
    if response == xres:
        return True
    else:
        return False

# Define function to handle client connections
def handle_client(client_socket, client_address):
    # Receive HELLO message from client
    hello_msg = client_socket.recv(1024).decode()
    if hello_msg.startswith('HELLO'):
        # Parse client ID from HELLO message
        client_id = hello_msg.split()[1]
        if client_id in clients:
            # Generate random challenge for client
            rand = str(hash(client_address))
            # Calculate expected response from client
            xres = hashlib.sha256((rand + clients[client_id]).encode()).hexdigest()
            # Send challenge to client
            challenge_msg = 'CHALLENGE ' + rand
            client_socket.send(challenge_msg.encode())
            # Receive response from client
            response_msg = client_socket.recv(1024).decode()
            if response_msg.startswith('RESPONSE'):
                # Parse response from client
                response = response_msg.split()[1]
                # Authenticate client
                if authenticate_client(client_id, rand, response):
                    # Generate encryption key for client
                    ck = hashlib.sha256((rand + clients[client_id]).encode()).hexdigest()
                    # Send authentication success message to client
                    auth_success_msg = 'AUTH_SUCCESS ' + rand + ' ' + str(PORT)
                    client_socket.send(ck.encrypt(auth_success_msg.encode()))
                    # Receive CONNECT message from client
                    connect_msg = ck.decrypt(client_socket.recv(1024)).decode()
                    if connect_msg.startswith('CONNECT'):
                        # Parse random cookie from CONNECT message
                        rand_cookie = connect_msg.split()[1]
                        # Send CONNECTED message to client
                        connected_msg = 'CONNECTED'
                        client_socket.send(ck.encrypt(connected_msg.encode()))
                        # Loop to handle chat sessions with client
                        while True:
                            # Receive message from client
                            msg = ck.decrypt(client_socket.recv(1024)).decode()
                            if msg.startswith('CHAT_REQUEST'):
                                # Parse target client ID from CHAT_REQUEST message
                                target_client_id = msg.split()[1]
                                if target_client_id in clients:
                                    # Check if target client is available for chat
                                    if chat_history.get((client_id, target_client_id)) is None and chat_history.get((target_client_id, client_id)) is None:
                                        # Generate session ID and send CHAT_STARTED message to both clients
                                        session_id = str(hash(client_address + target_client_id.encode()))
                                        chat_history[(client_id, target_client_id)] = []
                                        chat_history[(target_client_id, client_id)] = []
                                        chat_started_msg = 'CHAT_STARTED ' + session_id + ' ' + target_client_id
                                        client_socket.send(ck.encrypt(chat_started_msg.encode()))
                                        target_client_socket = client_sockets[clients.index(target_client_id)]
                                        target_client_socket.send(ck.encrypt(chat_started
                                                                             

# SNIPPET 2
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################
###########################################################################################################################################################################################################################################################################################################################

import random

# Define a dictionary to store the possible responses
responses = {
    "greeting": ["Hello!", "Hi there!", "Hey!", "Greetings!"],
    "goodbye": ["Goodbye!", "Bye bye!", "See you later!", "Farewell!"],
    "thanks": ["You're welcome!", "No problem!", "My pleasure!"],
    "age": ["I'm just a computer program, so I don't have an age."],
    "weather": ["I'm sorry, I don't have access to live weather data."],
    "default": ["I'm not sure I understand. Can you please be more specific?", 
                "I'm sorry, I didn't quite catch that. Can you please repeat?", 
                "I'm not programmed to understand that. Can you try asking something else?"]
}

# Define a function to generate the response
def generate_response(input):
    # Remove leading/trailing white space and convert to lowercase
    input = input.strip().lower()

    # Check if input contains a greeting keyword
    if any(word in input for word in ["hello", "hi", "hey", "greetings"]):
        return random.choice(responses["greeting"])

    # Check if input contains a goodbye keyword
    elif any(word in input for word in ["goodbye", "bye", "see you", "farewell"]):
        return random.choice(responses["goodbye"])

    # Check if input contains a thanks keyword
    elif any(word in input for word in ["thank", "thanks", "appreciate"]):
        return random.choice(responses["thanks"])

    # Check if input contains an age-related keyword
    elif any(word in input for word in ["age", "old"]):
        return random.choice(responses["age"])

    # Check if input contains a weather-related keyword
    elif any(word in input for word in ["weather", "temperature", "forecast"]):
        return random.choice(responses["weather"])

    # If no specific keyword is found, use the default response
    else:
        return random.choice(responses["default"])