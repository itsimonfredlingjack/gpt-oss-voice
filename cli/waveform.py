"""Audio waveform visualization for the CLI.

Provides animated waveform that responds to application state.
"""

from dataclasses import dataclass
from typing import Callable, Optional
from rich.text import Text
import random
import math


@dataclass
class WaveformConfig:
    """Configuration for waveform display.

    Attributes:
        width: Number of characters wide.
        style: Rich style to apply.
    """
    width: int = 28
    style: str = 'waveform'


class Waveform:
    """Animated waveform visualization.

    Displays a flat line when idle, animated waves when talking.

    Attributes:
        config: WaveformConfig instance.
    """

    # Unicode block characters for waveform height
    BLOCKS = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

    def __init__(self, config: Optional[WaveformConfig] = None):
        """Initialize waveform.

        Args:
            config: Optional configuration, uses defaults if None.
        """
        self.config = config or WaveformConfig()
        self._phase = 0.0
        self._amplitude_callback: Optional[Callable[[], float]] = None

    @property
    def width(self) -> int:
        """Get waveform width."""
        return self.config.width

    def set_amplitude_callback(self, callback: Callable[[], float]) -> None:
        """Set callback for real audio amplitude.

        Args:
            callback: Function returning amplitude 0.0-1.0.
        """
        self._amplitude_callback = callback

    def get_frame(self, state: str) -> str:
        """Generate waveform frame based on state.

        Args:
            state: Current state ('IDLE', 'THINKING', 'TALKING').

        Returns:
            String of block characters representing waveform.
        """
        if state == 'IDLE':
            # Flat line with occasional tiny pulse
            if random.random() < 0.05:
                return self._generate_pulse()
            return '─' * self.config.width

        elif state == 'THINKING':
            # Subtle pulsing pattern
            return self._generate_thinking()

        elif state == 'TALKING':
            # Full animated waveform with gradient colors
            return self._generate_talking_gradient()

        return ' ' * self.config.width
    
    def get_frame_rich(self, state: str) -> Text:
        """Generate waveform frame with gradient colors (Rich Text).

        Args:
            state: Current state ('IDLE', 'THINKING', 'TALKING').

        Returns:
            Rich Text with gradient-colored waveform.
        """
        if state == 'TALKING':
            return self._generate_talking_gradient_rich()
        else:
            # For IDLE and THINKING, return simple string as Text
            return Text(self.get_frame(state), style='waveform')

    def _generate_pulse(self) -> str:
        """Generate a small pulse animation."""
        result = ['─'] * self.config.width
        center = self.config.width // 2
        result[center] = '▂'
        if center > 0:
            result[center - 1] = '▁'
        if center < self.config.width - 1:
            result[center + 1] = '▁'
        return ''.join(result)

    def _generate_thinking(self) -> str:
        """Generate subtle thinking animation."""
        self._phase += 0.2
        result = []

        for i in range(self.config.width):
            # Slow, small sine wave
            wave = math.sin(self._phase + i * 0.3) * 0.3 + 0.3
            height = int(wave * 3)
            height = max(0, min(len(self.BLOCKS) - 1, height))
            result.append(self.BLOCKS[height])

        return ''.join(result)

    def _generate_talking(self) -> str:
        """Generate active talking waveform with enhanced patterns."""
        # Get amplitude from callback or use random
        if self._amplitude_callback:
            amp = self._amplitude_callback()
        else:
            amp = random.uniform(0.5, 1.0)

        self._phase += 0.5  # Slightly faster for more dynamic feel
        result = []

        for i in range(self.config.width):
            # More complex wave combination for richer pattern
            wave1 = math.sin(self._phase + i * 0.5) * 0.4
            wave2 = math.sin(self._phase * 1.5 + i * 0.3) * 0.3
            wave3 = math.sin(self._phase * 2.0 + i * 0.7) * 0.2  # Additional harmonic
            noise = random.uniform(-0.15, 0.15)

            combined = (wave1 + wave2 + wave3 + noise + 0.5) * amp
            height = int(combined * (len(self.BLOCKS) - 1))
            height = max(0, min(len(self.BLOCKS) - 1, height))
            result.append(self.BLOCKS[height])

        return ''.join(result)
    
    def _generate_talking_gradient(self) -> str:
        """Generate talking waveform (string version for compatibility)."""
        return self._generate_talking()
    
    def _generate_talking_gradient_rich(self) -> Text:
        """Generate talking waveform with gradient colors (supreme design).
        
        Returns:
            Rich Text with gradient colors based on height.
        """
        # Get amplitude from callback or use random
        if self._amplitude_callback:
            amp = self._amplitude_callback()
        else:
            amp = random.uniform(0.5, 1.0)

        self._phase += 0.5
        result = Text()

        for i in range(self.config.width):
            # More complex wave combination for richer pattern
            wave1 = math.sin(self._phase + i * 0.5) * 0.4
            wave2 = math.sin(self._phase * 1.5 + i * 0.3) * 0.3
            wave3 = math.sin(self._phase * 2.0 + i * 0.7) * 0.2
            noise = random.uniform(-0.15, 0.15)

            combined = (wave1 + wave2 + wave3 + noise + 0.5) * amp
            height = int(combined * (len(self.BLOCKS) - 1))
            height = max(0, min(len(self.BLOCKS) - 1, height))
            char = self.BLOCKS[height]
            
            # Supreme design: Gradient coloring based on height
            # High peaks = pink, mid = cyan, low = dim blue
            if height > 6:
                style = 'waveform.peak'  # High peaks = neon pink
            elif height > 3:
                style = 'waveform.mid'   # Mid = cyan
            else:
                style = 'waveform.low'   # Low = dim blue
            
            result.append(char, style=style)

        return result

    def reset(self) -> None:
        """Reset waveform phase."""
        self._phase = 0.0
