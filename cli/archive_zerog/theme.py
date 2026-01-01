"""Theme definitions for the CLI interface.

Provides both Solarized Light (default) and Cyberpunk themes.
"""

from rich.theme import Theme


# Solarized Light Color Palette
SOLARIZED_COLORS = {
    # Backgrounds (light)
    'base3':  '#fdf6e3',  # Main background (cream white)
    'base2':  '#eee8d5',  # Highlight background

    # Text (dark on light)
    'base00': '#657b83',  # Body text
    'base01': '#586e75',  # Emphasis
    'base02': '#073642',  # High contrast (borders)
    'base03': '#002b36',  # Maximum contrast

    # Accents
    'blue':    '#268bd2',  # Primary accent, borders
    'cyan':    '#2aa198',  # Secondary accent
    'green':   '#859900',  # Success
    'yellow':  '#b58900',  # Warning
    'orange':  '#cb4b16',  # User input
    'red':     '#dc322f',  # Error/danger
    'magenta': '#d33682',  # AI/Avatar eyes
    'violet':  '#6c71c4',  # Links
}


# Midnight Tokyo - Supreme Design Palette
NEO_TOKYO_COLORS = {
    # Backgrounds - Deep cyberpunk blacks
    'bg_void': '#050508',      # Deepest black-blue
    'bg_grid': '#0f0f1a',      # Panel background
    'bg_panel': '#12121a',     # Component background
    
    # Neon Accents - Electric and vibrant
    'neon_cyan': '#00f3ff',    # Main UI accent (bright cyan)
    'neon_pink': '#ff00ff',    # AI/Personality (magenta)
    'neon_acid': '#39ff14',    # Success/Active (electric green)
    'neon_warn': '#ffbd00',    # Warnings (amber)
    'neon_err': '#ff2a2a',     # Critical errors (red)
    'neon_orange': '#ff6600',  # User input (orange)
    
    # Text Colors - High contrast
    'text_main': '#e0e0e0',    # Primary text
    'text_dim': '#4a4a6a',     # Secondary/Borders
    'text_glow': '#ffffff',    # Highlights
    
    # Status Colors
    'success': '#39ff14',      # neon_acid
    'warning': '#ffbd00',      # neon_warn
    'error': '#ff2a2a',        # neon_err
    'info': '#00f3ff',         # neon_cyan
}

# Legacy alias for compatibility
CYBERPUNK_COLORS = NEO_TOKYO_COLORS


SOLARIZED_LIGHT_THEME = Theme({
    # Base styles
    'base': SOLARIZED_COLORS['base00'],
    'dim': SOLARIZED_COLORS['base01'],
    'bright_text': SOLARIZED_COLORS['base03'],

    # Header - enhanced with more visual impact
    'header': f"bold {SOLARIZED_COLORS['blue']} on {SOLARIZED_COLORS['base3']}",
    'header.subtitle': f"italic {SOLARIZED_COLORS['base01']}",
    'header.glow': f"bold {SOLARIZED_COLORS['cyan']}",

    # Avatar - enhanced with gradient-like effects
    'avatar.frame': f"bold {SOLARIZED_COLORS['base02']}",
    'avatar.core': f"bold {SOLARIZED_COLORS['magenta']}",
    'avatar.eyes': f"bold {SOLARIZED_COLORS['magenta']}",
    'avatar.mouth': f"bold {SOLARIZED_COLORS['base01']}",
    'avatar.thinking': f"bold {SOLARIZED_COLORS['orange']}",
    'avatar.pulse': f"bold {SOLARIZED_COLORS['cyan']}",

    # Waveform - enhanced with glow effects
    'waveform': f"{SOLARIZED_COLORS['green']}",
    'waveform.active': f"bold {SOLARIZED_COLORS['cyan']}",
    'waveform.peak': f"bold {SOLARIZED_COLORS['cyan']}",

    # Status indicator - more visual
    'status.idle': f"dim {SOLARIZED_COLORS['base01']}",
    'status.thinking': f"bold {SOLARIZED_COLORS['orange']}",
    'status.talking': f"bold {SOLARIZED_COLORS['green']}",
    'status.pulse': f"bold {SOLARIZED_COLORS['cyan']}",

    # User input - enhanced
    'user_input': f"bold {SOLARIZED_COLORS['orange']}",
    'user_prompt': f"{SOLARIZED_COLORS['blue']}",
    'user_cursor': f"bold {SOLARIZED_COLORS['orange']}",

    # AI response - enhanced
    'ai_response': SOLARIZED_COLORS['base00'],
    'ai_label': f"bold {SOLARIZED_COLORS['magenta']}",
    'ai_streaming': f"italic {SOLARIZED_COLORS['cyan']}",

    # Borders - enhanced
    'border': f"bold {SOLARIZED_COLORS['blue']}",
    'border.dim': SOLARIZED_COLORS['base01'],
    'border.glow': f"{SOLARIZED_COLORS['cyan']}",

    # Info/Warning/Error - enhanced
    'info': f"bold {SOLARIZED_COLORS['blue']}",
    'warning': f"bold {SOLARIZED_COLORS['yellow']}",
    'danger': f"bold {SOLARIZED_COLORS['red']}",
    'success': f"bold {SOLARIZED_COLORS['green']}",
    
    # Special effects
    'glow': f"{SOLARIZED_COLORS['cyan']}",
    'shimmer': f"bold {SOLARIZED_COLORS['magenta']}",
})



# Deep Void - Project Zero-G Palette
DEEP_VOID_COLORS = {
    # Backgrounds - Void-like
    'bg_void': '#0a0a0a',      # Main Deep Void background
    'bg_panel': '#0f0f15',     # Subtle panel background
    
    # Accents - Electric Cyan & Neon Purple
    'cyan': '#00f3ff',         # Electric Cyan (Primary Accent)
    'purple': '#bf00ff',       # Neon Purple (Secondary Accent)
    'dim_cyan': '#005f7f',     # Dimmed Cyan (Borders/Low activity)
    'dim_purple': '#4a0066',   # Dimmed Purple
    
    # Functional
    'text': '#e0e0e0',         # Main text
    'dim': '#4a4a50',          # Dim text
    'danger': '#ff2a2a',       # Error
    'warning': '#ffbd00',      # Warning
    'success': '#00ff41',      # Success
}

DEEP_VOID_THEME = Theme({
    # Base styles
    'base': DEEP_VOID_COLORS['text'],
    'dim': DEEP_VOID_COLORS['dim'],
    
    # Header - Live Monitor style
    'header': f"bold {DEEP_VOID_COLORS['cyan']}",
    'header.label': f"bold {DEEP_VOID_COLORS['purple']}",
    'header.value': f"{DEEP_VOID_COLORS['cyan']}",
    
    # Avatar - Antigravity Particles
    'avatar.particle': f"{DEEP_VOID_COLORS['cyan']}",
    'avatar.core': f"bold {DEEP_VOID_COLORS['purple']}",
    'avatar.thinking': f"bold {DEEP_VOID_COLORS['warning']}",
    'avatar.talking': f"bold {DEEP_VOID_COLORS['cyan']}",
    
    # Command Deck
    'user_prompt': f"bold {DEEP_VOID_COLORS['cyan']}",
    'user_input': f"bold {DEEP_VOID_COLORS['text']}",
    'user_cursor': f"bold {DEEP_VOID_COLORS['purple']}",
    
    # Borders - Glass-like
    'border': DEEP_VOID_COLORS['dim_cyan'],
    'border.active': DEEP_VOID_COLORS['cyan'],
    
    # Status
    'info': DEEP_VOID_COLORS['cyan'],
    'warning': DEEP_VOID_COLORS['warning'],
    'error': DEEP_VOID_COLORS['danger'],
})

# Default theme alias
DEFAULT_THEME = DEEP_VOID_THEME
SOLARIZED_THEME = DEEP_VOID_THEME  # Compatibility
CYBERPUNK_THEME = DEEP_VOID_THEME  # Compatibility
mid_night_tokyo_colors = DEEP_VOID_COLORS # Compatibility

