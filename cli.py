from rich.theme import Theme

# Solarized Light Palette
SOLARIZED_THEME = Theme({
    "info": "#268bd2",       # Blue
    "warning": "#d33682",    # Magenta
    "danger": "#cb4b16",     # Orange
    "success": "#2aa198",    # Cyan
    "base": "#657b83",       # Base text
    "header": "bold #268bd2",
    "avatar.eyes": "#268bd2",
    "avatar.mouth": "#d33682",
    "waveform": "#2aa198",
    "user_input": "#cb4b16",
})

if __name__ == "__main__":
    print("Core CLI Module. Import into main application.")
