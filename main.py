import websocket
import json
import time
import os
import requests

WS_URL = "wss://ws.smartiwheel.com/websocket/services?master&domain=1wmefm.com&version=1.3.342"

TOKEN_TELEGRAM = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

historique = []

def envoyer_telegram(msg):
    if not TOKEN_TELEGRAM or not CHAT_ID:
        print("Telegram non configuré")
        return

    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        print("Erreur Telegram:", e)

def analyser_faille(score):
    global historique
    historique.append(score)
    if len(historique) > 10:
        historique.pop(0)

    print(f"Score reçu : {score}x")

    if len(historique) >= 5:
        v1, b1, b2, b3, v_conf = historique[-5:]
        if (v1 >= 2.0 and (b1 < b2 < b3 < 2.0) and v_conf >= 3.0):
            envoyer_telegram(
                f"🌩️ Faille détectée !\nSéquence : {v1} -> {b1} < {b2} < {b3} -> {v_conf}"
            )

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "pub" in data and "data" in data["pub"]:
            score = float(data["pub"]["data"].get("coefficient", 0))
            if score > 0:
                analyser_faille(score)
    except Exception as e:
        print("Erreur message:", e)

def on_error(ws, error):
    print("Erreur WebSocket:", error)

def on_close(ws, close_status_code, close_msg):
    print("Connexion fermée")

def on_open(ws):
    print("Connexion ouverte")
    envoyer_telegram("🚀 Sniper activé")

def run():
    while True:
        try:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except Exception as e:
            print("Crash:", e)
        print("Reconnexion dans 5 secondes...")
        time.sleep(5)

if __name__ == "__main__":
    run()
