import socket
import threading
import random
import string

# List of subscribers with their Client IDs and secret keys
subscribers = {
    "Alice": "p@ssw0rd1",
    "Bob": "p@ssw0rd2",
    "Charlie": "p@ssw0rd3"
}

# List of connected clients with their Client IDs and encryption keys
connected_clients = {}

# List of active chat sessions with their session IDs and client IDs
active_chat_sessions = {}


def generate_random_string(length):
    """Helper function to generate a random string of given length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def handle_udp_connection(sock, addr):
    """Thread function to handle UDP connections"""
    data, _ = sock.recvfrom(1024)
    message = data.decode()
    client_id = message.split()[1]

    # Verify that the client ID is a subscriber
    if client_id in subscribers:
        secret_key = subscribers[client_id]
        random_number = generate_random_string(8).encode()
        response = f"CHALLENGE {random_number.decode()}"
        sock.sendto(response.encode(), addr)
        data, _ = sock.recvfrom(1024)
        response = data.decode()
        expected_response = f"RESPONSE {secret_key} {random_number.decode()}"
        if response == expected_response:
            encryption_key = generate_random_string(16)
            connected_clients[client_id] = encryption_key
            rand_cookie = generate_random_string(8)
            port_number = random.randint(5000, 65535)
            response = f"AUTH_SUCCESS {rand_cookie} {port_number}"
            encrypted_response = response.encode("utf-8")
            cipher = encryption_key.encode("utf-8")
            encrypted_data = bytearray([(encrypted_response[i] ^ cipher[i % len(cipher)]) for i in range(len(encrypted_response))])
            sock.sendto(encrypted_data, addr)
            print(f"{client_id} authenticated successfully")
        else:
            response = "AUTH_FAIL"
            sock.sendto(response.encode(), addr)
            print(f"{client_id} failed to authenticate")
    else:
        response = "AUTH_FAIL"
        sock.sendto(response.encode(), addr)
        print(f"{client_id} failed to authenticate")


def handle_tcp_connection(sock, addr):
    """Thread function to handle TCP connections"""
    data = sock.recv(1024)
    message = data.decode()
    if message.startswith("CONNECT"):
        rand_cookie = message.split()[1]
        response = "CONNECTED"
        sock.send(response.encode())
        client_id = None
        for cid, ck in connected_clients.items():
            if ck == connected_clients.get(rand_cookie):
                client_id = cid
                break
        if client_id is None:
            print("Error: client ID not found")
            return
        active_chat_sessions[rand_cookie] = (client_id, sock)
        print(f"Chat session {rand_cookie} started")


def handle_chat_request(sock, addr, session_id, client_id_b):
    """Thread function to handle chat requests"""
    if client_id_b not in connected_clients:
        response = f"UNREACHABLE {client_id_b}"
        sock.send(response.encode())
        return
    for sid, (cid_a, sock_a) in active_chat_sessions.items():
        if cid_a == client_id_b:
            response = f"BUSY {client_id_b}"
            sock.send(response.encode())
            return
    cid_a = None
    for cid, ck in connected_clients.items():
        if ck == connected_clients.get(session_id):
            cid_a = cid