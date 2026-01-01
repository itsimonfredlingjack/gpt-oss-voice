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


# Midnight Tokyo Theme - Supreme Design
MIDNIGHT_TOKYO_THEME = Theme({
    # Base styles - High contrast dark theme
    'base': NEO_TOKYO_COLORS['text_main'],
    'dim': NEO_TOKYO_COLORS['text_dim'],
    'bright_text': NEO_TOKYO_COLORS['text_glow'],

    # Header - Glowing tech aesthetic
    'header': f"bold {NEO_TOKYO_COLORS['neon_cyan']}",
    'header.subtitle': f"italic {NEO_TOKYO_COLORS['text_dim']}",
    'header.glow': f"bold {NEO_TOKYO_COLORS['neon_cyan']}",

    # Avatar - Holographic depth-based coloring
    'avatar.core': f"bold white on {NEO_TOKYO_COLORS['neon_cyan']}",  # Brightest core
    'avatar.bright': f"bold {NEO_TOKYO_COLORS['neon_cyan']}",         # Bright surface
    'avatar.medium': f"{NEO_TOKYO_COLORS['neon_cyan']}",              # Medium depth
    'avatar.dim': f"#005f7f",                                         # Dim edges
    'avatar.frame': NEO_TOKYO_COLORS['neon_cyan'],
    'avatar.eyes': f"bold {NEO_TOKYO_COLORS['neon_pink']}",
    'avatar.mouth': f"bold {NEO_TOKYO_COLORS['neon_pink']}",
    'avatar.thinking': f"bold {NEO_TOKYO_COLORS['neon_warn']}",
    'avatar.pulse': f"bold {NEO_TOKYO_COLORS['neon_cyan']}",

    # Waveform - Gradient spectral analyzer
    'waveform': NEO_TOKYO_COLORS['neon_acid'],
    'waveform.active': f"bold {NEO_TOKYO_COLORS['neon_cyan']}",
    'waveform.peak': f"bold {NEO_TOKYO_COLORS['neon_pink']}",  # High peaks = pink
    'waveform.mid': f"{NEO_TOKYO_COLORS['neon_cyan']}",        # Mid = cyan
    'waveform.low': f"#005f7f",                                 # Low = dim blue

    # Status indicator - Enhanced visibility
    'status.idle': f"dim {NEO_TOKYO_COLORS['text_dim']}",
    'status.thinking': f"bold {NEO_TOKYO_COLORS['neon_warn']}",
    'status.talking': f"bold {NEO_TOKYO_COLORS['neon_acid']}",
    'status.pulse': f"bold {NEO_TOKYO_COLORS['neon_cyan']}",

    # User input - Enhanced
    'user_input': f"bold {NEO_TOKYO_COLORS['neon_orange']}",
    'user_prompt': f"{NEO_TOKYO_COLORS['neon_cyan']}",
    'user_cursor': f"bold {NEO_TOKYO_COLORS['neon_orange']}",

    # AI response - Glowing
    'ai_response': NEO_TOKYO_COLORS['text_main'],
    'ai_label': f"bold {NEO_TOKYO_COLORS['neon_pink']}",
    'ai_streaming': f"italic {NEO_TOKYO_COLORS['neon_cyan']}",

    # Borders - Tech aesthetic
    'border': f"bold {NEO_TOKYO_COLORS['neon_cyan']}",
    'border.dim': NEO_TOKYO_COLORS['text_dim'],
    'border.glow': f"{NEO_TOKYO_COLORS['neon_cyan']}",

    # Info/Warning/Error - High visibility
    'info': f"bold {NEO_TOKYO_COLORS['info']}",
    'warning': f"bold {NEO_TOKYO_COLORS['warning']}",
    'danger': f"bold {NEO_TOKYO_COLORS['error']}",
    'success': f"bold {NEO_TOKYO_COLORS['success']}",
    
    # Special effects
    'glow': f"{NEO_TOKYO_COLORS['neon_cyan']}",
    'shimmer': f"bold {NEO_TOKYO_COLORS['neon_pink']}",
})

# Legacy alias
CYBERPUNK_THEME = MIDNIGHT_TOKYO_THEME


# Default theme - Midnight Tokyo (Supreme Design)
DEFAULT_THEME = MIDNIGHT_TOKYO_THEME
# Legacy alias
SOLARIZED_THEME = SOLARIZED_LIGHT_THEME
