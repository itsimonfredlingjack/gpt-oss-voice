# Spec: Implement the Core CLI Application

## Overview
Create `cli.py`, a "Single Screen Application" for the terminal that provides a futuristic, retro-futuristic interface for the Google Home AI assistant.

## Requirements
- **Theme:** Solarized Light (Background: #fdf6e3, Text: #657b83).
- **Library:** Use `rich` for layout and rendering.
- **Components:**
    - `AIAvatar`: ASCII robot face with `IDLE` and `TALKING` states.
    - `Waveform`: Block-character visualization that animates during speech.
    - `Layout`: Header ("DEV STATION"), Sidebar (Avatar + Waveform), Main Log (History with Markdown), Footer (Status).
- **Concurrency:** Use `threading` to run `speak()` in the background so animations don't freeze.
- **Interaction:** Synchronous input with asynchronous visual feedback during response generation and playback.

## Acceptance Criteria
- [ ] `cli.py` runs without errors.
- [ ] UI displays the correct Solarized Light theme colors.
- [ ] Avatar blinks during `IDLE` and moves mouth during `TALKING`.
- [ ] Waveform is flat during `IDLE` and animates during `TALKING`.
- [ ] AI responses are rendered as Markdown in the history panel.
- [ ] UI remains responsive/animated while audio is playing on Google Home.
