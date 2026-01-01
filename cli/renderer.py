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
        char_delay: Base delay between characters (seconds).
        period_delay: Delay after period/exclamation/question (.!?).
        comma_delay: Delay after comma (,).
        colon_delay: Delay after colon/semicolon (:;).
        newline_delay: Delay after newline (\n).
        sentence_space_delay: Delay for space after sentence-ending punctuation.
        word_delay: Additional delay after regular spaces (deprecated, use char_delay).
        line_delay: Additional delay after newlines (deprecated, use newline_delay).
    """
    char_delay: float = 0.02
    period_delay: float = 0.08
    comma_delay: float = 0.04
    colon_delay: float = 0.05
    newline_delay: float = 0.15
    sentence_space_delay: float = 0.03
    # Backward compatibility
    word_delay: float = 0.05
    line_delay: float = 0.1

    def get_delay(self, char: str, prev_char: str = '') -> float:
        """Calculate delay for a character based on punctuation rules.

        Args:
            char: Current character being displayed.
            prev_char: Previous character (for context-aware delays).

        Returns:
            Delay in seconds for this character.
        """
        # Sentence-ending punctuation
        if char in '.!?':
            return self.period_delay

        # Comma
        if char == ',':
            return self.comma_delay

        # Colon/semicolon
        if char in ':;':
            return self.colon_delay

        # Newline
        if char == '\n':
            return self.newline_delay

        # Space after sentence-ending punctuation
        if char == ' ' and prev_char in '.!?':
            return self.sentence_space_delay

        # Regular space (backward compatibility fallback)
        if char == ' ':
            return self.char_delay + self.word_delay

        # Default character delay
        return self.char_delay


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
                prev_char = self._full_text[self._current_pos - 1] if self._current_pos > 0 else ''
                self._current_pos += 1

            # Calculate delay using punctuation-aware method
            delay = self.config.get_delay(char, prev_char)

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

        # Get previous character for context-aware delays
        prev_char = text[i - 1] if i > 0 else ''
        delay = cfg.get_delay(char, prev_char)

        time.sleep(delay)
