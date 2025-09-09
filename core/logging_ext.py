#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/logging_ext.py
🎯 PURPOSE: Logging filter to inject request_id from contextvars
📤 EXPORTS: RequestIdFilter, attach_request_id_filter()
"""

from __future__ import annotations

import logging
from typing import Optional
from core.request_id import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore
        try:
            record.request_id = get_request_id()
        except Exception:
            record.request_id = "-"
        return True


def attach_request_id_filter() -> None:
    """Attach filter to all root handlers and ensure format contains request_id.

    If a handler formatter is present and does not reference %(request_id)s,
    wrap it with a new formatter that appends " [rid=%(request_id)s]".
    """
    root = logging.getLogger()
    f = RequestIdFilter()
    for h in list(root.handlers):
        try:
            h.addFilter(f)
            fmt = getattr(h.formatter, "_fmt", None) if h.formatter else None
            datefmt = getattr(h.formatter, "datefmt", None) if h.formatter else None
            FormatterCls = h.formatter.__class__ if h.formatter else logging.Formatter
            if fmt and "%(request_id)" not in fmt:
                new_fmt = f"{fmt} [rid=%(request_id)s]"
                h.setFormatter(FormatterCls(new_fmt, datefmt=datefmt))
            elif not fmt:
                h.setFormatter(FormatterCls("%(asctime)s - %(levelname)s - %(message)s [rid=%(request_id)s]"))
        except Exception:
            # Do not interfere with logging if handler is unusual
            pass

