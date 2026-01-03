# Google Home Hack / GPT-OSS Voice

A voice-activated AI assistant that integrates a local LLM (Ollama) with Google Home speakers via Chromecast. The main interface is **"The Core CLI"** - a cyberpunk-themed Rich-based terminal UI with animated avatar, waveform visualization, and non-blocking input.

## Features

- 🎤 **Voice-First Interface**: Speak to your AI assistant via Google Home speakers
- 🤖 **Local LLM Integration**: Uses Ollama for privacy-focused AI responses
- 🎨 **Cyberpunk Terminal UI**: Rich-based interface with animated avatar and effects
- 🇸🇪 **Swedish Language Support**: Optimized for Swedish language interaction
- ⚡ **Real-time Streaming**: Typewriter effect for AI responses
- 🎯 **State Management**: Robust state machine for reliable operation
- 📊 **System Monitoring**: Real-time CPU, RAM, and network stats

## Architecture

```
cli.py (entry point)
  └── cli/app.py (CLIApp)
        ├── cli/state.py      StateManager (IDLE→THINKING→TALKING→ERROR)
        ├── cli/raw_input.py  RawInputHandler (termios, escape sequences)
        ├── cli/renderer.py   StreamingRenderer (typewriter effect)
        ├── cli/avatar.py     MechaCoreAvatar (cyberpunk avatar)
        ├── cli/waveform.py   Waveform animation
        ├── cli/layout.py     Rich Layout composition
        ├── cli/theme.py      Chimera theme (cyberpunk styling)
        ├── brain.py          Ollama API wrapper
        ├── speak.py          GoogleHomeSpeaker (Chromecast TTS)
        └── config.py         Configuration management
```

### State Machine

The application uses a state machine to manage workflow:

```
IDLE → THINKING → TALKING → IDLE
         ↓          ↓
       ERROR  ←  ERROR  → IDLE
```

- **IDLE**: Ready for user input
- **THINKING**: Processing user query with Ollama
- **TALKING**: Speaking response via Google Home
- **ERROR**: Error state with auto-recovery

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running locally
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull a Swedish-optimized model (or your preferred model)
   ollama pull gptoss-agent
   ```

3. **Google Home Device** on the same network

### Dependencies

Install required Python packages:

```bash
pip install rich pychromecast requests psutil
```

Optional (for .env file support):
```bash
pip install python-dotenv
```

## Configuration

Configuration is managed via environment variables or a `.env` file. Priority: environment variables > `.env` file > defaults.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_HOME_DEVICE` | Google Home device name | `Kontor` |
| `OLLAMA_URL` | Ollama API endpoint | `http://localhost:11434/api/chat` |
| `OLLAMA_MODEL` | Ollama model name | `gptoss-agent` |
| `CLI_FPS` | Frames per second for rendering | `20` |
| `CLI_MAX_HISTORY` | Max conversation history entries | `50` |
| `CLI_STREAM_TEXT` | Enable streaming text effect | `true` |
| `CLI_BOOT_SEQUENCE` | Show boot sequence | `true` |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `LOG_FILE` | Log file path | `core.log` |
| `LOG_MAX_BYTES` | Max log file size before rotation | `10485760` (10MB) |
| `LOG_BACKUP_COUNT` | Number of backup log files | `5` |

### Using .env File

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:
   ```bash
   GOOGLE_HOME_DEVICE=Sovrum
   OLLAMA_MODEL=llama2
   CLI_FPS=15
   ```

## Usage

### Running the CLI

```bash
# Method 1: Direct entry point
python cli.py

# Method 2: Module execution
python -m cli.app
```

### Testing Individual Components

```bash
# Test TTS directly
python speak.py "Hej, detta är ett test."

# Test AI brain interactively
python brain.py
```

### Keyboard Controls

- **Enter**: Submit input
- **Arrow Keys**: Navigate input and history
- **Ctrl+C**: Interrupt current operation (first press interrupts, second exits)
- **Ctrl+D**: Exit application
- **Backspace**: Delete character before cursor

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_avatar.py
pytest tests/test_raw_input.py
pytest tests/test_state.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Style

This project follows the Google Python Style Guide:
- 80 character line limit
- 4-space indentation
- Type hints on public functions
- `snake_case` for functions, `PascalCase` for classes
- Docstrings on all public functions

### Project Structure

- `cli/` - CLI application components
- `tests/` - Test suite
- `config.py` - Configuration management
- `brain.py` - Ollama API integration
- `speak.py` - Google Home TTS integration
- `cli.py` - Entry point

## Troubleshooting

### Google Home Device Not Found

1. Ensure device is powered on and connected to the same network
2. Check device name matches `GOOGLE_HOME_DEVICE` setting
3. Verify device appears in Google Home app
4. Try restarting the device

### Ollama Connection Errors

1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Check model is available:
   ```bash
   ollama list
   ```

3. Ensure `OLLAMA_URL` matches your Ollama setup

### Terminal Display Issues

1. Ensure terminal supports Unicode and colors
2. Try increasing terminal size
3. Check `CLI_FPS` setting (lower values may help on slow systems)

### Logging

Logs are written to `core.log` (configurable via `LOG_FILE`). Log rotation is automatic:
- Files rotate when reaching `LOG_MAX_BYTES`
- Keeps `LOG_BACKUP_COUNT` backup files
- Set `LOG_LEVEL=DEBUG` for detailed debugging

## Async + Threading Pattern

The main loop uses `asyncio`, but blocking I/O operations use thread pools:

```python
# Brain queries run in executor
response = await loop.run_in_executor(None, ask_brain, prompt)

# TTS runs in executor
await loop.run_in_executor(None, self.speaker.speak, text)
```

**Important**: Both `speak()` and `ask_brain()` are blocking functions. Never call them directly in the async loop.

## Input Handling

`RawInputHandler` uses `termios` in cbreak mode for character-by-character capture:
- Arrow keys for cursor movement and history navigation
- Escape sequence parsing with buffering for incomplete sequences
- Ctrl+C interrupts current state, second press exits
- Maximum 10,000 character input buffer

## Error Handling

Custom exceptions provide targeted error messages:
- `BrainConnectionError`: Cannot connect to Ollama
- `BrainEmptyResponseError`: Ollama returned empty response
- `DeviceNotFoundError`: Google Home device not found

The application automatically recovers from errors after 5 seconds.

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal UI
- Uses [pychromecast](https://github.com/home-assistant-libs/pychromecast) for Google Home integration
- Powered by [Ollama](https://ollama.ai) for local LLM inference

