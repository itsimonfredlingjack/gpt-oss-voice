# Plan: Refactor CLI for Concurrency and State Management

## Phase 1: Foundation & Test Reliability
- [x] Task: Refactor `tests/test_threading.py` to use polling assertions instead of hardcoded sleeps 842247d
- [x] Task: Implement `set_is_speaking(False)` in test setup to prevent state pollution 842247d
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Test Reliability' (Protocol in workflow.md)

## Phase 2: Decoupling & State Machine
- [ ] Task: Refactor `brain.py` to return text string instead of calling `speak`
- [ ] Task: Implement `APP_STATE` State Machine in `cli.py` (IDLE, THINKING, TALKING)
- [ ] Task: Implement `AIAvatar` "Thinking" state frame
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Decoupling & State Machine' (Protocol in workflow.md)

## Phase 3: Concurrency Implementation
- [ ] Task: Implement background thread for `ask_brain` with Queue for results
- [ ] Task: Refactor `speak_threaded` to set flag immediately in main thread
- [ ] Task: Implement main loop polling for state transitions and Queue handling
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Concurrency Implementation' (Protocol in workflow.md)
