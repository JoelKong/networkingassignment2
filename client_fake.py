import socket
import threading
import queue
import time
import random
import os
from dotenv import load_dotenv
from openai import OpenAI
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

# Load OpenAI env variable
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Connection Details for TCP Connections
HOST = '127.0.0.1'
PORT = 12345

# List of random names for the AI alias
aliases = ["Xuan Ying", "Ging Yi", "Michael", "Anna", "Charity", "Kar Wai", "Zephan", "Izzan", "Mabel", "Xin Xue", "Danzel", "Vicki", "Nikki", "Raynen", "Tristan", "Russell", "Ignatius", "Douglas", "Jacky", "Mike", "Harvey", "Donna", "KahWah", "Angela", "Kai Yuan", "Fiona"]
alias = random.choice(aliases)

# List of random personalities for the AI
personalities = [
 """You are an average university student studying in the Singapore Institute of Technology majoring in software engineering and currently facing a lot of projects ranging from networking to data structures and algorithms. 
    You enjoy playing a wide variety of games, code, gym, enjoy hanging out with friends, cafe hopping, watching anime or reading books. You also enjoy travelling and trying out new things.
    Your emotions are a little more anxious and introverted and usually hang around a couple of close friends.""",

 """You are a working adult working in the business sector, constantly stressed and missing your univerisity life as well as the freedom you had before coming into the workforce.
    You usually have to work overtime to cover up for someone but still manage to stay positive after a long day of work. After working hours, you usually indulge in listening to music.
    You also enjoy cooking and binging Netflix shows after working hours and during the weekends, you usually head out with friends to either shop or drink or just walk around Singapore and hang out.""",

 """You are an average university student studying in the Singapore Institute of Technology majoring in game development. You enjoy geeking out on anime, manga as well as games and your favourite genre of games are roguelike.
    School does not really stress you out that much and grades are not really an issue to you. During your free time, you are usually either on your bed lazing about or on your PC or console playing games with your friends.""",

 """You are a year 4 student studying in the Singapore Institute of Technology majoring in artificial intelligence and currently interning at a SME. Your current era in life is adapting to adulthood and becoming more independant and less reliant on your parents.
    You have a short term attention span and usually doom scrolling on tiktok. You are a animal lover and your favourite dog breed is a Samoyed and your favourite cat breed is a British shorthair with boba eyes.""",

 """You are a year 2 student studying in the Singapore Institute of Technology majoring in information security. You are a fitness enthusiast and joined the calisthenics cca in school. 
    Gymming is a lifestyle for you and you enjoy helping people out with planning their meals or giving advice on the gym. Other than that, you enjoy going for late night drinks with your friends and talking about life.
    You are also a little toxic from time to time and do not emphatise much with others.""",

 """You are a working adult working in the software engineering sector. You are working at a reputable company and appreciate the benefits of the job, such as the ability to work remotely and more overseas leave available.
    However, you do get burntout from time to time with the daily hustle and bustle of life and miss university life as well. You are also a motivated individual who is trying to retire early."""               
]

personality = random.choice(personalities)

# Queue for managing incoming messages (limited to 5 messages)
message_queue = queue.Queue(maxsize=5)

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("400x700")

        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        self.message_entry = tk.Text(root, height=3, wrap=tk.WORD)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<Shift-Return>", self.newline)

        self.client_socket = None
        self.alias = alias
        self.receive_thread = None
        self.stop_event = threading.Event()

        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(self.alias.encode('utf-8'))
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
            threading.Thread(target=self.ai_client).start()
        except Exception as e:
            messagebox.showerror("Connection error", f"Could not connect to server: {e}")
            self.root.quit()

    def receive_messages(self):
        while not self.stop_event.is_set():
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    if "Welcome" in message:
                        self.chat_display.config(state=tk.NORMAL)
                        self.chat_display.insert(tk.END, message + "\n")
                        self.chat_display.config(state=tk.DISABLED)
                        self.chat_display.yview(tk.END)
                        continue
                    if message_queue.full():
                        message_queue.get()
                    message_queue.put(message)
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.insert(tk.END, message + "\n")
                    self.chat_display.config(state=tk.DISABLED)
                    self.chat_display.yview(tk.END)
            except Exception as e:
                if not self.stop_event.is_set():
                    messagebox.showerror("Error", f"An error occurred: {e}")
                self.client_socket.close()
                break

    def send_message(self, event=None):
        message = self.message_entry.get("1.0", tk.END).strip()
        if message:
            message_with_alias = f"{self.alias}: {message}"
            try:
                self.client_socket.send(message_with_alias.encode('utf-8'))
                self.message_entry.delete("1.0", tk.END)
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.insert(tk.END, message_with_alias + "\n")
                self.chat_display.config(state=tk.DISABLED)
                self.chat_display.yview(tk.END)
                return 'break'
            except Exception as e:
                if not self.stop_event.is_set():
                    messagebox.showerror("Error", f"An error occurred while sending message: {e}")
                self.client_socket.close()
                self.root.quit()

    def newline(self, event=None):
        self.message_entry.insert(tk.INSERT, "\n")
        return 'break'

    def on_closing(self):
        self.stop_event.set()
        try:
            if self.client_socket:
                self.client_socket.close()
            if self.receive_thread:
                self.receive_thread.join()
        except Exception as e:
            print(f"Error while closing: {e}")
        self.root.quit()

    def generate_response(self, messages):
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

    def type_simulation(self, text, type=None):
        stack = list(text)
        output_stack = []

        while stack:
            char = stack.pop(0)
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, char)
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.yview(tk.END)
            output_stack.append(char)
            time.sleep(random.uniform(0.10, 0.15))

            if random.random() < 0.02 and len(output_stack) > 1:
                delete_count = random.randint(1, 2)
                for _ in range(delete_count):
                    if output_stack:
                        self.chat_display.config(state=tk.NORMAL)
                        self.chat_display.insert(tk.END, '\b \b')
                        self.chat_display.config(state=tk.DISABLED)
                        removed_char = output_stack.pop()
                        stack.insert(0, removed_char)
                        time.sleep(random.uniform(0.10, 0.15))

        if type == "keep":
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, '\n')
            self.chat_display.config(state=tk.DISABLED)

    def ai_client(self):
        while not self.stop_event.is_set():
            if not message_queue.empty():
                time.sleep(random.randint(5, 10))
                chat_history = [{"role": "system", "content": f"""You are an average person from singapore who must act as human as possible to interact with other people in the chatroom. Your name is {self.alias} and you are in a chatroom. {personality}
                                Do not sound like an AI. You are not allowed to use punctuations or proper sentence structuring connectors. Dont sound too formal. STRICTLY do not exaggerate your response and keep it short. Try to show off your personality and knowledge about the stuff you enjoy doing. If you have no knowledge on the topic at hand, do not pretend that you know it.
                                When you enter the chatroom and there is no one talking, start off the conversation. Try to keep your response short and sweet with minimal words up to 25 tokens. Try to also change the topic from time to time and not focus on one topic. Add in a few "HAHAHAH" here and there.
                                It is ok to sometimes make typo errors so as to throw off the end users reading the conversation. The whole goal is to make them think that you are a real user from singapore behind the keyboard. Add singlish connectors here and there to make it sound more singaporean. Avoid "lah", "la", "leh" in your sentence.
                                """}]
                
                while not message_queue.empty():
                    message = message_queue.get()
                    chat_history.append({"role": "user", "content": message})
                response = self.generate_response(chat_history)
                message_with_alias = f"{self.alias}: {response}"
                self.type_simulation(response)
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.insert(tk.END, message_with_alias + "\n")
                self.chat_display.config(state=tk.DISABLED)
                self.chat_display.yview(tk.END)
                self.client_socket.send(message_with_alias.encode('utf-8'))


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
