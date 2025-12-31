import pychromecast
import time
import sys

# --- INSTÄLLNINGAR ---
# Vi siktar på Kontor eftersom det är din dev-hörna
DEVICE_NAME = "Kontor" 
# Vill du byta till sovrummet senare? Ändra till "Sovis"
# ---------------------

def speak(text):
    print(f"📡  Ansluter till {DEVICE_NAME}...")
    
    # Sök specifikt efter Kontor
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[DEVICE_NAME])

    if not chromecasts:
        print(f"❌  Hittade inte '{DEVICE_NAME}'. Är den strömsatt?")
        return

    # Välj första träffen (det ska bara finnas en)
    cast = chromecasts[0]
    cast.wait() # Säkerställ anslutning
    
    print(f"✅  Uppkopplad mot {cast.name} ({cast.cast_info.host})")

    # Förbered texten för Google Translate API (Svenska)
    safe_text = text.replace(" ", "+")
    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={safe_text}&tl=sv&client=tw-ob"

    print(f"🗣️   Sänder meddelande: '{text}'")
    
    # Skicka ljudet
    mc = cast.media_controller
    mc.play_media(tts_url, 'audio/mp3')
    
    # Vänta tills den börjar prata
    mc.block_until_active()
    
    # Ge den lite tid att prata klart (enkelt hack)
    time.sleep(1) 
    print("👋  Klar.")

if __name__ == "__main__":
    # Om du skriver text efter filnamnet, säg det. Annars kör standardfras.
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
    else:
        msg = "Systemet online. AI servern är redo."
    
    speak(msg)
