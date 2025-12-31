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

try:
    from brain import ask_brain
except ImportError:
    def ask_brain(prompt):
        return f"Mock reply to: {prompt}"

from rich.live import Live
from rich.console import Console
from rich.markdown import Markdown
from rich.renderable import RenderableType
import time

def run_cli():
    console = Console(theme=SOLARIZED_THEME)
    layout = make_layout()
    avatar = AIAvatar()
    waveform = Waveform()
    
    # Placeholders for Header and Footer
    layout["header"].update(Panel(Text("DEV STATION", justify="center", style="header")))
    layout["footer"].update(Panel(Text("Modell: GPT-OSS | Output: Google Home", justify="center", style="base")))
    
    # history will now store Renderable objects or raw text to be rendered
    history = []

    with Live(layout, console=console, refresh_per_second=10) as live:
        while True:
            # Update visual components
            state = "TALKING" if get_is_speaking() else "IDLE"
            
            # The get_frame methods already handle the randomization for blinking/mouth
            avatar_frame = avatar.get_frame(state)
            waveform_frame = waveform.get_frame(state)

            layout["sidebar"].update(
                Panel(
                    Text(avatar_frame, style="avatar.eyes") + 
                    Text("\n\n") + 
                    Text(waveform_frame, style="waveform"),
                    title="AI STATUS",
                    border_style="base"
                )
            )
            
            # Render history log
            log_group = []
            for item in history[-10:]:
                if item.startswith("User: "):
                    log_group.append(Text(item, style="user_input"))
                elif item.startswith("AI: "):
                    # Strip the "AI: " prefix for cleaner markdown rendering
                    ai_text = item[4:]
                    log_group.append(Text("AI:", style="info"))
                    log_group.append(Markdown(ai_text))
            
            from rich.console import Group
            layout["log"].update(Panel(Group(*log_group), title="STATION LOG", border_style="base"))

            live.refresh()
            
            # Non-blocking input is tricky in standard terminal without curses/prompt_toolkit
            # The spec says: "Ta input från användaren (animationen kan pausa här, det är ok)"
            # So we exit the Live context to take input, or use a separate thread for input.
            # Let's follow the spec: "animationen kan pausa här, det är ok"
            
            # To take input while Live is running, we can stop Live temporarily
            live.stop()
            try:
                user_input = console.input("[user_input]User > [/user_input]")
            except EOFError:
                break
            if user_input.lower() in ["exit", "quit"]:
                break
            
            history.append(f"User: {user_input}")
            
            # Thinking state
            layout["log"].update(Panel(Text(log_content + f"\nUser: {user_input}\nThinking...", style="base"), title="STATION LOG", border_style="base"))
            live.start()
            
            response = ask_brain(user_input)
            history.append(f"AI: {response}")
            
            # Start speaking
            speak_threaded(response)
            
            # Continue loop to animate TALKING state

if __name__ == "__main__":
    run_cli()
    print("Core CLI Module. Import into main application.")
