# Making use of socket and threading libraries
import socket
import threading


# Connection Details for TCP connections
HOST = '127.0.0.1'
PORT = 12345


# Initialising list of connected clients, aliases, chat history and locks
clients = []
aliases = []
chat_history = []
lock = threading.Lock()


# Broadcast messages to all clients in the chatroom
def broadcast_messages(message, sender_socket=None):
    with lock:
        chat_history.append(message)
        for client in clients:
            if client != sender_socket:
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
                index = clients.index(client)
                clients.remove(client)
                client.close()
                alias = aliases.pop(index)

            leave_message = f'{alias} has left the chatroom!'
            print(f'[*] {leave_message}')
            broadcast_messages(f'{leave_message}')
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

            # Only can append information to our lists 1 at a time
            with lock:
                aliases.append(alias)
                clients.append(client)

            join_message = f'{alias} has joined the chatroom!'
            print(f'[*] {join_message}')

            client.send(f'Welcome {alias} to the chatroom.'.encode('utf-8'))
            broadcast_messages(f'{join_message}', client)

            # Start the threads
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except Exception as e:
            print(f"Error accepting client connection: {e}")


if __name__ == "__main__":
    initialise_socket()
