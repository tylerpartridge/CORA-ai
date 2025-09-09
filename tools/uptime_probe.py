#!/usr/bin/env python3
"""
Minimal uptime probe: pings /health (or /ping) and /api/status.
Appends a line to logs/cora_uptime_probe.log and prints it.
Always exits 0 to keep schedulers quiet.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def http_code(url: str, timeout: float = 5.0) -> int:
    try:
        req = Request(url, headers={"User-Agent": "cora-uptime-probe/1"})
        with urlopen(req, timeout=timeout) as resp:
            return getattr(resp, "status", 200)
    except HTTPError as e:
        return int(getattr(e, "code", 0) or 0)
    except URLError:
        return 0
    except Exception:
        return 0


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    base = os.getenv("BASE", "http://127.0.0.1:8000").rstrip("/")

    # Health: prefer /health; if 404, try /ping
    h_code = http_code(f"{base}/health")
    if h_code == 404:
        h_code = http_code(f"{base}/ping")

    # Status: map 404 to 000, keep other codes
    s_code = http_code(f"{base}/api/status")
    if s_code == 404:
        s_code = 0

    line = f"{now_iso()} health={h_code:03d} status={s_code:03d}"

    # Append to logs/cora_uptime_probe.log
    try:
        logs_dir = Path(__file__).resolve().parents[1] / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "cora_uptime_probe.log"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # Ignore file errors; still print to stdout
        pass

    print(line)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Never raise to scheduler
        print(f"{now_iso()} health=000 status=000")
        sys.exit(0)

