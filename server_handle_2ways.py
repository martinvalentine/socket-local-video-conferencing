# Server Code
import socket
import threading

# Server configuration
SERVER_IP = "192.168.2.16"  # Replace with your server's IP address
FORWARDING_PORT = 6000  # Port for forwarding video data

# Dictionary to store client ports dynamically
client_ports = {}

# Initialize the server socket for forwarding
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, FORWARDING_PORT))
print("Server listening on port:", FORWARDING_PORT)


# Handle receiving and forwarding video frames
def handle_forwarding():
    while True:
        # Receive message from any client
        msg, client_addr = server_socket.recvfrom(65536)
        client_ip, client_port = client_addr

        # Register client and assign pairing if first-time connection
        if client_ip not in client_ports:
            client_ports[client_ip] = {"send": client_port, "recv": None}
            print(f"Registered client at {client_ip} with send port {client_port}")
        elif client_ports[client_ip]["recv"] is None:
            client_ports[client_ip]["recv"] = client_port
            print(f"Updated client at {client_ip} with receive port {client_port}")

        # Get the paired client's address
        for other_ip, ports in client_ports.items():
            if other_ip != client_ip and ports["recv"] and client_ports[client_ip]["recv"]:
                # Forward to the paired client's receiving port
                forward_address = (other_ip, ports["recv"])
                server_socket.sendto(msg, forward_address)
                print(f"Forwarded data from {client_ip}:{client_port} to {other_ip}:{ports['recv']}")
                break


# Start forwarding in a thread
forwarding_thread = threading.Thread(target=handle_forwarding)
forwarding_thread.start()
