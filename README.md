# Video Calling Application with Python, Flask, and UDP

## Project Overview
A simple video calling application using Python’s `socket` library, Flask for client management, and UDP for low-latency video streaming. The application allows clients to register, list available clients, start a call, send video frames and messages, and disconnect.

---

## Project Structure

### 1. Server
The server manages:
- **Client Registration**: Registers clients with names to be listed as available for connection.
- **Client List**: Provides a list of registered clients available for calls.
- **Call Management**: Handles initiation and termination of calls between two clients.
- **Video Streaming**: Receives video frames from one client and relays them to the connected client using UDP.
- **Messaging**: Relays text messages between clients during a call.

### 2. Client
The client features include:
- **User Registration**: Registers with a name to the server to be listed for potential connections.
- **Request Client List**: Retrieves a list of available clients from the server for initiating calls.
- **Start Call**: Initiates a video call with another client by requesting the server.
- **Video Streaming**: Captures video frames from the webcam, sends frames via UDP to the server, and displays incoming frames.
- **Messaging**: Sends and receives text messages during an active call.
- **End Call**: Disconnects from the server and notifies it of call termination.

---

## Components

### `server.py`
- Uses Flask for handling HTTP requests for client registration, list requests, and call management.
- Uses UDP sockets to handle real-time video streaming between clients.

### `client.py`
- Captures video with OpenCV, serializes frames with `pickle`, and transmits them over UDP.
- Requests server endpoints for registration, call initiation, and disconnection.

---

## Implementation Steps

1. **Set Up Server**
   - Create Flask endpoints for client registration, client listing, and call initiation/endpoints.
   - Set up a UDP socket to handle video frame relay between clients.

2. **Client Registration and Listing**
   - Client registers with the server and can request a list of available clients for initiating calls.

3. **Initiate and Manage Calls**
   - Start a call by notifying the server of both the caller and callee.
   - Server updates client status to manage video frame relay.

4. **Real-Time Video Streaming with UDP**
   - Capture video frames using OpenCV and send them over UDP.
   - Server receives and relays frames between connected clients.
   - Display received frames on the client’s interface.

5. **Messaging During Calls**
   - Enable text messaging during an active call via server relay.

---

## Technologies Used

- **Python socket library**: For UDP and TCP socket programming.
- **Flask**: For HTTP endpoints to manage client registration, listing, and call control.
- **OpenCV**: For video capture and display.
- **Pickle & Struct**: For serializing and deserializing video frames.

---

## Future Improvements

- **Switching to WebRTC**: For more optimized video streaming and handling.
- **Error Handling**: Better management of dropped frames and disconnections.
- **UI Enhancements**: Adding a front-end interface for improved user experience.

---

## Setup & Run Instructions

1. Install necessary libraries: `pip install flask opencv-python requests`.
2. Run the server: `python server.py`.
3. Run the client: `python client.py` (register with a unique name).
4. Start and manage calls through client interactions with the server.
