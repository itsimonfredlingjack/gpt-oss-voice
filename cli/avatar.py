"""Spherical Braille AI Avatar with organic animations.

Provides a geodesic, circular avatar using high-res Braille patterns
that breathes, rotates, and pulses based on application state.
"""

from dataclasses import dataclass
from typing import Optional
from rich.text import Text
import random
import math


class BrailleAvatar:
    """Organic spherical avatar using Braille patterns.

    The avatar displays different organic animations based on state:
    - IDLE: Subtle breathing rotation with density shifts
    - THINKING: Faster rotation with vertical data streams
    - TALKING: Pulsates in sync with audio waveform

    Attributes:
        radius: Radius of the sphere in characters (default 5).
    """

    # Braille density levels (empty to full)
    BRAILLE_DENSITY = [
        ' ',      # Empty
        '⠁', '⠂', '⠄', '⠈', '⠐', '⠠',  # Sparse
        '⠃', '⠅', '⠉', '⠑', '⠡', '⠰',  # Low density
        '⡀', '⡁', '⡂', '⡄', '⡈', '⡐',  # Medium-low
        '⣀', '⣁', '⣂', '⣄', '⣈', '⣐',  # Medium
        '⣠', '⣡', '⣢', '⣤', '⣨', '⣰',  # Medium-high
        '⣷', '⣯', '⣿',                    # High density
    ]

    # Braille patterns for data streams (vertical emphasis)
    STREAM_PATTERNS = [
        '⠁', '⠃', '⠇', '⡇', '⣇', '⣧', '⣷', '⣿',
        '⡿', '⠿', '⠟', '⠛', '⠓', '⠑', '⠁',
    ]

    def __init__(self, radius: int = 5):
        """Initialize Braille avatar.

        Args:
            radius: Radius of the spherical avatar.
        """
        self.radius = radius
        self.width = radius * 2 + 1
        self.height = radius * 2 + 1

        # Animation state
        self._rotation = 0.0
        self._breathing_phase = 0.0
        self._pulse_scale = 1.0
        self._stream_offset = 0
        self._glitch_intensity = 0.0

    def render(self, state: str) -> Text:
        """Render avatar as Rich Text with organic animation.

        Args:
            state: Current state ('IDLE', 'THINKING', 'TALKING').

        Returns:
            Rich Text object with styled spherical avatar.
        """
        if state == 'IDLE':
            return self._render_idle()
        elif state == 'THINKING':
            return self._render_thinking()
        elif state == 'TALKING':
            return self._render_talking()
        else:
            return self._render_idle()

    def _render_idle(self) -> Text:
        """Render idle state: gentle breathing and rotation."""
        # Update breathing animation
        self._breathing_phase += 0.05
        self._rotation += 0.02

        # Breathing effect: subtle scale oscillation
        breath_scale = 1.0 + 0.1 * math.sin(self._breathing_phase)

        text = Text()

        for y in range(self.height):
            line = Text()
            for x in range(self.width):
                # Calculate distance from center
                dx = x - self.radius
                dy = (y - self.radius) * 1.8  # Adjust for character aspect ratio
                distance = math.sqrt(dx*dx + dy*dy) / breath_scale

                # Sphere surface calculation
                if distance < self.radius:
                    # Calculate depth (z-coordinate)
                    z = math.sqrt(max(0, self.radius*self.radius - distance*distance))

                    # Add rotation for organic motion
                    angle = math.atan2(dy, dx) + self._rotation

                    # Calculate density based on depth and rotation
                    density = (z / self.radius) * 0.8 + 0.2
                    density *= (1.0 + 0.2 * math.sin(angle * 3))

                    # Add subtle noise
                    density += random.uniform(-0.05, 0.05)
                    density = max(0, min(1, density))

                    # Map to Braille character
                    braille_idx = int(density * (len(self.BRAILLE_DENSITY) - 1))
                    char = self.BRAILLE_DENSITY[braille_idx]

                    # Supreme design: Depth-based gradient coloring
                    # z/depth determines brightness - closer = brighter
                    depth_ratio = z / self.radius
                    if depth_ratio > 0.8:
                        style = 'avatar.core'  # Blinding core - brightest
                    elif depth_ratio > 0.5:
                        style = 'avatar.bright'  # Bright surface - cyan
                    elif depth_ratio > 0.3:
                        style = 'avatar.medium'  # Medium depth - dimmer cyan
                    else:
                        style = 'avatar.dim'  # Dim edges - fade to dark

                    line.append(char, style=style)
                else:
                    line.append(' ')

            text.append(line)
            text.append('\n')

        return text

    def _render_thinking(self) -> Text:
        """Render thinking state: faster rotation with data streams."""
        # Update thinking animation - faster rotation
        self._rotation += 0.08
        self._stream_offset = (self._stream_offset + 1) % len(self.STREAM_PATTERNS)

        text = Text()

        for y in range(self.height):
            line = Text()
            for x in range(self.width):
                dx = x - self.radius
                dy = (y - self.radius) * 1.8
                distance = math.sqrt(dx*dx + dy*dy)

                if distance < self.radius:
                    z = math.sqrt(max(0, self.radius*self.radius - distance*distance))
                    angle = math.atan2(dy, dx) + self._rotation

                    # Base density
                    density = (z / self.radius) * 0.8 + 0.2

                    # Add vertical data stream effect
                    stream_phase = (y + self._stream_offset) % len(self.STREAM_PATTERNS)
                    if abs(dx) < 2 and random.random() > 0.3:  # Central vertical stream
                        char = self.STREAM_PATTERNS[stream_phase]
                        style = 'avatar.thinking'
                    else:
                        density *= (1.0 + 0.3 * math.sin(angle * 5))
                        density = max(0, min(1, density))
                        braille_idx = int(density * (len(self.BRAILLE_DENSITY) - 1))
                        char = self.BRAILLE_DENSITY[braille_idx]

                        if density > 0.6:
                            style = 'avatar.thinking'
                        else:
                            style = 'dim'

                    line.append(char, style=style)
                else:
                    line.append(' ')

            text.append(line)
            text.append('\n')

        return text

    def _render_talking(self) -> Text:
        """Render talking state: pulsating sphere."""
        # Update pulse animation
        self._breathing_phase += 0.2
        self._rotation += 0.05

        # Strong pulse effect
        pulse = 0.5 + 0.5 * math.sin(self._breathing_phase)
        self._pulse_scale = 0.8 + 0.4 * pulse

        text = Text()

        for y in range(self.height):
            line = Text()
            for x in range(self.width):
                dx = x - self.radius
                dy = (y - self.radius) * 1.8
                distance = math.sqrt(dx*dx + dy*dy) / self._pulse_scale

                if distance < self.radius:
                    z = math.sqrt(max(0, self.radius*self.radius - distance*distance))
                    angle = math.atan2(dy, dx) + self._rotation

                    # Density with pulse modulation
                    density = (z / self.radius) * 0.9 + 0.1
                    density *= (1.0 + 0.3 * math.sin(angle * 4 + self._breathing_phase))

                    # Add pulse rings
                    ring_dist = abs(distance - self.radius * 0.7)
                    if ring_dist < 0.5:
                        density = min(1.0, density + 0.3 * (1.0 - ring_dist * 2))

                    density = max(0, min(1, density))
                    braille_idx = int(density * (len(self.BRAILLE_DENSITY) - 1))
                    char = self.BRAILLE_DENSITY[braille_idx]

                    # Enhanced talking state with pulse effect
                    pulse_mod = 0.3 * math.sin(self._breathing_phase * 2)
                    if density > 0.8:
                        style = 'avatar.pulse'  # Pulsing cyan core
                    elif density > 0.6:
                        style = 'waveform.active'  # Bold cyan
                    elif density > 0.4:
                        style = 'avatar.frame'
                    else:
                        style = 'dim'

                    line.append(char, style=style)
                else:
                    line.append(' ')

            text.append(line)
            text.append('\n')

        return text

    def set_pulse_scale(self, scale: float) -> None:
        """Set pulse scale from external source (e.g., audio amplitude).

        Args:
            scale: Pulse scale factor (0.5-1.5 recommended).
        """
        self._pulse_scale = max(0.5, min(1.5, scale))

    def reset(self) -> None:
        """Reset animation state."""
        self._rotation = 0.0
        self._breathing_phase = 0.0
        self._pulse_scale = 1.0
        self._stream_offset = 0


# Legacy compatibility alias
AIAvatar = BrailleAvatar
