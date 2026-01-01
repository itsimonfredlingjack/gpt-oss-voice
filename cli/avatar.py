"""Mecha-Core Unit 734 - High Density Cybernetic Entity.

Constructed from heavy block elements and Unicode geometry.
"""

from rich.text import Text
import time
import random
import math

class MechaCoreAvatar:
    """A heavy robotic head constructed from block characters.
    
    States:
    - IDLE (Sentry): Scanning eye, subtle plate shifts.
    - THINKING (Trauma): Glitching, red eye, erratic movement.
    - TALKING (Voice): Jaw movement, sonic rings.
    """

    def __init__(self, width: int = 40, height: int = 15):
        self.width = width
        self.height = height
        
        # ASCII/Unicode Art Structure
        # 15 lines height
        self.base_structure = [
            # 0
            "      ▄▄████████████████████▄▄      ",
            # 1
            "    ▄██████████████████████████▄    ",
            # 2
            "   ███▀▀    ▀▀████████▀▀    ▀▀███   ",
            # 3 (Eye Level) - Index 3
            "  ███│  ░░░░  │██████│  ░░░░  │███  ", 
            # 4
            "  ███│  ░░░░  │██████│  ░░░░  │███  ",
            # 5
            "  ███▄        ▄██████▄        ▄███  ",
            # 6
            "   ████▄▄  ▄▄██████████▄▄  ▄▄████   ",
            # 7
            "   ▀████████████████████████████▀   ",
            # 8 (Mouth Level) - Index 8
            "    ▀██████████████████████████▀    ",
            # 9
            "     ▀████████▀▀    ▀▀████████▀     ",
            # 10
            "      ▀████▀            ▀████▀      ",
            # 11
            "       ▀██                ██▀       ",
            # 12
            "         ▀█▄            ▄█▀         ",
            # 13
            "           ▀█▄▄      ▄▄█▀           ",
            # 14
            "             ▀▀▀▀▀▀▀▀▀▀             ",
        ]
        
        self.scan_pos = 0
        self.scan_dir = 1
        self.jaw_offset = 0

    def render(self, state: str) -> Text:
        """Render the Mecha-Core."""
        output = Text()
        
        t = time.time()
        
        # --- State Logic ---
        
        # 1. SCANNER (Eye Movement)
        if state == "THINKING":
            # Erratic movement
            self.scan_pos = random.randint(0, 10)
            eye_color = "mech.eye.active"
            base_style = "mech.armor"
            
            # Global color shift for overheating
            if random.random() < 0.3:
                base_style = "glitch.1"
                
        elif state == "IDLE":
            # Smooth Sentry Scan
            # Map sine wave to 0-6 range for eye width
            self.scan_pos = int((math.sin(t * 2) + 1) * 3) 
            eye_color = "mech.eye"
            base_style = "mech.armor"
            
        else: # TALKING
            self.scan_pos = 3 # Center
            eye_color = "mech.eye.active"
            base_style = "mech.armor"

        # 2. JAW (Speaking)
        jaw_shift = 0
        if state == "TALKING":
            # Simple mouth open/close
            if math.sin(t * 15) > 0:
                jaw_shift = 1
        
        
        # --- Rendering ---
        
        for i, line in enumerate(self.base_structure):
            row_text = Text(line, style=base_style)
            
            # Apply Eye Overlay (Rows 3 & 4)
            if i in [3, 4]:
                # Locate the "░░░░" segments and replace with "████" or "▒▒▒▒" based on scan
                # The visual has two eyes. We'll scan both.
                # Left Eye area approx char index 8-12
                # Right Eye area approx char index 24-28
                
                # We'll just construct a "Scan Line" overlay
                # Simple approach: Replace the 'dotted' area with proper scan block
                
                plain_line = line
                # Modify string for scanner
                if state == "THINKING" or state == "IDLE":
                     # Scanner overlay logic
                     # Let's say scanner is a bright block moving L-R inside the eye sockets
                     left_socket_start = 8
                     left_socket_width = 4
                     right_socket_start = 24
                     right_socket_width = 4
                     
                     scan_idx = self.scan_pos % 4
                     
                     chars = list(plain_line)
                     # Left Eye
                     if chars[left_socket_start + scan_idx] == '░':
                         chars[left_socket_start + scan_idx] = '█'
                     # Right Eye
                     if chars[right_socket_start + scan_idx] == '░':
                         chars[right_socket_start + scan_idx] = '█'
                         
                     row_text = Text("".join(chars), style=base_style)
                     
                     # Highlight the eye pixels specifically
                     row_text.stylize(eye_color, left_socket_start, left_socket_start + 4)
                     row_text.stylize(eye_color, right_socket_start, right_socket_start + 4)

            # Apply Jaw Movement (Rows 8+)
            # If jaw is open, we push these rows down or modify them
            # Since we can't easily "push" locally in terminal without clearing,
            # We will modify the mouth area texture
            if i == 9 and jaw_shift > 0:
                 # Open mouth visual
                 row_text = Text("     ▀████████▄▄    ▄▄████████▀     ", style="mech.mouth")
            
            # Glitch effect (Random char replacement logic for structural trauma)
            if state == "THINKING" and random.random() < 0.1:
                # Corrupt this line
                row_text = Text("".join([random.choice("█▓▒░#") for _ in line]), style="glitch.1")

            output.append(row_text)
            output.append("\n")
            
        return output

# Alias
AIAvatar = MechaCoreAvatar
TesseractAvatar = MechaCoreAvatar # Compat
AntigravityAvatar = MechaCoreAvatar # Compat
