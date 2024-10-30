import socket
import cv2
import base64
import threading
import numpy as np
import time

# Client configuration
SERVER_IP = "192.168.2.16"  # Replace with your server's IP address
SERVER_PORT = 6000  # Server's forwarding port

# Socket for sending and receiving data
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(3)  # Timeout to detect when no data is received (for black screen fallback)

# Notify server of readiness (sends an initial "registration" message)
client_socket.sendto(b"REGISTER", (SERVER_IP, SERVER_PORT))

# Define frame dimensions for the black screen
frame_width, frame_height = 640, 480
black_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)


# Video capture and sending function
def send_video():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Resize and encode the frame
        frame = cv2.resize(frame, (frame_width, frame_height))
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        encoded_frame = base64.b64encode(buffer)
        client_socket.sendto(encoded_frame, (SERVER_IP, SERVER_PORT))
    cap.release()


# Video receiving and display function
def receive_video():
    last_received_time = time.time()
    cv2.imshow("Receiving Video", black_frame)
    cv2.waitKey(1)  # Initialize the window with a black screen

    while True:
        try:
            # Try to receive data from the server
            data, _ = client_socket.recvfrom(65536)
            last_received_time = time.time()  # Update the last received time
            frame = base64.b64decode(data)
            np_frame = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
        except socket.timeout:
            # Check if we have timed out waiting for data
            if time.time() - last_received_time > 2:  # Timeout duration to reset to black screen
                np_frame = black_frame
        except Exception as e:
            print("Error receiving data:", e)
            break

        # Display the frame (either video or black screen)
        cv2.imshow("Receiving Video", np_frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    client_socket.close()


# Start both send and receive threads
threading.Thread(target=send_video, daemon=True).start()
threading.Thread(target=receive_video, daemon=True).start()

# Keep the main thread running
while True:
    try:
        time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        break
