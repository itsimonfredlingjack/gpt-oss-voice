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
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return
        time.sleep(interval)
    raise TimeoutError("Condition not met within timeout")

def test_speak_threaded_updates_flag():
    from cli import set_is_speaking, get_is_speaking
    set_is_speaking(False)
    assert not get_is_speaking()
    
    speak_threaded("Hello world")
    
    # Flag should be true immediately after starting thread
    # We might need a tiny sleep or just assert, depending on how fast the thread starts.
    # But since we want to fix the race condition in the NEXT task, for now we just verify it eventually becomes true.
    # Actually, the spec says "Refactor speak_threaded to set flag immediately". 
    # But this task is just about fixing the TEST.
    # So let's use wait_for_condition to be robust.
    
    wait_for_condition(lambda: get_is_speaking())
    assert get_is_speaking()
    
    # Wait for thread to finish (mocked to sleep 0.5s)
    wait_for_condition(lambda: not get_is_speaking(), timeout=2.0)
    assert not get_is_speaking()
