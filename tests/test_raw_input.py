"""Tests for cli/raw_input.py - RawInputHandler."""

import pytest
import sys
import os
import termios
import tty
from unittest.mock import patch, MagicMock, mock_open

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cli.raw_input import RawInputHandler, InputEvent, InputEventType


class TestRawInputHandler:
    """Test suite for RawInputHandler."""
    
    def test_init(self):
        """Test RawInputHandler initialization."""
        handler = RawInputHandler()
        assert handler.input_text == ""
        assert handler.cursor_position == 0
        assert handler._enabled is False
        assert len(handler._events) == 0
        assert len(handler._history) == 0
    
    def test_input_text_property(self):
        """Test input_text property."""
        handler = RawInputHandler()
        handler._input_buffer = "test input"
        assert handler.input_text == "test input"
    
    def test_cursor_position_property(self):
        """Test cursor_position property."""
        handler = RawInputHandler()
        handler._cursor_pos = 5
        assert handler.cursor_position == 5
    
    def test_enable_disable(self):
        """Test enable/disable methods."""
        handler = RawInputHandler()
        handler.enable()
        assert handler._enabled is True
        handler.disable()
        assert handler._enabled is False
    
    def test_clear_buffer(self):
        """Test buffer clearing."""
        handler = RawInputHandler()
        handler._input_buffer = "test"
        handler._cursor_pos = 2
        handler.clear_buffer()
        assert handler.input_text == ""
        assert handler.cursor_position == 0
    
    def test_max_input_length(self):
        """Test maximum input length enforcement."""
        handler = RawInputHandler()
        # Fill buffer to max
        handler._input_buffer = "x" * handler.MAX_INPUT_LENGTH
        
        # Mock stdin to return a character
        with patch('sys.stdin.read', return_value='a'):
            with patch('select.select', return_value=([sys.stdin], [], [])):
                event = handler.get_event()
                # Should return None when buffer is full
                assert event is None or event.type != InputEventType.CHAR
    
    def test_exit_commands(self):
        """Test exit command detection."""
        handler = RawInputHandler()
        assert 'exit' in handler.EXIT_COMMANDS
        assert 'quit' in handler.EXIT_COMMANDS
        assert '/exit' in handler.EXIT_COMMANDS
    
    def test_history_management(self):
        """Test history storage and retrieval."""
        handler = RawInputHandler()
        
        # Simulate adding to history
        handler._history.append("test1")
        handler._history.append("test2")
        
        assert len(handler._history) == 2
        assert handler._history[0] == "test1"
        assert handler._history[1] == "test2"
    
    def test_history_max_size(self):
        """Test history size limit."""
        handler = RawInputHandler()
        
        # Fill history beyond limit
        for i in range(150):
            handler._history.append(f"test{i}")
        
        # Should be capped at 100
        assert len(handler._history) <= 100
    
    @patch('termios.tcgetattr')
    @patch('termios.tcsetattr')
    @patch('tty.setcbreak')
    def test_start_stop(self, mock_setcbreak, mock_tcsetattr, mock_tcgetattr):
        """Test start/stop terminal mode management."""
        handler = RawInputHandler()
        
        # Mock terminal settings
        mock_tcgetattr.return_value = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        
        handler.start()
        assert handler._old_settings is not None
        assert handler._enabled is True
        mock_setcbreak.assert_called_once()
        
        handler.stop()
        assert handler._old_settings is None
        assert handler._enabled is False
        mock_tcsetattr.assert_called()
    
    def test_ctrl_c_interrupt(self):
        """Test Ctrl+C interrupt handling."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        
        with patch('select.select', return_value=([sys.stdin], [], [])):
            with patch('sys.stdin.read', return_value='\x03'):  # Ctrl+C
                event = handler.get_event()
                assert event is not None
                assert event.type == InputEventType.INTERRUPT
    
    def test_ctrl_d_exit(self):
        """Test Ctrl+D exit handling."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        
        with patch('select.select', return_value=([sys.stdin], [], [])):
            with patch('sys.stdin.read', return_value='\x04'):  # Ctrl+D
                event = handler.get_event()
                assert event is not None
                assert event.type == InputEventType.EXIT
    
    def test_enter_submits_text(self):
        """Test Enter key submits text."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._input_buffer = "test input"
        
        with patch('select.select', return_value=([sys.stdin], [], [])):
            with patch('sys.stdin.read', return_value='\n'):
                event = handler.get_event()
                assert event is not None
                assert event.type == InputEventType.TEXT
                assert event.text == "test input"
                assert handler.input_text == ""  # Buffer cleared
    
    def test_backspace_deletes_char(self):
        """Test backspace deletes character before cursor."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._input_buffer = "test"
        handler._cursor_pos = 2
        
        with patch('select.select', return_value=([sys.stdin], [], [])):
            with patch('sys.stdin.read', return_value='\x7f'):  # Backspace
                event = handler.get_event()
                assert handler.input_text == "tst"
                assert handler.cursor_position == 1
    
    def test_backspace_at_start_does_nothing(self):
        """Test backspace at start of buffer does nothing."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._input_buffer = "test"
        handler._cursor_pos = 0
        
        with patch('select.select', return_value=([sys.stdin], [], [])):
            with patch('sys.stdin.read', return_value='\x7f'):
                event = handler.get_event()
                assert handler.input_text == "test"  # Unchanged
                assert handler.cursor_position == 0
    
    def test_printable_char_insertion(self):
        """Test printable character insertion at cursor."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._input_buffer = "te"
        handler._cursor_pos = 1
        
        with patch('select.select', return_value=([sys.stdin], [], [])):
            with patch('sys.stdin.read', return_value='x'):
                event = handler.get_event()
                assert handler.input_text == "txe"
                assert handler.cursor_position == 2
    
    def test_escape_buffer_handling(self):
        """Test escape sequence buffer handling."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        
        # Simulate incomplete escape sequence
        handler._escape_buffer = "\x1b["
        
        # First call - no more data yet
        with patch('select.select', return_value=([], [], [])):
            event = handler.get_event()
            assert event is None
            assert handler._escape_buffer == "\x1b["  # Still buffered
        
        # Second call - complete sequence
        with patch('select.select', return_value=([sys.stdin], [], [])):
            with patch('sys.stdin.read', return_value='C'):  # Right arrow
                event = handler.get_event()
                assert handler._escape_buffer == ""  # Cleared
    
    def test_arrow_key_right(self):
        """Test right arrow key moves cursor right."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._input_buffer = "test"
        handler._cursor_pos = 1
        
        # Simulate right arrow: \x1b[C
        with patch('select.select', side_effect=[
            ([sys.stdin], [], []),  # First read for ESC
            ([sys.stdin], [], []),  # Second read for [
            ([sys.stdin], [], [])   # Third read for C
        ]):
            with patch('sys.stdin.read', side_effect=['\x1b', '[', 'C']):
                event = handler.get_event()
                assert handler.cursor_position == 2
    
    def test_arrow_key_left(self):
        """Test left arrow key moves cursor left."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._input_buffer = "test"
        handler._cursor_pos = 2
        
        # Simulate left arrow: \x1b[D
        with patch('select.select', side_effect=[
            ([sys.stdin], [], []),
            ([sys.stdin], [], []),
            ([sys.stdin], [], [])
        ]):
            with patch('sys.stdin.read', side_effect=['\x1b', '[', 'D']):
                event = handler.get_event()
                assert handler.cursor_position == 1
    
    def test_arrow_key_up_history(self):
        """Test up arrow navigates history."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._history = ["cmd1", "cmd2", "cmd3"]
        handler._history_index = -1
        
        # Simulate up arrow: \x1b[A
        with patch('select.select', side_effect=[
            ([sys.stdin], [], []),
            ([sys.stdin], [], []),
            ([sys.stdin], [], [])
        ]):
            with patch('sys.stdin.read', side_effect=['\x1b', '[', 'A']):
                event = handler.get_event()
                assert handler.input_text == "cmd3"  # Last history item
                assert handler._history_index == -3
    
    def test_arrow_key_down_history(self):
        """Test down arrow navigates history."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._history = ["cmd1", "cmd2"]
        handler._history_index = -2  # At first item
        
        # Simulate down arrow: \x1b[B
        with patch('select.select', side_effect=[
            ([sys.stdin], [], []),
            ([sys.stdin], [], []),
            ([sys.stdin], [], [])
        ]):
            with patch('sys.stdin.read', side_effect=['\x1b', '[', 'B']):
                event = handler.get_event()
                assert handler.input_text == "cmd2"  # Next item
                assert handler._history_index == -1
    
    def test_empty_input_not_submitted(self):
        """Test empty input is not submitted."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        handler._input_buffer = "   "  # Only whitespace
        
        with patch('select.select', return_value=([sys.stdin], [], [])):
            with patch('sys.stdin.read', return_value='\n'):
                event = handler.get_event()
                # Should not create TEXT event for empty input
                assert event is None or event.type != InputEventType.TEXT
    
    def test_disabled_handler_returns_none(self):
        """Test disabled handler returns None."""
        handler = RawInputHandler()
        handler._enabled = False
        
        event = handler.get_event()
        assert event is None
    
    def test_no_data_returns_none(self):
        """Test no available data returns None."""
        handler = RawInputHandler()
        handler._enabled = True
        handler._old_settings = [0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        
        with patch('select.select', return_value=([], [], [])):
            event = handler.get_event()
            assert event is None

