import pytest
from rich.theme import Theme
import sys
import os

# Add the project root to sys.path so we can import cli
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_cli_exists():
    """Verify that cli.py exists."""
    assert os.path.exists("cli.py")

def test_theme_definition():
    """Verify that the Solarized Light theme is correctly defined."""
    try:
        from cli import SOLARIZED_THEME
    except ImportError:
        pytest.fail("Could not import SOLARIZED_THEME from cli.py")

    assert isinstance(SOLARIZED_THEME, Theme)
    
    # Check for specific styles defined in the product guidelines
    styles = SOLARIZED_THEME.styles
    assert styles["info"].color.name == "#268bd2" # Primary Accent
    assert styles["warning"].color.name == "#d33682" # Secondary Accent
    
    # We'll check the specific hex codes if possible, or just the mapping
    # Based on product guidelines:
    # Text: #657b83
    # Accent (Avatar): #268bd2 (Blue)
    # Accent (Mouth): #d33682 (Magenta)
    # Waveform: #2aa198 (Cyan)
    # Alert/User: #cb4b16 (Orange)

