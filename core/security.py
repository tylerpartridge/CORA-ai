#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/security.py
🎯 PURPOSE: Build CORS/hosts config from env and attach simple security headers
📤 EXPORTS: build_cors_config_from_env, build_trusted_hosts_from_env, security_headers_middleware
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional
from fastapi import FastAPI, Request


def _split_csv(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


def build_cors_config_from_env() -> Optional[Dict]:
    """Return CORS config dict or None if disabled.

    Keys: origins, methods, headers, credentials
    """
    if not _env_bool("CORS_ENABLED", False):
        return None

    origins = _split_csv(os.getenv("CORS_ORIGINS", ""))
    if not origins:
        origins = [
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        ]

    methods = _split_csv(os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS"))
    headers = _split_csv(os.getenv("CORS_HEADERS", "*") or "*")
    credentials = _env_bool("CORS_CREDENTIALS", False)

    return {
        "origins": origins,
        "methods": methods,
        "headers": headers,
        "credentials": credentials,
    }


def build_trusted_hosts_from_env() -> List[str]:
    hosts = _split_csv(os.getenv("TRUSTED_HOSTS", ""))
    return hosts


def security_headers_middleware(app: FastAPI) -> None:
    """Attach minimal security headers to every response.

    - X-Frame-Options: DENY
    - X-Content-Type-Options: nosniff
    - Referrer-Policy: no-referrer
    - Strict-Transport-Security only when HTTPS
    """

    @app.middleware("http")
    async def _security_headers(request: Request, call_next):  # type: ignore
        response = await call_next(request)
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        try:
            if request.url.scheme == "https":
                response.headers.setdefault(
                    "Strict-Transport-Security",
                    "max-age=31536000; includeSubDomains; preload",
                )
        except Exception:
            pass
        return response

