import socket
import threading

# Client settings
HOST = '127.0.0.1'  # Server address
PORT = 12345        # Server port

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
        except:
            print("An error occurred.")
            client_socket.close()
            break

# Main function to connect to the server and send messages
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    threading.Thread(target=receive_messages, args=(client,)).start()

    while True:
        message = input()
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    main()
