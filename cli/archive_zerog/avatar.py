"""Antigravity Avatar - The Nebula.

A particle-based floating avatar that simulates a living cloud of data.
"""

from rich.text import Text
import random
import math
import time

class AntigravityAvatar:
    """Particle-based Nebula Avatar.
    
    States:
    - IDLE: Particles gently orbit an invisible center.
    - THINKING: Implosion (fast spin towards center).
    - TALKING: Expansion/Pulse (reacts to voice).
    """

    PARTICLE_CHARS = ['·', '°', '+', '⋆', '•', '·']
    
    def __init__(self, width: int = 40, height: int = 20):
        self.width = width
        self.height = height
        self.particles = []
        self._init_particles(30) # Start with 30 particles
        self.center_x = width // 2
        self.center_y = height // 2
        
    def _init_particles(self, count: int):
        self.particles = []
        for _ in range(count):
            self.particles.append({
                'angle': random.uniform(0, 6.28),
                'speed': random.uniform(0.02, 0.1),
                'radius': random.uniform(2, 8),
                'char': random.choice(self.PARTICLE_CHARS),
                'z': random.uniform(0.5, 1.5) # Depth factor
            })

    def render(self, state: str) -> Text:
        # Create empty grid
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        t = time.time()
        
        # Style selection
        if state == "THINKING":
            style_base = "avatar.thinking"
        elif state == "TALKING":
            style_base = "avatar.talking"
        else:
            style_base = "avatar.particle"
            
        for p in self.particles:
            # Physics Calculation
            if state == "THINKING":
                # Implosion: Fast spin, radius shrinks
                target_r = 1.0
                r_force = (target_r - p['radius']) * 0.1
                p['radius'] += r_force
                speed = p['speed'] * 8.0 # Super fast spin
                
            elif state == "TALKING":
                # Pulse: Radius expands/contracts rhythmically
                pulse = math.sin(t * 8) * 3.0
                base_r = 6.0 + pulse
                r_force = (base_r - p['radius']) * 0.2
                p['radius'] += r_force
                speed = p['speed'] * 2.0
                
            else: # IDLE
                # Float: Gentle orbit with slight radial drift
                drift = math.sin(t * 0.5 + p['angle']) * 1.0
                target_r = 5.0 + drift
                r_force = (target_r - p['radius']) * 0.05
                p['radius'] += r_force
                speed = p['speed']

            # Update angle
            p['angle'] += speed
            
            # Calculate 2D position from Polar coordinates
            # Correct aspect ratio (terminals are usually 2:1 height wise)
            aspect = 0.5 
            
            x = int(self.center_x + math.cos(p['angle']) * p['radius'] * 2.0)
            y = int(self.center_y + math.sin(p['angle']) * p['radius'])
            
            # Boundary check
            if 0 <= y < self.height and 0 <= x < self.width:
                grid[y][x] = p['char']

        # Add center core if Thinking or Talking
        if state in ["THINKING", "TALKING"]:
             if 0 <= self.center_y < self.height and 0 <= self.center_x < self.width:
                 grid[self.center_y][self.center_x] = "✦"

        # Convert to Rich Text
        text = Text()
        for row in grid:
            line_str = "".join(row)
            text.append(line_str + "\n", style=style_base)
            
        return text

# Alias for backward compatibility
AIAvatar = AntigravityAvatar
