"""CLI package for The Core terminal interface.

This package provides a cyberpunk-themed terminal UI for the AI assistant.
"""

import queue
import threading
import time

from cli.state import (
    AppState,
    StateManager,
    get_state_manager,
    STATE_MESSAGES,
    STATE_HINTS,
)
from cli.theme import (
    SOLARIZED_LIGHT_THEME,
    CYBERPUNK_THEME,
    SOLARIZED_COLORS,
    CYBERPUNK_COLORS,
)
from cli.avatar import AIAvatar, AntigravityAvatar
from cli.waveform import Waveform
from cli.layout import make_layout

# --- Legacy theme alias ---
SOLARIZED_THEME = SOLARIZED_LIGHT_THEME
COLORS = SOLARIZED_COLORS  # Default to Solarized Light colors

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


__all__ = [
    # New exports
    'AppState',
    'StateManager',
    'get_state_manager',
    'SOLARIZED_LIGHT_THEME',
    'CYBERPUNK_THEME',
    'SOLARIZED_COLORS',
    'CYBERPUNK_COLORS',
    'COLORS',
    'AIAvatar',
    'BrailleAvatar',
    'Waveform',
    'make_layout',
    # Legacy exports
    'SOLARIZED_THEME',
    'APP_STATE',
    'response_queue',
    'is_speaking',
    'get_is_speaking',
    'set_is_speaking',
    'set_app_state',
    'speak_threaded',
]
