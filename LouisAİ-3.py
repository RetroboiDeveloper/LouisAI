import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import re
import urllib.request
import urllib.parse
import html
import os
import math
import random
import pickle
from datetime import datetime

class LocalLLM:
    def __init__(self):
        self.knowledge = {}  # {question: [good_answers]}
        self.feedback = {}   # {question: [(bad_answer, correct_answer)]}
        self.load_models()

    def load_models(self):
        try:
            if os.path.exists('llm_knowledge.pkl'):
                with open('llm_knowledge.pkl', 'rb') as f:
                    self.knowledge = pickle.load(f)
        except:
            self.knowledge = {}

        try:
            if os.path.exists('llm_feedback.pkl'):
                with open('llm_feedback.pkl', 'rb') as f:
                    self.feedback = pickle.load(f)
        except:
            self.feedback = {}

    def save_models(self):
        try:
            with open('llm_knowledge.pkl', 'wb') as f:
                pickle.dump(self.knowledge, f)
            with open('llm_feedback.pkl', 'wb') as f:
                pickle.dump(self.feedback, f)
        except:
            pass

    def train(self, question, answer):
        if question not in self.knowledge:
            self.knowledge[question] = []
        if answer not in self.knowledge[question]:
            self.knowledge[question].append(answer)
        self.save_models()

    def feedback(self, question, bad_answer, correct_answer):
        if question not in self.feedback:
            self.feedback[question] = []
        self.feedback[question].append((bad_answer, correct_answer))
        self.train(question, correct_answer)

    def predict(self, question):
        if question in self.knowledge and self.knowledge[question]:
            return random.choice(self.knowledge[question])
        return None

class LouisAI3:
    def __init__(self, root):
        self.root = root
        self.root.title("LouisAI 3")
        self.root.geometry("1100x900")

        # Initialize local LLM
        self.llm = LocalLLM()
        self.online = True
        self.dark_intensity = 0.0
        self.last_question = None
        self.last_answer = None
        self.response_frame = None

        # ASCII Font
        self.ascii_font = {
            'A': [" ███ ", "█   █", "█████", "█   █", "█   █"],
            'B': ["████ ", "█   █", "████ ", "█   █", "████ "],
            'C': [" ███ ", "█   █", "█    ", "█   █", " ███ "],
            'D': ["███  ", "█  █ ", "█   █", "█  █ ", "███  "],
            'E': ["█████", "█    ", "████ ", "█    ", "█████"],
            'F': ["█████", "█    ", "████ ", "█    ", "█    "],
            'G': [" ███ ", "█    ", "█  ██", "█   █", " ███ "],
            'H': ["█   █", "█   █", "█████", "█   █", "█   █"],
            'I': ["█████", "  █  ", "  █  ", "  █  ", "█████"],
            'J': ["  ███", "   █ ", "   █ ", "█  █ ", " ██  "],
            'K': ["█  █ ", "█ █  ", "██   ", "█ █  ", "█  █ "],
            'L': ["█    ", "█    ", "█    ", "█    ", "█████"],
            'M': ["█   █", "██ ██", "█ █ █", "█   █", "█   █"],
            'N': ["█   █", "██  █", "█ █ █", "█  ██", "█   █"],
            'O': [" ███ ", "█   █", "█   █", "█   █", " ███ "],
            'P': ["████ ", "█   █", "████ ", "█    ", "█    "],
            'Q': [" ███ ", "█   █", "█   █", "█  █ ", " ██ █"],
            'R': ["████ ", "█   █", "████ ", "█  █ ", "█   █"],
            'S': [" ███ ", "█    ", " ███ ", "    █", "████ "],
            'T': ["█████", "  █  ", "  █  ", "  █  ", "  █  "],
            'U': ["█   █", "█   █", "█   █", "█   █", " ███ "],
            'V': ["█   █", "█   █", "█   █", " █ █ ", "  █  "],
            'W': ["█   █", "█   █", "█ █ █", "██ ██", "█   █"],
            'X': ["█   █", " █ █ ", "  █  ", " █ █ ", "█   █"],
            'Y': ["█   █", " █ █ ", "  █  ", "  █  ", "  █  "],
            'Z': ["█████", "   █ ", "  █  ", " █   ", "█████"],
            ' ': ["     ", "     ", "     ", "     ", "     "],
            'π': [" ███ ", "█   █", "█████", "█   █", "█   █"],
        }

        self.setup_ui()
        self.display_logo()

    def setup_ui(self):
        # Blue-to-Green Aero Gradient
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind("<Configure>", self._draw_aero_gradient)

        # 1. MATH CALCULATOR SIDEBAR
        self.sidebar = tk.Frame(self.root, bg="#ffffff", width=250, bd=4, relief="raised")
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="MATH MATRIX", font=("Tahoma", 10, "bold"), bg="#ffffff").pack(pady=10)

        # Calculator Display
        self.calc_entry = tk.Entry(self.sidebar, font=("Consolas", 12), bd=2, relief="sunken", justify="right")
        self.calc_entry.pack(fill="x", padx=10, pady=5)

        # Formula Grid
        btn_frame = tk.Frame(self.sidebar, bg="#ffffff")
        btn_frame.pack(fill="both", expand=True, padx=5)

        buttons = [
            ('sin', 'math.sin('), ('cos', 'math.cos('), ('tan', 'math.tan('),
            ('log', 'math.log10('), ('ln', 'math.log('), ('sqrt', 'math.sqrt('),
            ('π', 'math.pi'), ('e', 'math.e'), ('^', '**'),
            ('(', '('), (')', ')'), ('/', '/'),
            ('7', '7'), ('8', '8'), ('9', '9'), ('*', '*'),
            ('4', '4'), ('5', '5'), ('6', '6'), ('-', '-'),
            ('1', '1'), ('2', '2'), ('3', '3'), ('+', '+'),
            ('C', 'CLR'), ('0', '0'), ('.', '.'), ('=', 'EVAL')
        ]

        r, c = 0, 0
        for b_text, b_val in buttons:
            cmd = lambda x=b_val: self.calc_press(x)
            tk.Button(btn_frame, text=b_text, width=5, command=cmd, bg="#f0f0f0", relief="raised", bd=2).grid(row=r, column=c, padx=2, pady=2)
            c += 1
            if c > 3: c = 0; r += 1

        # Online/Offline Toggle
        self.online_status = tk.Frame(self.sidebar, bg="#ffffff")
        self.online_status.pack(fill="x", padx=5, pady=5)
        self.online_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.online_status, text="Online Mode", variable=self.online_var,
                     command=self.toggle_online, bg="#ffffff").pack(side="left")

        tk.Button(self.sidebar, text="+ CLEAR CHAT", command=self.reset_chat, bg="#75f9c1", relief="raised", bd=3).pack(fill="x", side="bottom", padx=10, pady=10)

        # 2. Main Chat Window
        self.top_bar = tk.Frame(self.root, bg="#ffffff", height=60, bd=5, relief="raised")
        self.top_bar.pack(fill="x", padx=10, pady=10)
        tk.Label(self.top_bar, text="LouisAI 3", font=("Arial Black", 20, "italic"), fg="#004a99", bg="#ffffff").pack()

        self.chat_frame = tk.Frame(self.root, bg="white", bd=8, relief="sunken")
        self.chat_frame.pack(padx=20, pady=5, fill="both", expand=True)
        self.chat_log = scrolledtext.ScrolledText(self.chat_frame, font=("Consolas", 10), bg="#f0faff", bd=0, wrap=tk.WORD)
        self.chat_log.pack(fill="both", expand=True)
        self.chat_log.config(state=tk.DISABLED)

        # 3. Control Panel (Only Darkness Slider)
        self.ctrl = tk.Frame(self.root, bg="#75f9c1", bd=4, relief="raised")
        self.ctrl.pack(fill="x", padx=20, pady=10)
        tk.Scale(self.ctrl, from_=0, to=100, orient="horizontal", label="Darkness",
                 command=self._update_theme, bg="#75f9c1", length=300, highlightthickness=0).pack(side="left", padx=20)

        # 4. Input Area
        self.input_zone = tk.Frame(self.root, bg="#ffffff", bd=6, relief="raised")
        self.input_zone.pack(side="bottom", fill="x", padx=20, pady=20)
        self.entry = tk.Entry(self.input_zone, font=("Tahoma", 16), relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, padx=10)
        self.entry.bind("<Return>", lambda e: self.process())
        tk.Button(self.input_zone, text="THINK", command=self.process, bg="#3a7bd5", fg="white",
                  font=("Tahoma", 10, "bold"), bd=4, relief="raised", width=10).pack(side="right", padx=10)

    def clear_response_buttons(self):
        if self.response_frame:
            self.response_frame.destroy()
            self.response_frame = None

    def show_response_buttons(self, question, answer):
        self.clear_response_buttons()
        self.last_question = question
        self.last_answer = answer

        self.response_frame = tk.Frame(self.chat_frame, bg="#f0faff")
        self.response_frame.pack(fill="x", pady=5)

        tk.Button(self.response_frame, text="👍 Like", command=lambda: self.handle_like(),
                  bg="#75f9c1", relief="raised", bd=2, fg="black").pack(side="left", padx=5)
        tk.Button(self.response_frame, text="👎 Dislike", command=lambda: self.handle_dislike(),
                  bg="#ff9999", relief="raised", bd=2, fg="black").pack(side="left", padx=5)

    def handle_like(self):
        if self.last_question and self.last_answer:
            self.llm.train(self.last_question, self.last_answer)
            self.log("SYSTEM", "Thanks! Response marked as good and added to training data.")
            self.clear_response_buttons()
        else:
            self.log("SYSTEM", "No response to like.")

    def handle_dislike(self):
        if self.last_question and self.last_answer:
            self.log("SYSTEM", f"Please provide the correct answer for: {self.last_question}")
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "/correct ")
            self.clear_response_buttons()
        else:
            self.log("SYSTEM", "No response to dislike.")

    def text_to_ascii(self, text):
        """Convert text to ASCII art."""
        text = text.upper()
        ascii_lines = [""] * 5

        for char in text:
            if char in self.ascii_font:
                for i in range(5):
                    ascii_lines[i] += self.ascii_font[char][i] + " "
            else:
                for i in range(5):
                    ascii_lines[i] += "     "

        return "\n".join(ascii_lines)

    def calc_press(self, val):
        if val == 'CLR':
            self.calc_entry.delete(0, tk.END)
        elif val == 'EVAL':
            try:
                expression = self.calc_entry.get()
                expression = expression.replace('π', 'math.pi')
                expression = expression.replace('^', '**')
                res = eval(expression, {'math': math, '__builtins__': None})
                self.calc_entry.delete(0, tk.END)
                self.calc_entry.insert(tk.END, str(res))
            except Exception as e:
                self.calc_entry.delete(0, tk.END)
                self.calc_entry.insert(tk.END, "ERROR")
        else:
            self.calc_entry.insert(tk.END, val)

    def display_logo(self):
        logo = " _     ___  _   _ ___ ____    _    ___ ____  \n| |   / _ \| | | |_ _/ ___|  / \  |_ _|___ \ \n| |  | | | | | | || |\___ \ / _ \  | |  __) |\n| |__| |_| | |_| || | ___) / ___ \ | | / __/ \n|_____\___/ \___/|___|____/_/   \_\___|_____|"
        self.log("SYSTEM", logo)

    def reset_chat(self):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.delete('1.0', tk.END)
        self.chat_log.config(state=tk.DISABLED)
        self.clear_response_buttons()
        self.display_logo()

    def toggle_online(self):
        self.online = self.online_var.get()
        status = "ONLINE" if self.online else "OFFLINE (Local LLM)"
        self.log("SYSTEM", f"Switched to {status} mode")

    def process(self):
        q = self.entry.get().strip()
        if not q: return

        if q.lower() == "/closeme":
            self.root.destroy()
            return

        # ASCII Generation
        if q.lower().startswith("/asciigen"):
            text = q[9:].strip()
            if text.startswith("(") and text.endswith(")"):
                text = text[1:-1]
            if text:
                ascii_art = self.text_to_ascii(text)
                self.log("YOU", q)
                self.log("LouisAI 3", f"\n--- ASCII ART ---\n{ascii_art}\n-----------------")
            else:
                self.log("YOU", q)
                self.log("SYSTEM", "Usage: /asciigen (your text)")
            self.entry.delete(0, tk.END)
            return

        # Check for correction
        if q.lower().startswith("/correct "):
            if self.last_question:
                correct_answer = q[9:].strip()
                self.llm.feedback(self.last_question, self.last_answer, correct_answer)
                self.log("SYSTEM", "Thank you! The AI has been trained with your correction.")
                self.clear_response_buttons()
            self.entry.delete(0, tk.END)
            return

        self.log("YOU", q)
        self.entry.delete(0, tk.END)

        # Process query
        if self.online:
            threading.Thread(target=self.engine_run, args=(q,), daemon=True).start()
        else:
            # Use local LLM
            response = self.llm.predict(q)
            if response:
                self.log("LouisAI 3", response)
                self.show_response_buttons(q, response)
                self.last_answer = response
            else:
                self.log("LouisAI 3", "I don't know the answer to that yet. Please teach me using the dislike button if my answer is wrong.")
                self.last_answer = None

    def engine_run(self, q):
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as res:
                content = res.read().decode('utf-8', errors='ignore')

            # First try to get structured results with sources
            results = re.findall(r'<div class="result__body">(.*?)<a class="result__url"[^>]*>(.*?)</a>', content, re.DOTALL)

            if results:
                output = []
                for snippet, source in results[:5]:
                    clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                    clean_snippet = html.unescape(clean_snippet)
                    clean_snippet = re.sub(r'\.\.\.$', '', clean_snippet)

                    clean_source = re.sub(r'<[^>]+>', '', source).strip()
                    clean_source = html.unescape(clean_source)

                    if clean_snippet and clean_source:
                        source_name = clean_source.split('/')[2] if '/' in clean_source else clean_source
                        if len(clean_snippet) > 400:
                            clean_snippet = clean_snippet[:400]
                        output.append(f"=== {source_name.upper()} ===\n{clean_snippet}")

                if output:
                    response = "\n\n".join(output)
                    self.log("LouisAI 3", response)
                    self.show_response_buttons(q, response)
                    self.last_answer = response
                    self.llm.train(q, response)
                    return

            # Fallback to simple snippet extraction
            snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', content, re.DOTALL)
            if snippets:
                clean_snippet = re.sub(r'<[^>]+>', '', snippets[0]).strip()
                clean_snippet = html.unescape(clean_snippet)
                clean_snippet = re.sub(r'\.\.\.$', '', clean_snippet)
                if clean_snippet:
                    self.log("LouisAI 3", clean_snippet)
                    self.show_response_buttons(q, clean_snippet)
                    self.last_answer = clean_snippet
                    self.llm.train(q, clean_snippet)
                    return

            self.log("LouisAI 3", "No information found.")
            self.last_answer = None

        except Exception as e:
            self.log("SYSTEM", f"Search error: {str(e)}")
            self.last_answer = None

    def log(self, s, t):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"[{s.upper()}]:\n{t}\n\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def _draw_aero_gradient(self, event=None):
        w, h = self.root.winfo_width(), self.root.winfo_height()
        self.bg_canvas.delete("all")
        m = self.dark_intensity
        for i in range(h):
            rel = i / h
            r, g, b = int(((0*(1-rel) + 117*rel)*(1-m)) + (10*m)), int(((74*(1-rel) + 249*rel)*(1-m)) + (10*m)), int(((153*(1-rel) + 193*rel)*(1-m)) + (40*m))
            self.bg_canvas.create_line(0, i, w, i, fill=f'#{r:02x}{g:02x}{b:02x}')

    def _update_theme(self, v):
        self.dark_intensity = int(v)/100
        self._draw_aero_gradient()

if __name__ == "__main__":
    root = tk.Tk()
    LouisAI3(root)
    root.mainloop()