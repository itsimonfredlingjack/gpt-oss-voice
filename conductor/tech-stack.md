# Tech Stack: The Core CLI

## Core Technologies
- **Programming Language:** Python 3.10+
- **UI & Terminal Rendering:** [Rich](https://github.com/Textualize/rich) (using `Layout`, `Live`, `Panel`, and `Theme` for the terminal interface).
- **AI Integration:** [Ollama](https://ollama.ai/) (Local LLM server running `gptoss-agent`).
- **Audio Output:** [PyChromecast](https://github.com/home-assistant-libs/pychromecast) (Streaming TTS to Google Home/Nest devices).
- **System Monitoring:** [psutil](https://github.com/giampaolo/psutil) (For hardware resource data).

## Libraries & Dependencies
- `requests`: For communicating with the Ollama API.
- `threading`: To handle non-blocking audio playback and UI animations.
- `pychromecast`: For discovery and control of Google Cast devices.

## Architecture
- **Threaded UI:** A main execution loop handles user input and `rich.live` rendering, while a background thread manages the blocking `speak()` calls.
- **State-Driven Animation:** UI components (`AIAvatar`, `Waveform`) update their visual state based on a global `is_speaking` flag.
- **Modular Design:** Integration with existing `brain.py` and `speak.py` modules.
