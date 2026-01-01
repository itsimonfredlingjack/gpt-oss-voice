"""CLI entry point and backward-compatible exports.

This file provides the main entry point for the CLI application
and maintains backward compatibility with existing tests and imports.

    ◢◤ THE CORE ◥◣
    Cyberpunk AI Terminal Interface
"""

import queue
import threading
import time

# --- New modular imports ---
from cli.state import AppState, StateManager, get_state_manager
from cli.theme import CYBERPUNK_THEME
from cli.avatar import AIAvatar
from cli.waveform import Waveform
from cli.layout import make_layout
from cli.app import CLIApp, run_cli

# --- Legacy theme alias ---
SOLARIZED_THEME = CYBERPUNK_THEME

# --- Legacy state management (backward compatibility) ---
APP_STATE = "IDLE"
response_queue: queue.Queue = queue.Queue()
is_speaking = False
_speaking_lock = threading.Lock()


def get_is_speaking() -> bool:
    """Get speaking state (legacy compatibility)."""
    with _speaking_lock:
        return is_speaking


def set_is_speaking(value: bool) -> None:
    """Set speaking state (legacy compatibility)."""
    global is_speaking
    with _speaking_lock:
        is_speaking = value


def set_app_state(new_state: str) -> None:
    """Set app state (legacy compatibility)."""
    global APP_STATE
    APP_STATE = new_state


# --- Legacy audio integration ---
try:
    from speak import speak
except ImportError:
    def speak(text: str) -> None:
        time.sleep(2)

try:
    from brain import ask_brain
except ImportError:
    def ask_brain(prompt: str) -> str:
        return f"Mock reply to: {prompt}"


def _speak_task(text: str) -> None:
    """Background speak task (legacy)."""
    try:
        speak(text)
    finally:
        set_is_speaking(False)
        set_app_state("IDLE")


def speak_threaded(text: str) -> None:
    """Speak in background thread (legacy)."""
    set_is_speaking(True)
    thread = threading.Thread(target=_speak_task, args=(text,), daemon=True)
    thread.start()


# --- Main entry point ---
if __name__ == "__main__":
    run_cli()
