"""Rich layout factory for the CLI interface.

Provides the main screen layout structure.
"""

from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.box import HEAVY, DOUBLE
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
    """Create styled header panel.

    Args:
        title: Main title text.
        subtitle: Optional subtitle.

    Returns:
        Styled Panel for header.
    """
    text = Text()
    text.append('◢◤ ', style='header')
    text.append(title, style='header')
    text.append(' ◥◣', style='header')

    if subtitle:
        text.append(f'\n{subtitle}', style='header.subtitle')

    return Panel(
        text,
        box=HEAVY,
        style='border',
        padding=(0, 1),
    )


def make_footer(
    model: str = 'GPT-OSS',
    output: str = 'Google Home',
    status: str = '',
    hint: str = ''
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

    # Hint line (user affordance)
    if hint:
        hint_text = Text()
        hint_text.append('◇ ', style='dim')
        hint_text.append(hint, style='dim italic')
        content = Group(status_text, Align.center(hint_text))
    else:
        content = status_text

    return Panel(
        content,
        box=HEAVY,
        style='border.dim',
        padding=(0, 1),
    )


def make_sidebar_panel(
    avatar_content: Text,
    waveform: str,
    state: str
) -> Panel:
    """Create styled sidebar panel with avatar and waveform.

    Args:
        avatar_content: Rich Text of rendered avatar.
        waveform: Waveform string.
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

    # Build content
    waveform_text = Text(waveform, style='waveform')

    content = Group(
        avatar_content,
        Text(),  # Spacer
        Align.center(waveform_text),
    )

    return Panel(
        content,
        title=f'[{status_style}]◈ {state} ◈[/{status_style}]',
        box=DOUBLE,
        style='border',
        padding=(0, 0),
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
        box=DOUBLE,
        style='border',
        padding=(0, 1),
    )
