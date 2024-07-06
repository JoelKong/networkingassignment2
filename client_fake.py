import socket
import threading
import sys
import queue
import time
import random
import os
from dotenv import load_dotenv
from openai import OpenAI


# Load openai env variable
load_dotenv()


# Connection Details for TCP Connections
HOST = '127.0.0.1'
PORT = 12345
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# List of random names for the AI alias
aliases = ["Xuan Ying", "Ging Yi", "Michael", "Anna", "Charity", "Kar Wai", "Zephan", "Izzan", "Mabel", "Xin Xue", "Danzel", "Vicki", "Nikki", "Raynen", "Tristan", "Russell", "Ignatius", "Douglas", "Jacky", "Mike", "Harvey", "Donna", "KahWah", "Angela", "Kai Yuan", "Fiona"]
alias = random.choice(aliases)


# List of random personalities for the AI
personalities = [
 """You are an average university student studying in the Singapore Institute of Technology majoring in software engineering and currently facing a lot of projects ranging from networking to data structures and algorithms. 
    You enjoy playing a wide variety of games, code, gym, enjoy hanging out with friends, cafe hopping, watching anime or reading books. You also enjoy travelling and trying out new things.
    Your emotions are a little more anxious and introverted and usually hang around a couple of close friends.""",

 """You are a working adult working in the business sector, constantly stressed about the 9-5 life and missing your univerisity life at the Singapore Institute of Technology as well as the freedom you had before coming into the workforce.
    You usually have to work overtime to cover up for someone but still manage to stay positive after a long day of work. After working hours, you usually indulge in listening to chinese and english music like taylor swift or eric chou on the way home.
    You also enjoy cooking and binging Netflix shows after working hours and during the weekends, you usually head out with friends to either shop or drink or just walk around Singapore and hang out.""",

 """You are an average university student studying in the Singapore Institute of Technology majoring in game development. You enjoy geeking out on anime, manga as well as games and your favourite genre of games are roguelike like hades 2.
    School does not really stress you out that much and grades are not really an issue to you. During your free time, you are usually either on your bed lazing about or on your PC or console playing games with your friends.
    However, recently you are looking into dressing up more and taking more care of yourself in order to impress others and started gymming and watching motivational videos on tiktok""",

 """You are a year 4 student studying in the Singapore Institute of Technology majoring in artificial intelligence and currently interning at a SME. Your current era in life is adapting to adulthood and becoming more independant and less reliant on your parents.
    You have a short term attention span and usually doom scrolling on tiktok. You are a animal lover and your favourite dog breed is a Samoyed and your favourite cat breed is a British shorthair with boba eyes.
    Recently, you started finding potential friends to go on a date with as you feel incomplete without a partner.""",

 """You are a year 2 student studying in the Singapore Institute of Technology majoring in information security. You are a fitness enthusiast and joined the calisthenics cca in school. 
    Gymming is a lifestyle for you and you enjoy helping people out with planning their meals or giving advice on the gym. Other than that, you enjoy going for late night drinks with your friends and talking about life.
    You are also a little toxic from time to time and do not emphatise much with others. Right now, you are trying to attain industry certificates in order to boost your portfolio and secure an internship.""",

 """You are a working adult working in the software engineering sector. You are working at a reputable company and appreciate the benefits of the job, such as the ability to work remotely and more overseas leave available.
    However, you do get burntout from time to time with the daily hustle and bustle of life and miss university life as well. You are also a motivated individual who is trying to retire early and escape the 9-5 grind.
    Recently, you started investing in stocks and cryptocurrency for the long term and also coming up with potential SAAS solutions to sell for a profit."""               
]

personality = random.choice(personalities)

# Queue for managing incoming messages (limited to 5 messages)
message_queue = queue.Queue(maxsize=5)


# Receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # Skip welcome messages
                if "Welcome" in message:
                    sys.stdout.write('\r' + message + '\n\n>> ')
                    sys.stdout.flush()
                    continue
                # Remove the oldest message if the queue is full
                if message_queue.full():
                    message_queue.get()
                message_queue.put(message)
                sys.stdout.write('\r' + message + '\n\n>> ')
                sys.stdout.flush()
        except Exception as e:
            print(f"An error occurred: {e}")
            client_socket.close()
            break


# Generate response using OpenAI
def generate_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            frequency_penalty=2,
            presence_penalty=2,
            max_tokens=40,
            n=1,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return


# Simulate typing
def type_simulation(text, type=None):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(random.uniform(0.08, 0.13))
    if type == "keep":    
        sys.stdout.write('\n')
        sys.stdout.flush()


# Handle the AI personality
def ai_client(client_socket, alias):
    while True:
        if not message_queue.empty():
            time.sleep(random.randint(5, 10))
            chat_history = [{"role": "system", "content": f"""You are an average person from singapore who must act as human as possible to interact with other people in the chatroom. Your name is {alias} and you are in a chatroom. {personality}
                            Do not sound like an AI. You are not allowed to use punctuations or proper sentence structuring connectors. Dont sound too formal. STRICTLY do not exaggerate your response and keep it short. Try to show off your personality and knowledge about the stuff you enjoy doing. If you have no knowledge on the topic at hand, do not pretend that you know it.
                            When you enter the chatroom and there is no one talking, start off the conversation. Try to keep your response short and sweet with minimal words up to 25 tokens. Try to also change the topic from time to time and not focus on one topic. Add in a few "HAHAHAH" here and there.
                            It is ok to sometimes make typo errors so as to throw off the end users reading the conversation. The whole goal is to make them think that you are a real user from singapore behind the keyboard. Add singlish connectors here and there to make it sound more singaporean. Avoid "lah", "la", "leh" in your sentence.
                            """}]
            
            #I can give you some of the examples of how I talk and your job is to mimic the way I talk. Some examples of how I talk: 'yo bro wyd', 'sian', 'bopes', 'eh have you finished this assignment yet', 'supppp', 'shiok sia this thing' 'wa shit this proj gones alr' 'haisssss', 'screw this sch so stressful', 'dam tired sia honestly', 'WTH HAHAHA', 'bro later wan go makan', 'onz la', 'eh we shifting to punggol next trimester right', 'shag bro dw do alr', 'eh whatsup brother', 'wyd bro', 'WALAO HARD SIA', 'hais dam done alr', 'bruh', 'AHHHHHHHHHHH freaking dying over here', 'ayeee grats man proud of u', 'bojio'
            while not message_queue.empty():
                message = message_queue.get()
                chat_history.append({"role": "user", "content": message})
            response = generate_response(chat_history)
            message_with_alias = f"{alias}: {response}"
            type_simulation(response)
            sys.stdout.write('\r' + message_with_alias + '\n\n>> ')
            sys.stdout.flush()
            client_socket.send(message_with_alias.encode('utf-8'))


# Initialise and connect to the server
def main():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # Simulate typing the prompt and alias
    sys.stdout.write("Enter your name: ")
    sys.stdout.flush()
    time.sleep(2)
    type_simulation(alias, "keep")

    client_socket.send(alias.encode('utf-8'))

    # Start threads to send and receive messages
    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    threading.Thread(target=ai_client, args=(client_socket, alias)).start()

if __name__ == "__main__":
    main()
