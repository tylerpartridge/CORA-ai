#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/csrf.py
🎯 PURPOSE: CSRF protection middleware for state-changing operations
🔗 IMPORTS: FastAPI, secrets, time
📤 EXPORTS: setup_csrf_protection, generate_csrf_token, validate_csrf_token
"""

from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
import secrets
import time
from typing import Dict, Optional
import os

# CSRF token storage (in production, use Redis)
csrf_tokens: Dict[str, Dict[str, any]] = {}

# Configuration
CSRF_TOKEN_EXPIRY = 3600  # 1 hour
CSRF_TOKEN_LENGTH = 32
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

def generate_csrf_token() -> str:
    """Generate a secure CSRF token"""
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)

def validate_csrf_token(token: str, user_email: str) -> bool:
    """Validate CSRF token for a user"""
    if not token or not user_email:
        return False
    
    if user_email not in csrf_tokens:
        return False
    
    user_tokens = csrf_tokens[user_email]
    
    # Check if token exists and is not expired
    if token not in user_tokens:
        return False
    
    token_data = user_tokens[token]
    if time.time() > token_data['expires_at']:
        # Remove expired token
        del user_tokens[token]
        return False
    
    return True

def cleanup_expired_tokens():
    """Remove expired CSRF tokens"""
    current_time = time.time()
    expired_users = []
    
    for user_email, tokens in csrf_tokens.items():
        expired_tokens = [
            token for token, data in tokens.items()
            if current_time > data['expires_at']
        ]
        
        for token in expired_tokens:
            del tokens[token]
        
        if not tokens:
            expired_users.append(user_email)
    
    for user_email in expired_users:
        del csrf_tokens[user_email]

async def csrf_middleware(request: Request, call_next):
    """CSRF protection middleware"""
    
    # Skip CSRF check for GET requests and static files
    if request.method == "GET" or request.url.path.startswith("/static/"):
        response = await call_next(request)
        return response
    
    # Skip CSRF check for login/register endpoints
    if request.url.path in ["/api/auth/login", "/api/auth/register"]:
        response = await call_next(request)
        return response
    
    # Get user email from JWT token
    user_email = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            # Import JWT decoding function
            from dependencies.auth import decode_token
            token = auth_header.split(" ")[1]
            user_data = decode_token(token)
            user_email = user_data.get("sub")  # sub contains the email
        except Exception as e:
            # If JWT decoding fails, skip CSRF check for now
            # In production, this should be more strict
            pass
    
    if not user_email:
        # Allow requests without authentication (for now)
        response = await call_next(request)
        return response
    
    # Check CSRF token
    csrf_token = request.headers.get(CSRF_HEADER_NAME)
    if not csrf_token:
        return JSONResponse(
            status_code=403,
            content={"error": "CSRF token required"}
        )
    
    if not validate_csrf_token(csrf_token, user_email):
        return JSONResponse(
            status_code=403,
            content={"error": "Invalid CSRF token"}
        )
    
    # Clean up expired tokens periodically
    if len(csrf_tokens) > 100:  # Arbitrary threshold
        cleanup_expired_tokens()
    
    response = await call_next(request)
    return response

def setup_csrf_protection(app):
    """Setup CSRF protection for the FastAPI app"""
    app.middleware("http")(csrf_middleware)
    
    @app.get("/api/csrf-token")
    async def get_csrf_token(request: Request):
        """Get a new CSRF token for the current user"""
        # Get user from JWT token
        user_email = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from dependencies.auth import decode_token
                token = auth_header.split(" ")[1]
                user_data = decode_token(token)
                user_email = user_data.get("sub")
            except Exception as e:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid authentication token"}
                )
        
        if not user_email:
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = generate_csrf_token()
        expires_at = time.time() + CSRF_TOKEN_EXPIRY
        
        if user_email not in csrf_tokens:
            csrf_tokens[user_email] = {}
        
        csrf_tokens[user_email][token] = {
            'created_at': time.time(),
            'expires_at': expires_at
        }
        
        response = JSONResponse(content={"csrf_token": token})
        response.set_cookie(
            CSRF_COOKIE_NAME,
            token,
            max_age=CSRF_TOKEN_EXPIRY,
            httponly=True,
            secure=os.getenv("ENVIRONMENT") == "production",
            samesite="strict"
        )
        
        return response 