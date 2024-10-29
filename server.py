import socket
import threading
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from flask import Flask, request, jsonify
import requests

# UDP server setup for video
SERVER_IP = "192.168.2.16"  # Replace with the actual IP address of the server laptop
VIDEO_SERVER_PORT = 9999    # This port is used for real-time video streaming between clients. It handles the actual transmission of video frames (in this case, using UDP).
SERVER_PORT = 5000          # This port is used by the Flask web server to handle HTTP requests from clients: Registering, listing, starting, stopping

# Global flag to control server loop
running = True  # Set this to False during shutdown to close the server

video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create a UDP socket
video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reusing the same address
video_socket.bind((SERVER_IP, VIDEO_SERVER_PORT)) # Bind the socket to the server IP and port


# Define Tkinter GUI class
class ServerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Video Call Server")

        # Display server information
        self.info_label = tk.Label(root,
                                   text=f"Server IP: {SERVER_IP} | Video Port: {VIDEO_SERVER_PORT} | Server Port: {SERVER_PORT}")
        self.info_label.pack(pady=5)

        # Scrolled text widget for logs
        self.log_text = ScrolledText(root, wrap=tk.WORD, width=80, height=40, font=("Arial", 11))
        self.log_text.pack(pady=5)

        # Disable editing for log_text to make it read-only
        self.log_text.config(state=tk.DISABLED)

        # Entry widget for commands
        self.command_entry = tk.Entry(root, width=50, font=("Arial", 13))
        self.command_entry.pack(pady=5, ipady=7)  # Increase ipady to increase height
        self.command_entry.bind("<Return>", self.process_command)  # Bind Enter key to command processing

        # Show server starting message
        self.log("Server started successfully!")
        self.log("Waiting for connection from other clients!")

        # Handle closing the server gracefully
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message):
        """Insert log message into the GUI in read-only mode with a timestamp."""
        if self.log_text.winfo_exists():  # Check if the log_text widget still exists
            # Get the current time for the timestamp
            current_time = time.strftime("[%H:%M:%S]")  # Format the current time as [HH:MM:SS]
            # Prepare the formatted message with a timestamp
            formatted_message = f"{current_time} {message}"
            # Temporarily enable the log_text widget to insert a new message
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, formatted_message + "\n")
            self.log_text.see(tk.END)  # Auto-scroll to the latest message
            # Set log_text back to read-only mode
            self.log_text.config(state=tk.DISABLED)

    def process_command(self, event):
        """Process user commands entered in the entry field."""
        command = self.command_entry.get()
        self.command_entry.delete(0, tk.END)  # Clear the entry field
        if command == "/shutdown":
            self.shutdown_server()
        else:
            self.log(f"Unknown command: {command}")

    def shutdown_server(self):
        """Handle shutting down the server gracefully."""
        global running
        self.log("Shutting down the server...")
        running = False  # Set running to 'False' to stop the video forwarding loop
        video_socket.close()  # Close the UDP socket
        self.root.after(2000, self.root.destroy)  # Close the Tkinter window after 2 seconds

    def on_closing(self):
        """Handle closing the server gracefully."""
        self.shutdown_server()


# Initialize Tkinter and Server GUI
root = tk.Tk()
server_gui = ServerGUI(root)


# Helper function to log events in the Tkinter GUI
def log_event(message):
    """Log event with a timestamp."""
    server_gui.log(message)  # Display log in GUI


# Data structure to store client info and connection state
# Data structure to store connected clients
clients = {} # This will store client addresses, e.g., { 'Client1': (ip, port, connected_status), 'Client2': (ip, port, connected_status) }
connected_pairs = set()  # Store connected client pairs for forwarding

# Initialize Flask app
app = Flask(__name__)

# Flask route to register a client
@app.route('/register', methods=['POST'])
def register_client():
    client_name = request.json.get("name")
    if client_name in clients:
        log_event(f"Failed registration attempt: Client name '{client_name}' already taken")
        return jsonify({"error": "Client name already taken"}), 400
    clients[client_name] = {"connected": False, "address": None}
    log_event(f"Client '{client_name}' registered successfully")
    return jsonify({"message": f"Client '{client_name}' registered successfully"}), 200

# Flask route to list available clients
@app.route('/clients', methods=['GET'])
def get_clients():
    available_clients = [client for client, data in clients.items() if not data["connected"]]
    log_event("Client requested list of available clients")
    return jsonify({"available_clients": available_clients})

# Flask route to start a call
@app.route('/start_call', methods=['POST'])
def start_call():
    caller = request.json.get("caller")
    callee = request.json.get("callee")
    if caller in clients and callee in clients and not clients[caller]["connected"] and not clients[callee]["connected"]:
        clients[caller]["connected"] = True
        clients[callee]["connected"] = True
        connected_pairs.add((caller, callee))
        log_event(f"Call started between {caller} and {callee}")
        return jsonify({"message": f"Call started between {caller} and {callee}"}), 200
    log_event(f"Failed call attempt: Clients {caller} or {callee} unavailable")
    return jsonify({"error": "Clients unavailable"}), 400

# Flask route to end a call
@app.route('/end_call', methods=['POST'])
def end_call():
    caller = request.json.get("caller")
    callee = request.json.get("callee")
    if (caller, callee) in connected_pairs or (callee, caller) in connected_pairs:
        clients[caller]["connected"] = False
        clients[callee]["connected"] = False
        connected_pairs.discard((caller, callee))
        connected_pairs.discard((callee, caller))
        log_event(f"Call ended between {caller} and {callee}")
        return jsonify({"message": "Call ended"}), 200
    log_event(f"Failed end call attempt: Clients {caller} and {callee} not in a call")
    return jsonify({"error": "Clients not in a call"}), 400


def video_forwarding_server():
    # Video forwarding function using UDP
    while running:  # Check the running flag to know when to stop
        try:
            # Receive video frame from one client
            frame_data, client_address = video_socket.recvfrom(65536)
            log_event(f"Received video frame from {client_address}")

            # Identify which client sent the data
            sender_name = next((name for name, data in clients.items() if data["address"] == client_address), None)

            if sender_name:
                log_event(f"Identified sender: {sender_name}")

                # Find the connected client to forward the video
                # \ meaning line continuation in Python
                recipient_name = next((callee for caller, callee in connected_pairs if caller == sender_name), None) or \
                                 next((caller for caller, callee in connected_pairs if callee == sender_name), None)

                if recipient_name and clients[recipient_name]["address"]:
                    # Forward the video frame to the connected client
                    video_socket.sendto(frame_data, clients[recipient_name]["address"])
                    log_event(
                        f"Forwarded video frame from {sender_name} to {recipient_name} at {clients[recipient_name]['address']}")
                else:
                    log_event(f"No connected recipient found for {sender_name}")

        except OSError:
            log_event("Socket closed, stopping video forwarding server.")
            break  # Exit loop if the socket is closed

        except Exception as e:
            log_event(f"Error in video forwarding server: {e}")

# Start the Flask server in a thread
def start_flask_server():
    app.run(host=SERVER_IP, port=SERVER_PORT)

# Start Flask server with a small
threading.Thread(target=start_flask_server, daemon=True).start()

# Start video forwarding server
threading.Thread(target=video_forwarding_server, daemon=True).start()

# Start the Tkinter GUI event loop to handle logs and shutdown events
root.mainloop()
