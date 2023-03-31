
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
