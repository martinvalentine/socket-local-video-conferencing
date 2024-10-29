import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from client import VideoClient
import cv2
from PIL import Image, ImageTk

class VideoCallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Call Application")
        self.client = None

        # Initial frame for entering name
        self.name_frame = tk.Frame(self.root)
        self.name_frame.pack(pady=20)
        self.name_label = tk.Label(self.name_frame, text="Enter your name:")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.name_frame, width=30)
        self.name_entry.pack(pady=5)
        self.connect_button = tk.Button(self.name_frame, text="Connect", command=self.connect_client)
        self.connect_button.pack(pady=10)

    def connect_client(self):
        client_name = self.name_entry.get()
        if not client_name:
            messagebox.showwarning("Warning", "Please enter a name.")
            return

        self.client = VideoClient(client_name)
        if not self.client.register():
            messagebox.showerror("Error", "Could not register client.")
            return

        available_clients = self.client.get_available_clients()
        self.name_frame.pack_forget()
        self.setup_call_interface(available_clients)

    def setup_call_interface(self, available_clients):
        # Video and message frames
        self.video_frame = tk.Frame(self.root)
        self.video_frame.pack(side=tk.LEFT)
        self.client1_video_label = tk.Label(self.video_frame, text="Your Video", width=20)
        self.client1_video_label.pack()
        self.client1_video = tk.Label(self.video_frame)
        self.client1_video.pack()

        self.client2_video_label = tk.Label(self.video_frame, text="Other Client's Video", width=20)
        self.client2_video_label.pack()
        self.client2_video = tk.Label(self.video_frame)
        self.client2_video.pack()

        # List of available clients with Refresh button
        self.available_clients_label = tk.Label(self.root, text="Available Clients:")
        self.available_clients_label.pack()
        self.available_clients_listbox = tk.Listbox(self.root)
        self.available_clients_listbox.pack()

        # Insert initial clients into listbox
        for client in available_clients:
            self.available_clients_listbox.insert(tk.END, client)

        # Refresh Button
        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_available_clients)
        self.refresh_button.pack()

        # Messaging panel
        self.message_panel = scrolledtext.ScrolledText(self.root, width=30, height=10)
        self.message_panel.pack()
        self.message_entry = tk.Entry(self.root, width=30)
        self.message_entry.pack()
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

        # End Call Button
        self.end_call_button = tk.Button(self.root, text="End Call", command=self.end_call)
        self.end_call_button.pack()

        # Start video streaming threads
        threading.Thread(target=self.client.start_video_stream).start()
        threading.Thread(target=self.client.listen_for_video, args=(self.update_client2_video,)).start()

    def refresh_available_clients(self):
        # Clear the listbox and fetch updated client list
        self.available_clients_listbox.delete(0, tk.END)
        updated_clients = self.client.get_available_clients()
        for client in updated_clients:
            self.available_clients_listbox.insert(tk.END, client)

    def update_client1_video(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (160, 120))
        img = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.client1_video.configure(image=img)
        self.client1_video.image = img

    def update_client2_video(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (160, 120))
        img = ImageTk.PhotoImage(image=Image.fromarray(img))
        self.client2_video.configure(image=img)
        self.client2_video.image = img

    def send_message(self):
        message = self.message_entry.get()
        self.message_panel.insert(tk.END, f"{self.client.client_name}: {message}\n")
        self.message_entry.delete(0, tk.END)
        self.client.send_message(message)

    def end_call(self):
        self.client.end_call()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCallApp(root)
    root.mainloop()
