"""python -m src.check_models -> which Gemini models still have free quota for your key?"""
import os, re
import requests
from dotenv import load_dotenv
from .extract import list_models, BASE
load_dotenv()
key = os.environ["GEMINI_API_KEY"]
names = [n for n in list_models() if re.fullmatch(r"gemini-[\d.]+-flash(-lite)?|gemini-flash(-lite)?-latest", n)]
for n in names:
    r = requests.post(f"{BASE}/models/{n}:generateContent", params={"key": key}, timeout=60,
        json={"contents": [{"parts": [{"text": "Reply with the word OK"}]}]})
    msg = " ".join(r.text.split())[:160] if r.status_code != 200 else "works"
    print(f"{n:28s} HTTP {r.status_code}  {msg}")
print("\nPut a model marked 'works' in .env as MODEL=<name>")
