import websocket
import json
import threading
import time
import http.server
import socketserver

# --- CONFIGURATION (Tes accès validés) ---
TOKEN = "212fec18-9b31-55f3-917a-13dfc380ad67"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
WS_URL = "wss://ws.smartiwheel.com/websocket/services?master&domain=1wmefm.com&version=1.3.342"

# --- MÉMOIRE DE STRATÉGIE ---
historique = []

# 1. SERVEUR ANTI-ERREUR (Pour Koyeb)
def run_fake_server():
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            httpd.serve_forever()
    except:
        pass

# 2. LOGIQUE DE DÉTECTION "TONNERRE" (V-B-B-B)
def analyser_sequence(cote):
    global historique
    couleur = "VIOLET" if cote >= 2.0 else "BLEU"
    historique.append(couleur)
    
    if len(historique) > 4:
        historique.pop(0)
    
    print(f"📡 [LIVE] Score: {cote}x -> {couleur} | Suite: {'-'.join(historique)}")

    if len(historique) == 4:
        # RÈGLE D'IBRAHIM : Violet puis 3 Bleus consécutifs
        if (historique[0] == "VIOLET" and 
            historique[1] == "BLEU" and 
            historique[2] == "BLEU" and 
            historique[3] == "BLEU"):
            
            print("🚀 !!! SIGNAL TONNERRE DÉTECTÉ !!! 🚀")
            print(">>> ACTION : MISE SUR VIOLET PROCHAIN TOUR <<<")

# 3. GESTION DU FLUX MASTER
def on_message(ws, message):
    try:
        data = json.loads(message)
        if "lucky_jet" in str(data):
            # Scan automatique du coefficient dans le message
            for k, v in data.items():
                if isinstance(v, (int, float)) and k not in ['ts', 'cid']:
                    analyser_sequence(float(v))
    except:
        pass

def on_open(ws):
    print("✅ Sniper V2 Connecté au Flux Master.")
    print("Stratégie : Violet + 3 Bleus consécutifs chargée.")

def start_bot():
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        header={"User-Agent": USER_AGENT, "Cookie": f"1w_token={TOKEN};"}
    )
    ws.run_forever()

if __name__ == "__main__":
    # Lancement du serveur pour Koyeb
    threading.Thread(target=run_fake_server, daemon=True).start()
    
    # Boucle de reconnexion automatique
    while True:
        try:
            start_bot()
        except Exception as e:
            print(f"🔄 Relance dans 5s : {e}")
            time.sleep(5)
