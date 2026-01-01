"""Rich layout factory for the CLI interface.

Provides the Project Zero-G HUD layout structure.
"""

from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.box import DOUBLE_EDGE, ROUNDED, HEAVY
from rich.align import Align
from rich.table import Table
from typing import Optional, Dict

# Layout dimensions
SIDEBAR_WIDTH = 40 # Wider for the nebula
HEADER_HEIGHT = 3
FOOTER_HEIGHT = 3

def make_layout() -> Layout:
    """Create the main application layout - HUD Style.
    
    Structure:
        ┌─────────────────────────────────────┐
        │       Top Bar: Live Monitor         │
        ├────────────┬────────────────────────┤
        │  SIDEBAR   │    CENTRAL VISUAL      │
        │ (Command)  │       (Avatar)         │
        ├────────────┴────────────────────────┤
        │      Command Deck (Input)           │
        └─────────────────────────────────────┘
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
        Layout(name='log', ratio=2),
        Layout(name='sidebar', ratio=1),
    )

    return layout

def make_header(cpu: float = 0.0, ram: float = 0.0, net_sent: float = 0.0, net_recv: float = 0.0) -> Panel:
    """Create Live Monitor Top Bar.
    
    Displays system stats in a tech-HUD style.
    """
    
    # Create a grid/table for stats
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="center", ratio=2)
    grid.add_column(justify="right", ratio=1)
    
    # Title Left
    title = Text(" PROJECT ZERO-G ", style="header")
    
    # Stats Center
    stats = Text()
    stats.append("CPU ", style="header.label")
    stats.append(f"{cpu:04.1f}% ", style="header.value")
    stats.append("│ ", style="dim")
    stats.append("RAM ", style="header.label")
    stats.append(f"{ram:04.1f}% ", style="header.value")
    
    # Net Right
    net = Text()
    net.append("NET ", style="header.label")
    net.append(f"↑{net_sent:.1f} ↓{net_recv:.1f} MB", style="header.value")
    
    grid.add_row(title, stats, net)
    
    return Panel(
        grid,
        box=HEAVY, # Heavy borders look more like physical glass panels
        border_style='border',
        padding=(0, 1),
    )

def make_command_deck(
    current_input: str = "",
    cursor_pos: int = 0,
    show_cursor: bool = True,
    prompt_state: str = "IDLE"
) -> Panel:
    """Create the Command Deck (Input Area).
    
    Floating panel design for user input.
    """
    
    text = Text()
    
    # Status Indicator/Prompt
    if prompt_state == "THINKING":
        text.append(" ◈ PROCESSING COMMAND... ", style="avatar.thinking")
    elif prompt_state == "TALKING":
        text.append(" ◈ INCOMING TRANSMISSION ", style="avatar.talking")
    else:
        text.append(" ❯ ", style="user_prompt")
        
        # Input rendering with manual cursor
        if not current_input and not show_cursor:
             text.append("AWAITING INSTRUCTIONS...", style="dim")
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
        box=HEAVY,
        border_style='border.active' if prompt_state == "IDLE" else 'border',
        title="[dim]COMMAND DECK[/dim]",
        title_align="center",
        padding=(0, 2)
    )

def make_sidebar_panel(avatar_content: Text) -> Panel:
    """Create styled sidebar panel for the Avatar."""
    return Panel(
        Align.center(avatar_content, vertical="middle"),
        box=ROUNDED,
        border_style='border',
        title="[dim]THE NEBULA[/dim]",
        padding=(0, 0),
    )

def make_log_panel(content, title: str = 'SYSTEM LOG') -> Panel:
    """Create styled log panel."""
    return Panel(
        content,
        title=f'[dim]{title}[/dim]',
        box=ROUNDED,
        border_style='border',
        padding=(1, 2),
    )
