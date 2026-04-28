import tkinter as tk
from tkinter import scrolledtext
import urllib.request
import urllib.parse
import re
import threading
import webbrowser

class LouisAI:
    def __init__(self, root):
        self.root = root
        self.root.title("LouisAI 1.0")
        self.root.geometry("750x900")
        
        # Language Matrix
        self.langs = {0: "ENGLISH", 1: "RUSSIAN", 2: "GERMAN", 3: "TURKISH"}
        self.current_lang = "ENGLISH"
        
        self.setup_ui()

    def setup_ui(self):
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind("<Configure>", self._draw_gradient)

        # Header 🫧
        self.header = tk.Label(self.root, text="LouisAI 1.0 🫧", font=("Segoe UI", 36, "bold"), 
                               fg="white", bg="#00d2ff")
        self.header.pack(pady=20)

        # Chat Log - Navy text for clarity
        self.chat_log = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Segoe UI", 12),
            bg="#f0faff", fg="#001a33", bd=0, highlightthickness=3, highlightbackground="white"
        )
        self.chat_log.pack(padx=40, pady=10, fill="both", expand=True)
        self.chat_log.config(state=tk.DISABLED)

        # Language Status Bar
        self.status = tk.Label(
            self.root, text=f"SIGNAL MODE: {self.current_lang}",
            font=("Segoe UI", 10, "bold"), fg="#004d40", bg="#b2dfdb", padx=15, pady=5
        )
        self.status.pack(pady=10)

        # Controls
        ctrl = tk.Frame(self.root, bg="#00d2ff")
        ctrl.pack(pady=20, fill="x", padx=40)

        self.slider = tk.Scale(
            ctrl, from_=0, to=3, orient=tk.HORIZONTAL,
            showvalue=0, command=self.update_lang, bg="#00d2ff",
            highlightthickness=0, length=120, troughcolor="white"
        )
        self.slider.pack(side="left")

        self.input_field = tk.Entry(ctrl, font=("Segoe UI", 14), bg="white", fg="#001a33", relief="flat", bd=10)
        self.input_field.pack(side="left", fill="x", expand=True, padx=10)
        self.input_field.bind("<Return>", lambda e: self.start_search())

        self.bolt_btn = tk.Button(ctrl, text="Send", font=("Segoe UI", 11, "bold"), bg="white", command=self.start_search)
        self.bolt_btn.pack(side="right")

    def update_lang(self, val):
        self.current_lang = self.langs[int(val)]
        self.status.config(text=f"SIGNAL MODE: {self.current_lang}")

    def _draw_gradient(self, event=None):
        self.bg_canvas.delete("all")
        w, h = self.root.winfo_width(), self.root.winfo_height()
        steps = 50
        for i in range(steps):
            r = int(0 + (145 - 0) * (i / steps))
            g = int(210 + (255 - 210) * (i / steps))
            b = int(255 + (174 - 255) * (i / steps))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.bg_canvas.create_rectangle(0, i*(h/steps), w, (i+1)*(h/steps), fill=color, outline=color)

    def log(self, sender, text):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"{sender}: {text}\n\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def start_search(self):
        query = self.input_field.get().strip()
        if not query: return
        self.log("YOU", query)
        self.input_field.delete(0, tk.END)
        threading.Thread(target=self.research_engine, args=(query,), daemon=True).start()

    def research_engine(self, query):
        low_q = query.lower()
        
        # Local Knowledge Base
        if "dolfiniez" in low_q:
            res = ("SEARCH RESULT: DOLFINIEZ\n\nSoftware engineer and hardware creator. "
                   "Architect of the LouisAI system. Specializes in Python-based "
                   "Frutiger Aero development and Arduino integration.")
            self.log("LOUIS", res)
            webbrowser.open("https://www.youtube.com/@Dolfiniez")
            return

        # Open Source Web Parsing
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
                snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', html, re.DOTALL)
                if snippets:
                    clean = [re.sub('<[^<]+?>', '', s).strip() for s in snippets[:3]]
                    self.log(f"LOUIS ({self.current_lang})", f"LIVE DATA:\n\n{' '.join(clean)}")
                else:
                    self.log("LOUIS", "No open data snippets found for this specific query.")
        except:
            self.log("LOUIS", "Network stream offline. Check connection.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LouisAI(root)
    root.mainloop()