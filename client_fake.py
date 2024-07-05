import socket
import threading
import time
import random
import openai

# Client settings
HOST = '127.0.0.1'  # Server address
PORT = 12345        # Server port


# Replace 'your-api-key' with your actual OpenAI API key
openai.api_key = ''

def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
                user_input = message
                response = chat_with_gpt(user_input)
                send_random_responses(client_socket, response)

                #debug failsafe to stop loop after 1 response
                time.sleep(9000)
        except:
            print("An error occurred.")
            client_socket.close()
            break

# Function to send random responses
def send_random_responses(client_socket, response):
    while True:
        client_socket.send(response.encode('utf-8'))
        time.sleep(random.randint(1, 10))

# Main function to connect to the server and send messages
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    threading.Thread(target=receive_messages, args=(client,)).start()
    # threading.Thread(target=send_random_responses, args=(client,)).start()

if __name__ == "__main__":
    main()