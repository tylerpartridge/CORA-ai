"""
Enhanced CSRF Protection Middleware
Protects all state-changing operations from CSRF attacks
"""

import secrets
import time
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import hashlib
import hmac
import os

# CSRF Configuration
CSRF_SECRET = os.getenv("CSRF_SECRET", secrets.token_hex(32))
CSRF_TOKEN_LENGTH = 32
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_TOKEN_EXPIRY = 3600 * 4  # 4 hours

# Endpoints that don't require CSRF protection
CSRF_EXEMPT_PATHS = {
    "/api/health",
    "/api/metrics",
    "/api/docs",
    "/api/openapi.json",
    "/api/redoc",
}

# Methods that require CSRF protection
CSRF_PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


class CSRFProtection:
    """Enhanced CSRF protection with double-submit cookie pattern"""
    
    @staticmethod
    def generate_token(session_id: str = None) -> str:
        """Generate a CSRF token tied to session"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_hex(16)
        
        if session_id:
            # Tie token to session for extra security
            data = f"{session_id}:{timestamp}:{random_part}"
        else:
            data = f"{timestamp}:{random_part}"
            
        # Create HMAC signature
        signature = hmac.new(
            CSRF_SECRET.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        return f"{data}:{signature}"
    
    @staticmethod
    def validate_token(token: str, session_id: str = None) -> bool:
        """Validate CSRF token"""
        try:
            parts = token.split(":")
            if len(parts) < 3:
                return False
                
            # Extract timestamp
            if session_id:
                if len(parts) != 4:
                    return False
                provided_session, timestamp_str, random_part, signature = parts
                if provided_session != session_id:
                    return False
                data = f"{provided_session}:{timestamp_str}:{random_part}"
            else:
                if len(parts) != 3:
                    return False
                timestamp_str, random_part, signature = parts
                data = f"{timestamp_str}:{random_part}"
            
            # Check token expiry
            timestamp = int(timestamp_str)
            if time.time() - timestamp > CSRF_TOKEN_EXPIRY:
                return False
            
            # Verify signature
            expected_signature = hmac.new(
                CSRF_SECRET.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()[:16]
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, AttributeError):
            return False


async def csrf_middleware(request: Request, call_next):
    """Enhanced CSRF protection middleware"""
    
    # Skip CSRF for exempt paths
    if request.url.path in CSRF_EXEMPT_PATHS:
        return await call_next(request)
    
    # Skip CSRF for safe methods (GET, HEAD, OPTIONS)
    if request.method not in CSRF_PROTECTED_METHODS:
        # For GET requests, ensure CSRF cookie is set
        response = await call_next(request)
        
        # Set CSRF cookie if not present
        if CSRF_COOKIE_NAME not in request.cookies:
            token = CSRFProtection.generate_token()
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=token,
                httponly=True,
                secure=True,  # Only over HTTPS in production
                samesite="strict",
                max_age=CSRF_TOKEN_EXPIRY
            )
        
        return response
    
    # For state-changing requests, validate CSRF token
    
    # Get token from cookie
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    if not cookie_token:
        return JSONResponse(
            status_code=403,
            content={"detail": "CSRF cookie not found"}
        )
    
    # Get token from header or form data
    header_token = request.headers.get(CSRF_HEADER_NAME)
    
    if not header_token:
        # Try to get from form data for form submissions
        if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            form = await request.form()
            header_token = form.get("csrf_token")
    
    if not header_token:
        return JSONResponse(
            status_code=403,
            content={"detail": "CSRF token not found in request"}
        )
    
    # Validate tokens match (double-submit cookie pattern)
    if not hmac.compare_digest(cookie_token, header_token):
        return JSONResponse(
            status_code=403,
            content={"detail": "CSRF token mismatch"}
        )
    
    # Validate token signature and expiry
    session_id = request.session.get("session_id") if hasattr(request, "session") else None
    if not CSRFProtection.validate_token(cookie_token, session_id):
        return JSONResponse(
            status_code=403,
            content={"detail": "Invalid or expired CSRF token"}
        )
    
    # Token valid, proceed with request
    response = await call_next(request)
    
    # Rotate token periodically for security
    # (Optional: implement token rotation logic here)
    
    return response


def get_csrf_token(request: Request) -> str:
    """Helper function to get CSRF token for forms"""
    token = request.cookies.get(CSRF_COOKIE_NAME)
    if not token:
        token = CSRFProtection.generate_token()
    return token


def validate_csrf(request: Request, token: str) -> bool:
    """Helper function to validate CSRF token"""
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    if not cookie_token or not token:
        return False
    
    if not hmac.compare_digest(cookie_token, token):
        return False
        
    session_id = request.session.get("session_id") if hasattr(request, "session") else None
    return CSRFProtection.validate_token(token, session_id)