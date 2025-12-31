"""Audio waveform visualization for the CLI.

Provides animated waveform that responds to application state.
"""

from dataclasses import dataclass
from typing import Callable, Optional
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
            # Full animated waveform
            return self._generate_talking()

        return ' ' * self.config.width

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
        """Generate active talking waveform."""
        # Get amplitude from callback or use random
        if self._amplitude_callback:
            amp = self._amplitude_callback()
        else:
            amp = random.uniform(0.4, 1.0)

        self._phase += 0.4
        result = []

        for i in range(self.config.width):
            # Combination of sine waves with noise
            wave1 = math.sin(self._phase + i * 0.5) * 0.4
            wave2 = math.sin(self._phase * 1.5 + i * 0.3) * 0.3
            noise = random.uniform(-0.2, 0.2)

            combined = (wave1 + wave2 + noise + 0.5) * amp
            height = int(combined * (len(self.BLOCKS) - 1))
            height = max(0, min(len(self.BLOCKS) - 1, height))
            result.append(self.BLOCKS[height])

        return ''.join(result)

    def reset(self) -> None:
        """Reset waveform phase."""
        self._phase = 0.0
