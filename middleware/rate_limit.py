#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/rate_limit.py
🎯 PURPOSE: Rate limiting middleware to prevent abuse
🔗 IMPORTS: FastAPI, slowapi
📤 EXPORTS: rate_limiter, get_remote_address
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import os


def client_ip(request: Request) -> str:
    """Best-effort client IP extraction honoring X-Forwarded-For."""
    xff = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if xff:
        return xff
    xr = request.headers.get("x-real-ip")
    if xr:
        return xr
    return request.client.host if request.client else "unknown"


DEFAULT_LIMIT = (
    os.getenv("RATE_LIMIT_DEFAULT")
    or os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE")
    or "200/minute"
)

_redis_url = os.getenv("REDIS_URL") or os.getenv("CORA_REDIS_URL")
_storage_uri = _redis_url if _redis_url else "memory://"

# Create limiter instance (falls back to memory when Redis not configured)
limiter = Limiter(
    key_func=client_ip,
    default_limits=[DEFAULT_LIMIT],
    storage_uri=_storage_uri,
    headers_enabled=True,
)

def custom_rate_limit_handler(request: Request, exc: Exception):
    """Custom rate limit exception handler that handles various exception types"""
    if hasattr(exc, 'detail'):
        message = exc.detail
    elif hasattr(exc, 'args') and exc.args:
        message = str(exc.args[0])
    else:
        message = "Rate limit exceeded"
    
    return JSONResponse(
        status_code=429,
        content={"error": f"Rate limit exceeded: {message}"},
        headers={
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "0"
        }
    )

def setup_rate_limiting(app):
    """Setup rate limiting for the FastAPI app"""
    # Add SlowAPI middleware
    app.state.limiter = limiter
    # Use robust custom handler (avoids assuming exc.detail exists on all exceptions)
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    return limiter
