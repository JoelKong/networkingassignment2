import socket
import threading
import sys
import os


# Connection Details for TCP Connections
HOST = '127.0.0.1'
PORT = 12345


# Receive messages from server and real time display update
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # Write the received message and show the prompt for new input
                sys.stdout.write('\r' + message + '\n\n>> ')
                sys.stdout.flush()
        except Exception as e:
            print(f"An error occurred: {e}")
            client_socket.close()
            break


# Initialise client, connect to the server and send messages
def initialise_client():
    os.system('cls||clear')
    alias = input("Enter your name: ")

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
    except Exception as e:
        print(f"Connection error: {e}")
        return

    try:
        client.send(alias.encode('utf-8'))
    except Exception as e:
        print(f"Error sending alias: {e}")
        client.close()
        return

    # Start the thread to receive messages
    threading.Thread(target=receive_messages, args=(client,)).start()

    while True:
        try:
            message = input("")
            message_with_alias = f"{alias}: {message}"
            # Clear the input line
            print('\033[1A' + '\033[K', end='')
            sys.stdout.write('\r' + message_with_alias + '\n\n>> ')
            sys.stdout.flush()
            client.send(message_with_alias.encode('utf-8'))
        except Exception as e:
            print(f"An error occurred while sending message: {e}")
            client.close()
            break
        except KeyboardInterrupt:
            print('\nLeaving the chatroom...')
            client.close()
            sys.exit(0)
        
if __name__ == "__main__":
    initialise_client()
