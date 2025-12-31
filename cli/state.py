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
        AppState.THINKING: {AppState.TALKING, AppState.IDLE},
        AppState.TALKING: {AppState.IDLE},
    }

    def __init__(self):
        """Initialize state manager in IDLE state."""
        self._state: AppState = AppState.IDLE
        self._lock: RLock = RLock()
        self._observers: list[Callable[[AppState, AppState], None]] = []
        self._history: list[StateTransition] = []

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
