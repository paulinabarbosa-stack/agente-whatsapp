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
    print("DADOS RECEBIDOS:", data)

    try:
        numero = None
        mensagem = None

        # Tenta diferentes formatos
        if "data" in data:
            d = data["data"]
            if "key" in d:
                numero = d["key"]["remoteJid"].replace("@s.whatsapp.net", "")
            if "message" in d:
                msg = d["message"]
                mensagem = msg.get("conversation") or msg.get("extendedTextMessage", {}).get("text")

        if not numero or not mensagem:
            print("Mensagem ignorada ou formato desconhecido")
            return "ok", 200

        print(f"De: {numero} | Mensagem: {mensagem}")
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
    r = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers)
    return r.json()["choices"][0]["message"]["content"]

def enviar_mensagem(numero, texto):
    url = f"{UAZAPI_BASE_URL}/send/text"
    headers = {"token": UAZAPI_TOKEN}
    body = {
        "to": f"{numero}@s.whatsapp.net",
        "text": texto
    }
    r = requests.post(url, json=body, headers=headers)
    print("Envio status:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
