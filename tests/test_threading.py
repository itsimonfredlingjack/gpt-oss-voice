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

def wait_for_condition(condition, timeout=2.0, interval=0.1):
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        if condition():
            return
        time.sleep(interval)
    raise TimeoutError("Condition not met within timeout")

@pytest.fixture(autouse=True)
def reset_speaking_state():
    try:
        from cli import set_is_speaking
        set_is_speaking(False)
    except ImportError:
        pass

def test_speak_threaded_updates_flag():
    from cli import get_is_speaking
    # Initial state guaranteed by fixture
    assert not get_is_speaking()
    
    speak_threaded("Hello world")
    
    # Flag should eventually become true. 
    # Using wait_for_condition handles the race where the thread hasn't started yet.
    wait_for_condition(lambda: get_is_speaking())
    assert get_is_speaking()
    
    # Wait for thread to finish (mocked to sleep 0.5s)
    wait_for_condition(lambda: not get_is_speaking(), timeout=2.0)
    assert not get_is_speaking()
