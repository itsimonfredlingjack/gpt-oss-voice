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
    """Verify that the theme is correctly defined."""
    try:
        from cli import SOLARIZED_THEME
    except ImportError:
        pytest.fail("Could not import SOLARIZED_THEME from cli.py")

    assert isinstance(SOLARIZED_THEME, Theme)

    # Check for required styles (color values vary by theme)
    styles = SOLARIZED_THEME.styles

    # Verify essential style keys exist
    assert "info" in styles
    assert "warning" in styles
    assert "waveform" in styles
    assert "user_input" in styles

    # Verify styles have colors defined
    assert styles["info"].color is not None
    assert styles["warning"].color is not None

