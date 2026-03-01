import websocket
import json
import time
import os
import requests
import datetime
from flask import Flask
from threading import Thread

# --- CONFIGURATION MASTER ---
# Récupère tes clés dans les variables d'environnement Koyeb
TOKEN_TELEGRAM = os.getenv("TELEGRAM_TOKEN") 
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TOKEN_1WIN = "212fec18-9b31-55f3-917a-13dfc380ad67"
WS_URL = "wss://ws.smartiwheel.com/websocket/services?master&domain=1wmefm.com&version=1.3.342"

historique = []

# --- FONCTION D'ALERTE (TON HAUT-PARLEUR) ---
def envoyer_alerte(message):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Erreur envoi Telegram: {e}")

# --- SERVEUR FANTÔME ---
app = Flask('')
@app.route('/')
def home(): return "✅ Sniper Ibrahim Opérationnel"

def run_keep_alive():
    app.run(host='0.0.0.0', port=8000)

# --- ANALYSE DE LA FAILLE (V -> B < B < B -> V3+) ---
def analyser_faille(cote):
    global historique
    historique.append(cote)
    if len(historique) > 5:
        historique.pop(0)
    
    print(f"📡 Score: {cote}x | File: {historique}")

    if len(historique) == 5:
        v1, b1, b2, b3, v_conf = historique
        
        # TA STRATÉGIE CHIRURGICALE
        if (v1 >= 2.0 and (b1 < b2 < b3 < 2.0) and v_conf >= 3.0):
            msg = "🚀 *FAILLE DÉTECTÉE (100%) !*\n\n"
            msg += f"Séquence : {v1} -> {b1} < {b2} < {b3} -> {v_conf}\n"
            msg += "🎯 *MISE CONSEILLÉE : x2.00*"
            envoyer_alerte(msg)

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "lucky_jet" in str(data):
            for key, value in data.items():
                if isinstance(value, (int, float)) and key not in ['ts', 'cid']:
                    analyser_faille(float(value))
    except: pass

def start_sniper():
    while True:
        try:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_message=on_message,
                header={"User-Agent": "Mozilla/5.0", "Cookie": f"1w_token={TOKEN_1WIN};"}
            )
            ws.run_forever()
        except:
            time.sleep(5)

if __name__ == "__main__":
    # Notification de démarrage
    envoyer_alerte("✅ *Sniper Ibrahim activé.* La chasse aux 100% commence.")
    Thread(target=run_keep_alive).start()
    start_sniper()
