"""Rich layout factory for the CLI interface.

Provides the main screen layout structure.
"""

from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
from typing import Optional


# Layout dimensions
SIDEBAR_WIDTH = 24
HEADER_HEIGHT = 3
FOOTER_HEIGHT = 3


def make_layout() -> Layout:
    """Create the main application layout.

    Structure:
        ┌─────────────────────────────────────┐
        │              HEADER                 │
        ├────────────┬────────────────────────┤
        │  SIDEBAR   │         LOG            │
        │  (Avatar)  │    (Conversation)      │
        ├────────────┴────────────────────────┤
        │              FOOTER                 │
        └─────────────────────────────────────┘

    Returns:
        Configured Rich Layout object.
    """
    layout = Layout(name='root')

    # Main vertical split
    layout.split(
        Layout(name='header', size=HEADER_HEIGHT),
        Layout(name='main'),
        Layout(name='footer', size=FOOTER_HEIGHT),
    )

    # Main horizontal split
    layout['main'].split_row(
        Layout(name='sidebar', size=SIDEBAR_WIDTH),
        Layout(name='log'),
    )

    return layout


def make_header(title: str = 'THE CORE', subtitle: str = '') -> Panel:
    """Create styled header panel with tech decorations (supreme design).

    Args:
        title: Main title text.
        subtitle: Optional subtitle.

    Returns:
        Styled Panel for header.
    """
    import random
    text = Text()
    text.append('◢◤ ', style='header')
    text.append(title, style='header')
    text.append(' ◥◣', style='header')

    if subtitle:
        text.append(f'\n{subtitle}', style='header.subtitle')
        # Add tech decoration (random hex-like string)
        hex_decoration = f"{random.randint(0, 0xFFFF):04X}"
        text.append(f' [{hex_decoration}]', style='dim')

    return Panel(
        text,
        box=ROUNDED,
        border_style='border',
        padding=(1, 2),
    )


def make_footer(
    model: str = 'GPT-OSS',
    output: str = 'Google Home',
    status: str = '',
    hint: str = '',
    speaking_text: Optional[str] = None
) -> Panel:
    """Create styled footer panel with status and user hints.

    Args:
        model: AI model name.
        output: Audio output device.
        status: Status message (state-based).
        hint: User guidance text.

    Returns:
        Styled Panel for footer.
    """
    from rich.console import Group
    from rich.align import Align

    # Status line
    status_text = Text()
    status_text.append('▸ MODEL: ', style='dim')
    status_text.append(model, style='info')
    status_text.append('  ▸ OUTPUT: ', style='dim')
    status_text.append(output, style='success')

    if status:
        # Error status gets danger style
        style = 'danger' if '✗' in status else 'warning'
        status_text.append(f'  ▸ {status}', style=style)

    # Speaking indicator (voice-first feature)
    if speaking_text:
        # Truncate if too long for display
        display_text = (
            speaking_text[:60] + "..." 
            if len(speaking_text) > 60 
            else speaking_text
        )
        speak_indicator = Text()
        speak_indicator.append('🔊 SPEAKING: ', style='bold success')
        speak_indicator.append(display_text, style='italic')
        
        # Combine with existing content
        if hint:
            hint_text = Text()
            hint_text.append('◇ ', style='dim')
            hint_text.append(hint, style='dim italic')
            content = Group(
                status_text,
                Align.center(speak_indicator),
                Align.center(hint_text)
            )
        else:
            content = Group(status_text, Align.center(speak_indicator))
    elif hint:
        # Hint line (user affordance) - only if not speaking
        hint_text = Text()
        hint_text.append('◇ ', style='dim')
        hint_text.append(hint, style='dim italic')
        content = Group(status_text, Align.center(hint_text))
    else:
        content = status_text

    return Panel(
        content,
        box=ROUNDED,
        border_style='border.dim',
        padding=(1, 2),
    )


def make_sidebar_panel(
    avatar_content: Text,
    waveform,  # Can be str or Rich Text
    state: str
) -> Panel:
    """Create styled sidebar panel with avatar and waveform.

    Args:
        avatar_content: Rich Text of rendered avatar.
        waveform: Waveform string or Rich Text (with gradient colors).
        state: Current state for styling.

    Returns:
        Styled Panel for sidebar.
    """
    from rich.align import Align
    from rich.console import Group

    # Get status style
    status_styles = {
        'IDLE': 'status.idle',
        'THINKING': 'status.thinking',
        'TALKING': 'status.talking',
        'ERROR': 'danger',
    }
    status_style = status_styles.get(state, 'dim')

    # Handle waveform - can be Rich Text (gradient) or string
    if isinstance(waveform, Text):
        waveform_text = waveform  # Already has gradient colors
    else:
        # Fallback: string with style
        waveform_style = 'waveform.active' if state == 'TALKING' else 'waveform'
        waveform_text = Text(waveform, style=waveform_style)

    content = Group(
        Align.center(avatar_content),
        Text(),  # Spacer
        Align.center(waveform_text),
    )

    # Enhanced title with visual indicators
    title_symbols = {
        'IDLE': '◈',
        'THINKING': '◇',
        'TALKING': '◆',
        'ERROR': '✗',
    }
    symbol = title_symbols.get(state, '◈')
    
    return Panel(
        content,
        title=f'[{status_style}]{symbol} {state} {symbol}[/{status_style}]',
        box=ROUNDED,
        border_style='border',
        padding=(1, 2),
    )


def make_log_panel(content, title: str = 'TRANSMISSIONS') -> Panel:
    """Create styled log panel for conversation.

    Args:
        content: Rich renderable content.
        title: Panel title.

    Returns:
        Styled Panel for log.
    """
    return Panel(
        content,
        title=f'[info]◈ {title} ◈[/info]',
        box=ROUNDED,
        border_style='border',
        padding=(1, 2),
    )
