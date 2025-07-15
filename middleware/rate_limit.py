#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/rate_limit.py
🎯 PURPOSE: Rate limiting middleware to prevent abuse
🔗 IMPORTS: FastAPI, slowapi
📤 EXPORTS: rate_limiter, get_remote_address
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import os

# Get rate limit from environment or use defaults
RATE_LIMIT = os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100/minute")

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT],
    storage_uri="memory://",
    headers_enabled=True  # Include rate limit headers in responses
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
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
    app.add_exception_handler(ValueError, custom_rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    return limiter