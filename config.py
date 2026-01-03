"""Configuration management for Google Home Hack.

Loads configuration from environment variables, .env file, and defaults.
Priority: environment variables > .env file > defaults.
"""

import os
from typing import Optional
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    _dotenv_available = True
except ImportError:
    _dotenv_available = False

# Load .env file if available
if _dotenv_available:
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)


def get_str(key: str, default: str) -> str:
    """Get string configuration value.
    
    Args:
        key: Environment variable name.
        default: Default value if not found.
    
    Returns:
        Configuration value as string.
    """
    return os.getenv(key, default)


def get_int(key: str, default: int) -> int:
    """Get integer configuration value.
    
    Args:
        key: Environment variable name.
        default: Default value if not found.
    
    Returns:
        Configuration value as integer.
    """
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_float(key: str, default: float) -> float:
    """Get float configuration value.
    
    Args:
        key: Environment variable name.
        default: Default value if not found.
    
    Returns:
        Configuration value as float.
    """
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def get_bool(key: str, default: bool) -> bool:
    """Get boolean configuration value.
    
    Args:
        key: Environment variable name.
        default: Default value if not found.
    
    Returns:
        Configuration value as boolean.
    """
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


# --- Google Home Configuration ---

def get_device_name() -> str:
    """Get Google Home device name.
    
    Returns:
        Device name (default: "Kontor").
    """
    return get_str('GOOGLE_HOME_DEVICE', 'Kontor')


# --- Ollama Configuration ---

def get_ollama_url() -> str:
    """Get Ollama API URL.
    
    Returns:
        Ollama URL (default: "http://localhost:11434/api/chat").
    """
    return get_str('OLLAMA_URL', 'http://localhost:11434/api/chat')


def get_model_name() -> str:
    """Get Ollama model name.
    
    Returns:
        Model name (default: "gptoss-agent").
    """
    return get_str('OLLAMA_MODEL', 'gptoss-agent')


# --- CLI Configuration ---

def get_fps() -> int:
    """Get frames per second for CLI rendering.
    
    Returns:
        FPS (default: 20).
    """
    return get_int('CLI_FPS', 20)


def get_max_history() -> int:
    """Get maximum conversation history size.
    
    Returns:
        Max history entries (default: 50).
    """
    return get_int('CLI_MAX_HISTORY', 50)


def get_stream_text() -> bool:
    """Get whether to stream text output.
    
    Returns:
        Stream text flag (default: True).
    """
    return get_bool('CLI_STREAM_TEXT', True)


def get_boot_sequence() -> bool:
    """Get whether to show boot sequence.
    
    Returns:
        Boot sequence flag (default: True).
    """
    return get_bool('CLI_BOOT_SEQUENCE', True)


def get_log_level() -> str:
    """Get logging level.
    
    Returns:
        Log level (default: "INFO").
    """
    return get_str('LOG_LEVEL', 'INFO').upper()


def get_log_file() -> str:
    """Get log file path.
    
    Returns:
        Log file path (default: "core.log").
    """
    return get_str('LOG_FILE', 'core.log')


def get_log_max_bytes() -> int:
    """Get maximum log file size in bytes.
    
    Returns:
        Max bytes (default: 10485760 = 10MB).
    """
    return get_int('LOG_MAX_BYTES', 10485760)


def get_log_backup_count() -> int:
    """Get number of log backup files to keep.
    
    Returns:
        Backup count (default: 5).
    """
    return get_int('LOG_BACKUP_COUNT', 5)

