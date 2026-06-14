# -*- coding: utf-8 -*-
import sys
import json
import os
import re
import time
from datetime import datetime

# --- COMPATIBILITY LAYER FOR PYTHON 2/3 ---
try:
    # Python 3
    import urllib.request as urllib2
    import urllib.parse
    from html import unescape
except ImportError:
    # Python 2
    import urllib2
    import urllib
    from HTMLParser import HTMLParser
    unescape = HTMLParser().unescape

class LouisAILight:
    def __init__(self):
        self.machine_user = "User"  # Fallback for iPad/unsupported systems
        try:
            self.machine_user = os.getlogin()  # Works on most systems
        except:
            pass
        self.current_conv_id = datetime.now().strftime("%Y%m%d_%H%M")
        self.greetings = {"hello", "hi", "hey", "greetings", "sup", "yo"}
        self.bad_review_keywords = ["bad", "terrible", "fix", "error", "hate", "sucks", "broken", "trash", "bug"]

    def log(self, sender, message):
        """Prints and logs messages to a JSON file."""
        print(f"{sender.upper()}: {message}\n")
        filename = f"Log_{self.current_conv_id}.json"
        data = []
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
            except:
                data = []
        data.append({
            "user": sender,
            "msg": message,
            "time": str(datetime.now())
        })
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def run_engine(self, q):
        """Fetches web search results using DuckDuckGo (HTML version)."""
        try:
            # Python 3
            if sys.version_info[0] >= 3:
                search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
                req = urllib2.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
            # Python 2
            else:
                search_url = "https://html.duckduckgo.com/html/?q=" + urllib.quote(q)
                req = urllib2.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})

            response = urllib2.urlopen(req, timeout=10)
            content = response.read()
            if sys.version_info[0] >= 3:
                content = content.decode('utf-8', errors='ignore')
            else:
                content = content.decode('utf-8', errors='ignore')

            # Extract snippets (works for both Python 2/3)
            snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', content, re.DOTALL)
            if snippets:
                ans = unescape(re.sub('<[^<]+?>', '', snippets[0]))
                self.log("LouisAI Light", f"[WEB_SEARCH]: {ans}")
            else:
                self.log("LouisAI Light", "SIGNAL_LOST: No data available.")
        except Exception as e:
            self.log("SYSTEM", f"WEB_ERROR: {str(e)}")

    def start(self):
        """Main loop for console interaction."""
        print("=== LouisAI Light (Universal Python) ===")
        print("Type your message and press Enter. Type 'exit' to quit.\n")
        while True:
            try:
                q = raw_input("You: ").strip()  # Python 2
            except NameError:
                q = input("You: ").strip()  # Python 3
            if q.lower() == "exit":
                break
            self.log(self.machine_user, q)

            # Greetings
            if q.lower() in self.greetings:
                self.log("LouisAI Light", f"GREETING_ACK: Hi {self.machine_user}, systems are optimal.")
                continue

            # Bad review intercept
            if any(word in q.lower() for word in self.bad_review_keywords):
                self.log("LouisAI Light", "FEEDBACK_NOTICE: Please comment on Dolfiniez YouTube videos; he will likely fix it.")
                continue

            self.run_engine(q)

if __name__ == "__main__":
    ai = LouisAILight()
    ai.start()