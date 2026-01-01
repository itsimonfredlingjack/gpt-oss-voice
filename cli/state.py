"""Thread-safe state machine for CLI application.

Provides a proper state management system with locking to prevent
race conditions during state transitions.
"""

from enum import Enum, auto
from threading import RLock
from typing import Callable, Optional
from dataclasses import dataclass, field
import time


class AppState(Enum):
    """Application states for the CLI."""
    IDLE = auto()
    THINKING = auto()
    TALKING = auto()
    ERROR = auto()


# UX-friendly messages for each state
STATE_MESSAGES = {
    AppState.IDLE: "◈ NEURAL LINK READY",
    AppState.THINKING: "◇ PROCESSING QUERY",
    AppState.TALKING: "◆ TRANSMITTING RESPONSE",
    AppState.ERROR: "✗ SIGNAL INTERRUPTED",
}

# Hints shown to user in each state
STATE_HINTS = {
    AppState.IDLE: "Type your message or /help for commands",
    AppState.THINKING: "Analyzing neural pathways...",
    AppState.TALKING: "Press Ctrl+C to skip",
    AppState.ERROR: "Press Enter to retry",
}


@dataclass
class StateTransition:
    """Record of a state transition."""
    from_state: AppState
    to_state: AppState
    timestamp: float


class StateManager:
    """Thread-safe state machine with observer pattern.

    Attributes:
        state: Current application state (read via property).

    Example:
        >>> manager = StateManager()
        >>> manager.state
        <AppState.IDLE: 1>
        >>> manager.transition_to(AppState.THINKING)
        True
    """

    VALID_TRANSITIONS = {
        AppState.IDLE: {AppState.THINKING},
        AppState.THINKING: {AppState.TALKING, AppState.IDLE, AppState.ERROR},
        AppState.TALKING: {AppState.IDLE, AppState.ERROR},
        AppState.ERROR: {AppState.IDLE},
    }

    def __init__(self):
        """Initialize state manager in IDLE state."""
        self._state: AppState = AppState.IDLE
        self._lock: RLock = RLock()
        self._observers: list[Callable[[AppState, AppState], None]] = []
        self._history: list[StateTransition] = []
        self._state_entered_at: float = time.time()
        self._last_error: Optional[str] = None
        self._speaking_text: Optional[str] = None  # Text currently being spoken

    @property
    def state(self) -> AppState:
        """Get current state (thread-safe)."""
        with self._lock:
            return self._state

    @property
    def state_name(self) -> str:
        """Get current state name as string."""
        with self._lock:
            return self._state.name

    @property
    def status_message(self) -> str:
        """Get UX-friendly status message for current state."""
        with self._lock:
            return STATE_MESSAGES.get(self._state, "◇ UNKNOWN STATE")

    @property
    def hint(self) -> str:
        """Get user guidance hint for current state."""
        with self._lock:
            return STATE_HINTS.get(self._state, "")

    @property
    def duration(self) -> float:
        """Seconds spent in current state."""
        with self._lock:
            return time.time() - self._state_entered_at

    @property
    def last_error(self) -> Optional[str]:
        """Get last error message if in ERROR state."""
        with self._lock:
            return self._last_error

    @property
    def speaking_text(self) -> Optional[str]:
        """Get text currently being spoken (for voice-first indicator)."""
        with self._lock:
            return self._speaking_text

    def set_speaking_text(self, text: Optional[str]) -> None:
        """Set text currently being spoken.
        
        Args:
            text: Text being spoken, or None if not speaking.
        """
        with self._lock:
            self._speaking_text = text

    def set_error(self, message: str) -> bool:
        """Transition to ERROR state with message.

        Args:
            message: Error description to display.

        Returns:
            True if transition succeeded.
        """
        with self._lock:
            self._last_error = message
            return self.transition_to(AppState.ERROR)

    def transition_to(self, new_state: AppState) -> bool:
        """Atomically transition to new state if valid.

        Args:
            new_state: The target state to transition to.

        Returns:
            True if transition succeeded, False if invalid.
        """
        with self._lock:
            if new_state in self.VALID_TRANSITIONS.get(self._state, set()):
                old_state = self._state
                self._state = new_state
                self._state_entered_at = time.time()
                # Clear error when leaving ERROR state
                if old_state == AppState.ERROR:
                    self._last_error = None
                self._history.append(
                    StateTransition(old_state, new_state, time.time())
                )
                self._notify_observers(old_state, new_state)
                return True
            return False

    def force_state(self, new_state: AppState) -> None:
        """Force state change without validation (use sparingly).

        Args:
            new_state: The state to force.
        """
        with self._lock:
            old_state = self._state
            self._state = new_state
            self._notify_observers(old_state, new_state)

    def add_observer(self, callback: Callable[[AppState, AppState], None]) -> None:
        """Register callback for state changes.

        Args:
            callback: Function called with (old_state, new_state).
        """
        with self._lock:
            self._observers.append(callback)

    def remove_observer(self, callback: Callable[[AppState, AppState], None]) -> None:
        """Unregister a callback.

        Args:
            callback: The callback to remove.
        """
        with self._lock:
            if callback in self._observers:
                self._observers.remove(callback)

    def _notify_observers(self, old: AppState, new: AppState) -> None:
        """Notify all observers of state change."""
        for observer in self._observers:
            try:
                observer(old, new)
            except Exception:
                pass  # Don't let observer errors break state machine


# Backward compatibility: Global instance
_global_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get or create the global state manager singleton."""
    global _global_manager
    if _global_manager is None:
        _global_manager = StateManager()
    return _global_manager
