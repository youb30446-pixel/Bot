import websocket
import json
import time

# --- TES PARAMÈTRES SÉCURISÉS ---
TOKEN = "212fec18-9b31-55f3-917a-13dfc380ad67"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
WS_URL = "wss://ws.smartiwheel.com/websocket/services?master&domain=1wmefm.com&version=1.3.342"

# Mémoire du bot pour la stratégie
historique = []

def analyser_tonnerre(cote):
    global historique
    
    # 1. Classification stricte
    couleur = "VIOLET" if cote >= 2.0 else "BLEU"
    historique.append(couleur)
    
    # Garder les 4 derniers pour la règle
    if len(historique) > 4:
        historique.pop(0)
    
    print(f"📡 [LIVE] Score: {cote}x -> {couleur} | Suite: {'-'.join(historique)}")

    # 2. TA RÈGLE : VIOLET -> BLEU -> BLEU -> BLEU
    if len(historique) == 4:
        if (historique[0] == "VIOLET" and 
            historique[1] == "BLEU" and 
            historique[2] == "BLEU" and 
            historique[3] == "BLEU"):
            
            print("🚀 !!! SIGNAL TONNERRE DÉTECTÉ !!! 🚀")
            print("Action : Prochain tour -> MISE SUR VIOLET (Cible 2.00x)")

def on_message(ws, message):
    try:
        data = json.loads(message)
        # On cherche les données de Lucky Jet dans le payload
        if "lucky_jet" in str(data):
            # Extraction du coefficient (le bot cherche la valeur numérique)
            # Cette partie s'adapte automatiquement au format du serveur
            for key, value in data.items():
                if isinstance(value, (int, float)) and key != 'ts' and key != 'cid':
                    analyser_tonnerre(float(value))
    except:
        pass

def on_open(ws):
    print("✅ Sniper V2 Opérationnel : Flux Master connecté.")
    print("Stratégie chargée : Violet + 3 Bleus consécutifs.")

def start_bot():
    # Construction de la connexion avec tes cookies de session
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        header={
            "User-Agent": USER_AGENT,
            "Cookie": f"1w_token={TOKEN};"
        }
    )
    ws.run_forever()

if __name__ == "__main__":
    while True:
        try:
            start_bot()
        except Exception as e:
            print(f"🔄 Relance automatique : {e}")
            time.sleep(5)

