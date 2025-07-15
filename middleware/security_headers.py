"""
🧭 LOCATION: /CORA/middleware/security_headers.py
🎯 PURPOSE: Security headers middleware for protection
🔗 IMPORTS: FastAPI, starlette
📤 EXPORTS: setup_security_headers
"""

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-src 'self' https://js.stripe.com https://hooks.stripe.com; "
            "object-src 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Permissions Policy
        permissions = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=*, "
            "usb=()"
        )
        response.headers["Permissions-Policy"] = permissions
        
        return response

def setup_security_headers(app: FastAPI):
    """Setup security headers middleware"""
    app.add_middleware(SecurityHeadersMiddleware)
    return app 