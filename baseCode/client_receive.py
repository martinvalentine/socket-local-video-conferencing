import base64
import socket
import cv2
import numpy as np

# Client configurations
SERVER_IP = "192.168.2.22"
VIDEO_SERVER_PORT = 6112

# Client setup for receiving video stream
BUFF_SIZE = 65536
client_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
client_receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)  # Set buffer size

socket_address = (SERVER_IP, VIDEO_SERVER_PORT)

# Notify server of readiness to receive video stream
message = b'I am ready to receive video stream'
client_receive_socket.sendto(message, socket_address)

# Receive and display video stream
while True:
    data, server_addr = client_receive_socket.recvfrom(BUFF_SIZE)
    nparr = np.frombuffer(base64.b64decode(data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imshow("Video receive", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
client_receive_socket.close()
