import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Connection Details for TCP connections
HOST = '127.0.0.1'
PORT = 12345

# Initializing list of connected clients, aliases, chat history and locks
clients = []
aliases = []
chat_history = []
lock = threading.Lock()


# Broadcast messages to all clients in the chatroom
def broadcast_messages(message, sender_socket=None):
    with lock:
        chat_history.append(message)
        for client in clients:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to client: {e}")


# Handle individual client messages and statuses
def handle_client(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(f'[*] {message}')
            broadcast_messages(message, client)
        except:
            with lock:
                if client in clients:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    alias = aliases.pop(index)
                    leave_message = f'{alias} has left the chatroom!'
                    print(f'[*] {leave_message}')
                    broadcast_messages(leave_message)
                    update_gui()
            break


# Initialisation of server socket and handle client connections
def initialise_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        server.listen()
        print('Server has initialised.')
    except Exception as e:
        print(f"Error initializing server: {e}")
        return

    while True:
        try:
            client, address = server.accept()
            alias = client.recv(1024).decode('utf-8')

            with lock:
                aliases.append(alias)
                clients.append(client)

            join_message = f'{alias} has joined the chatroom!'
            print(f'[*] {join_message}')

            client.send(f'Welcome {alias} to the chatroom.'.encode('utf-8'))
            broadcast_messages(join_message, client)

            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            update_gui()
        except Exception as e:
            print(f"Error accepting client connection: {e}")


def start_server():
    threading.Thread(target=initialise_socket, daemon=True).start()


def update_gui():
    with lock:
        client_list.delete(0, tk.END)
        for alias in aliases:
            client_list.insert(tk.END, alias)

        chat_display.config(state=tk.NORMAL)
        chat_display.delete('1.0', tk.END)
        for message in chat_history:
            chat_display.insert(tk.END, message + "\n")
        chat_display.config(state=tk.DISABLED)


# GUI Implementation
root = tk.Tk()
root.title("Chat Server")
root.geometry("500x700")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

client_list_label = tk.Label(frame, text="Connected Clients")
client_list_label.pack()

client_list = tk.Listbox(frame, height=5)
client_list.pack(fill=tk.BOTH, expand=True)

chat_display_label = tk.Label(frame, text="Chat History")
chat_display_label.pack()

chat_display = scrolledtext.ScrolledText(frame, state=tk.DISABLED)
chat_display.pack(fill=tk.BOTH, expand=True)

start_button = tk.Button(root, text="Start Server", command=start_server)
start_button.pack(pady=5)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.quit()

root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    root.mainloop()
