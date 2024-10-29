import cv2
import socket
import pickle
import threading
import requests

SERVER_IP = "192.168.2.16"  # Replace with the actual server IP address
SERVER_PORT = 5000  # HTTP port for API
VIDEO_PORT = 9999  # UDP port for video stream

class VideoClient:
    def __init__(self, client_name):
        self.client_name = client_name
        self.available_clients = []

    def register(self):
        """Register the client with the server."""
        try:
            response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/register', json={"name": self.client_name})
            if response.status_code == 200:
                print(f"Registered as {self.client_name}")
                return True
            else:
                print(f"Registration failed: {response.json().get('error', 'Unknown error')}")
                return False
        except requests.ConnectionError:
            print("Could not connect to the server.")
            return False

    def get_available_clients(self):
        """Fetch available clients from the server."""
        response = requests.get(f'http://{SERVER_IP}:{SERVER_PORT}/available_clients')
        if response.status_code == 200:
            self.available_clients = response.json().get('clients', [])
        return self.available_clients

    def start_video_stream(self):
        """Start capturing and sending video frames."""
        cap = cv2.VideoCapture(0)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Serialize and send the frame
            data = pickle.dumps(frame)
            sock.sendto(data, (SERVER_IP, VIDEO_PORT))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def listen_for_video(self, update_video_callback):
        """Receive video frames from other clients and update the GUI."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((SERVER_IP, VIDEO_PORT))

        while True:
            data, addr = sock.recvfrom(65536)
            frame = pickle.loads(data)
            update_video_callback(frame)

    def send_message(self, message):
        """Send a message to the server."""
        requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/send_message', json={"message": message})

    def end_call(self):
        """Notify the server to end the call."""
        requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/end_call')
