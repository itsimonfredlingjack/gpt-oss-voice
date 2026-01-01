import requests
import json
import sys

# --- KONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gptoss-agent"


class BrainConnectionError(Exception):
    """Raised when unable to connect to Ollama service."""
    pass


class BrainEmptyResponseError(Exception):
    """Raised when Ollama returns an empty response."""
    pass

def ask_brain(prompt):
    """Query the AI brain via Ollama.
    
    Args:
        prompt: User's prompt/question.
    
    Returns:
        AI response string. Raises exceptions on error (no print statements).
    """
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
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise BrainConnectionError(f"Cannot connect to Ollama at {OLLAMA_URL}") from e
    except requests.exceptions.Timeout as e:
        raise BrainConnectionError("Ollama request timed out") from e
    except requests.exceptions.RequestException as e:
        raise BrainConnectionError(f"Ollama request failed: {e}") from e
    
    data = response.json()
    ai_reply = data.get('message', {}).get('content', '')
    
    if not ai_reply:
        raise BrainEmptyResponseError("Model returned empty response")
    
    return ai_reply

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(ask_brain(user_input))
    else:
        print("--- INTERAKTIVT LÄGE (Skriv 'exit' för att sluta) ---")
        print("Kanalen är öppen. Vad vill du?")
        while True:
            try:
                user_input = input("Du: ")
                if user_input.lower() in ["exit", "sluta", "quit"]:
                    break
                if user_input.strip() == "":
                    continue
                reply = ask_brain(user_input)
                print(f"AI: {reply}")
            except KeyboardInterrupt:
                print("\nStänger ner.")
                break
            except BrainConnectionError as e:
                print(f"⚠️  Nätverksfel: {e}")
            except BrainEmptyResponseError as e:
                print(f"⚠️  Varning: {e}")
            except Exception as e:
                print(f"⚠️  Ett fel inträffade: {e}")