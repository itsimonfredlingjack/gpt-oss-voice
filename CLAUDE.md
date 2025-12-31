# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Google Home Hack** is a voice-activated AI assistant that integrates a local LLM (Ollama) with Google Home speakers via Chromecast. The main interface is "The Core CLI" - a futuristic Rich-based terminal UI featuring an animated AI avatar and waveform visualization.

## Commands

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run a single test file
pytest tests/test_avatar.py

# Run the CLI interface
python cli.py

# Direct TTS test
python speak.py "Hej, detta är ett test."

# Interactive AI chat (standalone)
python brain.py

# System monitoring with voice output
python monitor.py
```

## Architecture

### Module Dependencies
```
cli.py  ──imports──>  brain.py  ──API──>  Ollama (localhost:11434)
   │
   └─────imports──>  speak.py  ──Cast──>  Google Home ("Kontor")
```

### Core Modules

| Module | Purpose |
|--------|---------|
| `cli.py` | Main Rich-based terminal UI with `AIAvatar`, `Waveform`, and threaded state machine |
| `brain.py` | Ollama API wrapper using `gptoss-agent` model. Key function: `ask_brain(prompt)` |
| `speak.py` | PyChromecast TTS via Google Translate. Key function: `speak(text)` (blocking) |
| `monitor.py` | System health reporter (CPU/RAM/Disk) with voice output |

### CLI State Machine (`cli.py`)

The application uses a global `APP_STATE` with three states:
- **IDLE**: Avatar blinking, waveform flat, waiting for user input
- **THINKING**: Brain thread processing, UI shows "Thinking..."
- **TALKING**: Speaking thread active, avatar mouth animates, waveform moves

Threading is critical: `speak()` is blocking, so `speak_threaded()` runs it in a daemon thread while the `Live` context continues rendering animations.

### Theme

Uses Solarized Light palette via `rich.theme.Theme`:
- Avatar eyes: `#268bd2` (Blue)
- Avatar mouth: `#d33682` (Magenta)
- Waveform: `#2aa198` (Cyan)
- User input: `#cb4b16` (Orange)

## Configuration

- **Google Home device**: Change `DEVICE_NAME` in `speak.py` (default: "Kontor")
- **LLM model**: Change `MODEL_NAME` in `brain.py` (default: "gptoss-agent")
- **Language**: Swedish (`tl=sv`) hardcoded in TTS and system prompt

## Conductor Workflow

This project uses the Conductor methodology for task management:
- Plans are tracked in `conductor/tracks/<track_name>/plan.md`
- Follow TDD: write failing tests first, then implement
- Mark tasks `[~]` (in progress) → `[x]` (complete) with commit SHA
- Target >80% code coverage

## Code Style

Follow Google Python Style Guide (see `conductor/code_styleguides/python.md`):
- 80 char line limit
- 4-space indentation
- `snake_case` for functions/variables, `PascalCase` for classes
- Type annotations encouraged
- All public functions need docstrings
