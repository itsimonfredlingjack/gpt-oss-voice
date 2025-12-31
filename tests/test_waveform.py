import pytest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from cli import Waveform
except ImportError:
    Waveform = None

def test_waveform_class_exists():
    if Waveform is None:
        pytest.fail("Waveform class not found in cli.py")

def test_waveform_get_frame_idle():
    waveform = Waveform()
    # IDLE should be relatively static/flat
    frame = waveform.get_frame("IDLE")
    assert isinstance(frame, str)
    # Check for flat line characters (assuming low blocks)
    # Valid blocks:  , ▂, ▃, ▄, ▅, ▆, ▇, █
    # Flat line usually ' ' or ' '
    
def test_waveform_get_frame_talking():
    waveform = Waveform()
    # TALKING should have variation
    frames = set()
    for _ in range(50):
        frames.add(waveform.get_frame("TALKING"))
    
    assert len(frames) > 1
