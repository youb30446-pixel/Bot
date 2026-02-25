import websocket
import json
import requests
import time
import os
import datetime
from flask import Flask
from threading import Thread

# --- CONFIGURATION SÉCURISÉE ---
TOKEN = os.getenv("TELEGRAM_TOKEN") 
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL_WS = "wss://ws.smartiwheel.com/websocket/services?master&domain=1wdght.com&version=1.3.342"

historique = []

app = Flask('')
@app.route('/')
def home(): return "Sniper Pablito en chasse..."

def envoyer_alerte(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def est_en_periode_observation():
    # Règle Ibrahim : Pas de mise les 10 premières minutes à 19h
    maintenant = datetime.datetime.now()
    return maintenant.hour == 19 and 0 <= maintenant.minute < 10

def on_message(ws, message):
    global historique
    try:
        data = json.loads(message)
        if "pub" in data and "data" in data["pub"]:
            score = float(data["pub"]["data"].get("coefficient", 0))
            if score > 0:
                historique.append(score)
                if len(historique) > 6: historique.pop(0)
                if est_en_periode_observation(): return
                
                if len(historique) >= 5:
                    v1, b1, b2, b3, v_conf = historique[-5:]
                    if v1 >= 2.0 and (b1 < b2 < b3 < 2.0) and v_conf >= 3.0:
                        envoyer_alerte("🌩️ *ALERTE TONNERRE !*\n🎯 Mise conseillée : x2.00")
    except: pass

def lancer_bot():
    while True:
        try:
            ws = websocket.WebSocketApp(URL_WS, on_message=on_message)
            ws.run_forever()
        except: time.sleep(5)

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    lancer_bot()