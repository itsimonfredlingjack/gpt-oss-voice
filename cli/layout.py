"""Rich layout factory for Project Chimera.

Provides the Tactical Readout HUD structure.
"""

from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.box import HEAVY, HEAVY_EDGE, DOUBLE
from rich.align import Align
from rich.table import Table
from typing import Optional

# Layout dimensions
# Sidebar width covers the dummy data columns
SIDEBAR_WIDTH = 42 
HEADER_HEIGHT = 3
FOOTER_HEIGHT = 3
DUMMY_WIDTH = 18

def make_layout() -> Layout:
    """Create the Tactical HUD layout.
    
    Structure:
        ┌─────────────────────────────────────┐
        │       Top Bar: Tactical Gauge       │
        ├────────────┬───────────┬────────────┤
        │   DUMMY    │   MAIN    │  MECHA     │
        │   DATA     │   LOG     │  CORE      │
        │  STREAM    │           │            │
        ├────────────┴───────────┴────────────┤
        │           Command Feed              │
        └─────────────────────────────────────┘
    """
    layout = Layout(name='root')

    layout.split(
        Layout(name='header', size=HEADER_HEIGHT),
        Layout(name='main'),
        Layout(name='footer', size=FOOTER_HEIGHT),
    )

    # 3-Column Layout
    layout['main'].split_row(
        Layout(name='dummy_L', size=DUMMY_WIDTH),
        Layout(name='log', ratio=2),
        Layout(name='sidebar', size=SIDEBAR_WIDTH),
    )

    return layout

def _make_block_gauge(value: float, width: int = 20) -> Text:
    """Create a heavy block gauge: [██████░░░░]"""
    # 8 chars: █ ⅞ ¾ ⅝ ½ ⅜ ¼ ⅛
    # Simple block version for "Heavy Metal" look
    frac = value / 100.0
    filled = int(frac * width)
    
    text = Text()
    text.append("[", style="dim")
    text.append("█" * filled, style="header.gauge.filled")
    text.append("░" * (width - filled), style="header.gauge.empty")
    text.append("]", style="dim")
    return text

def make_header(cpu: float = 0.0, ram: float = 0.0, net_sent: float = 0.0, net_recv: float = 0.0) -> Panel:
    """Create Tactical Gauge Top Bar."""
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="center", ratio=2)
    grid.add_column(justify="right", ratio=1)
    
    # Left: Unit ID
    title = Text(" ☢ UNIT 734 ", style="header.value")
    
    # Center: Gauges
    stats = Text()
    stats.append("CPU ", style="header.label")
    stats.append(_make_block_gauge(cpu, 10))
    stats.append(" MEM ", style="header.label")
    stats.append(_make_block_gauge(ram, 10))
    
    # Right: Data Rate
    net = Text()
    net.append(f"TX {int(net_sent*100):03} ", style="dim")
    net.append(f"RX {int(net_recv*100):03}", style="header.value")
    
    grid.add_row(title, stats, net)
    
    return Panel(
        grid,
        box=HEAVY,
        border_style='border',
        padding=(0, 1),
    )

def make_command_deck(
    current_input: str = "",
    cursor_pos: int = 0,
    show_cursor: bool = True,
    prompt_state: str = "IDLE"
) -> Panel:
    """Create the Command Feed."""
    
    text = Text()
    
    border_style = "border"
    title_text = " TACTICAL INPUT "
    
    if prompt_state == "THINKING":
        text.append(" /// PROCESSING TRAUMA /// ", style="glitch.1")
        border_style = "border.warning"
    elif prompt_state == "TALKING":
        text.append(" /// AUDIO OUTPUT ACTIVE /// ", style="border.active")
        border_style = "border.active"
    else:
        border_style = "border.active"
        text.append(" >> ", style="user_prompt")
        
        if not current_input and not show_cursor:
             text.append("WAITING FOR DIRECTIVE...", style="dim")
        else:
            before = current_input[:cursor_pos]
            after = current_input[cursor_pos:]
            
            text.append(before, style="user_input")
            if show_cursor:
                text.append(" ", style="user_cursor") # Reverse cursor block
            else:
                if cursor_pos < len(current_input):
                    text.append(current_input[cursor_pos], style="user_input")
                else:
                     text.append(" ", style="user_input")
            
            text.append(after[1:] if show_cursor and cursor_pos < len(current_input) else after, style="user_input")

    return Panel(
        text,
        box=HEAVY,
        border_style=border_style,
        title=title_text,
        title_align="right",
        padding=(0, 2)
    )

def make_sidebar_panel(avatar_content: Text, state: str) -> Panel:
    """Create Mecha-Core container."""
    
    border_style = "border"
    title = "SENTRY MODE"
    
    if state == "THINKING":
        border_style = "border.warning"
        title = "!!! OVERHEAT !!!"
    elif state == "TALKING":
        border_style = "border.active"
        title = "VOICE PROJECTION"
        
    return Panel(
        Align.center(avatar_content, vertical="middle"),
        box=HEAVY,
        border_style=border_style,
        title=f"[bold]{title}[/bold]",
        padding=(0, 0),
    )

def make_dummy_panel(content: Text) -> Panel:
    """Create side dummy data panel."""
    return Panel(
        content,
        box=HEAVY,
        border_style="dim",
        title="[dim]RAW_HEX[/dim]",
        padding=(0,0)
    )

def make_log_panel(content, title: str = 'LIVE FEED') -> Panel:
    """Create styled log panel."""
    return Panel(
        content,
        title=f'[bold]{title}[/bold]',
        box=HEAVY,
        border_style='border',
        padding=(1, 2),
    )
