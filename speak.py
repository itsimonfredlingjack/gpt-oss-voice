import pychromecast
import time
import sys
import threading
import logging
import re
from urllib.parse import quote
from typing import Optional

import config
import debug_ndjson

logger = logging.getLogger(__name__)


class DeviceNotFoundError(Exception):
    """Raised when the specified Google Home device cannot be found."""
    pass


class GoogleHomeSpeaker:
    """Manages connection and TTS for Google Home with interrupt capability."""
    
    def __init__(self, device_name: Optional[str] = None):
        """Initialize Google Home speaker.
        
        Args:
            device_name: Name of the Google Home device. If None, uses
                value from config (GOOGLE_HOME_DEVICE env var or default).
        """
        self.device_name = device_name or config.get_device_name()
        self.cast: Optional[pychromecast.Chromecast] = None
        self.mc: Optional[pychromecast.media_controller.MediaController] = None
        self._connect_lock = threading.Lock()
        self._speak_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._browser = None

    def connect(self) -> None:
        """Connect to the Chromecast device."""
        if self.cast:
            return

        logger.info("Connecting to Google Home device", extra={
            "device": self.device_name
        })
        chromecasts, browser = pychromecast.get_listed_chromecasts(
            friendly_names=[self.device_name]
        )
        self._browser = browser
        
        if not chromecasts:
            logger.error("Device not found", extra={
                "device": self.device_name
            })
            raise DeviceNotFoundError(
                f"Device '{self.device_name}' not found. Is it powered on?"
            )

        self.cast = chromecasts[0]
        self.cast.wait()  # Säkerställ anslutning
        self.mc = self.cast.media_controller
        logger.info("Connected to device", extra={"device": self.device_name})

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

        if not self.mc:
            return

        # Serialize playback across concurrent Flask requests; overlapping calls
        # can cause "PLAYING" with no audible output.
        with self._speak_lock:
            chunks = _split_tts_text(text, max_chars=180)
            # region agent log
            debug_ndjson.log_debug(
                hypothesis_id="H2",
                location="speak.py:GoogleHomeSpeaker.speak",
                message="speak start",
                data={
                    "device": self.device_name,
                    "text_len": len(text or ""),
                    "chunks": len(chunks),
                },
            )
            # endregion agent log
            logger.debug(
                "Starting TTS playback",
                extra={
                    "chunks": len(chunks),
                    "text_length": len(text),
                    "device": self.device_name,
                },
            )

            try:
                played = 0
                for idx, chunk in enumerate(chunks, start=1):
                    if self._stop_event.is_set():
                        break

                    safe_text = quote(chunk, safe="")
                    tts_url = (
                        "https://translate.google.com/translate_tts?"
                        f"ie=UTF-8&q={safe_text}&tl=sv&client=tw-ob"
                    )

                    # DEBUG: show URL for diagnostics.
                    print(
                        f"DEBUG: CASTING URL TO SPEAKER {self.device_name} "
                        f"({idx}/{len(chunks)} len={len(chunk)}): {tts_url}",
                        flush=True,
                    )

                    logger.debug(
                        "Starting chunk playback",
                        extra={
                            "chunk": idx,
                            "total_chunks": len(chunks),
                            "chunk_length": len(chunk),
                            "device": self.device_name,
                        },
                    )

                    self.mc.play_media(tts_url, "audio/mp3")
                    self.mc.block_until_active()

                    # Wait for media to actually start playing (PLAYING state)
                    # This ensures the chunk has actually started, not just queued
                    max_wait_playing = 3.0  # Max wait time for playback to start
                    wait_start = time.time()
                    started_playing = False
                    
                    while time.time() - wait_start < max_wait_playing:
                        if self._stop_event.is_set():
                            break
                        time.sleep(0.1)
                        self.mc.update_status()
                        state = self.mc.status.player_state
                        
                        if state == "PLAYING":
                            started_playing = True
                            logger.debug(
                                "Chunk started playing",
                                extra={
                                    "chunk": idx,
                                    "device": self.device_name,
                                },
                            )
                            break
                        elif state == "IDLE":
                            # If IDLE right after block_until_active, might be an error
                            # Wait a bit and check again
                            time.sleep(0.2)
                            self.mc.update_status()
                            state = self.mc.status.player_state
                            if state == "PLAYING":
                                started_playing = True
                                logger.debug(
                                    "Chunk started playing (after IDLE check)",
                                    extra={
                                        "chunk": idx,
                                        "device": self.device_name,
                                    },
                                )
                                break
                            elif state == "IDLE":
                                # Still IDLE - might be an error, but continue anyway
                                logger.warning(
                                    "Chunk still IDLE after block_until_active",
                                    extra={
                                        "chunk": idx,
                                        "device": self.device_name,
                                    },
                                )
                                # Give it one more chance
                                time.sleep(0.3)
                                self.mc.update_status()
                                if self.mc.status.player_state == "PLAYING":
                                    started_playing = True
                                    break

                    if not started_playing and not self._stop_event.is_set():
                        logger.warning(
                            "Chunk did not start playing within timeout",
                            extra={
                                "chunk": idx,
                                "device": self.device_name,
                                "final_state": self.mc.status.player_state,
                            },
                        )

                    # Wait until chunk is complete (IDLE after PLAYING)
                    # This ensures the audio has actually finished playing
                    if started_playing:
                        while not self._stop_event.is_set():
                            time.sleep(0.1)
                            self.mc.update_status()
                            state = self.mc.status.player_state
                            
                            if state == "IDLE":
                                # Verify we actually played (not just IDLE from start)
                                # Wait a bit extra to ensure audio is completely finished
                                time.sleep(0.3)
                                logger.debug(
                                    "Chunk playback completed",
                                    extra={
                                        "chunk": idx,
                                        "device": self.device_name,
                                    },
                                )
                                break
                    else:
                        # If chunk didn't start playing, wait a bit anyway
                        # before trying next chunk
                        time.sleep(0.5)

                    played = idx

                    # Small delay between chunks to ensure device is ready
                    # This prevents race conditions where next chunk starts
                    # before previous one is fully finished
                    if idx < len(chunks) and not self._stop_event.is_set():
                        time.sleep(0.2)

                if self._stop_event.is_set():
                    logger.info("TTS interrupted by user")
                    try:
                        self.mc.stop()
                    except Exception:
                        pass
                else:
                    logger.debug("TTS playback completed")

                # region agent log
                debug_ndjson.log_debug(
                    hypothesis_id="H2",
                    location="speak.py:GoogleHomeSpeaker.speak",
                    message="speak end",
                    data={
                        "device": self.device_name,
                        "played_chunks": played,
                        "total_chunks": len(chunks),
                        "interrupted": bool(self._stop_event.is_set()),
                    },
                )
                # endregion agent log
            except Exception as e:
                logger.error(
                    "TTS playback error",
                    extra={"error": str(e), "device": self.device_name},
                    exc_info=True,
                )
                # Force reconnect next time
                self.cast = None
                raise

    def stop(self) -> None:
        """Interrupt current speech."""
        logger.debug("Stopping TTS")
        self._stop_event.set()
        if self.mc:
            try:
                self.mc.stop()
            except Exception as e:
                logger.warning("Error stopping TTS", extra={"error": str(e)})


# --- Backward Compatibility ---
_speaker_instance: Optional[GoogleHomeSpeaker] = None


def speak(text: str, device_name: Optional[str] = None) -> None:
    """Speak text via Google Home device (backward compatibility).
    
    Args:
        text: Text to speak (will be URL-encoded).
        device_name: Optional device name override.
    
    Raises:
        DeviceNotFoundError: If device cannot be found.
    """
    global _speaker_instance
    if _speaker_instance is None or device_name is not None:
        _speaker_instance = GoogleHomeSpeaker(device_name)
    _speaker_instance.speak(text)


def _split_tts_text(text: str, max_chars: int = 180) -> list[str]:
    """Split text into safe chunks for Google Translate TTS.

    Long query strings can lead to silent playback or upstream errors. Keep each
    chunk short and whitespace-normalized.
    """
    cleaned = re.sub(r"\s+", " ", (text or "")).strip()
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]

    # Prefer splitting on sentence-like boundaries.
    parts = re.split(r"(?<=[.!?;:])\s+", cleaned)
    chunks: list[str] = []
    cur = ""

    def flush() -> None:
        nonlocal cur
        if cur:
            chunks.append(cur.strip())
            cur = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if not cur:
            if len(part) <= max_chars:
                cur = part
                continue
        if cur and len(cur) + 1 + len(part) <= max_chars:
            cur = f"{cur} {part}"
            continue

        flush()
        if len(part) <= max_chars:
            cur = part
            continue

        # Hard-split very long parts by words.
        words = part.split()
        buf = ""
        for w in words:
            if not buf:
                buf = w
                continue
            if len(buf) + 1 + len(w) <= max_chars:
                buf = f"{buf} {w}"
            else:
                chunks.append(buf)
                buf = w
        if buf:
            chunks.append(buf)

    flush()
    return chunks

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
