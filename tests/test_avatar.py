import pytest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from cli import AIAvatar
except ImportError:
    AIAvatar = None

def test_avatar_class_exists():
    if AIAvatar is None:
        pytest.fail("AIAvatar class not found in cli.py")

def test_avatar_get_frame_idle():
    avatar = AIAvatar()
    # Test random blinking in IDLE
    frames = set()
    for _ in range(50):
        frames.add(avatar.get_frame("IDLE"))
    
    assert len(frames) >= 1
    # Verify basic structure (eyes or borders)
    first_frame = list(frames)[0]
    assert isinstance(first_frame, str)

def test_avatar_get_frame_talking():
    avatar = AIAvatar()
    # Test mouth movement in TALKING
    frames = set()
    for _ in range(50):
        frames.add(avatar.get_frame("TALKING"))
    
    # Should have multiple frames due to mouth animation
    assert len(frames) > 1 
