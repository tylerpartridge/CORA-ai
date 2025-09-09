#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/access_log.py
🎯 PURPOSE: Lightweight access log middleware (rid-aware)
📤 EXPORTS: install_access_log_middleware
"""

from __future__ import annotations

import logging
import time
from fastapi import FastAPI, Request


def _client_ip(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if xff:
        return xff
    xr = req.headers.get("x-real-ip")
    if xr:
        return xr
    return req.client.host if req.client else "unknown"


def install_access_log_middleware(app: FastAPI) -> None:
    logger = logging.getLogger("cora.access")

    @app.middleware("http")
    async def _access_mw(request: Request, call_next):  # type: ignore
        t0 = time.perf_counter()
        response = await call_next(request)
        ms = int(round((time.perf_counter() - t0) / 0.001))
        try:
            logger.info(
                "access",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": ms,
                    "user_agent": request.headers.get("user-agent", ""),
                    "client_ip": _client_ip(request),
                },
            )
        except Exception:
            # Never fail request due to logging
            pass
        return response

