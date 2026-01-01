"""Raw character-by-character input handler for Rich Live.

Uses termios and select to capture keystrokes without terminal
management conflicts. Input text is rendered in Rich layout,
not by the terminal.
"""

import sys
import select
import termios
import tty
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class InputEventType(Enum):
    """Types of input events."""
    TEXT = auto()
    EXIT = auto()
    INTERRUPT = auto()
    CHAR = auto()  # Single character typed (for rendering)


@dataclass
class InputEvent:
    """An input event from the user."""
    type: InputEventType
    text: str = ""
    char: str = ""  # For CHAR events


class RawInputHandler:
    """Character-by-character input handler using raw terminal mode.

    Captures keystrokes without terminal management, allowing Rich
    Live to fully control the display. Input text is stored and
    can be rendered in the Rich layout.

    Example:
        >>> handler = RawInputHandler()
        >>> handler.start()
        >>> # In main loop:
        >>> event = handler.get_event()
        >>> if event:
        ...     if event.type == InputEventType.CHAR:
        ...         print(f"Typed: {event.char}")
        ...     elif event.type == InputEventType.TEXT:
        ...         process_input(event.text)
    """

    EXIT_COMMANDS = {'exit', 'quit', '/exit', '/quit'}
    MAX_INPUT_LENGTH = 10000  # Maximum input buffer size

    def __init__(self):
        """Initialize raw input handler."""
        self._input_buffer: str = ""
        self._cursor_pos: int = 0  # Cursor position in buffer
        self._old_settings: Optional[list] = None
        self._enabled: bool = False
        self._events: list[InputEvent] = []
        self._history: list[str] = []
        self._history_index: int = -1
        # Track incomplete escape sequences between calls
        self._escape_buffer: str = ""
        # Track if we just processed an escape (to catch leftover chars)
        self._last_was_escape: bool = False

    @property
    def input_text(self) -> str:
        """Get current input buffer text."""
        return self._input_buffer
    
    @property
    def cursor_position(self) -> int:
        """Get current cursor position in input buffer."""
        return self._cursor_pos

    def start(self) -> None:
        """Enable raw input mode - set terminal to cbreak mode."""
        if self._old_settings is not None:
            return  # Already started

        # Save current terminal settings
        self._old_settings = termios.tcgetattr(sys.stdin)
        # Set cbreak mode once - terminal stays in this mode
        tty.setcbreak(sys.stdin.fileno())
        self._enabled = True

    def stop(self) -> None:
        """Clean up input handler."""
        if self._old_settings is None:
            return

        # Restore terminal settings if we changed them
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
        except (OSError, termios.error):
            pass  # Terminal might already be restored
        self._old_settings = None
        self._enabled = False

    def enable(self) -> None:
        """Enable input processing."""
        self._enabled = True

    def disable(self) -> None:
        """Disable input processing."""
        self._enabled = False

    def clear_buffer(self) -> None:
        """Clear the input buffer."""
        self._input_buffer = ""
        self._cursor_pos = 0

    def get_event(self) -> Optional[InputEvent]:
        """Get next input event (non-blocking).

        Returns:
            InputEvent or None if no event available.
        """
        if not self._enabled or self._old_settings is None:
            return None

        try:
            # Terminal already in cbreak mode (set in start())
            # CRITICAL: Check escape_buffer FIRST, before checking for new data
            # This allows us to continue reading escape sequences even when no new data is available yet
            if self._escape_buffer:
                # We're in the middle of an escape sequence - try to complete it (NON-BLOCKING)
                # Use non-blocking read (timeout=0) to prevent freezing
                if select.select([sys.stdin], [], [], 0)[0]:
                    char = sys.stdin.read(1)
                    self._escape_buffer += char
                    # Check if we now have a complete sequence
                    if len(self._escape_buffer) >= 3:
                        seq = self._escape_buffer
                        self._escape_buffer = ""  # Clear buffer
                        # Process the complete sequence directly
                        if seq[1] == '[' and seq[2] in 'ABCD':
                            arrow_key = seq[2]
                            escape_handled = True
                            # Handle arrow key directly
                            if arrow_key == 'C':  # Right arrow
                                if self._cursor_pos < len(self._input_buffer):
                                    self._cursor_pos += 1
                                    self._events.append(InputEvent(InputEventType.CHAR, char=""))
                            elif arrow_key == 'D':  # Left arrow
                                if self._cursor_pos > 0:
                                    self._cursor_pos -= 1
                                    self._events.append(InputEvent(InputEventType.CHAR, char=""))
                            elif arrow_key == 'A':  # Up arrow
                                if self._history:
                                    self._history_index = max(-len(self._history), self._history_index - 1)
                                    self._input_buffer = self._history[self._history_index]
                                    self._cursor_pos = len(self._input_buffer)
                                    self._events.append(InputEvent(InputEventType.CHAR, char=""))
                            elif arrow_key == 'B':  # Down arrow
                                if self._history_index < -1:
                                    self._history_index += 1
                                    self._input_buffer = self._history[self._history_index]
                                    self._cursor_pos = len(self._input_buffer)
                                else:
                                    self._input_buffer = ""
                                    self._cursor_pos = 0
                                    self._history_index = -1
                                self._events.append(InputEvent(InputEventType.CHAR, char=""))
                            # Clear escape flag after handling
                            self._last_was_escape = False
                            if self._events:
                                return self._events.pop(0)
                            return None
                        else:
                            # Not a recognized sequence - clear and ignore
                            self._escape_buffer = ""
                            return None
                    else:
                        # Sequence still incomplete - keep buffer for next call
                        # Buffer is kept, return None to wait for more data
                        return None
                else:
                    # No more data available yet - keep buffer for next call (don't clear)
                    # This allows the escape sequence to be completed across multiple get_event() calls
                    return None
            
            # Check if stdin has data (non-blocking) - only after escape_buffer handling
            if not select.select([sys.stdin], [], [], 0)[0]:
                return None
            
            # Read one character directly
            char = sys.stdin.read(1)
            
            # Flag to track if we handled an escape sequence
            escape_handled = False

            # Handle special keys
            if ord(char) == 3:  # Ctrl+C
                self._events.append(InputEvent(InputEventType.INTERRUPT))
            elif ord(char) == 4:  # Ctrl+D (EOF)
                self._events.append(InputEvent(InputEventType.EXIT))
            elif ord(char) == 13 or ord(char) == 10:  # Enter
                text = self._input_buffer.strip()
                if text:
                    # Add to history
                    if not self._history or self._history[-1] != text:
                        self._history.append(text)
                        if len(self._history) > 100:
                            self._history.pop(0)
                    self._history_index = -1

                    # Check for exit commands
                    if text.lower() in self.EXIT_COMMANDS:
                        self._events.append(InputEvent(InputEventType.EXIT))
                    else:
                        self._events.append(
                            InputEvent(InputEventType.TEXT, text=text)
                        )
                self._input_buffer = ""
                self._cursor_pos = 0
            elif ord(char) == 127 or ord(char) == 8:  # Backspace
                if self._cursor_pos > 0:
                    # Remove character before cursor
                    self._input_buffer = (
                        self._input_buffer[:self._cursor_pos - 1] +
                        self._input_buffer[self._cursor_pos:]
                    )
                    self._cursor_pos -= 1
                    self._events.append(
                        InputEvent(InputEventType.CHAR, char="")
                    )
                escape_handled = True  # Mark as handled to skip printable char check
            elif ord(char) == 27:  # Escape sequence start (\x1b)
                # Try to read more for arrow keys (NON-BLOCKING only to prevent freezing)
                # Arrow keys are: \x1b[A (up), \x1b[B (down), \x1b[C (right), \x1b[D (left)
                seq = char
                
                # Read available characters NON-BLOCKING (timeout=0)
                # If not all bytes are available, save to escape_buffer for next call
                if select.select([sys.stdin], [], [], 0)[0]:
                    next_char = sys.stdin.read(1)
                    seq += next_char
                    # If we got '[', try to get the arrow key char (non-blocking)
                    if len(seq) >= 2 and seq[1] == '[':
                        if select.select([sys.stdin], [], [], 0)[0]:
                            next_char = sys.stdin.read(1)
                            seq += next_char
                
                # Check if we got a complete arrow key sequence
                if len(seq) >= 3 and seq[1] == '[':
                    arrow_key = seq[2]
                    if arrow_key == 'A':  # Up arrow
                        if self._history:
                            self._history_index = max(
                                -len(self._history),
                                self._history_index - 1
                            )
                            self._input_buffer = self._history[
                                self._history_index
                            ]
                            self._cursor_pos = len(self._input_buffer)  # Move to end
                            self._events.append(
                                InputEvent(InputEventType.CHAR, char="")
                            )
                        escape_handled = True
                    elif arrow_key == 'B':  # Down arrow
                        if self._history_index < -1:
                            self._history_index += 1
                            self._input_buffer = self._history[
                                self._history_index
                            ]
                            self._cursor_pos = len(self._input_buffer)  # Move to end
                        else:
                            self._input_buffer = ""
                            self._cursor_pos = 0
                            self._history_index = -1
                        self._events.append(
                            InputEvent(InputEventType.CHAR, char="")
                        )
                        escape_handled = True
                    elif arrow_key == 'C':  # Right arrow
                        # Move cursor right
                        if self._cursor_pos < len(self._input_buffer):
                            self._cursor_pos += 1
                            self._events.append(
                                InputEvent(InputEventType.CHAR, char="")
                            )
                        escape_handled = True
                    elif arrow_key == 'D':  # Left arrow
                        # Move cursor left
                        if self._cursor_pos > 0:
                            self._cursor_pos -= 1
                            self._events.append(
                                InputEvent(InputEventType.CHAR, char="")
                            )
                        escape_handled = True
                    else:
                        # Unknown escape sequence - consume and ignore
                        escape_handled = True
                        self._last_was_escape = True
                else:
                    # Incomplete escape sequence - save for next call
                    # CRITICAL FIX: Save even if only ESC (len==1) so next call can complete it
                    # Save to escape_buffer so next get_event() call can complete the sequence
                    self._escape_buffer = seq
                    escape_handled = True
                    self._last_was_escape = True
            
            # Only process as printable character if not an escape sequence
            if not escape_handled and ord(char) >= 32:  # Printable character
                # CRITICAL FIX: Check if this might be part of an escape sequence
                # If we see '[' (91) or 'C'/'D' (67/68) right after an escape was processed,
                # they might be leftover characters from an incomplete escape sequence
                # We need to check if there's more data that suggests this is an escape sequence
                if ord(char) == 91:  # '[' character
                    # This could be the second char of an escape sequence
                    # Check if there's more data coming that would complete it
                    if select.select([sys.stdin], [], [], 0.05)[0]:
                        next_char = sys.stdin.read(1)
                        if next_char in 'ABCD':  # Arrow key!
                            # This IS part of an escape sequence - ignore both chars
                            escape_handled = True
                        else:
                            # Not an arrow key - might be a real '[' character
                            # But to be safe, if next_char is printable, process both
                            if ord(next_char) >= 32:
                                # Process '[' as normal
                                pass
                            else:
                                # Non-printable - ignore '[' too
                                escape_handled = True
                    else:
                        # No more data - could be standalone '[', but ignore to be safe
                        escape_handled = True
                elif ord(char) in (67, 68):  # 'C' or 'D' character
                    # This could be the third char of an escape sequence
                    # If we just processed an escape, this is likely leftover
                    # Check if there was a recent escape
                    if self._escape_buffer or (hasattr(self, '_last_was_escape') and self._last_was_escape):
                        # Likely part of escape sequence - ignore
                        escape_handled = True
                        self._last_was_escape = False
                
                if not escape_handled:
                    # Security: Prevent buffer overflow
                    if len(self._input_buffer) >= self.MAX_INPUT_LENGTH:
                        # Buffer full - ignore further input
                        return None
                    
                    # Insert character at cursor position
                    self._input_buffer = (
                        self._input_buffer[:self._cursor_pos] +
                        char +
                        self._input_buffer[self._cursor_pos:]
                    )
                    self._cursor_pos += 1
                    self._events.append(
                        InputEvent(InputEventType.CHAR, char=char)
                    )

        except (EOFError, OSError):
            self._events.append(InputEvent(InputEventType.EXIT))

        # Return first event if any
        if self._events:
            return self._events.pop(0)

        return None
