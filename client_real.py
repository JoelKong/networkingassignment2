# Use Socket and threading and tkinter library
import socket
import threading
import tkinter as tk
from tkinter import font, scrolledtext, messagebox

# Connection Details for TCP Connections
# 127.0.0.1
# HOST = '35.212.224.171' for cloud
HOST = '127.0.0.1' # for local
PORT = 12345

# GUI for entering name
class CustomDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.geometry("200x150")
        # Bring the dialog to the front
        self.dialog.wm_attributes("-topmost", 1)

        
        self.label = tk.Label(self.dialog, text="Enter your name")
        self.label.pack(fill='both', pady=20)
        
        # Entry widget for user input
        self.entry = tk.Entry(self.dialog)
        self.entry.pack(pady=10,padx=20)
        
        # Bind the Enter key to close the dialog and return the entry value
        self.entry.bind("<Return>", self.on_enter_pressed)
        
        # Focus on entry widget
        self.entry.focus_force()
        self.entry.focus_set()
        self.value = None
        
        # wait for dialog to close
        self.dialog.grab_set()
        self.parent.wait_window(self.dialog)

    def on_enter_pressed(self, event):
        # Close the dialog and return the entry value
        self.value = self.entry.get()
        if self.value.strip():
            self.dialog.destroy()

    def get_value(self):
        return self.value

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("400x700")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # font config
        font_config = font.Font(family="Helvetica", size=12)

        # name label
        self.name_label = tk.Label(root, text="")
        self.name_label.pack(padx=10, pady=5, anchor=tk.W)

        # chat scrolled text
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, font=font_config)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # chat input with multiline
        self.message_entry = tk.Text(root, height=6, wrap=tk.WORD, font=font_config)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<Shift-Return>", self.newline)

        self.client_socket = None
        self.alias = None
        self.receive_thread = None
        self.stop_event = threading.Event()

        self.connect_to_server()

    def connect_to_server(self):
        self.dialog = CustomDialog(self.root)
        self.alias = self.dialog.get_value()
        if not self.alias:
            self.quit_app()
            return
        
        try:
            # connect and update name label
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(self.alias.encode('utf-8'))

            self.name_label.config(text=f"Name: {self.alias}")
            self.root.focus_force()

            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        except Exception as e:
            messagebox.showerror("Connection error", f"Could not connect to server: {e}")
            self.quit_app()

    def receive_messages(self):
        # handle receiving message from server broadcast
        while not self.stop_event.is_set():
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.insert(tk.END, message + "\n\n")
                    self.chat_display.config(state=tk.DISABLED)
                    self.chat_display.yview(tk.END)
            except Exception as e:
                if not self.stop_event.is_set():
                    messagebox.showerror("Error", f"An error occurred: {e}")
                break

    def send_message(self, event=None):
        # send message to server
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
                self.quit_app()

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
        self.root.destroy()

    def quit_app(self):
        self.stop_event.set()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
