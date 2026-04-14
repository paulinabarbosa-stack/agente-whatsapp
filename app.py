from flask import Flask, request
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
UAZAPI_BASE_URL = "https://free.uazapi.com"
UAZAPI_TOKEN = "08dd3ec9-c3fc-4069-8b02-c8afe369df67"
INSTANCE_ID = "instanciaurora"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        numero = data["data"]["key"]["remoteJid"].replace("@s.whatsapp.net", "")
        mensagem = data["data"]["message"]["conversation"]
    except:
        return "ok", 200

    resposta = perguntar_openai(mensagem)
    enviar_mensagem(numero, resposta)

    return "ok", 200

def perguntar_openai(mensagem):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": mensagem}]
    }
    r = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers)
    return r.json()["choices"][0]["message"]["content"]

def enviar_mensagem(numero, texto):
    url = f"{UAZAPI_BASE_URL}/send/text"
    headers = {"token": UAZAPI_TOKEN}
    body = {
        "to": f"{numero}@s.whatsapp.net",
        "text": texto
    }
    requests.post(url, json=body, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
