"""Cyberpunk theme for the CLI interface.

High contrast dark theme with neon accents.
"""

from rich.theme import Theme


# Cyberpunk Color Palette
COLORS = {
    # Backgrounds
    'bg_dark': '#0a0a0f',
    'bg_panel': '#12121a',

    # Primary colors
    'neon_cyan': '#00ffff',
    'neon_magenta': '#ff00ff',
    'neon_green': '#00ff41',
    'neon_orange': '#ff6600',
    'neon_pink': '#ff0080',

    # Text
    'text_primary': '#e0e0e0',
    'text_dim': '#606080',
    'text_bright': '#ffffff',

    # Status
    'success': '#00ff41',
    'warning': '#ffcc00',
    'error': '#ff3333',
    'info': '#00ccff',
}


CYBERPUNK_THEME = Theme({
    # Base styles
    'base': COLORS['text_primary'],
    'dim': COLORS['text_dim'],
    'bright': COLORS['text_bright'],

    # Header
    'header': f"bold {COLORS['neon_cyan']}",
    'header.subtitle': COLORS['text_dim'],

    # Avatar
    'avatar.frame': COLORS['neon_cyan'],
    'avatar.eyes': f"bold {COLORS['neon_magenta']}",
    'avatar.mouth': f"bold {COLORS['neon_pink']}",
    'avatar.thinking': f"bold {COLORS['neon_orange']}",

    # Waveform
    'waveform': COLORS['neon_green'],
    'waveform.active': f"bold {COLORS['neon_cyan']}",

    # Status indicator
    'status.idle': COLORS['text_dim'],
    'status.thinking': f"bold {COLORS['neon_orange']}",
    'status.talking': f"bold {COLORS['neon_green']}",

    # User input
    'user_input': f"bold {COLORS['neon_orange']}",
    'user_prompt': COLORS['neon_cyan'],

    # AI response
    'ai_response': COLORS['text_primary'],
    'ai_label': f"bold {COLORS['neon_magenta']}",

    # Borders
    'border': COLORS['neon_cyan'],
    'border.dim': COLORS['text_dim'],

    # Info/Warning/Error
    'info': COLORS['info'],
    'warning': COLORS['warning'],
    'danger': COLORS['error'],
    'success': COLORS['success'],
})


# Legacy compatibility alias
SOLARIZED_THEME = CYBERPUNK_THEME
