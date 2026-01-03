"""NDJSON debug logger for Cursor debug mode.

Writes one JSON object per line to:
  /home/ai-server/google-home-hack/.cursor/debug.log

This module is intentionally tiny and best-effort (never raises).
"""

from __future__ import annotations

import json
import time
from typing import Any, Mapping, Optional


_LOG_PATH = "/home/ai-server/google-home-hack/.cursor/debug.log"
_SESSION_ID = "debug-session"


def log_debug(
    *,
    hypothesis_id: str,
    location: str,
    message: str,
    data: Optional[Mapping[str, Any]] = None,
    run_id: str = "pre-fix",
) -> None:
    """Append one NDJSON debug line (best-effort)."""
    payload = {
        "sessionId": _SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": dict(data or {}),
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        return


