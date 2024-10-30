import base64
import socket
import cv2

# Client configurations
SERVER_IP = "192.168.2.22"
VIDEO_SERVER_PORT = 6112

# Client setup for sending video stream
BUFF_SIZE = 65536
client_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
client_send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)  # Set buffer size

socket_address = (SERVER_IP, VIDEO_SERVER_PORT)

# Notify server of readiness to send video stream
message = b'I am ready to send video stream'
client_send_socket.sendto(message, socket_address)

# Open the camera and send video stream to server
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame to reduce size
    frame = cv2.resize(frame, (640, 480))  # Adjust as needed (e.g., (320, 240) for smaller frames)

    # Encode frame
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    jpg_as_text = base64.b64encode(buffer)

    # Check size before sending
    if len(jpg_as_text) <= BUFF_SIZE:
        client_send_socket.sendto(jpg_as_text, socket_address)
    else:
        print("Frame too large to send.")

cap.release()
client_send_socket.close()
