import websocket
import json
import time
import os
from flask import Flask
from threading import Thread

# --- PARAMÈTRES ---
TOKEN = "212fec18-9b31-55f3-917a-13dfc380ad67"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
WS_URL = "wss://ws.smartiwheel.com/websocket/services?master&domain=1wmefm.com&version=1.3.342"

historique = []

# Petit serveur pour que Koyeb reste "Healthy"
app = Flask('')
@app.route('/')
def home(): return "Bot en ligne"

def analyser_tonnerre(cote):
    global historique
    historique.append(cote)
    if len(historique) > 5:
        historique.pop(0)
    
    print(f"📡 Score: {cote}x | Historique: {historique}")

    # TA STRATÉGIE MASTER
    if len(historique) == 5:
        v1, b1, b2, b3, v_conf = historique
        
        # Vérification : 1 Violet -> 3 Bleus montants -> 1 Violet confirmation (3.0+)
        if (v1 >= 2.0 and 
            (b1 < b2 < b3 < 2.0) and 
            v_conf >= 3.0):
            
            print("🚀 !!! SIGNAL TONNERRE DÉTECTÉ !!! 🚀")
            print(f"Séquence : {v1} -> {b1} < {b2} < {b3} -> {v_conf}")

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "lucky_jet" in str(data):
            for key, value in data.items():
                if isinstance(value, (int, float)) and key != 'ts' and key != 'cid':
                    analyser_tonnerre(float(value))
    except: pass

def start_bot():
    while True:
        try:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_message=on_message,
                header={"User-Agent": USER_AGENT, "Cookie": f"1w_token={TOKEN};"}
            )
            ws.run_forever()
        except: time.sleep(5)

if __name__ == "__main__":
    # Lancement du serveur sur le port 8080 (par défaut sur Koyeb)
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    start_bot()
