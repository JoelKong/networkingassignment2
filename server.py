import socket
import threading
import tkinter as tk
from tkinter import font, scrolledtext, messagebox

# Connection Details for TCP connections
# use '' if using external ip with cloud
# server cloud ip address is 35.212.224.171

# use '127.0.0.1' if not hosting in cloud
# use '' to host using external ip
HOST = '127.0.0.1' # locally
# HOST = '' for cloud
PORT = 12345

# Initializing list of connected clients, aliases, chat history and locks
clients = []
aliases = []
chat_history = []
lock = threading.Lock()
server_socket = None

# Function to update GUI with chat history and client list
def update_gui():
    with lock:
        # Update client list
        client_list.delete(0, tk.END)
        for alias in aliases:
            client_list.insert(tk.END, alias)

        # Update chat history
        chat_display.config(state=tk.NORMAL)
        chat_display.delete('1.0', tk.END)
        for message in chat_history:
            chat_display.insert(tk.END,"[*] " + message + "\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)

# Broadcast messages to all clients in the chatroom
def broadcast_messages(message, sender_socket=None, message_type=None):
    with lock:
        chat_history.append(message)
        for client in clients:
            try:
                # not a join message or is a join message and dont show ownself entering chat
                if message_type == None or (message_type == "join" and client != sender_socket):
                    client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to client: {e}")
    # Update GUI after broadcasting message
    root.after(0, update_gui)

# Handle individual client messages and statuses
def handle_client(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                print(f'[*] {message}')
                broadcast_messages(message, client)
            else:
                raise Exception("Client disconnected")
        except:
            with lock:
                #remove closed clients
                if client in clients:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    alias = aliases.pop(index)
                    leave_message = f'{alias} has left the chatroom!'
                    print(f'[*] {leave_message}')
            # put broadcast outside of lock to prevent deadlock
            broadcast_messages(leave_message)
            break
        
# Initialisation of server socket and handle client connectionsz
def initialise_socket():
    global server_socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print('Server has initialised.')
    except Exception as e:
        print(f"Error initializing server: {e}")
        return

    while True:
        try:
            client, address = server_socket.accept()
            alias = client.recv(1024).decode('utf-8')

            with lock:
                aliases.append(alias)
                clients.append(client)

            join_message = f'{alias} has joined the chatroom!'
            print(f'[*] {join_message}')

            client.send(f'Welcome {alias} to the chatroom.'.encode('utf-8'))
            broadcast_messages(join_message, client, "join")

            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except Exception as e:
            print(f"Error accepting client connection: {e}")

def start_server():
    threading.Thread(target=initialise_socket, daemon=True).start()

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if server_socket:  # Check if server_socket is initialized
            server_socket.close()  # Close the server socket
        root.quit()

# GUI Implementation
root = tk.Tk()
root.title("Chat Server")
root.geometry("500x700")
root.protocol("WM_DELETE_WINDOW", on_closing)
font_config = font.Font(family="Helvetica", size=12)

frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

client_list_label = tk.Label(frame, text="Connected Clients")
client_list_label.pack()

client_list = tk.Listbox(frame, height=5,font=font_config)
client_list.pack(fill=tk.BOTH, expand=True)

chat_display_label = tk.Label(frame, text="Chat History")
chat_display_label.pack()

chat_display = scrolledtext.ScrolledText(frame, state=tk.DISABLED, font=font_config)
chat_display.pack(fill=tk.BOTH, expand=True)

start_button = tk.Button(root, text="Start Server", command=start_server)
start_button.pack(pady=5)

if __name__ == "__main__":
    root.mainloop()
