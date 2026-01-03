import requests
import json
import sys
import os
import time
import logging
import importlib.util
from collections import deque
from typing import Any
import threading

import debug_ndjson

# Ensure we import the ROOT config.py (not dashboard/config.py)
_brain_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_brain_dir, "config.py")
_spec = importlib.util.spec_from_file_location("root_config", _config_path)
config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(config)

logger = logging.getLogger(__name__)

_PERF_LOCK = threading.Lock()
_PERF_HISTORY: deque[dict[str, Any]] = deque(maxlen=50)


def get_recent_perf(n: int = 3) -> list[dict[str, Any]]:
    """Return the most recent brain call timings (newest last)."""
    if n <= 0:
        return []
    with _PERF_LOCK:
        return list(_PERF_HISTORY)[-n:]


class BrainConnectionError(Exception):
    """Raised when unable to connect to Ollama service."""
    pass


class BrainEmptyResponseError(Exception):
    """Raised when Ollama returns an empty response."""
    pass

def ask_brain(prompt):
    """Query the AI brain via Ollama.
    
    Args:
        prompt: User's prompt/question.
    
    Returns:
        AI response string. Raises exceptions on error (no print statements).
    """
    # Vi ändrar prompten lite för att säkra att den faktiskt pratar
    system_prompt = (
        "Du är 'GPT', en skön AI-assistent. "
        "Svara direkt till användaren. "
        "Håll svaret kort och koncist (max 2 meningar). "
        "Svara på svenska."
    )

    # Keep responses short-ish to avoid timeouts and TTS length issues, but note
    # that gpt-oss may emit a large "thinking" field that also consumes tokens.
    # Allow override via env vars for experiments.
    try:
        num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", "256"))
    except ValueError:
        num_predict = 256
    if num_predict < 32:
        num_predict = 32

    try:
        temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
    except ValueError:
        temperature = 0.2
    if temperature < 0.0:
        temperature = 0.0
    if temperature > 2.0:
        temperature = 2.0

    try:
        timeout_s = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
    except ValueError:
        timeout_s = 60.0

    # region agent log
    debug_ndjson.log_debug(
        hypothesis_id="H3",
        location="brain.py:ask_brain",
        message="ask_brain entry",
        data={
            "pid": os.getpid(),
            "thread": threading.get_ident(),
            "model": config.get_model_name(),
            "prompt_len": len(prompt),
            "num_predict": num_predict,
            "temperature": temperature,
            "timeout_s": timeout_s,
        },
    )
    # endregion agent log

    def _build_payload(*, temperature: float, predict: int, include_stop: bool) -> dict[str, Any]:
        options: dict[str, Any] = {
            "temperature": temperature,
            "num_predict": predict,
        }
        # Stop tokens can cause rare "empty reply" if the model starts with one.
        # Keep a conservative default and allow retry without stop tokens.
        if include_stop:
            options["stop"] = ["\nUser:"]

        return {
            "model": config.get_model_name(),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": options,
        }

    payload = _build_payload(temperature=temperature, predict=num_predict, include_stop=True)

    ollama_url = config.get_ollama_url()
    model_name = config.get_model_name()
    
    logger.debug("Querying Ollama", extra={
        "model": model_name,
        "prompt_length": len(prompt),
        "url": ollama_url
    })
    
    t0 = time.perf_counter()
    try:
        response = requests.post(ollama_url, json=payload, timeout=timeout_s)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        dt = time.perf_counter() - t0
        with _PERF_LOCK:
            _PERF_HISTORY.append(
                {
                    "ts": time.time(),
                    "duration_s": round(dt, 3),
                    "prompt_len": len(prompt),
                    "response_len": 0,
                    "model": model_name,
                    "error": "connection_error",
                }
            )
        logger.error("Cannot connect to Ollama", extra={"url": ollama_url, "error": str(e)})
        # region agent log
        debug_ndjson.log_debug(
            hypothesis_id="H3",
            location="brain.py:ask_brain",
            message="request connection_error",
            data={"duration_s": round(dt, 3), "prompt_len": len(prompt)},
        )
        # endregion agent log
        raise BrainConnectionError(f"Cannot connect to Ollama at {ollama_url}") from e
    except requests.exceptions.Timeout as e:
        dt = time.perf_counter() - t0
        with _PERF_LOCK:
            _PERF_HISTORY.append(
                {
                    "ts": time.time(),
                    "duration_s": round(dt, 3),
                    "prompt_len": len(prompt),
                    "response_len": 0,
                    "model": model_name,
                    "error": "timeout",
                }
            )
        logger.error("Ollama request timed out", extra={"url": ollama_url})
        # region agent log
        debug_ndjson.log_debug(
            hypothesis_id="H3",
            location="brain.py:ask_brain",
            message="request timeout",
            data={
                "duration_s": round(dt, 3),
                "timeout_s": timeout_s,
                "prompt_len": len(prompt),
                "attempt": "first",
            },
        )
        # endregion agent log
        raise BrainConnectionError("Ollama request timed out") from e
    except requests.exceptions.RequestException as e:
        dt = time.perf_counter() - t0
        with _PERF_LOCK:
            _PERF_HISTORY.append(
                {
                    "ts": time.time(),
                    "duration_s": round(dt, 3),
                    "prompt_len": len(prompt),
                    "response_len": 0,
                    "model": model_name,
                    "error": "request_error",
                }
            )
        logger.error("Ollama request failed", extra={"url": ollama_url, "error": str(e)})
        # region agent log
        debug_ndjson.log_debug(
            hypothesis_id="H3",
            location="brain.py:ask_brain",
            message="request_error",
            data={"duration_s": round(dt, 3), "prompt_len": len(prompt)},
        )
        # endregion agent log
        raise BrainConnectionError(f"Ollama request failed: {e}") from e
    
    data = response.json()
    ai_reply = (data.get("message", {}) or {}).get("content", "") or ""
    ai_reply = ai_reply.strip()
    thinking = ((data.get("message", {}) or {}).get("thinking", "") or "").strip()

    dt = time.perf_counter() - t0

    # region agent log
    debug_ndjson.log_debug(
        hypothesis_id="H3",
        location="brain.py:ask_brain",
        message="ask_brain response parsed",
        data={
            "done_reason": data.get("done_reason"),
            "content_len": len(ai_reply),
            "thinking_len": len(thinking),
            "duration_s": round(dt, 3),
        },
    )
    # endregion agent log
    
    if not ai_reply:
        try:
            data_preview = json.dumps(data, ensure_ascii=False)[:800]
        except Exception:
            data_preview = str(data)[:800]
        with _PERF_LOCK:
            _PERF_HISTORY.append(
                {
                    "ts": time.time(),
                    "duration_s": round(dt, 3),
                    "prompt_len": len(prompt),
                    "response_len": 0,
                    "model": model_name,
                    "error": "empty_response",
                }
            )
        logger.warning("Empty response from Ollama")  # keep terminal clean

        # region agent log
        debug_ndjson.log_debug(
            hypothesis_id="H3",
            location="brain.py:ask_brain",
            message="empty content -> retry",
            data={
                "done_reason": data.get("done_reason"),
                "thinking_len": len(thinking),
                "retry_predict": max(num_predict, 512),
            },
        )
        # endregion agent log

        # Retry once without stop tokens + lower temperature.
        retry_payload = _build_payload(
            # Lower temperature reduces runaway "thinking", higher predict gives it
            # room to actually produce message.content.
            temperature=min(temperature, 0.2),
            predict=max(num_predict, 512),
            include_stop=False,
        )
        t1 = time.perf_counter()
        try:
            retry_resp = requests.post(ollama_url, json=retry_payload, timeout=timeout_s)
            retry_resp.raise_for_status()
            retry_data = retry_resp.json()
            retry_reply = ((retry_data.get("message", {}) or {}).get("content", "") or "").strip()
        except requests.exceptions.Timeout as e:
            dt2 = time.perf_counter() - t1
            with _PERF_LOCK:
                _PERF_HISTORY.append(
                    {
                        "ts": time.time(),
                        "duration_s": round(dt2, 3),
                        "prompt_len": len(prompt),
                        "response_len": 0,
                        "model": model_name,
                        "error": "timeout",
                    }
                )
            # region agent log
            debug_ndjson.log_debug(
                hypothesis_id="H3",
                location="brain.py:ask_brain",
                message="retry timeout",
                data={
                    "duration_s": round(dt2, 3),
                    "timeout_s": timeout_s,
                    "prompt_len": len(prompt),
                    "attempt": "retry",
                },
            )
            # endregion agent log
            raise BrainConnectionError("Ollama request timed out") from e
        except requests.exceptions.RequestException as e:
            dt2 = time.perf_counter() - t1
            with _PERF_LOCK:
                _PERF_HISTORY.append(
                    {
                        "ts": time.time(),
                        "duration_s": round(dt2, 3),
                        "prompt_len": len(prompt),
                        "response_len": 0,
                        "model": model_name,
                        "error": "request_error",
                    }
                )
            raise BrainConnectionError(f"Ollama request failed: {e}") from e

        dt2 = time.perf_counter() - t1
        # region agent log
        debug_ndjson.log_debug(
            hypothesis_id="H3",
            location="brain.py:ask_brain",
            message="retry parsed",
            data={
                "duration_s": round(dt2, 3),
                "retry_content_len": len(retry_reply),
                "retry_done_reason": retry_data.get("done_reason"),
            },
        )
        # endregion agent log
        if not retry_reply:
            with _PERF_LOCK:
                _PERF_HISTORY.append(
                    {
                        "ts": time.time(),
                        "duration_s": round(dt2, 3),
                        "prompt_len": len(prompt),
                        "response_len": 0,
                        "model": model_name,
                        "error": "empty_response",
                    }
                )
            raise BrainEmptyResponseError("Model returned empty response")

        # Success on retry.
        with _PERF_LOCK:
            _PERF_HISTORY.append(
                {
                    "ts": time.time(),
                    "duration_s": round(dt2, 3),
                    "prompt_len": len(prompt),
                    "response_len": len(retry_reply),
                    "model": model_name,
                    "error": None,
                }
            )
        # region agent log
        debug_ndjson.log_debug(
            hypothesis_id="H3",
            location="brain.py:ask_brain",
            message="returning retry content",
            data={"content_len": len(retry_reply)},
        )
        # endregion agent log
        return retry_reply
    
    with _PERF_LOCK:
        _PERF_HISTORY.append(
            {
                "ts": time.time(),
                "duration_s": round(dt, 3),
                "prompt_len": len(prompt),
                "response_len": len(ai_reply),
                "model": model_name,
                "error": None,
            }
        )

    logger.info("Received response from Ollama", extra={
        "model": model_name,
        "response_length": len(ai_reply)
    })

    # region agent log
    debug_ndjson.log_debug(
        hypothesis_id="H3",
        location="brain.py:ask_brain",
        message="returning primary content",
        data={"content_len": len(ai_reply)},
    )
    # endregion agent log
    
    return ai_reply


class Brain:
    """Lightweight wrapper exposing generate(prompt) for dashboard/CLI."""

    def __init__(self) -> None:
        self.model_name = config.get_model_name()
        self.ollama_url = config.get_ollama_url()

    def generate(self, prompt: str) -> str:
        return ask_brain(prompt)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(ask_brain(user_input))
    else:
        print("--- INTERAKTIVT LÄGE (Skriv 'exit' för att sluta) ---")
        print("Kanalen är öppen. Vad vill du?")
        while True:
            try:
                user_input = input("Du: ")
                if user_input.lower() in ["exit", "sluta", "quit"]:
                    break
                if user_input.strip() == "":
                    continue
                reply = ask_brain(user_input)
                print(f"AI: {reply}")
            except KeyboardInterrupt:
                print("\nStänger ner.")
                break
            except BrainConnectionError as e:
                print(f"⚠️  Nätverksfel: {e}")
            except BrainEmptyResponseError as e:
                print(f"⚠️  Varning: {e}")
            except Exception as e:
                print(f"⚠️  Ett fel inträffade: {e}")