import socket
import threading

# list of subscribers with their client IDs and secret keys
subscribers = {
    'ClientA': 'SecretKeyA',
    'ClientB': 'SecretKeyB',
    'ClientC': 'SecretKeyC'
}

# dictionary to keep track of connected clients and their keys
connected_clients = {}

# dictionary to keep track of ongoing chat sessions
chat_sessions = {}

# UDP port number for authentication and challenge-response protocol
UDP_PORT = 5000

# TCP port number for chat sessions
TCP_PORT = 6000


def handle_udp_auth(connection, address):
    """Handle the authentication and challenge-response protocol for a client"""
    data, client_address = connection.recvfrom(1024)
    client_id = data.decode('utf-8').split(' ')[1]
    if client_id in subscribers:
        secret_key = subscribers[client_id]
        # generate random challenge
        rand = 'random_challenge'
        connection.sendto(rand.encode('utf-8'), client_address)
        data, client_address = connection.recvfrom(1024)
        response = data.decode('utf-8').split(' ')[1]
        if response == secret_key:
            # generate encryption key
            ck = 'encryption_key'
            connected_clients[client_id] = {'address': client_address, 'key': ck}
            # send authentication success message
            auth_success_message = f'AUTH_SUCCESS({rand}, {TCP_PORT})'
            encrypted_message = ck + auth_success_message
            connection.sendto(encrypted_message.encode('utf-8'), client_address)
        else:
            # send authentication failure message
            connection.sendto('AUTH_FAIL'.encode('utf-8'), client_address)


def handle_tcp_chat(connection, address):
    """Handle chat sessions between clients"""
    # receive initial CONNECT message with random cookie
    data = connection.recv(1024).decode('utf-8')
    rand_cookie = data.split(' ')[1]
    client_id = ''
    for c_id, client in connected_clients.items():
        if client['address'] == address:
            client_id = c_id
            break
    while True:
        data = connection.recv(1024).decode('utf-8')
        if data.startswith('CHAT_REQUEST'):
            # initiate chat session with another client
            target_id = data.split(' ')[1]
            if target_id in connected_clients and target_id != client_id:
                session_id = 'random_session_id'
                chat_sessions[session_id] = (client_id, target_id)
                message_a = f'CHAT_STARTED({session_id}, {target_id})'
                message_b = f'CHAT_STARTED({session_id}, {client_id})'
                target_address = connected_clients[target_id]['address']
                send_tcp_message(message_a, target_address, connected_clients[target_id]['key'])
                send_tcp_message(message_b, address, connected_clients[client_id]['key'])
            else:
                message = f'UNREACHABLE({target_id})'
                send_tcp_message(message, address, connected_clients[client_id]['key'])
        elif data.startswith('END_REQUEST'):
            # end chat session
            session_id = data.split(' ')[1]
            if session_id in chat_sessions and client_id in chat_sessions[session_id]:
                other_id = chat_sessions[session_id][0] if client_id == chat_sessions[session_id][1] else chat_sessions[session_id][1]
                message = f'END_NOTIF({session_id})'
                other_address = connected_clients[other_id]['address']
                send_tcp_message(message
