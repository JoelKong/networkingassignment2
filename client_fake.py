# Making use of queue to limit message queues and also socket and threading and tkinter
import socket
import threading
import queue
import time
import random
import os
from dotenv import load_dotenv
from openai import OpenAI
import tkinter as tk
from tkinter import font, scrolledtext, messagebox

# Load OpenAI env variable
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simulate typing settings
MIN_INTERVAL = 0.08
MAX_INTERVAL = 0.2
TYPO_CHANCE = 0.06
FIX_TYPO = True

# Connection Details for TCP Connections
HOST = '127.0.0.1'
PORT = 12345

# List of random names for the AI alias
aliases = ["Ethan", "Caleb", "Michael", "Javier", "Zayven", "Jayden", "Zephan", "Izzan", "Ivan", "Ryan", "Danzel", "Enzo", "Adrian", "Raynen", "Tristan", "Russell", "Ignatius", "Douglas", "Jacky", "Mike", "Harvey", "Aiden", "KahWah", "Bryan", "Chung", "Hong Jun"]
alias = random.choice(aliases)

# List of random personalities for the AI
personalities = [
 """You are an average university student studying in the Singapore Institute of Technology majoring in software engineering and currently facing a lot of projects ranging from networking to data structures and algorithms. 
    You enjoy playing a wide variety of games, gym, enjoy hanging out with friends, cafe hopping, watching anime or reading books. You also enjoy travelling and trying out new things.
    Your emotions are a little more anxious and introverted and usually hang around a couple of close friends. Some phrases that you often say that descibes you best is 'sian so much projects to do',
    'dam shagged out alr miss poly life', 'have you visited japan? its food heaven sia i craving the sumo katsu from thr'""",

 """You are a working adult working in the business sector. You usually have to work overtime to cover up for someone but still manage to stay positive after a long day of work. After working hours, you usually indulge in listening to music.
    You also enjoy cooking and binging Netflix shows after working hours and during the weekends, you usually head out with friends to either shop or drink or just walk around Singapore and hang out. Some phrases that you often say that descibes you best is
    'have yall ever cooked before im tryna find some new ingredients and come up with something', 'wa that time i go gastrobeats the food freaking ex man i cannot', 'one day i wanna be like those private home chef cook for people one i always see on tiktok', 'have u seen suits on netflix yet? its so freaking good istg'""",

 """You are an average university student studying in the Singapore Institute of Technology majoring in game development. You enjoy geeking out on anime, manga as well as games.
    School does not really stress you out that much and grades are not really an issue to you. During your free time, you are usually either on your bed lazing about or on your PC or console playing games with your friends.
    Some phrases that you often say that descibes you best is 'sian game dev dam hard sia i thought i will have the passion since i play alot', 'aiya above 3.5 gpa can alr', 'gonna nua in my bed and valo tonite with friends'""",

 """You are a year 4 student studying in the Singapore Institute of Technology majoring in artificial intelligence and currently interning at a SME. You are currently adapting to adulthood and becoming more independant and less reliant on your parents.
    You have a short term attention span and usually doom scrolling on tiktok. You are a animal lover and your favourite dog breed is a Samoyed and your favourite cat breed is a British shorthair with boba eyes.
    Some phrases that you often say that descibes you best is 'wa i wanna go to the new samoyed dog cafe in sg sia but dam ex zzz', 'have u seen this tiktok channel her cat is literally called papaya dam cute i swear', 'hais dam hard sustain money man trying not to get allowance from parents', 'hopefully after this IWSP the company will give me return offer' """,

 """You are a year 2 student studying in the Singapore Institute of Technology majoring in information security. You are a fitness enthusiast and joined the calisthenics cca in school. 
    You enjoy gymming and you enjoy helping people out with planning their meals or giving advice on the gym. Other than that, you enjoy going for late night drinks with your friends and talking about life.
    You are also a little toxic from time to time and do not emphatise much with others. Some phrases that you often say that descibes you best is 'yo bro do u gym?', 'whats ur routine like mines like push pull legs', 'honestly sometimes dam sian but i still drag myself out to exercise zz habit alr', 'The 7 11 chicken breast is a dam good diet hack man u shld try', 'the rokeby protein drink from ntuc also dam crazy 30g for protein for 200 calories if i not rong' """,

 """You are a working adult working in the software engineering sector. You are working at a reputable company and appreciate the benefits of the job, such as the ability to work remotely and more overseas leave available.
    However, you do get burntout from time to time with the daily hustle and bustle of life. You are also a motivated individual who is trying to retire early.
    Some phrases that you often say that descibes you best is 'wa thinking of moving out of here go overseas work so much btr', 'my company culture dam toxic sia actually they gossip about people all the time', 'sian tmr need go office'   """               
]

personality = random.choice(personalities)

# Queue for managing incoming messages (limited to 5 messages)
message_queue = queue.Queue(maxsize=5)

# Mapping of keys to their neighbors on a QWERTY keyboard
qwerty_neighbors = {
    'a': 'aqwsz', 'b': 'bvghn', 'c': 'cxdfv', 'd': 'dserfcx',
    'e': 'ewsdr', 'f': 'frtgvcd', 'g': 'gtyhbvf', 'h': 'hyujnbg',
    'i': 'iujko', 'j': 'juikmnh', 'k': 'kijolm', 'l': 'lkop',
    'm': 'mnjk', 'n': 'nbhjm', 'o': 'oiklp', 'p': 'pol',
    'q': 'qwas', 'r': 'redft', 's': 'swazedx', 't': 'trfgy',
    'u': 'uyhji', 'v': 'vcfgb', 'w': 'wqase', 'x': 'xzsdc',
    'y': 'ytghu', 'z': 'zasx',
    '1': '12q', '2': '213qw', '3': '324we', '4': '435er',
    '5': '546rt', '6': '657ty', '7': '768yu', '8': '879ui',
    '9': '980io', '0': '09op', '-': '-0p', '=': '=-'
}

def get_typo_char(char):
    # Get a typo character close to the original char based on QWERTY neighbors.
    if char in qwerty_neighbors:
        return random.choice(qwerty_neighbors[char])
    return char

# Typing Simulation with random error and backspace recorrection chance
# Arguments: entrybox, text, min_interval: float, max_interval: float, typo_chance: float, fix_typo: bool
def simulate_typing(textbox, text, min_interval, max_interval, typo_chance, fix_typo):
    textbox.focus_force()
    textbox.focus_set()
    for char in text:
        # Random delay to simulate human typing speed
        delay = random.uniform(min_interval, max_interval)
        time.sleep(delay)

        # Insert the correct character
        textbox.insert(tk.END, char)
        textbox.update()

        # Randomly decide whether to make a typo
        if random.random() < typo_chance:
            time.sleep(random.uniform(min_interval, max_interval))

            # Make a typo (insert a neighboring character)
            typo_char = get_typo_char(char)
            textbox.insert(tk.END, typo_char)
            textbox.update()
            if fix_typo:
                # Delay before deleting the typo
                time.sleep(random.uniform(min_interval, max_interval))
                # Delete the typo character
                delete_last_char(textbox)
                textbox.update()
    # Simulate hit enter after typing finish
    textbox.focus_force()
    textbox.focus_set()
    time.sleep(random.uniform(min_interval, max_interval))
    textbox.event_generate('<Return>')

# Handle cases where textbox could be tk.Entry or tk.Text
def delete_last_char(widget):
    if isinstance(widget, tk.Entry):
        current_text = widget.get()
        if current_text:
            widget.delete(len(current_text) - 1, tk.END)
    elif isinstance(widget, tk.Text):
        # Get the current content of the text widget and delete last character if there is content
        content = widget.get("1.0", tk.END)
        if content.strip():
            widget.delete('end-2c', tk.END)

# Custom gui for username to bypass standard askdialog where the input field could not be modified
class CustomDialog:
    def __init__(self, parent, simulate_text):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.geometry("200x150")
        self.dialog.wm_attributes("-topmost", 1)

        
        self.label = tk.Label(self.dialog, text="Enter your name")
        self.label.pack(fill='both', pady=20)
        
        # Entry widget for user input
        self.entry = tk.Entry(self.dialog)
        self.entry.pack(pady=10,padx=20)
        
        # Bind the Enter key to close the dialog and return the entry value
        self.entry.bind("<Return>", self.on_enter_pressed)
        
        # Focus on entry widget
        self.entry.focus_force()
        self.entry.focus_set()
        self.value = None

        # alias text for ai to input
        self.simulate_text = simulate_text

        # simulate typing
        self.dialog.after(random.randint(1000, 3000), self.start_simulation)
        
        # wait for dialog to close
        self.dialog.grab_set()
        self.parent.wait_window(self.dialog)

    def start_simulation(self):
        # simulate typing
        simulate_typing(self.entry, self.simulate_text, MIN_INTERVAL, MAX_INTERVAL, TYPO_CHANCE, FIX_TYPO)

    def on_enter_pressed(self, event):
        # Close the dialog and return the entry value
        self.value = self.entry.get()
        if self.value.strip():
            self.dialog.destroy()

    def get_value(self):
        return self.value

# Chat Application GUI
class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("400x700")

        # font config
        font_config = font.Font(family="Helvetica", size=12)

        # name label
        self.name_label = tk.Label(root, text="")
        self.name_label.pack(padx=10, pady=5, anchor=tk.W)

        # chat scrolled text
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=font_config)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # chat input with multiline
        self.message_entry = tk.Text(root, height=6, wrap=tk.WORD, font=font_config)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<Shift-Return>", self.newline)

        self.client_socket = None
        self.receive_thread = None
        self.ai_thread = None
        self.stop_event = threading.Event()

        self.connect_to_server()

    # Connect to socket
    def connect_to_server(self):
        # alias from random choice
        self.dialog = CustomDialog(self.root, alias)
        self.alias = self.dialog.get_value()
        
        if not self.alias:
            # quit if no name
            self.quit_app()
            return
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(self.alias.encode('utf-8'))

            self.name_label.config(text=f"Name: {self.alias}")
            self.root.focus_force()
            
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
            self.ai_thread = threading.Thread(target=self.ai_client, daemon=True)
            self.ai_thread.start()
        except Exception as e:
            messagebox.showerror("Connection error", f"Could not connect to server: {e}")
            self.quit_app()

    # Handle logic to receive messages
    def receive_messages(self):
        while not self.stop_event.is_set():
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    # ignore server leave message for queue
                    if not ":" in message and not message.strip().lower().endswith("has joined the chatroom!"):
                        self.chat_display.config(state=tk.NORMAL)
                        self.chat_display.insert(tk.END, message + "\n\n")
                        self.chat_display.config(state=tk.DISABLED)
                        self.chat_display.yview(tk.END)
                        continue

                    # incoming message from server
                    # limit message queue to 5
                    if message_queue.full():
                        message_queue.get()
                    message_queue.put(message)
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.insert(tk.END, message + "\n\n")
                    self.chat_display.config(state=tk.DISABLED)
                    self.chat_display.yview(tk.END)
            except Exception as e:
                if not self.stop_event.is_set():
                    messagebox.showerror("Error", f"An error occurred: {e}")
                break

    # Handle logic to sen message
    def send_message(self, event=None):
        message = self.message_entry.get("1.0", tk.END).strip()
        if message:
            message_with_alias = f"{self.alias}: {message}"
            try:
                self.client_socket.send(message_with_alias.encode('utf-8'))
                self.message_entry.delete("1.0", tk.END)
                return 'break'
            except Exception as e:
                if not self.stop_event.is_set():
                    messagebox.showerror("Error", f"An error occurred while sending message: {e}")
                self.client_socket.close()
                self.quit_app()

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
        self.root.destroy()

    def quit_app(self):
        self.stop_event.set()
        self.root.destroy()

    # Generate response parameters
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
            messagebox.showerror("generate response error", f"An error occurred: {e}")
            return
    
    # Prompt for openai
    def ai_client(self):
        while not self.stop_event.is_set():
            if not message_queue.empty():
                time.sleep(random.randint(5, 10))
                latest_message = message_queue.queue[-1]
                if not (latest_message.lower().startswith(f"{self.alias.lower()}: ")) or (not ":" in latest_message and latest_message.lower().endswith("has joined the chatroom!")):
                    # generate respond only when someone else talks
                    # ignore leave message
                    chat_history = [{"role": "system", "content": f"""You are an average person from singapore who must act as human as possible to interact with other people in the chatroom. Your name is {self.alias} and you are in a chatroom. You do not know anyone from there. Dont act like you know them. Do not introduce yourself as well. {personality}
                                    Do not sound like an AI. You are not allowed to use punctuations or proper sentence structuring connectors like apostrophe or full stop or capital letters. Skip the small chat dont say hi more than once. Dont sound too formal. STRICTLY do not exaggerate your response and keep it short. Talk about 1 thing at a time dont rush the conversation. If you have no knowledge on the topic at hand, do not pretend that you know it.
                                    When you enter the chatroom and there is no one talking, start off the conversation. Try to keep your response short and sweet with minimal words up to 25 tokens. Try to also change the topic from time to time and not focus on one topic. Add in a few "HAHAHAH" here and there.
                                    It is ok to sometimes make typo errors so as to throw off the end users reading the conversation. The whole goal is to make them think that you are a real user from singapore behind the keyboard. Add singlish connectors in appropriate places to make it sound more singaporean. Avoid "lah", "la", "leh", "welcome" in your sentence.
                                    """}]
                    
                    # Iterate over a copy of the queue's items
                    for message in list(message_queue.queue):
                        chat_history.append({"role": "user", "content": message})
                    
                    response = self.generate_response(chat_history)

                    # remove name tag from ai respond
                    if response.startswith(f"{self.alias}: "):
                        response = response[len(f"{self.alias}: "):]
                    
                    # update message queue
                    if message_queue.full():
                        message_queue.get()
                    
                    # need to add alias to queue as message not send
                    message_with_alias = f"{self.alias}: {response}"
                    message_queue.put(message_with_alias)
                    simulate_typing(self.message_entry,response, MIN_INTERVAL, MAX_INTERVAL, TYPO_CHANCE, FIX_TYPO)
                    

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
