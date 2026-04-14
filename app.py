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
        numero = None
        mensagem = None

        # Pega o número do remetente
        msg = data.get("message", {})
        chat = data.get("chat", {})
        
        numero = msg.get("chatid", "").replace("@s.whatsapp.net", "")
        if not numero:
            numero = chat.get("wa_chatid", "").replace
