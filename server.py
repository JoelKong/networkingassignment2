import socket
import threading

# Connection Details
HOST = '127.0.0.1'
PORT = 12345

# Initialising list of connected clients and aliases and locks
clients = []
aliases = []
lock = threading.Lock()

# Broadcast messages to all clients in the chatroom
def broadcast_messages(message, sender_socket=None):
    with lock:
        for client in clients:
            if client != sender_socket:
                client.send(message)

# Handle client messages and statuses
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast_messages(message, client)
        except:
            with lock:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                alias = aliases.pop(index)

            broadcast_messages(f'{alias} has left the chatroom!'.encode('utf-8'))

            if aliases:
                print(f'Connected clients: {", ".join(aliases)}')
            else:
                print("No Connected Clients.")

            break

# Initialisation of connections and threads and handling clients
def initialise_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print('Server has initialised.')

    while True:
        client, address = server.accept()

        alias = client.recv(1024).decode('utf-8')
        with lock:
            aliases.append(alias)
            clients.append(client)

        print(f'Connected clients: {", ".join(aliases)}')

        client.send(f'Welcome {alias} to the chatroom.'.encode('utf-8'))
        broadcast_messages(f'{alias} has joined the chatroom!'.encode('utf-8'), client)

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


if __name__ == "__main__":
    initialise_socket()