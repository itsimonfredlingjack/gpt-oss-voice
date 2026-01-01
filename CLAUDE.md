# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Google Home Hack** is a voice-activated AI assistant that integrates a local LLM (Ollama) with Google Home speakers via Chromecast. The main interface is "The Core CLI" - a cyberpunk-themed Rich-based terminal UI with animated avatar, waveform visualization, and non-blocking input.

## Commands

```bash
# Run the CLI interface (two ways)
python cli.py
python -m cli.app

# Run tests
pytest
pytest tests/test_avatar.py           # Single file
pytest --cov=. --cov-report=html      # With coverage

# Direct module tests
python speak.py "Hej, detta är ett test."  # TTS
python brain.py                             # AI chat
```

## Architecture

```
cli.py (entry point)
  └── cli/app.py (CLIApp)
        ├── cli/state.py      StateManager (IDLE→THINKING→TALKING→ERROR)
        ├── cli/raw_input.py  RawInputHandler (termios, escape sequences)
        ├── cli/renderer.py   StreamingRenderer (typewriter effect)
        ├── cli/avatar.py     BrailleAvatar (depth-based coloring)
        ├── cli/waveform.py   Waveform animation
        ├── cli/layout.py     Rich Layout composition
        ├── cli/theme.py      Midnight Tokyo / Solarized themes
        ├── brain.py          Ollama API (localhost:11434)
        └── speak.py          GoogleHomeSpeaker (Chromecast TTS)
```

### Async + Threading Pattern

The main loop is `asyncio` but blocking I/O uses thread pools:
```python
# In CLIApp._brain_worker()
response = await loop.run_in_executor(None, ask_brain, prompt)

# In CLIApp._speak_worker()
await loop.run_in_executor(None, self.speaker.speak, text)
```

**Critical**: Both `speak()` and `ask_brain()` are blocking. Never call them directly in the async loop.

### State Machine

`StateManager` in `cli/state.py` enforces valid transitions:
```
IDLE → THINKING → TALKING → IDLE
         ↓          ↓
       ERROR  ←  ERROR  → IDLE
```

States control input handling, avatar animation, and waveform behavior.

### Input Handling

`RawInputHandler` uses `termios` in cbreak mode for character-by-character capture without conflicting with Rich Live. Key features:
- Arrow keys for cursor movement and history
- Escape sequence parsing with `_escape_buffer`
- Ctrl+C interrupts current state, second press exits
- Max 10,000 char buffer with validation

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Google Home device | `speak.py:DEVICE_NAME` | "Kontor" |
| LLM model | `brain.py:MODEL_NAME` | "gptoss-agent" |
| Language | `speak.py` TTS URL + `brain.py` system prompt | Swedish |
| Theme | `cli/app.py:CLIApp.__init__` | MIDNIGHT_TOKYO_THEME |
| FPS | `cli/app.py:AppConfig.fps` | 15 |

## Error Handling

Custom exceptions enable targeted UX messages:
- `BrainConnectionError` / `BrainEmptyResponseError` in `brain.py`
- `DeviceNotFoundError` in `speak.py`

The app shows user-friendly error messages and auto-recovers after 5 seconds.

## Conductor Workflow

Plans tracked in `conductor/tracks/<track_name>/plan.md`:
- Mark tasks `[~]` (in progress) → `[x]` (complete) with commit SHA
- Follow TDD: failing test → implementation → green
- Target >80% coverage

## Code Style

Google Python Style Guide (`conductor/code_styleguides/python.md`):
- 80 char lines, 4-space indent
- Type hints, docstrings on public functions
- `snake_case` functions, `PascalCase` classes
