# Plan: Implement the Core CLI Application

## Phase 1: Foundation & Theme
- [x] Task: Create `cli.py` and implement the `Rich` theme for Solarized Light 4b090c7
- [x] Task: Define the `AIAvatar` class with ASCII art and state management (IDLE/TALKING) f1f0d6a
- [x] Task: Define the `Waveform` class with block-character animation logic 4b1c97a
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Theme' (Protocol in workflow.md)

## Phase 2: Layout & Concurrency
- [ ] Task: Implement the `Rich` layout (Header, Sidebar, Log, Footer)
- [ ] Task: Implement the background threading logic for `speak()` using a global `is_speaking` flag
- [ ] Task: Integrate the interactive loop (Input -> Brain -> Speak)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Layout & Concurrency' (Protocol in workflow.md)

## Phase 3: Polish & Integration
- [ ] Task: Implement Markdown rendering for AI responses in the history log
- [ ] Task: Add blinking and mouth animation logic to the `Live` update loop
- [ ] Task: Final integration testing with `brain.py` and `speak.py`
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Polish & Integration' (Protocol in workflow.md)
