import pytest
import sys
import os
from rich.layout import Layout

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from cli import make_layout
except ImportError:
    make_layout = None

def test_make_layout_exists():
    if make_layout is None:
        pytest.fail("make_layout function not found in cli.py")

def test_layout_structure():
    layout = make_layout()
    assert isinstance(layout, Layout)
    
    # Check for core sections defined in the spec
    # Header, Sidebar, Log, Footer
    assert layout["header"]
    assert layout["footer"]
    assert layout["main"]
    assert layout["sidebar"]
    assert layout["log"]
