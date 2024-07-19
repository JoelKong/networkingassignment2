import tkinter as tk
import random
import time
import threading

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
    """Get a typo character close to the original char based on QWERTY neighbors."""
    if char in qwerty_neighbors:
        return random.choice(qwerty_neighbors[char])
    return char  # If no neighbors defined, return the same character

def simulate_typing(textbox, text, min_interval, max_interval, typo_chance, fix_typo):
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
            # Random delay before fixing the typo
            time.sleep(random.uniform(min_interval, max_interval))
            # Make a typo (insert a neighboring character)
            typo_char = get_typo_char(char)
            textbox.insert(tk.END, typo_char)
            textbox.update()
            if fix_typo:
                # Delay before deleting the typo
                time.sleep(random.uniform(min_interval, max_interval))
                # Delete the typo character
                textbox.delete('end-2c', tk.END)
                textbox.update()

def start_typing():
    text = "This is a simulated typing example with random intervals and typos."
    min_interval = float(min_interval_entry.get())
    max_interval = float(max_interval_entry.get())
    typo_chance = float(typo_chance_entry.get())
    fix_typo = fix_typo_var.get()
    threading.Thread(target=simulate_typing, args=(textbox, text, min_interval, max_interval, typo_chance, fix_typo)).start()

# Set up the GUI
root = tk.Tk()
root.title("Typing Simulation")

textbox = tk.Text(root, width=60, height=10, wrap='word')
textbox.pack(padx=20, pady=20)

controls_frame = tk.Frame(root)
controls_frame.pack(pady=10)

tk.Label(controls_frame, text="Min Interval:").grid(row=0, column=0, padx=5, pady=5)
min_interval_entry = tk.Entry(controls_frame)
min_interval_entry.grid(row=0, column=1, padx=5, pady=5)
min_interval_entry.insert(0, "0.05")

tk.Label(controls_frame, text="Max Interval:").grid(row=1, column=0, padx=5, pady=5)
max_interval_entry = tk.Entry(controls_frame)
max_interval_entry.grid(row=1, column=1, padx=5, pady=5)
max_interval_entry.insert(0, "0.3")

tk.Label(controls_frame, text="Typo Chance:").grid(row=2, column=0, padx=5, pady=5)
typo_chance_entry = tk.Entry(controls_frame)
typo_chance_entry.grid(row=2, column=1, padx=5, pady=5)
typo_chance_entry.insert(0, "0.1")

fix_typo_var = tk.BooleanVar(value=True)
fix_typo_check = tk.Checkbutton(controls_frame, text="Fix Typos", variable=fix_typo_var)
fix_typo_check.grid(row=3, columnspan=2, pady=5)

start_button = tk.Button(root, text="Start Typing", command=start_typing)
start_button.pack(pady=10)

root.mainloop()
