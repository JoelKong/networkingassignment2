import socket
import threading
import sys

# Connection Details
HOST = '127.0.0.1'
PORT = 12345

# Receive messages from server and real time display update
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                sys.stdout.write('\r' + message + '\n>> ')
                sys.stdout.flush()
        except:
            print("An error occurred.")
            client_socket.close()
            break

# Connect to the server and send messages
def initialise_client():
    alias = input("Enter your name: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    client.send(alias.encode('utf-8'))

    threading.Thread(target=receive_messages, args=(client,)).start()

    while True:
        message = input("")
        print('\033[1A' + '\033[K', end='')
        message_with_alias = f"{alias}: {message}"
        sys.stdout.write('\r' + message_with_alias + '\n>> ')
        sys.stdout.flush()
        client.send(message_with_alias.encode('utf-8'))
        


if __name__ == "__main__":
    initialise_client()
