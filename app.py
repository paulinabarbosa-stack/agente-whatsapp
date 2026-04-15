from flask import Flask, request
import requests
import os

app = Flask(__name__)

KEY = os.environ.get("OPENAI_API_KEY")
BASE = os.environ.get("UAZAPI_BASE_URL", "https://auroradtna.uazapi.com")
TOKEN = os.environ.get("UAZAPI_TOKEN")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("DATA:", data)
    try:
        msg = data.get("message", {})
        chat = data.get("chat", {})
        num = msg.get("chatid", "").replace("@s.whatsapp.net", "")
        if not num:
            num = chat.get("wa_chatid", "").replace("@s.whatsapp.net", "")
        txt = msg.get("content") or msg.get("text") or chat.get("wa_lastMessageTextVote")
        print(num, txt)
        if not num or not txt:
            return "ok", 200
        rep = call_ai(txt)
        print(rep)
        send(num, rep)
    except Exception as e:
        print("ERR:", e)
    return "ok", 200

def call_ai(txt):
    h = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    b = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": txt}]}
    r = requests.post("https://api.openai.com/v1/chat/completions", json=b, headers=h)
    return r.json()["choices"][0]["message"]["content"]

def send(num, txt):
    h = {"token": TOKEN}
    b = {"Phone": num, "Body": txt}
    r = requests.post(f"{BASE}/send/text", json=b, headers=h)
    print("SEND:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
