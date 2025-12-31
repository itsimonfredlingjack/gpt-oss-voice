from rich.theme import Theme
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.console import Console
from rich.markdown import Markdown
from rich.console import Group
import random
import threading
import queue
import time

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

# --- STATE MACHINE DEFINITIONS ---
APP_STATE = "IDLE"  # Options: IDLE, THINKING, TALKING
response_queue = queue.Queue()

def set_app_state(new_state):
    global APP_STATE
    APP_STATE = new_state

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
        
        # THINKING: Eyes looking up
        elif state == "THINKING":
            eyes = "O   O"
            mouth = "  o  " # Small mouth
            # Maybe shift eyes or something simple
            if random.random() < 0.5:
                 eyes = "o   o" # Squint?

        # TALKING: Mouth movement
        elif state == "TALKING":
            mouth_variants = ["  o  ", "  O  ", " --- ", "  -  "]
            mouth = random.choice(mouth_variants)
            # Occasional blink while talking too
            if random.random() < (self.blink_rate / 2):
                eyes = "-   -"

        # ASCII Art Construction
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
        if state == "TALKING":
            # Generate random waveform
            return "".join(random.choice(self.blocks) for _ in range(self.width))
        return " " * self.width

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

# --- AUDIO & BRAIN INTEGRATION ---
try:
    from speak import speak
except ImportError:
    def speak(text):
        time.sleep(2)

try:
    from brain import ask_brain
except ImportError:
    def ask_brain(prompt):
        return f"Mock reply to: {prompt}"

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
    # Flag is set by caller (speak_threaded) to avoid race condition
    try:
        speak(text)
    finally:
        set_is_speaking(False)
        set_app_state("IDLE") # Return to IDLE after speaking

def speak_threaded(text):
    set_is_speaking(True) # Set immediately
    thread = threading.Thread(target=_speak_task, args=(text,), daemon=True)
    thread.start()

def _brain_task(prompt):
    try:
        response = ask_brain(prompt)
        response_queue.put(response)
    except Exception as e:
        response_queue.put(f"Error: {e}")

def run_cli():
    console = Console(theme=SOLARIZED_THEME)
    layout = make_layout()
    avatar = AIAvatar()
    waveform = Waveform()
    
    # Placeholders for Header and Footer
    layout["header"].update(Panel(Text("DEV STATION", justify="center", style="header")))
    layout["footer"].update(Panel(Text("Modell: GPT-OSS | Output: Google Home", justify="center", style="base")))
    
    history = []

    with Live(layout, console=console, refresh_per_second=10) as live:
        while True:
            # Check for AI response
            try:
                ai_text = response_queue.get_nowait()
                history.append(f"AI: {ai_text}")
                set_app_state("TALKING")
                speak_threaded(ai_text)
            except queue.Empty:
                pass

            # Update visual components based on APP_STATE
            avatar_frame = avatar.get_frame(APP_STATE)
            waveform_frame = waveform.get_frame(APP_STATE)

            layout["sidebar"].update(
                Panel(
                    Text(avatar_frame, style="avatar.eyes") + 
                    Text("\n\n") + 
                    Text(waveform_frame, style="waveform"),
                    title=f"AI STATUS: {APP_STATE}",
                    border_style="base"
                )
            )
            
            # Render history log
            log_group = []
            for item in history[-10:]:
                if item.startswith("User: "):
                    log_group.append(Text(item, style="user_input")
                elif item.startswith("AI: "):
                    ai_text = item[4:]
                    log_group.append(Text("AI:", style="info"))
                    log_group.append(Markdown(ai_text))
            
            # Add thinking indicator
            if APP_STATE == "THINKING":
                log_group.append(Text("Thinking...", style="info"))

            layout["log"].update(Panel(Group(*log_group), title="STATION LOG", border_style="base"))

            live.refresh()
            
            # Input handling - ONLY when IDLE
            if APP_STATE == "IDLE":
                # We need to peek if user wants to type, but standard input() is blocking.
                # To make it truly non-blocking without robust input libs is hard.
                # BUT, we can pause animation to take input as agreed in spec.
                # However, the loop must continue to update animations if we are NOT idle.
                # Since we are in IDLE block, we can block here for input.
                
                # Check if we should prompt
                # NOTE: This implementation effectively pauses the IDLE animation (blinking)
                # while waiting for input. This is a known trade-off.
                # To fix this properly requires async input or threads for input.
                # For this Hack, we will accept that IDLE animation stops while waiting for user.
                
                live.stop()
                try:
                    user_input = console.input("[user_input]User > [/user_input]")
                    if user_input.lower() in ["exit", "quit"]:
                        break
                    if user_input.strip():
                        history.append(f"User: {user_input}")
                        set_app_state("THINKING")
                        # Spawn brain thread
                        threading.Thread(target=_brain_task, args=(user_input,), daemon=True).start()
                except EOFError:
                    break
                finally:
                    live.start()

if __name__ == "__main__":
    run_cli()