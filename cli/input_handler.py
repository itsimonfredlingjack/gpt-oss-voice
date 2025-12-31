"""Non-blocking input handler using threading.

Allows the main render loop to continue animations while
waiting for user input in a separate thread.
"""

import threading
import queue
import sys
from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto


class InputEventType(Enum):
    """Types of input events."""
    TEXT = auto()      # User submitted text
    EXIT = auto()      # User wants to exit
    INTERRUPT = auto() # Ctrl+C pressed


@dataclass
class InputEvent:
    """An input event from the user.

    Attributes:
        type: The event type.
        text: The input text (for TEXT events).
    """
    type: InputEventType
    text: str = ''


class InputHandler:
    """Non-blocking input handler using a dedicated thread.

    The handler runs input() in a background thread, allowing
    the main thread to continue rendering animations. Input
    events are passed via a thread-safe queue.

    Example:
        >>> handler = InputHandler()
        >>> handler.start()
        >>> # In main loop:
        >>> event = handler.get_event()
        >>> if event and event.type == InputEventType.TEXT:
        ...     process_input(event.text)
    """

    def __init__(self, prompt: str = ''):
        """Initialize input handler.

        Args:
            prompt: Prompt string (displayed by main thread, not here).
        """
        self._prompt = prompt
        self._queue: queue.Queue[InputEvent] = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._input_enabled = threading.Event()
        self._waiting_for_input = threading.Event()

    @property
    def is_running(self) -> bool:
        """Check if handler is running."""
        return self._running.is_set()

    @property
    def is_waiting(self) -> bool:
        """Check if currently waiting for input."""
        return self._waiting_for_input.is_set()

    def start(self) -> None:
        """Start the input listener thread."""
        if self._thread and self._thread.is_alive():
            return

        self._running.set()
        self._input_enabled.set()
        self._thread = threading.Thread(
            target=self._input_loop,
            daemon=True,
            name='InputHandler'
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the input listener thread."""
        self._running.clear()
        self._input_enabled.set()  # Unblock if waiting
        if self._thread:
            self._thread.join(timeout=0.5)

    def enable_input(self) -> None:
        """Allow input to be captured (call when IDLE)."""
        self._input_enabled.set()

    def disable_input(self) -> None:
        """Ignore input (call during THINKING/TALKING)."""
        self._input_enabled.clear()

    def get_event(self, timeout: float = 0.0) -> Optional[InputEvent]:
        """Get next input event (non-blocking by default).

        Args:
            timeout: Max seconds to wait (0 = non-blocking).

        Returns:
            InputEvent or None if no event available.
        """
        try:
            if timeout > 0:
                return self._queue.get(timeout=timeout)
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def clear_queue(self) -> None:
        """Clear any pending input events."""
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def _input_loop(self) -> None:
        """Background thread that reads input."""
        while self._running.is_set():
            # Wait until input is enabled
            if not self._input_enabled.wait(timeout=0.1):
                continue

            # Check if we should still run
            if not self._running.is_set():
                break

            try:
                self._waiting_for_input.set()
                line = input()  # Blocking in this thread, OK
                self._waiting_for_input.clear()

                # Check exit commands
                if line.lower().strip() in ('exit', 'quit', '/exit', '/quit'):
                    self._queue.put(InputEvent(InputEventType.EXIT))
                elif line.strip():
                    self._queue.put(InputEvent(InputEventType.TEXT, line.strip()))
                # Empty lines are ignored

            except EOFError:
                self._waiting_for_input.clear()
                self._queue.put(InputEvent(InputEventType.EXIT))
                break
            except KeyboardInterrupt:
                self._waiting_for_input.clear()
                self._queue.put(InputEvent(InputEventType.INTERRUPT))
            except Exception:
                self._waiting_for_input.clear()
                # Ignore other errors, keep trying
                continue
