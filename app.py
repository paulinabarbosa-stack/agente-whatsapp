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
    print("DADOS:", data)
    try:
        msg = data.get("message", {})
        chat = data.get("chat", {})
        numero = msg.get("chatid", "").replace("@s.whatsapp.net", "")
        if not numero:
            numero = chat.get("wa_chatid", "").replace("@s.whatsapp.net", "")
        mensagem = msg.get("content") or msg.get("text") or chat.get("wa_lastMessageTextVote")
        print(f"Numero: {numero} | Mensagem: {mensagem}")
        if not numero or not mensagem:
            print("Ignorado")
            return "ok", 200
        resposta = perguntar_openai(mensagem)
        print(f"Resposta: {resposta}")
        enviar_mensagem(numero, resposta)
    except Exception as e:
        print("ERRO:", e)
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
