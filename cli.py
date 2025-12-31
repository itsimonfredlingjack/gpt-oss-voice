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

if __name__ == "__main__":
    print("Core CLI Module. Import into main application.")
