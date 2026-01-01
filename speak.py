import pychromecast
import time
import sys
import threading
from urllib.parse import quote
from typing import Optional


class DeviceNotFoundError(Exception):
    """Raised when the specified Google Home device cannot be found."""
    pass


# --- INSTÄLLNINGAR ---
# Vi siktar på Kontor eftersom det är din dev-hörna
DEVICE_NAME = "Kontor" 
# Vill du byta till sovrummet senare? Ändra till "Sovis"
# ---------------------


class GoogleHomeSpeaker:
    """Manages connection and TTS for Google Home with interrupt capability."""
    
    def __init__(self, device_name: str = DEVICE_NAME):
        """Initialize Google Home speaker.
        
        Args:
            device_name: Name of the Google Home device.
        """
        self.device_name = device_name
        self.cast: Optional[pychromecast.Chromecast] = None
        self.mc: Optional[pychromecast.media_controller.MediaController] = None
        self._connect_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._browser = None

    def connect(self) -> None:
        """Connect to the Chromecast device."""
        if self.cast:
            return

        chromecasts, browser = pychromecast.get_listed_chromecasts(
            friendly_names=[self.device_name]
        )
        self._browser = browser
        
        if not chromecasts:
            raise DeviceNotFoundError(
                f"Device '{self.device_name}' not found. Is it powered on?"
            )

        self.cast = chromecasts[0]
        self.cast.wait()  # Säkerställ anslutning
        self.mc = self.cast.media_controller

    def speak(self, text: str) -> None:
        """Speak text. Blocks until finished or stopped.
        
        Args:
            text: Text to speak (will be URL-encoded).
        
        Raises:
            DeviceNotFoundError: If device cannot be found.
        """
        self._stop_event.clear()
        
        with self._connect_lock:
            if not self.cast:
                try:
                    self.connect()
                except DeviceNotFoundError:
                    # Retry once
                    self.cast = None
                    self.connect()

        # Förbered texten för Google Translate API (Svenska)
        safe_text = quote(text, safe='')
        tts_url = (
            f"https://translate.google.com/translate_tts?"
            f"ie=UTF-8&q={safe_text}&tl=sv&client=tw-ob"
        )

        if not self.mc:
            return

        try:
            # Skicka ljudet
            self.mc.play_media(tts_url, 'audio/mp3')
            
            # Vänta tills den börjar prata
            self.mc.block_until_active()
            
            # Block while playing, allowing interruption
            # Check stop event and player state periodically
            while not self._stop_event.is_set():
                time.sleep(0.1)
                self.mc.update_status()
                if self.mc.status.player_state == 'IDLE':
                    break
                    
            # If stopped, stop the media
            if self._stop_event.is_set():
                self.mc.stop()
        except Exception:
            # Force reconnect next time
            self.cast = None
            raise

    def stop(self) -> None:
        """Interrupt current speech."""
        self._stop_event.set()
        if self.mc:
            try:
                self.mc.stop()
            except Exception:
                pass  # Ignore errors when stopping


# --- Backward Compatibility ---
_speaker_instance: Optional[GoogleHomeSpeaker] = None


def speak(text: str) -> None:
    """Speak text via Google Home device (backward compatibility).
    
    Args:
        text: Text to speak (will be URL-encoded).
    
    Raises:
        DeviceNotFoundError: If device cannot be found.
    """
    global _speaker_instance
    if _speaker_instance is None:
        _speaker_instance = GoogleHomeSpeaker()
    _speaker_instance.speak(text)

if __name__ == "__main__":
    # Om du skriver text efter filnamnet, säg det. Annars kör standardfras.
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
    else:
        msg = "Systemet online. AI servern är redo."
    
    try:
        speak(msg)
        print("👋  Klar.")
    except Exception as e:
        print(f"❌  Fel: {e}")
        sys.exit(1)
