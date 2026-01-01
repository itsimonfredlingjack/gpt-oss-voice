import pytest
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from cli import AIAvatar, BrailleAvatar
except ImportError:
    AIAvatar = None
    BrailleAvatar = None

from rich.text import Text


def test_avatar_class_exists():
    if AIAvatar is None:
        pytest.fail("AIAvatar class not found in cli")
    if BrailleAvatar is None:
        pytest.fail("BrailleAvatar class not found in cli")


def test_avatar_render_idle():
    """Test BrailleAvatar renders IDLE state."""
    avatar = BrailleAvatar()
    result = avatar.render("IDLE")

    # Should return Rich Text object
    assert isinstance(result, Text)

    # Should have content (Braille patterns)
    plain = result.plain
    assert len(plain) > 0

    # Should contain Braille or space characters
    assert any(c != ' ' for c in plain.replace('\n', ''))


def test_avatar_render_thinking():
    """Test BrailleAvatar renders THINKING state with streams."""
    avatar = BrailleAvatar()

    # Render multiple frames to check animation
    frames = []
    for _ in range(5):
        frames.append(avatar.render("THINKING").plain)

    # Should produce output
    assert all(len(f) > 0 for f in frames)

    # Animation should change between frames
    unique_frames = set(frames)
    assert len(unique_frames) > 1, "THINKING animation should vary"


def test_avatar_render_talking():
    """Test BrailleAvatar renders TALKING state with pulse."""
    avatar = BrailleAvatar()

    # Render multiple frames to check pulse animation
    frames = []
    for _ in range(5):
        frames.append(avatar.render("TALKING").plain)

    # Should produce output
    assert all(len(f) > 0 for f in frames)

    # Animation should change between frames
    unique_frames = set(frames)
    assert len(unique_frames) > 1, "TALKING animation should vary"


def test_avatar_reset():
    """Test avatar state can be reset."""
    avatar = BrailleAvatar()

    # Advance animation state
    for _ in range(10):
        avatar.render("THINKING")

    # Reset should work without error
    avatar.reset()

    # Should render normally after reset
    result = avatar.render("IDLE")
    assert isinstance(result, Text)


def test_avatar_pulse_scale():
    """Test avatar pulse scale can be set."""
    avatar = BrailleAvatar()

    # Should accept pulse scale without error
    avatar.set_pulse_scale(1.0)
    avatar.set_pulse_scale(0.5)
    avatar.set_pulse_scale(1.5)

    # Should clamp to valid range
    avatar.set_pulse_scale(0.1)  # Below min
    avatar.set_pulse_scale(2.0)  # Above max

    # Should still render
    result = avatar.render("TALKING")
    assert isinstance(result, Text)


def test_legacy_alias():
    """Test AIAvatar is an alias for BrailleAvatar."""
    assert AIAvatar is BrailleAvatar
