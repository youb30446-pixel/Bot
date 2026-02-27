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
    
    # On stocke la cote numérique pour vérifier la montée
    historique.append(cote)
    
    # On garde les 5 derniers scores pour la règle : V -> B1 < B2 < B3 -> V_conf
    if len(historique) > 5:
        historique.pop(0)
    
    print(f"📡 [LIVE] Score: {cote}x | Historique: {historique}")

    # --- TA STRATÉGIE MASTER ---
    if len(historique) == 5:
        v1 = historique[0]     # Premier Violet
        b1 = historique[1]     # Bleu 1
        b2 = historique[2]     # Bleu 2
        b3 = historique[3]     # Bleu 3
        v_conf = historique[4] # Violet de Confirmation

        # Vérification stricte :
        # 1. v1 est violet (>= 2.0)
        # 2. b1, b2, b3 sont bleus ET montent (b1 < b2 < b3 < 2.0)
        # 3. v_conf est violet de confirmation (>= 3.0)
        if (v1 >= 2.0 and 
            (b1 < b2 < b3 < 2.0) and 
            v_conf >= 3.0):
            
            print("🚀 !!! SIGNAL TONNERRE DÉTECTÉ !!! 🚀")
            print(f"Séquence validée : {v1} -> {b1} < {b2} < {b3} -> {v_conf}")
            print("Action : Prochain tour -> MISE SUR VIOLET (Cible 2.00x)")

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "lucky_jet" in str(data):
            for key, value in data.items():
                if isinstance(value, (int, float)) and key != 'ts' and key != 'cid':
                    analyser_tonnerre(float(value))
    except:
        pass

def on_open(ws):
    print("✅ Sniper V2 Opérationnel : Flux Master connecté.")
    print("Stratégie chargée : V -> B montants -> V de confirmation (3.0+).")

def start_bot():
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

