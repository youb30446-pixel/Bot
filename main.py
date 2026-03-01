import websocket
import json
import time
import os
import requests
from flask import Flask
from threading import Thread

# --- TES PARAMÈTRES (Vérifie bien ton URL WebSocket) ---
# Si ça ne connecte pas, change juste le domaine (ex: 1wdght.com)
WS_URL = "wss://ws.smartiwheel.com/websocket/services?master&domain=1wmefm.com&version=1.3.342"
TOKEN_TELEGRAM = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

historique = []

# --- LE SERVEUR FANTÔME (Pour que Koyeb dise "Healthy") ---
app = Flask('')
@app.route('/')
def home(): return "🤖 Sniper Faille 100% en ligne"

def run_flask():
    # Koyeb préfère le port 8000 ou 8080
    app.run(host='0.0.0.0', port=8000)

# --- L'ALERTE DÉCISIVE ---
def envoyer_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

# --- ANALYSE DE LA FAILLE (Ce que tu as entouré en vert) ---
def analyser_faille(score):
    global historique
    historique.append(score)
    if len(historique) > 6: historique.pop(0)

    print(f"📡 Score capté: {score}x | File: {historique}")

    if len(historique) >= 5:
        # v1 (Départ), b1, b2, b3 (Les 3 bleus montants), v_conf (Confirmation)
        v1, b1, b2, b3, v_conf = historique[-5:]

        # --- TA LOGIQUE CHIRURGICALE ---
        if (v1 >= 2.0 and 
            (b1 < b2 < b3 < 2.0) and 
            v_conf >= 3.0):
            
            message = "🌩️ *ALERTE FAILLE DETECTÉE (100%) !*\n\n"
            message += f"Séquence : {v1} -> {b1} < {b2} < {b3} -> {v_conf}\n"
            message += "💰 *MISE CONSEILLÉE : x2.00*"
            envoyer_telegram(message)

def on_message(ws, message):
    try:
        data = json.loads(message)
        # On cherche le coefficient dans le flux "pub" (vu sur ta photo code)
        if "pub" in data and "data" in data["pub"]:
            score = float(data["pub"]["data"].get("coefficient", 0))
            if score > 0:
                analyser_faille(score)
    except: pass

def start_bot():
    while True:
        try:
            ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
            ws.run_forever()
        except:
            time.sleep(5) # Reconnexion auto

if __name__ == "__main__":
    # 1. On lance le serveur web pour Koyeb
    Thread(target=run_flask).start()
    # 2. On informe Telegram que le Master est là
    envoyer_telegram("✅ *Sniper activé.* Prêt à encaisser la faille.")
    # 3. On lance la chasse
    start_bot()
