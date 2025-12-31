import requests
import json
import sys
from speak import speak 

# --- KONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gptoss-agent" 

def ask_brain(prompt):
    print(f"🧠  Skickar tanke till {MODEL_NAME}: '{prompt}'")
    
    # Vi ändrar prompten lite för att säkra att den faktiskt pratar
    system_prompt = (
        "Du är 'GPT', en skön AI-assistent. "
        "Svara direkt till användaren. "
        "Håll svaret kort och koncist (max 2 meningar). "
        "Svara på svenska."
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7, 
            "num_predict": 512,  # <--- ÄNDRAT FRÅN 100 TILL 512! Mer utrymme.
            "stop": ["\nUser:", "\nDu:"] # Stoppa den från att prata med sig själv
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # --- DEBUG: Se exakt vad modellen skickar tillbaka (även det dolda) ---
        # Om den svarar tomt ser vi varför här:
        # print(f"DEBUG RAW: {data}") 
        # ---------------------------------------------------------------------

        ai_reply = data.get('message', {}).get('content', '')
        
        if not ai_reply:
            print("⚠️  Varning: Modellen svarade tomt! (Kolla om den 'tänker' utan att prata)")
            # Ibland kan modeller fastna i thought-loops, vi tvingar fram ett ljud:
            speak("Jag hörde dig, men min tankeprocess returnerade ingen data.")
            return

        print(f"🤖 AI Svar: {ai_reply}")
        
        # Prata!
        speak(ai_reply)

    except Exception as e:
        print(f"🔥 KRASCH: {e}")
        speak("Systemfel i neurala nätverket.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        ask_brain(user_input)
    else:
        print("--- INTERAKTIVT LÄGE (Skriv 'exit' för att sluta) ---")
        speak("Kanalen är öppen. Vad vill du?")
        while True:
            try:
                user_input = input("Du: ")
                if user_input.lower() in ["exit", "sluta", "quit"]:
                    break
                if user_input.strip() == "":
                    continue
                ask_brain(user_input)
            except KeyboardInterrupt:
                print("\nStänger ner.")
                break
