import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

# Connection Details for TCP Connections
HOST = '127.0.0.1'
PORT = 12345

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("400x700")

        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        self.message_entry = tk.Text(root, height=3, wrap=tk.WORD)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<Shift-Return>", self.newline)

        self.client_socket = None
        self.alias = None
        self.receive_thread = None
        self.stop_event = threading.Event()

        self.connect_to_server()

    def connect_to_server(self):
        self.alias = simpledialog.askstring("Alias", "Enter your name:")
        if not self.alias:
            self.root.quit()
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(self.alias.encode('utf-8'))
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except Exception as e:
            messagebox.showerror("Connection error", f"Could not connect to server: {e}")
            self.root.quit()

    def receive_messages(self):
        while not self.stop_event.is_set():
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.insert(tk.END, message + "\n")
                    self.chat_display.config(state=tk.DISABLED)
                    self.chat_display.yview(tk.END)
            except Exception as e:
                if not self.stop_event.is_set():
                    messagebox.showerror("Error", f"An error occurred: {e}")
                break

    def send_message(self, event=None):
        message = self.message_entry.get("1.0", tk.END).strip()
        if message:
            message_with_alias = f"{self.alias}: {message}"
            try:
                self.client_socket.send(message_with_alias.encode('utf-8'))
                self.message_entry.delete("1.0", tk.END)
                # Prevent new line on Enter key
                return 'break'
            except Exception as e:
                if not self.stop_event.is_set():
                    messagebox.showerror("Error", f"An error occurred while sending message: {e}")
                self.client_socket.close()
                self.root.quit()

    def newline(self, event=None):
        self.message_entry.insert(tk.INSERT, "\n")
        return 'break'

    def on_closing(self):
        self.stop_event.set()
        try:
            if self.client_socket:
                self.client_socket.close()
            if self.receive_thread:
                self.receive_thread.join()
        except Exception as e:
            print(f"Error while closing: {e}")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
