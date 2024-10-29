import tkinter as tk
from tkinter import messagebox, scrolledtext
import cv2
import socket
import pickle
import threading
import requests

# Constants
SERVER_IP = "192.168.x.x"  # Replace with the server's IP address
SERVER_PORT = 5000  # Server port
VIDEO_PORT = 5001  # UDP port for video stream


class VideoCallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Call Application")

        self.client_name = None  # Store the client's name

        # Pre-GUI for entering name
        self.name_frame = tk.Frame(self.root)
        self.name_frame.pack(pady=20)

        self.name_label = tk.Label(self.name_frame, text="Enter your name:")
        self.name_label.pack()

        self.name_entry = tk.Entry(self.name_frame, width=30)
        self.name_entry.pack(pady=5)

        self.connect_button = tk.Button(self.name_frame, text="Connect", command=self.connect_client)
        self.connect_button.pack(pady=10)

    def connect_client(self):
        self.client_name = self.name_entry.get()
        if not self.client_name:
            messagebox.showwarning("Warning", "Please enter a name.")
            return

        # Request available clients from server
        response = requests.get(f'http://{SERVER_IP}:{SERVER_PORT}/available_clients')
        available_clients = response.json().get('clients', [])

        # Update the GUI to show available clients
        self.name_frame.pack_forget()  # Hide the name entry frame
        self.setup_call_interface(available_clients)

    def setup_call_interface(self, available_clients):
        # Create frames for video and messages
        self.frame1 = tk.Frame(self.root)
        self.frame1.pack(side=tk.LEFT)

        self.frame2 = tk.Frame(self.root)
        self.frame2.pack(side=tk.RIGHT)

        # Client 1 Video
        self.client1_video_label = tk.Label(self.frame1, text="Client 1 Video", width=20)
        self.client1_video_label.pack()
        self.client1_video = tk.Label(self.frame1)
        self.client1_video.pack()

        # Client 2 Video
        self.client2_video_label = tk.Label(self.frame2, text="Client 2 Video", width=20)
        self.client2_video_label.pack()
        self.client2_video = tk.Label(self.frame2)
        self.client2_video.pack()

        # Available Clients List
        self.available_clients_label = tk.Label(self.root, text="Available Clients:")
        self.available_clients_label.pack()

        self.available_clients_listbox = tk.Listbox(self.root)
        for client in available_clients:
            self.available_clients_listbox.insert(tk.END, client)
        self.available_clients_listbox.pack()

        # Message Panel
        self.message_panel = scrolledtext.ScrolledText(self.root, width=30, height=10)
        self.message_panel.pack()

        self.message_entry = tk.Entry(self.root, width=30)
        self.message_entry.pack()

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

        # End Call Button
        self.end_call_button = tk.Button(self.root, text="End Call", command=self.end_call)
        self.end_call_button.pack()

        # Start video stream
        self.video_thread = threading.Thread(target=self.start_video_stream)
        self.video_thread.start()

        # Start listening for incoming video
        self.incoming_video_thread = threading.Thread(target=self.listen_for_video)
        self.incoming_video_thread.start()

    def start_video_stream(self):
        cap = cv2.VideoCapture(0)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Serialize the frame
            data = pickle.dumps(frame)
            sock.sendto(data, (SERVER_IP, VIDEO_PORT))

            # Update the client 1 video display
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(frame, (160, 120))  # Resize for display
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imshow("Client 1 Video", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def listen_for_video(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((SERVER_IP, VIDEO_PORT))

        while True:
            data, addr = sock.recvfrom(65536)
            frame = pickle.loads(data)

            # Update the client 2 video display
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(frame, (320, 240))  # Resize for display
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imshow("Client 2 Video", img)

    def send_message(self):
        message = self.message_entry.get()
        self.message_panel.insert(tk.END, f"{self.client_name}: {message}\n")
        self.message_entry.delete(0, tk.END)

        # Optionally send the message to the server
        requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/send_message', json={"message": message})

    def end_call(self):
        # Call Flask API to end the call
        requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/end_call')
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCallApp(root)
    root.mainloop()
