from rich.theme import Theme

# Solarized Light Palette
SOLARIZED_THEME = Theme({
    "info": "#268bd2",       # Blue
    "warning": "#d33682",    # Magenta
    "danger": "#cb4b16",     # Orange
    "success": "#2aa198",    # Cyan
    "base": "#657b83",       # Base text
    "header": "bold #268bd2",
    "avatar.eyes": "#268bd2",
    "avatar.mouth": "#d33682",
    "waveform": "#2aa198",
    "user_input": "#cb4b16",
})

import random

class AIAvatar:
    def __init__(self):
        self.blink_rate = 0.05  # Chance to blink per frame

    def get_frame(self, state):
        eyes = "O   O"  # Open eyes
        mouth = " --- "  # Closed mouth

        # IDLE: Blinking logic
        if state == "IDLE":
            if random.random() < self.blink_rate:
                eyes = "-   -"  # Blink
        
        # TALKING: Mouth movement
        elif state == "TALKING":
            mouth_variants = ["  o  ", "  O  ", " --- ", "  -  "]
            mouth = random.choice(mouth_variants)
            # Occasional blink while talking too
            if random.random() < (self.blink_rate / 2):
                eyes = "-   -"

        # ASCII Art Construction
        # Using box drawing chars as per guidelines
        frame = (
            f" ┌───────────────┐ \n"
            f" │    {eyes}    │ \n"
            f" │    {mouth}    │ \n"
            f" └───────────────┘ "
        )
        return frame

class Waveform:
    def __init__(self):
        self.blocks = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        self.width = 30 # Default width

    def get_frame(self, state):
        if state == "IDLE":
            # Return a flat line
            return " " * self.width
        elif state == "TALKING":
            # Generate random waveform
            return "".join(random.choice(self.blocks) for _ in range(self.width))
        return " " * self.width

from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

def make_layout() -> Layout:
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="sidebar", size=25),
        Layout(name="log"),
    )
    return layout

import threading
try:
    from speak import speak
except ImportError:
    def speak(text):
        import time
        time.sleep(2)

is_speaking = False
_speaking_lock = threading.Lock()

def get_is_speaking():
    global is_speaking
    with _speaking_lock:
        return is_speaking

def set_is_speaking(value):
    global is_speaking
    with _speaking_lock:
        is_speaking = value

def _speak_task(text):
    set_is_speaking(True)
    try:
        speak(text)
    finally:
        set_is_speaking(False)

def speak_threaded(text):
    thread = threading.Thread(target=_speak_task, args=(text,), daemon=True)
    thread.start()

if __name__ == "__main__":
    print("Core CLI Module. Import into main application.")
