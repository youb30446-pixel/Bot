import websocket
import json
import time
import os
import requests

# --- CONFIGURATION (Vérifie ton URL WebSocket !) ---
WS_URL = "wss://ws.smartiwheel.com/websocket/services?master&domain=1wmefm.com&version=1.3.342"
TOKEN_TELEGRAM = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

historique = []

def envoyer_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=5)
    except: pass

def analyser_faille(score):
    global historique
    historique.append(score)
    if len(historique) > 10: historique.pop(0)

    # Log pour que tu vois que ça travaille dans Koyeb
    print(f"✅ Score reçu: {score}x | Analyse en cours...")

    if len(historique) >= 5:
        # Ta séquence : V -> B < B < B -> V_conf
        v1, b1, b2, b3, v_conf = historique[-5:]

        if (v1 >= 2.0 and (b1 < b2 < b3 < 2.0) and v_conf >= 3.0):
            msg = "🌩️ *FAILLE DÉTECTÉE (100%) !*\n\n"
            msg += f"Séquence : {v1} -> {b1} < {b2} < {b3} -> {v_conf}\n"
            msg += "💰 *MISE CONSEILLÉE : x2.00*"
            envoyer_telegram(msg)

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "pub" in data and "data" in data["pub"]:
            score = float(data["pub"]["data"].get("coefficient", 0))
            if score > 0:
                analyser_faille(score)
    except: pass

def start_bot():
    # On informe Telegram que le Sniper est en chasse
    envoyer_telegram("🚀 *Sniper Ibrahim en ligne.* Port ignoré pour éviter les erreurs. La chasse commence !")
    while True:
        try:
            ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
            ws.run_forever()
        except:
            time.sleep(5)

if __name__ == "__main__":
    start_bot()
