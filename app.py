from flask import Flask, request
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
UAZAPI_BASE_URL = os.environ.get("UAZAPI_BASE_URL", "https://auroradtna.uazapi.com")
UAZAPI_TOKEN = os.environ.get("UAZAPI_TOKEN")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("DATA:", data)
    try:
        msg = data.get("message", {})
        chat = data.get("chat", {})
        number = msg.get("chatid", "").replace("@s.whatsapp.net", "")
        if not number:
            number = chat.get("wa_chatid", "").replace("@s.whatsapp.net", "")
        text = msg.get("content") or msg.get("text") or chat.get("wa_lastMessageTextVote")
        print(f"Number: {number} | Text: {text}")
        if not number or not text:
            print("Ignored")
            return "ok", 200
        reply = ask_openai(text)
        print(f"Reply: {reply}")
        send_message(number, reply)
    except Exception as e:
        print("ERROR:", e)
    return "ok", 200

def ask_openai(text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": text}]
    }
    r = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers)
    return r.json()["choices"][0]["message"]["content"]

def send_message(number, text):
    url = f"{UAZAPI_BASE_URL}/send
    headers = {"token": UAZAPI_TOKEN}
    body = {
        "phone": number,
        "message": text
    }
    r = requests.post(url, json=body, headers=headers)
    print("Send status:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
