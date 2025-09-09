#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/logging_json.py
🎯 PURPOSE: Env-driven structured logging (text by default, JSON opt-in)
📤 EXPORTS: setup_logging()
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone
from typing import Optional

_configured = False


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if v is not None else default


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore
        try:
            message = record.getMessage()
        except Exception:
            message = record.msg if isinstance(record.msg, str) else str(record.msg)

        obj = {
            "time": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "request_id": getattr(record, "request_id", "-"),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "pid": record.process,
        }
        # Optional HTTP fields
        for k in ("method", "path", "status_code", "duration_ms", "user_agent", "client_ip"):
            if hasattr(record, k):
                obj[k] = getattr(record, k)
        return json.dumps(obj, ensure_ascii=False)


def setup_logging() -> None:
    """Configure logging based on env.

    - LOG_FORMAT: "text" (default) | "json"
    - LOG_LEVEL: default INFO
    - LOG_FILE: path (optional, RotatingFileHandler 10MB x5)
    Idempotent: calling multiple times won't duplicate handlers.
    """
    global _configured
    # Only reconfigure when JSON is requested; otherwise leave existing config
    if (_env("LOG_FORMAT", "text").lower() != "json"):
        return
    if _configured:
        return

    level_name = _env("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    # Clear existing handlers to avoid mixed formats
    for h in list(root.handlers):
        root.removeHandler(h)

    formatter = JSONFormatter()

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Optional file handler
    log_file = _env("LOG_FILE")
    if log_file:
        try:
            d = os.path.dirname(log_file)
            if d:
                os.makedirs(d, exist_ok=True)
        except Exception:
            pass
        fh = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        fh.setLevel(level)
        fh.setFormatter(formatter)
        root.addHandler(fh)

    # Align uvicorn loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True
        lg.setLevel(level)

    _configured = True
