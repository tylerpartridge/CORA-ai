"""
Rate limiting middleware for CORA
Prevents abuse and DDoS attacks
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 600):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_buckets = defaultdict(list)
        self.hour_buckets = defaultdict(list)
        self.blocked_ips = set()
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, identifier: str) -> Tuple[bool, str]:
        """Check if request is allowed"""
        async with self.lock:
            now = datetime.now()
            
            # Check if IP is blocked
            if identifier in self.blocked_ips:
                return False, "IP temporarily blocked due to rate limit violations"
            
            # Clean old entries
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            # Clean minute bucket
            self.minute_buckets[identifier] = [
                timestamp for timestamp in self.minute_buckets[identifier]
                if timestamp > minute_ago
            ]
            
            # Clean hour bucket
            self.hour_buckets[identifier] = [
                timestamp for timestamp in self.hour_buckets[identifier]
                if timestamp > hour_ago
            ]
            
            # Check minute limit
            if len(self.minute_buckets[identifier]) >= self.requests_per_minute:
                # In development, do not block; just return a soft limit message
                return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
            
            # Check hour limit
            if len(self.hour_buckets[identifier]) >= self.requests_per_hour:
                # In development, do not block; just return a soft limit message
                return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
            
            # Add current request
            self.minute_buckets[identifier].append(now)
            self.hour_buckets[identifier].append(now)
            
            return True, ""
    
    async def _unblock_after_delay(self, identifier: str, delay: int):
        """Unblock IP after delay"""
        await asyncio.sleep(delay)
        self.blocked_ips.discard(identifier)
        logger.info(f"Unblocked IP: {identifier}")

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        # Different limits for different endpoints
        self.api_limiter = RateLimiter(requests_per_minute=300, requests_per_hour=3000)
        self.auth_limiter = RateLimiter(requests_per_minute=100, requests_per_hour=1000)
        self.public_limiter = RateLimiter(requests_per_minute=600, requests_per_hour=6000)
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_ip = request.client.host
        path = request.url.path
        
        # Skip rate limiting for static files
        if path.startswith("/static/") or path.startswith("/favicon"):
            return await call_next(request)
        
        # Determine which limiter to use
        if path.startswith("/api/auth") or path.startswith("/login") or path.startswith("/signup"):
            limiter = self.auth_limiter
        elif path.startswith("/api/"):
            limiter = self.api_limiter
        else:
            limiter = self.public_limiter
        
        # Check rate limit
        allowed, message = await limiter.is_allowed(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_ip} on {path}: {message}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": message,
                    "retry_after": "60"
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(limiter.requests_per_minute),
                    "X-RateLimit-Reset": str(int((datetime.now() + timedelta(minutes=1)).timestamp()))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            limiter.requests_per_minute - len(limiter.minute_buckets[client_ip])
        )
        
        return response