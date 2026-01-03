from __future__ import annotations

import os
import socket
import time
from datetime import datetime, timezone
from typing import Any, Optional


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _try_import_psutil():
    try:
        import psutil  # type: ignore

        return psutil
    except Exception:
        return None


def _bytes_to_gib(value: Optional[int]) -> Optional[float]:
    if value is None:
        return None
    return round(value / (1024**3), 2)


def _load_meminfo() -> dict[str, int]:
    info: dict[str, int] = {}
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) != 2:
                    continue
                key = parts[0].strip()
                rest = parts[1].strip().split()
                if not rest:
                    continue
                # meminfo reports kB
                try:
                    info[key] = int(rest[0]) * 1024
                except ValueError:
                    continue
    except Exception:
        pass
    return info


def _read_uptime_seconds() -> Optional[float]:
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            return float(f.read().split()[0])
    except Exception:
        return None


def _get_primary_ip() -> Optional[str]:
    # Best-effort: connect UDP socket to a public IP without sending data.
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        return None


def get_system_status() -> dict[str, Any]:
    """
    Return lightweight CPU/RAM status for the top HUD bar.
    Never throws; always returns a dict.
    """
    psutil = _try_import_psutil()

    hostname = None
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = None

    ip = _get_primary_ip()

    cpu_percent: Optional[float] = None
    cpu_cores: Optional[int] = None
    load_1m: Optional[float] = None
    try:
        load_1m = os.getloadavg()[0]
    except Exception:
        load_1m = None

    mem_total: Optional[int] = None
    mem_used: Optional[int] = None
    mem_available: Optional[int] = None
    mem_percent: Optional[float] = None

    uptime_s = _read_uptime_seconds()

    if psutil is not None:
        try:
            cpu_percent = float(psutil.cpu_percent(interval=0.1))
        except Exception:
            cpu_percent = None
        try:
            cpu_cores = int(psutil.cpu_count() or 0) or None
        except Exception:
            cpu_cores = None
        try:
            vm = psutil.virtual_memory()
            mem_total = int(vm.total)
            mem_used = int(vm.used)
            mem_available = int(vm.available)
            mem_percent = float(vm.percent)
        except Exception:
            pass
    else:
        meminfo = _load_meminfo()
        mem_total = meminfo.get("MemTotal")
        mem_available = meminfo.get("MemAvailable")
        if mem_total is not None and mem_available is not None:
            mem_used = mem_total - mem_available
            mem_percent = round((mem_used / mem_total) * 100, 1) if mem_total else None

    return {
        "ts": _iso_now(),
        "hostname": hostname,
        "ip": ip,
        "uptime_s": uptime_s,
        "cpu": {
            "percent": cpu_percent,
            "cores": cpu_cores,
            "load_1m": load_1m,
        },
        "memory": {
            "total_bytes": mem_total,
            "used_bytes": mem_used,
            "available_bytes": mem_available,
            "percent": mem_percent,
            "total_gib": _bytes_to_gib(mem_total),
            "used_gib": _bytes_to_gib(mem_used),
        },
    }


