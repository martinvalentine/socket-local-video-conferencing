import socket
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Server configurations
SERVER_IP = "192.168.2.22"  # Set to server's IP
VIDEO_SERVER_PORT = 6112  # UDP port for video streaming
SERVER_PORT = 5000  # HTTP port for FastAPI

# Client management and connection setup
clients = {} # IP address of clients
connected_pairs = {} # Dictionary to store connected pairs of clients (sender, receiver)

# Setup server
BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)  # Set buffer size

socket_address = (SERVER_IP, VIDEO_SERVER_PORT)
server_socket.bind(socket_address)  # Bind the socket to the address

print('Listening at:', socket_address)


# Handle client connections
def handle_client(client_addr):
    while True:
        msg, addr = server_socket.recvfrom(BUFF_SIZE)
        if addr in connected_pairs:
            receiver_addr = connected_pairs[addr]
            if receiver_addr:
                server_socket.sendto(msg, receiver_addr)


# Accept clients and pair them
def accept_clients():
    while True:
        msg, client_addr = server_socket.recvfrom(BUFF_SIZE) # Receive message from client
        print("Client connected:", client_addr)

        # Pair clients
        if client_addr not in clients:
            if len(clients) % 2 == 0:
                clients[client_addr] = None
            else:
                for other_client in clients:
                    if clients[other_client] is None:
                        clients[other_client] = client_addr
                        clients[client_addr] = other_client
                        connected_pairs[client_addr] = other_client
                        connected_pairs[other_client] = client_addr
                        break

        # Start a new thread for each client
        threading.Thread(target=handle_client, args=(client_addr,)).start()


# Start accepting clients
accept_thread = threading.Thread(target=accept_clients)
accept_thread.start()

app = FastAPI()
uvicorn.run(app, host=SERVER_IP, port=SERVER_PORT)
