# Spec: Refactor CLI for Concurrency and State Management

## Overview
Refactor the `cli.py` architecture to eliminate UI freezing and race conditions during AI interaction. The core solution involves implementing a formal State Machine (`IDLE`, `THINKING`, `TALKING`) and decoupling the AI generation phase from the audio playback phase.

## Functional Requirements

### 1. Architectural Refactoring (State Machine)
- Introduce a global `APP_STATE` variable in `cli.py`.
- States:
    - `IDLE`: System is ready for user input.
    - `THINKING`: System is waiting for LLM response from `ask_brain()`.
    - `TALKING`: System is playing back audio via `speak_threaded()`.
- **Constraint:** User input must be disabled or ignored when `APP_STATE` is not `IDLE`.

### 2. Decoupled Integration (`brain.py`)
- Modify `brain.py` so `ask_brain(prompt)` returns the generated text string directly.
- **Dependency:** Remove the internal call to `speak()` within `ask_brain()`.

### 3. Non-Blocking Generation (`cli.py`)
- When a prompt is submitted:
    1. Set `APP_STATE = THINKING`.
    2. Execute `ask_brain()` in a background daemon thread.
    3. The background thread must place the resulting text into a `queue.Queue`.
- The main loop must poll this queue while continuing to render `AIAvatar` and `Waveform` animations.

### 4. Non-Blocking Playback (`cli.py`)
- Once text is retrieved from the queue:
    1. Set `APP_STATE = TALKING`.
    2. Invoke `speak_threaded(text)`.
- Refactor `speak_threaded` to set the `is_speaking` flag **immediately** in the main thread to prevent UI flicker.
- Ensure the background thread resets the flag in a `finally` block.

### 5. UI Feedback
- **THINKING State:** 
    - Display "Thinking..." in the Station Log.
    - Implement a "thinking" animation frame for `AIAvatar` (e.g., eyes shifted upward).
- **TALKING State:** Existing mouth movement and waveform animations.

### 6. Test Reliability (`tests/test_threading.py`)
- Replace all hardcoded `time.sleep()` calls with a robust polling assertion helper (`wait_for_condition`).
- Ensure `set_is_speaking(False)` is called in test setup to prevent cross-test pollution.

## Acceptance Criteria
- [ ] UI animations (Avatar/Waveform) remain fluid and do not freeze during the "Thinking" phase.
- [ ] No visual "flicker" to IDLE occurs between the start of a response and the start of audio.
- [ ] `brain.py` no longer triggers audio playback directly.
- [ ] Threading tests pass consistently on slow or fast machines without hardcoded delays.
- [ ] User cannot submit a new prompt while the AI is currently thinking or speaking.
