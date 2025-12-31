"""Streaming text renderer for Matrix-style output.

Provides character-by-character text display effect.
"""

import time
import threading
from typing import Optional, Generator
from dataclasses import dataclass


@dataclass
class StreamConfig:
    """Configuration for streaming text.

    Attributes:
        char_delay: Seconds between characters.
        word_delay: Additional delay after spaces.
        line_delay: Additional delay after newlines.
    """
    char_delay: float = 0.02
    word_delay: float = 0.05
    line_delay: float = 0.1


class StreamingRenderer:
    """Renders text with streaming effect.

    Text is revealed character-by-character, creating
    a "typing" or "Matrix" style effect.

    Example:
        >>> renderer = StreamingRenderer()
        >>> renderer.start_stream("Hello, world!")
        >>> while not renderer.is_complete:
        ...     print(renderer.current_text)
        ...     time.sleep(0.05)
    """

    def __init__(self, config: Optional[StreamConfig] = None):
        """Initialize renderer.

        Args:
            config: Optional configuration.
        """
        self.config = config or StreamConfig()
        self._full_text = ''
        self._current_pos = 0
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._complete = threading.Event()
        self._lock = threading.Lock()

    @property
    def current_text(self) -> str:
        """Get currently revealed text."""
        with self._lock:
            return self._full_text[:self._current_pos]

    @property
    def is_complete(self) -> bool:
        """Check if streaming is complete."""
        return self._complete.is_set()

    @property
    def is_streaming(self) -> bool:
        """Check if currently streaming."""
        return self._running.is_set() and not self._complete.is_set()

    def start_stream(self, text: str) -> None:
        """Start streaming new text.

        Args:
            text: The full text to stream.
        """
        self.stop()

        with self._lock:
            self._full_text = text
            self._current_pos = 0

        self._complete.clear()
        self._running.set()

        self._thread = threading.Thread(
            target=self._stream_loop,
            daemon=True,
            name='StreamingRenderer'
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop streaming and reveal full text."""
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.1)

        with self._lock:
            self._current_pos = len(self._full_text)
        self._complete.set()

    def skip(self) -> None:
        """Skip to end of current stream."""
        self.stop()

    def _stream_loop(self) -> None:
        """Background thread that advances text position."""
        while self._running.is_set():
            with self._lock:
                if self._current_pos >= len(self._full_text):
                    break

                char = self._full_text[self._current_pos]
                self._current_pos += 1

            # Calculate delay based on character
            delay = self.config.char_delay
            if char == ' ':
                delay += self.config.word_delay
            elif char == '\n':
                delay += self.config.line_delay

            time.sleep(delay)

        self._complete.set()


def stream_chars(text: str, config: Optional[StreamConfig] = None) -> Generator[str, None, None]:
    """Generator that yields text progressively.

    Args:
        text: Full text to stream.
        config: Optional timing configuration.

    Yields:
        Progressively longer substrings of text.
    """
    cfg = config or StreamConfig()

    for i, char in enumerate(text):
        yield text[:i + 1]

        delay = cfg.char_delay
        if char == ' ':
            delay += cfg.word_delay
        elif char == '\n':
            delay += cfg.line_delay

        time.sleep(delay)
