from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

from Agentai import askAI  

app = FastAPI()

load_dotenv()
VERIFY_TOKEN = "abcd1234"
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")


@app.get("/webhook")
def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "verification failed"}


@app.post("/webhook")
async def whatsapp_webhook(req: Request):
    data = await req.json()

    # parse:
    entry = data.get("entry", [])
    if entry:
        changes = entry[0].get("changes", [])
        if changes:
            value = changes[0].get("value", {})
            messages = value.get("messages")
            if messages:
                msg = messages[0]
                from_number = msg.get("from")         
                user_text = msg.get("text", {}).get("body")

                ai_reply = askAI(user_text)

                # send back to whatsapp
                send_whatsapp_text(from_number, ai_reply)

    return {"status": "ok"}


def send_whatsapp_text(to, message):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    requests.post(url, headers=headers, json=payload)
