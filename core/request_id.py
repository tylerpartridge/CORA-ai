#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/request_id.py
🎯 PURPOSE: Per-request ID context + middleware for correlation
📤 EXPORTS: request_id_var, get_request_id, install_request_id_middleware
"""

from __future__ import annotations

import contextvars
import uuid
from typing import Optional
from fastapi import FastAPI, Request


# Context variable for request id
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-"
)


def get_request_id() -> str:
    """Return the current request id ("-" if none)."""
    try:
        return request_id_var.get()
    except LookupError:
        return "-"


def install_request_id_middleware(app: FastAPI) -> None:
    """Attach middleware to ensure every request has a request-id.

    - Accept inbound X-Request-ID; otherwise generate uuid4
    - Store in contextvar and echo in X-Request-ID response header
    - If Sentry is available, attach as a scope tag
    """

    @app.middleware("http")
    async def _request_id_mw(request: Request, call_next):  # type: ignore
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        token = request_id_var.set(rid)
        # Attach to Sentry scope if available
        try:
            import sentry_sdk  # type: ignore

            with sentry_sdk.configure_scope() as scope:  # type: ignore
                try:
                    scope.set_tag("request_id", rid)
                except Exception:
                    pass
        except Exception:
            pass

        try:
            response = await call_next(request)
        finally:
            # Ensure context is reset to avoid leakage across tasks
            try:
                request_id_var.reset(token)
            except Exception:
                pass
        try:
            response.headers.setdefault("X-Request-ID", rid)
        except Exception:
            pass
        return response

