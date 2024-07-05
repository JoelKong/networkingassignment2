import socket
import threading
import sys
import queue
from openai import OpenAI
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
HOST = '127.0.0.1'
PORT = 12345
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# List of random names for the AI alias
aliases = ["Xuan Ying", "Ging Yi", "Michael", "Anna", "Charity", "Kar Wai", "Zephan", "Izzan", "Mabel", "Xin Xue", "Danzel", "Vicki", "Nikki", "Raynen", "Tristan", "Russell", "Ignatius", "Douglas", "Jacky", "Mike", "Harvey", "Donna", "KahWah", "Angela", "Kai Yuan", "Fiona"]
alias = random.choice(aliases)

# Queue for managing incoming messages (limited to 5 messages)
message_queue = queue.Queue(maxsize=5)

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                if message_queue.full():
                    message_queue.get()  # Remove the oldest message if the queue is full
                message_queue.put(message)  # Add message to the queue
                sys.stdout.write('\r' + message + '\n>> ')
                sys.stdout.flush()
        except:
            print("An error occurred.")
            client_socket.close()
            break

# Function to generate responses using OpenAI
def generate_response(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        frequency_penalty=1,
        max_tokens=30,
        n=1,
        temperature=0.55
    )
    return response.choices[0].message.content

# Function to handle the AI client
def ai_client(client_socket, alias):
    while True:
        if not message_queue.empty():
            time.sleep(random.randint(10, 20))
            chat_history = [{"role": "system", "content": f"""You are a normal Singaporean who must act as human and as singaporean as possible to interact with other people in the chatroom. Your personality is an average university student studying in the Singapore Institute of Technology majoring in software engineering. 
                            You enjoy playing a wide variety of games such as Valorant or League of Legends, gymming, enjoy hanging out with friends, cafe hopping or watching anime. Your name is {alias} and the user messages passed to you are in the form of a chatroom. System messages will be shown to you such as when a new person joins the chatroom. User messages will be given in the form of their name being displayed first followed by a colon. You do not know anyone in the chatroom in real life. 
                            Do not sound like an AI. STRICTLY do not address anyone's names when you give your response and do not use any punctuations, full stop or capital letter in your response. Try to show off your personality and knowledge about the stuff you enjoy doing more such as advice on gym etc. You can also ask for feedback or advice on certain aspects of life too. Try to keep the conversation more lively and interesting.
                            When you enter the chatroom and there is no one talking, start off the conversation. However, if you just entered the chatroom and there seems to be people talking try your best to slide in smoothly and figure out whats going on and get to know one another. Try to keep you response short and sweet and broken english. 
                            Try your best to use singlish from time to time and use the singapore language to shorten your words. I can give you some of the examples of how I talk and your job is to mimic the way I talk. It is ok to sometimes make typo errors so as to throw off the end users reading the conversation. The whole goal is to make them think that you are a real user behind the keyboard. 
                            Some examples of how I talk: 'yo bro wyd', 'wa shit this proj gones alr' 'haisssss', 'screw this sch so stressful', 'dam tired sia honestly', 'WTH HAHAHA', 'bro later wan go makan', 'onz la', 'eh we shifting to punggol next trimester right', 'shag bro dw do alr', 'eh whatsup brother', 'wyd bro', 'WALAO HARD SIA', 'hais dam done alr', 'bruh', 'AHHHHHHHHHHH freaking dying over here', 'ayeee grats man proud of u', 'bojio'"""}]
            while not message_queue.empty():
                message = message_queue.get()
                chat_history.append({"role": "user", "content": message})
            response = generate_response(chat_history)
            message_with_alias = f"{alias}: {response}"
            client_socket.send(message_with_alias.encode('utf-8'))
            sys.stdout.write('\r' + message_with_alias + '\n>> ')
            sys.stdout.flush()

# Main function to connect to the server and start AI client
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    client.send(alias.encode('utf-8'))  # Send the alias to the server

    threading.Thread(target=receive_messages, args=(client,)).start()
    threading.Thread(target=ai_client, args=(client, alias)).start()

if __name__ == "__main__":
    main()
