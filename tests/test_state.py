"""Tests for cli/state.py - StateManager."""

import pytest
import sys
import os
import time
import threading
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cli.state import StateManager, AppState, StateTransition


class TestStateManager:
    """Test suite for StateManager."""
    
    def test_init(self):
        """Test StateManager initialization."""
        manager = StateManager()
        assert manager.state == AppState.IDLE
        assert manager.state_name == "IDLE"
        assert manager.duration >= 0
        assert manager.last_error is None
        assert manager.speaking_text is None
    
    def test_initial_state(self):
        """Test initial state is IDLE."""
        manager = StateManager()
        assert manager.state == AppState.IDLE
    
    def test_state_name_property(self):
        """Test state_name property."""
        manager = StateManager()
        assert manager.state_name == "IDLE"
        manager.force_state(AppState.THINKING)
        assert manager.state_name == "THINKING"
    
    def test_status_message(self):
        """Test status_message property."""
        manager = StateManager()
        assert "READY" in manager.status_message or "IDLE" in manager.status_message
    
    def test_hint_property(self):
        """Test hint property."""
        manager = StateManager()
        assert len(manager.hint) > 0
    
    def test_duration_tracking(self):
        """Test duration property tracks time in state."""
        manager = StateManager()
        initial_duration = manager.duration
        time.sleep(0.1)
        assert manager.duration >= initial_duration
    
    def test_valid_transition_idle_to_thinking(self):
        """Test valid transition: IDLE -> THINKING."""
        manager = StateManager()
        assert manager.state == AppState.IDLE
        result = manager.transition_to(AppState.THINKING)
        assert result is True
        assert manager.state == AppState.THINKING
    
    def test_valid_transition_thinking_to_talking(self):
        """Test valid transition: THINKING -> TALKING."""
        manager = StateManager()
        manager.transition_to(AppState.THINKING)
        result = manager.transition_to(AppState.TALKING)
        assert result is True
        assert manager.state == AppState.TALKING
    
    def test_valid_transition_talking_to_idle(self):
        """Test valid transition: TALKING -> IDLE."""
        manager = StateManager()
        manager.transition_to(AppState.THINKING)
        manager.transition_to(AppState.TALKING)
        result = manager.transition_to(AppState.IDLE)
        assert result is True
        assert manager.state == AppState.IDLE
    
    def test_invalid_transition_idle_to_talking(self):
        """Test invalid transition: IDLE -> TALKING."""
        manager = StateManager()
        result = manager.transition_to(AppState.TALKING)
        assert result is False
        assert manager.state == AppState.IDLE
    
    def test_invalid_transition_talking_to_thinking(self):
        """Test invalid transition: TALKING -> THINKING."""
        manager = StateManager()
        manager.transition_to(AppState.THINKING)
        manager.transition_to(AppState.TALKING)
        result = manager.transition_to(AppState.THINKING)
        assert result is False
        assert manager.state == AppState.TALKING
    
    def test_force_state(self):
        """Test force_state bypasses validation."""
        manager = StateManager()
        manager.force_state(AppState.TALKING)
        assert manager.state == AppState.TALKING
    
    def test_error_state(self):
        """Test error state handling."""
        manager = StateManager()
        result = manager.set_error("Test error")
        assert result is True
        assert manager.state == AppState.ERROR
        assert manager.last_error == "Test error"
    
    def test_error_state_from_thinking(self):
        """Test error state from THINKING."""
        manager = StateManager()
        manager.transition_to(AppState.THINKING)
        result = manager.set_error("Error during thinking")
        assert result is True
        assert manager.state == AppState.ERROR
    
    def test_error_state_from_talking(self):
        """Test error state from TALKING."""
        manager = StateManager()
        manager.transition_to(AppState.THINKING)
        manager.transition_to(AppState.TALKING)
        result = manager.set_error("Error during talking")
        assert result is True
        assert manager.state == AppState.ERROR
    
    def test_error_recovery(self):
        """Test recovery from ERROR state."""
        manager = StateManager()
        manager.set_error("Test error")
        result = manager.transition_to(AppState.IDLE)
        assert result is True
        assert manager.state == AppState.IDLE
        assert manager.last_error is None
    
    def test_observer_pattern(self):
        """Test observer pattern for state changes."""
        manager = StateManager()
        callback_called = []
        
        def observer(old_state, new_state):
            callback_called.append((old_state, new_state))
        
        manager.add_observer(observer)
        manager.transition_to(AppState.THINKING)
        
        assert len(callback_called) == 1
        assert callback_called[0] == (AppState.IDLE, AppState.THINKING)
    
    def test_multiple_observers(self):
        """Test multiple observers are notified."""
        manager = StateManager()
        callbacks_called = []
        
        def observer1(old_state, new_state):
            callbacks_called.append(1)
        
        def observer2(old_state, new_state):
            callbacks_called.append(2)
        
        manager.add_observer(observer1)
        manager.add_observer(observer2)
        manager.transition_to(AppState.THINKING)
        
        assert len(callbacks_called) == 2
        assert 1 in callbacks_called
        assert 2 in callbacks_called
    
    def test_remove_observer(self):
        """Test removing observer."""
        manager = StateManager()
        callback_called = []
        
        def observer(old_state, new_state):
            callback_called.append(True)
        
        manager.add_observer(observer)
        manager.transition_to(AppState.THINKING)
        assert len(callback_called) == 1
        
        manager.remove_observer(observer)
        manager.transition_to(AppState.TALKING)
        assert len(callback_called) == 1  # Not called again
    
    def test_observer_error_handling(self):
        """Test observer errors don't break state machine."""
        manager = StateManager()
        
        def bad_observer(old_state, new_state):
            raise Exception("Observer error")
        
        manager.add_observer(bad_observer)
        # Should not raise exception
        result = manager.transition_to(AppState.THINKING)
        assert result is True
    
    def test_transition_history(self):
        """Test transition history tracking."""
        manager = StateManager()
        initial_history_len = len(manager._history)
        
        manager.transition_to(AppState.THINKING)
        assert len(manager._history) == initial_history_len + 1
        
        transition = manager._history[-1]
        assert isinstance(transition, StateTransition)
        assert transition.from_state == AppState.IDLE
        assert transition.to_state == AppState.THINKING
    
    def test_speaking_text_property(self):
        """Test speaking_text property."""
        manager = StateManager()
        assert manager.speaking_text is None
        
        manager.set_speaking_text("Hello, world!")
        assert manager.speaking_text == "Hello, world!"
        
        manager.set_speaking_text(None)
        assert manager.speaking_text is None
    
    def test_thread_safety_concurrent_transitions(self):
        """Test thread safety with concurrent transitions."""
        manager = StateManager()
        results = []
        errors = []
        
        def transition_worker():
            try:
                for _ in range(10):
                    manager.transition_to(AppState.THINKING)
                    manager.transition_to(AppState.TALKING)
                    manager.transition_to(AppState.IDLE)
                    results.append(True)
            except Exception as e:
                errors.append(e)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=transition_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should complete without errors
        assert len(errors) == 0
        assert len(results) == 50  # 5 threads * 10 iterations
    
    def test_thread_safety_state_access(self):
        """Test thread safety for state property access."""
        manager = StateManager()
        states_read = []
        
        def read_state():
            for _ in range(100):
                states_read.append(manager.state)
        
        def change_state():
            for _ in range(10):
                manager.transition_to(AppState.THINKING)
                manager.transition_to(AppState.IDLE)
        
        reader_thread = threading.Thread(target=read_state)
        changer_thread = threading.Thread(target=change_state)
        
        reader_thread.start()
        changer_thread.start()
        
        reader_thread.join()
        changer_thread.join()
        
        # Should read valid states without errors
        assert len(states_read) == 100
        assert all(state in AppState for state in states_read)
    
    def test_duration_reset_on_transition(self):
        """Test duration resets when transitioning to new state."""
        manager = StateManager()
        initial_duration = manager.duration
        
        time.sleep(0.1)
        manager.transition_to(AppState.THINKING)
        
        # Duration should reset (be small)
        assert manager.duration < initial_duration + 0.05
    
    def test_error_cleared_on_transition_from_error(self):
        """Test error message cleared when leaving ERROR state."""
        manager = StateManager()
        manager.set_error("Test error")
        assert manager.last_error == "Test error"
        
        manager.transition_to(AppState.IDLE)
        assert manager.last_error is None
    
    def test_force_state_updates_history(self):
        """Test force_state updates transition history."""
        manager = StateManager()
        initial_history_len = len(manager._history)
        
        manager.force_state(AppState.TALKING)
        assert len(manager._history) == initial_history_len + 1

