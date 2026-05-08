import tkinter as tk
from tkinter import scrolledtext
import threading
import re
import urllib.request
import urllib.parse
import html
import os
from datetime import datetime

class LouisAI2:
    def __init__(self, root):
        self.root = root
        self.root.title("LouisAI 2")
        self.root.geometry("1100x900")

        # Session Data
        self.dark_intensity = 0.0
        self.max_results = 5

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

        tk.Button(self.sidebar, text="+ CLEAR CHAT", command=self.reset_chat, bg="#75f9c1", relief="raised", bd=3).pack(fill="x", side="bottom", padx=10, pady=10)

        # 2. Main Chat Window
        self.top_bar = tk.Frame(self.root, bg="#ffffff", height=60, bd=5, relief="raised")
        self.top_bar.pack(fill="x", padx=10, pady=10)
        tk.Label(self.top_bar, text="LouisAI 2", font=("Arial Black", 20, "italic"), fg="#004a99", bg="#ffffff").pack()

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
                res = eval(self.calc_entry.get())
                self.calc_entry.delete(0, tk.END)
                self.calc_entry.insert(tk.END, str(res))
            except:
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
        self.display_logo()

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
                self.log("LouisAI 2", f"\n--- ASCII ART ---\n{ascii_art}\n-----------------")
            else:
                self.log("YOU", q)
                self.log("SYSTEM", "Usage: /asciigen (your text)")
            self.entry.delete(0, tk.END)
            return

        self.log("YOU", q)
        self.entry.delete(0, tk.END)

        bad_keywords = ["bad", "terrible", "fix", "error", "hate", "sucks"]
        if any(word in q.lower() for word in bad_keywords):
            self.log("LouisAI 2", "Feedback acknowledged.")
            return

        threading.Thread(target=self.engine_run, args=(q,), daemon=True).start()

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
                for snippet, source in results[:self.max_results]:
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
                    self.log("LouisAI 2", "\n\n".join(output))
                    return

            # Fallback to simple snippet extraction
            snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', content, re.DOTALL)
            if snippets:
                clean_snippet = re.sub(r'<[^>]+>', '', snippets[0]).strip()
                clean_snippet = html.unescape(clean_snippet)
                clean_snippet = re.sub(r'\.\.\.$', '', clean_snippet)
                if clean_snippet:
                    self.log("LouisAI 2", clean_snippet)
                    return

            # Final fallback - try to get any text content
            text_content = re.sub(r'<[^>]+>', ' ', content)
            text_content = html.unescape(text_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            if len(text_content) > 100:
                self.log("LouisAI 2", text_content[:500])
            else:
                self.log("LouisAI 2", "No information found.")

        except Exception as e:
            self.log("SYSTEM", f"Search error: {str(e)}")

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
    LouisAI2(root)
    root.mainloop()