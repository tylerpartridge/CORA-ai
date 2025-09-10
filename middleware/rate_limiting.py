#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/rate_limiting.py
🎯 PURPOSE: Rate limiting middleware to prevent abuse and brute force attacks
🔗 IMPORTS: FastAPI, time, collections
📤 EXPORTS: setup_rate_limiting, RateLimiter
"""

from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
import time
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple
import os
from utils.redis_manager import redis_manager

class RateLimiter:
    """Rate limiter implementation using Redis for persistence"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def _redis_key(self, key: str) -> str:
        return f"ratelimit:{key}"
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key using Redis"""
        redis_key = self._redis_key(key)
        current_count = redis_manager.get(redis_key)
        if current_count is None:
            # First request, set with expiry
            redis_manager.set(redis_key, "1", self.window_seconds)
            return True
        else:
            count = int(current_count)
            if count >= self.max_requests:
                return False
            else:
                redis_manager.set(redis_key, str(count + 1), self.window_seconds)
                return True
    
    def get_remaining(self, key: str) -> int:
        redis_key = self._redis_key(key)
        current_count = redis_manager.get(redis_key)
        if current_count is None:
            return self.max_requests
        return max(0, self.max_requests - int(current_count))
    
    def get_reset_time(self, key: str) -> float:
        redis_key = self._redis_key(key)
        # Redis TTL returns seconds until expiry; NullRedis has no ttl
        client = getattr(redis_manager, "redis_client", None)
        if client is None or not hasattr(client, "ttl"):
            return time.time() + self.window_seconds
        ttl = client.ttl(redis_key)
        if ttl is None or ttl < 0:
            return time.time() + self.window_seconds
        return time.time() + ttl

# Rate limit configurations
RATE_LIMITS = {
    # General API endpoints
    "default": RateLimiter(max_requests=100, window_seconds=60),  # 100 requests per minute
    
    # Authentication endpoints (stricter)
    "auth": RateLimiter(max_requests=5, window_seconds=300),  # 5 attempts per 5 minutes
    
    # Login attempts (very strict)
    "login": RateLimiter(max_requests=3, window_seconds=300),  # 3 attempts per 5 minutes
    
    # Password reset (strict)
    "password_reset": RateLimiter(max_requests=2, window_seconds=3600),  # 2 attempts per hour
    
    # File uploads
    "file_upload": RateLimiter(max_requests=10, window_seconds=60),  # 10 uploads per minute
    
    # Admin endpoints (moderate)
    "admin": RateLimiter(max_requests=50, window_seconds=60),  # 50 requests per minute
}

def get_client_ip(request: Request) -> str:
    """Get client IP address, handling proxies"""
    # Check for forwarded headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def get_rate_limit_key(request: Request) -> Tuple[str, str]:
    """Get rate limit key and type for the request"""
    path = request.url.path
    client_ip = get_client_ip(request)
    
    # Get user email if authenticated
    user_email = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            from dependencies.auth import decode_token
            token = auth_header.split(" ")[1]
            user_data = decode_token(token)
            user_email = user_data.get("sub")
        except Exception:
            pass
    
    # Determine rate limit type based on endpoint
    if path.startswith("/api/auth/login"):
        rate_limit_type = "login"
    elif path.startswith("/api/auth/register"):
        rate_limit_type = "auth"
    elif path.startswith("/api/auth/password-reset"):
        rate_limit_type = "password_reset"
    elif path.startswith("/api/admin"):
        rate_limit_type = "admin"
    elif path.startswith("/api/upload") or "upload" in path:
        rate_limit_type = "file_upload"
    else:
        rate_limit_type = "default"
    
    # Create unique key
    if user_email:
        key = f"{rate_limit_type}:{user_email}"
    else:
        key = f"{rate_limit_type}:{client_ip}"
    
    return key, rate_limit_type

async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Skip rate limiting for static files and core health/ops endpoints
    if (
        request.url.path.startswith("/static/")
        or request.url.path in {"/health", "/api/health", "/ping", "/metrics", "/smoke"}
        or request.url.path.startswith("/health/")
    ):
        response = await call_next(request)
        return response
    
    # Get rate limit key and type
    key, rate_limit_type = get_rate_limit_key(request)
    rate_limiter = RATE_LIMITS.get(rate_limit_type, RATE_LIMITS["default"])
    
    # Check if request is allowed
    if not rate_limiter.is_allowed(key):
        remaining_time = rate_limiter.get_reset_time(key) - time.time()
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again in {int(remaining_time)} seconds.",
                "retry_after": int(remaining_time)
            },
            headers={
                "Retry-After": str(int(remaining_time)),
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(rate_limiter.get_reset_time(key)))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    
    remaining = rate_limiter.get_remaining(key)
    reset_time = rate_limiter.get_reset_time(key)
    
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(reset_time))
    
    return response

def setup_rate_limiting(app):
    """Setup rate limiting for the FastAPI app"""
    app.middleware("http")(rate_limiting_middleware)
    
    @app.get("/api/rate-limit/status")
    async def get_rate_limit_status(request: Request):
        """Get current rate limit status for the user"""
        key, rate_limit_type = get_rate_limit_key(request)
        rate_limiter = RATE_LIMITS.get(rate_limit_type, RATE_LIMITS["default"])
        
        return {
            "rate_limit_type": rate_limit_type,
            "max_requests": rate_limiter.max_requests,
            "window_seconds": rate_limiter.window_seconds,
            "remaining": rate_limiter.get_remaining(key),
            "reset_time": int(rate_limiter.get_reset_time(key))
        }

# Cleanup function to prevent memory leaks
def cleanup_old_requests():
    """Clean up old rate limit data"""
    now = time.time()
    
    for rate_limiter in RATE_LIMITS.values():
        for key in list(rate_limiter.requests.keys()):
            # Remove requests older than 2x window size
            while (rate_limiter.requests[key] and 
                   rate_limiter.requests[key][0] < now - (rate_limiter.window_seconds * 2)):
                rate_limiter.requests[key].popleft()
            
            # Remove empty entries
            if not rate_limiter.requests[key]:
                del rate_limiter.requests[key] 