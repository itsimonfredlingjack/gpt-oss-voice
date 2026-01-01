"""Rich layout factory for Project Tesseract.

Provides the Orbital HUD layout structure.
"""

from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.box import HEAVY_EDGE, ROUNDED
from rich.align import Align
from rich.table import Table
from rich.progress_bar import ProgressBar
from typing import Optional

# Layout dimensions
SIDEBAR_WIDTH = 45 # Wider for 3D projection
HEADER_HEIGHT = 3
Footer_HEIGHT = 4

def make_layout() -> Layout:
    """Create the Orbital HUD layout.
    
    Structure:
        ┌─────────────────────────────────────┐
        │       Top Bar: Orbital Feed         │
        ├──────────────────────┬──────────────┤
        │                      │              │
        │   MAIN FEED (Log)    │  TESSERACT   │
        │      (Decaying)      │   ENGINE     │
        │                      │              │
        ├──────────────────────┴──────────────┤
        │      Command Link (Input)           │
        └─────────────────────────────────────┘
    """
    layout = Layout(name='root')

    layout.split(
        Layout(name='header', size=HEADER_HEIGHT),
        Layout(name='main'),
        Layout(name='footer', size=Footer_HEIGHT),
    )

    # Note: Tesseract is on the RIGHT for "Satellite Feed" look
    layout['main'].split_row(
        Layout(name='log', ratio=2),
        Layout(name='sidebar', ratio=1),
    )

    return layout

def _make_bar(value: float, width: int = 10, style="header.value") -> Text:
    """Create a text-based progress bar."""
    blocks = " ▂▃▄▅▆▇█"
    num_full = int((value / 100.0) * width)
    
    text = Text("[", style="dim")
    text.append("█" * num_full, style=style)
    text.append("-" * (width - num_full), style="dim")
    text.append("]", style="dim")
    return text

def make_header(cpu: float = 0.0, ram: float = 0.0, net_sent: float = 0.0, net_recv: float = 0.0) -> Panel:
    """Create Orbital Feed Top Bar."""
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="center", ratio=2)
    grid.add_column(justify="right", ratio=1)
    
    # Left: Identity
    title = Text(" ❖ TESSERACT v4.0 ", style="header")
    
    # Center: Resource Loads
    stats = Text()
    stats.append("NEURAL LOAD ", style="header.label")
    stats.append(f"{int(cpu):02}% ", style="header.value")
    stats.append(_make_bar(cpu, 5, "header.value"))
    stats.append("   SYNAPTIC MEM ", style="header.label")
    stats.append(f"{int(ram):02}% ", style="header.value")
    stats.append(_make_bar(ram, 5, "header.value"))
    
    # Right: Uplink
    net = Text()
    net.append("UPLINK ", style="header.label")
    net.append(f"↑{net_sent:.1f} ↓{net_recv:.1f}", style="header.value")
    
    grid.add_row(title, stats, net)
    
    return Panel(
        grid,
        box=HEAVY_EDGE,
        border_style='border',
        padding=(0, 1),
    )

def make_command_deck(
    current_input: str = "",
    cursor_pos: int = 0,
    show_cursor: bool = True,
    prompt_state: str = "IDLE"
) -> Panel:
    """Create the Command Link (Input Area)."""
    
    text = Text()
    
    # Dynamic Border Color based on state
    border_style = "border"
    title_text = " COMMAND LINK "
    
    if prompt_state == "THINKING":
        text.append(" ❖ PROCESSING VECTOR STREAM... ", style="avatar.wobble")
        border_style = "border.thinking"
    elif prompt_state == "TALKING":
        text.append(" ❖ INCOMING DATA PACKET ", style="avatar.pulse")
        border_style = "border.talking"
    else:
        border_style = "border.active"
        text.append(" ❯ ", style="user_prompt")
        
        # Input rendering
        if not current_input and not show_cursor:
             text.append("INITIATE SEQUENCE...", style="dim")
        else:
            before = current_input[:cursor_pos]
            after = current_input[cursor_pos:]
            
            text.append(before, style="user_input")
            if show_cursor:
                text.append("█", style="user_cursor")
            else:
                if cursor_pos < len(current_input):
                    text.append(current_input[cursor_pos], style="user_input")
                else:
                     text.append(" ", style="user_input")
            
            text.append(after[1:] if show_cursor and cursor_pos < len(current_input) else after, style="user_input")

    return Panel(
        text,
        box=ROUNDED,
        border_style=border_style,
        title=title_text,
        title_align="right",
        padding=(0, 2)
    )

def make_sidebar_panel(avatar_content: Text, state: str) -> Panel:
    """Create styled sidebar panel for the Tesseract."""
    
    border_style = "border"
    if state == "TALKING":
        border_style = "border.talking"
    elif state == "THINKING":
        border_style = "border.thinking"
        
    return Panel(
        Align.center(avatar_content, vertical="middle"),
        box=ROUNDED,
        border_style=border_style,
        title="[dim]HYPERCUBE[/dim]",
        padding=(0, 0),
    )

def make_log_panel(content, title: str = 'DATA FEED') -> Panel:
    """Create styled log panel."""
    return Panel(
        content,
        title=f'[dim]{title}[/dim]',
        box=ROUNDED,
        border_style='border',
        padding=(1, 2),
    )
