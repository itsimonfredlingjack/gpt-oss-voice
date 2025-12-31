import pytest
import sys
import os
import time
import threading

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock speak.py if it depends on hardware
from unittest import mock
sys.modules['speak'] = mock.Mock()
import speak
speak.speak = lambda x: time.sleep(0.5)

try:
    from cli import speak_threaded, is_speaking
except ImportError:
    speak_threaded = None
    is_speaking = None

def test_threading_logic_exists():
    if speak_threaded is None:
        pytest.fail("speak_threaded function not found in cli.py")

def test_speak_threaded_updates_flag():
    from cli import is_speaking
    assert not is_speaking
    
    speak_threaded("Hello world")
    
    # Flag should be true immediately after starting thread
    from cli import get_is_speaking
    assert get_is_speaking()
    
    # Wait for thread to finish
    time.sleep(1.0)
    assert not get_is_speaking()
