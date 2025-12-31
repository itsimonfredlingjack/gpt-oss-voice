"""AI Avatar with cyberpunk ASCII art and state-based animations.

Provides a multi-component avatar that can display different
expressions based on the application state.
"""

from dataclasses import dataclass
from typing import Optional
from rich.text import Text
import random
import math


@dataclass
class AvatarComponent:
    """A single line of the avatar with its style."""
    content: str
    style: str


class AIAvatar:
    """Cyberpunk AI avatar with expressive animations.

    The avatar displays different expressions based on state:
    - IDLE: Calm, occasional blinking, ambient glow
    - THINKING: Eyes scanning, neural activity indicator
    - TALKING: Mouth animating, sound waves emanating

    Attributes:
        blink_rate: Probability of blinking per frame (default 0.03).
    """

    # Eye variants - more expressive
    EYES = {
        'open': '◉ ◉',
        'blink': '─ ─',
        'wide': '⊙ ⊙',
        'squint': '◡ ◡',
        'look_left': '◉  ◉',
        'look_right': ' ◉ ◉',
        'look_up': '◠ ◠',
        'glitch': '█ █',
        'scan': '▣ ▣',
        'glow': '◎ ◎',
    }

    # Mouth variants - more animation frames
    MOUTHS = {
        'closed': '━━━━━',
        'smile': '╰─┬─╯',
        'talk_1': '╭─○─╮',
        'talk_2': '│ ● │',
        'talk_3': '╰─◎─╯',
        'talk_4': '├─●─┤',
        'think': '╌╌╌╌╌',
        'processing': '▰▰▰▰▰',
        'hum': '∿∿∿∿∿',
    }

    # Antenna animations
    ANTENNA = {
        'idle': '   ╽   ',
        'pulse_1': '  ╿╽╿  ',
        'pulse_2': ' ╿ ╽ ╿ ',
        'pulse_3': '╿  ╽  ╿',
        'scan': '  ◠╽◠  ',
        'transmit': '  ≋╽≋  ',
    }

    # Status indicators with glow effect
    STATUS_ICONS = {
        'IDLE': ('◇', '◆'),
        'THINKING': ('◈', '◉'),
        'TALKING': ('◆', '●'),
    }

    def __init__(self, blink_rate: float = 0.03):
        """Initialize avatar.

        Args:
            blink_rate: Probability of blinking per frame.
        """
        self.blink_rate = blink_rate
        self._thinking_frame = 0
        self._talking_frame = 0
        self._idle_frame = 0
        self._glitch_counter = 0
        self._pulse_phase = 0.0

    def get_frame(self, state: str) -> str:
        """Get avatar frame as plain string (legacy compatibility).

        Args:
            state: Current state ('IDLE', 'THINKING', 'TALKING').

        Returns:
            ASCII art string of the avatar.
        """
        text = self.render(state)
        return text.plain

    def render(self, state: str) -> Text:
        """Render avatar as Rich Text with component styling.

        Args:
            state: Current state ('IDLE', 'THINKING', 'TALKING').

        Returns:
            Rich Text object with styled avatar.
        """
        eyes, mouth, eye_style, antenna = self._get_state_parts(state)
        status_pair = self.STATUS_ICONS.get(state, ('◇', '◆'))

        # Animate status icon
        self._pulse_phase += 0.15
        status = status_pair[0] if math.sin(self._pulse_phase) > 0 else status_pair[1]

        text = Text()

        # Outer antenna/signal
        text.append(f'     {antenna}     \n', style='avatar.frame')

        # Top border with corner accents
        text.append('  ╔═══════════════╗\n', style='avatar.frame')

        # Status indicator row
        text.append('  ║', style='avatar.frame')
        text.append(f'    ┌─{status}─┐    ', style=eye_style)
        text.append('║\n', style='avatar.frame')

        # Eyes row with side panels
        text.append('  ║', style='avatar.frame')
        text.append(' ◄ ', style='dim')
        text.append(f'  {eyes}  ', style=eye_style)
        text.append(' ► ', style='dim')
        text.append('║\n', style='avatar.frame')

        # Nose/sensor row
        text.append('  ║', style='avatar.frame')
        text.append('    └──▽──┘    ', style='avatar.frame')
        text.append('║\n', style='avatar.frame')

        # Mouth row
        text.append('  ║', style='avatar.frame')
        text.append(f'    ╱{mouth}╲    ', style='avatar.mouth')
        text.append('║\n', style='avatar.frame')

        # Bottom detail row
        text.append('  ║', style='avatar.frame')
        text.append('   ╰───────╯   ', style='dim')
        text.append('║\n', style='avatar.frame')

        # Bottom border
        text.append('  ╚═══════════════╝', style='avatar.frame')

        return text

    def _get_state_parts(self, state: str) -> tuple[str, str, str, str]:
        """Get eyes, mouth, eye style, and antenna for current state.

        Args:
            state: Current state string.

        Returns:
            Tuple of (eyes, mouth, eye_style, antenna).
        """
        eye_style = 'avatar.eyes'
        antenna = self.ANTENNA['idle']

        if state == 'IDLE':
            # Occasional blink, otherwise calm
            self._idle_frame = (self._idle_frame + 1) % 60
            if random.random() < self.blink_rate:
                eyes = self.EYES['blink']
            elif self._idle_frame % 30 == 0:
                eyes = self.EYES['glow']
            else:
                eyes = self.EYES['open']
            mouth = self.MOUTHS['closed']
            antenna = self.ANTENNA['idle']

        elif state == 'THINKING':
            # Animated thinking - cycle through looks
            self._thinking_frame = (self._thinking_frame + 1) % 12
            eye_style = 'avatar.thinking'

            if self._thinking_frame < 3:
                eyes = self.EYES['look_left']
            elif self._thinking_frame < 6:
                eyes = self.EYES['scan']
            elif self._thinking_frame < 9:
                eyes = self.EYES['look_right']
            else:
                eyes = self.EYES['squint']

            # Processing mouth animation
            dots = (self._thinking_frame % 4)
            mouth = '▪' * dots + '─' * (5 - dots)

            # Antenna pulse animation
            pulse_seq = ['pulse_1', 'pulse_2', 'pulse_3', 'pulse_2']
            antenna = self.ANTENNA[pulse_seq[self._thinking_frame % 4]]

        elif state == 'TALKING':
            # Animated talking
            self._talking_frame = (self._talking_frame + 1) % 8

            # Occasional blink while talking
            if random.random() < self.blink_rate / 2:
                eyes = self.EYES['blink']
            elif self._talking_frame % 4 == 0:
                eyes = self.EYES['wide']
            else:
                eyes = self.EYES['open']

            # Mouth animation cycle
            mouth_seq = ['talk_1', 'talk_2', 'talk_3', 'talk_4']
            mouth = self.MOUTHS[mouth_seq[self._talking_frame % 4]]

            # Transmit antenna
            antenna = self.ANTENNA['transmit']

        else:
            # Default/unknown state
            eyes = self.EYES['open']
            mouth = self.MOUTHS['closed']
            antenna = self.ANTENNA['idle']

        return eyes, mouth, eye_style, antenna

    def glitch(self) -> Text:
        """Render a glitched frame (for errors/transitions).

        Returns:
            Rich Text with glitch effect.
        """
        self._glitch_counter += 1

        text = Text()
        glitch_chars = '█▓▒░╔╗║╚╝═'

        for _ in range(6):
            line = ''.join(random.choice(glitch_chars) for _ in range(17))
            text.append(line + '\n', style='danger')

        return text
