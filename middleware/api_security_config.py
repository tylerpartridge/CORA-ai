#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/api_security_config.py
🎯 PURPOSE: API security configuration for CORS, request size limits, and API versioning
🔗 IMPORTS: FastAPI, os, typing
📤 EXPORTS: setup_api_security, get_cors_config, get_request_limits
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logging_config import get_logger

logger = get_logger(__name__)

class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request size limits"""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next):
        # Check content length for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_length = request.headers.get('content-length')
            if content_length:
                try:
                    size = int(content_length)
                    if size > self.max_request_size:
                        logger.warning(f"Request too large: {size} bytes from {request.client.host}")
                        return JSONResponse(
                            status_code=413,
                            content={
                                "error": "Request too large",
                                "message": f"Request size exceeds maximum allowed size of {self.max_request_size // (1024*1024)}MB",
                                "max_size_mb": self.max_request_size // (1024*1024)
                            }
                        )
                except ValueError:
                    pass  # Invalid content-length header
        
        response = await call_next(request)
        return response

class APIVersionMiddleware(BaseHTTPMiddleware):
    """Middleware to handle API versioning"""
    
    def __init__(self, app, default_version: str = "v1"):
        super().__init__(app)
        self.default_version = default_version
        self.supported_versions = ["v1", "v2"]
        self.deprecated_versions = ["v1"]  # Mark v1 as deprecated
    
    async def dispatch(self, request: Request, call_next):
        # Extract version from path
        path = request.url.path
        version = self._extract_version(path)
        
        if version:
            # Check if version is supported
            if version not in self.supported_versions:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Unsupported API version",
                        "message": f"API version '{version}' is not supported. Supported versions: {', '.join(self.supported_versions)}",
                        "supported_versions": self.supported_versions
                    }
                )
            
            # Check if version is deprecated
            if version in self.deprecated_versions:
                response = await call_next(request)
                response.headers["X-API-Version-Deprecated"] = "true"
                response.headers["X-API-Version-Sunset"] = "2025-12-31"
                return response
        
        response = await call_next(request)
        return response
    
    def _extract_version(self, path: str) -> Optional[str]:
        """Extract API version from path"""
        if path.startswith('/api/v'):
            parts = path.split('/')
            if len(parts) >= 3 and parts[1] == 'api' and parts[2].startswith('v'):
                return parts[2]
        return None

def get_cors_config() -> Dict[str, Any]:
    """Get CORS configuration based on environment"""
    
    # Production origins
    PROD_ORIGINS = [
        "https://coraai.tech",
        "https://www.coraai.tech",
        "https://app.coraai.tech"
    ]
    
    # Development origins
    DEV_ORIGINS = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "http://localhost:3000",  # React dev server
        "http://localhost:5173"   # Vite dev server
    ]
    
    # Get environment
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        origins = PROD_ORIGINS
        allow_credentials = True
        allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        allow_headers = ["*"]
    else:
        origins = PROD_ORIGINS + DEV_ORIGINS
        allow_credentials = True
        allow_methods = ["*"]
        allow_headers = ["*"]
    
    return {
        "allow_origins": origins,
        "allow_credentials": allow_credentials,
        "allow_methods": allow_methods,
        "allow_headers": allow_headers,
        "expose_headers": [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining", 
            "X-RateLimit-Reset",
            "X-API-Version",
            "X-API-Version-Deprecated",
            "X-API-Version-Sunset"
        ]
    }

def get_request_limits() -> Dict[str, int]:
    """Get request size limits based on endpoint type"""
    return {
        "default": 10 * 1024 * 1024,      # 10MB
        "file_upload": 50 * 1024 * 1024,  # 50MB
        "api": 5 * 1024 * 1024,           # 5MB
        "auth": 1 * 1024 * 1024,          # 1MB
        "admin": 20 * 1024 * 1024         # 20MB
    }

def setup_api_security(app: FastAPI) -> None:
    """Setup comprehensive API security configuration"""
    
    # Get configurations
    cors_config = get_cors_config()
    request_limits = get_request_limits()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
        expose_headers=cors_config["expose_headers"]
    )
    
    # Add request size middleware
    app.add_middleware(RequestSizeMiddleware, max_request_size=request_limits["default"])
    
    # Add API version middleware
    app.add_middleware(APIVersionMiddleware, default_version="v1")
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    logger.info("API security configuration applied")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enhanced security headers middleware"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy (development-friendly). NOTE: A stricter, enhanced CSP is applied via
        # middleware.security_headers_enhanced; this fallback must not block required third-party SDKs.
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://cdn.plaid.com https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.openai.com https://cdn.plaid.com https://production.plaid.com https://sandbox.plaid.com https://api.stripe.com; "
            "frame-src 'self' https://cdn.plaid.com https://js.stripe.com https://hooks.stripe.com; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # HSTS (only in production)
        if os.getenv("ENVIRONMENT", "development").lower() == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response

# API versioning utilities
def get_api_version(request: Request) -> str:
    """Get API version from request"""
    path = request.url.path
    if path.startswith('/api/v'):
        parts = path.split('/')
        if len(parts) >= 3 and parts[1] == 'api' and parts[2].startswith('v'):
            return parts[2]
    return "v1"

def is_deprecated_version(version: str) -> bool:
    """Check if API version is deprecated"""
    deprecated_versions = ["v1"]
    return version in deprecated_versions

def get_supported_versions() -> List[str]:
    """Get list of supported API versions"""
    return ["v1", "v2"]

# Request validation utilities
def validate_request_size(content_length: Optional[str], max_size: int) -> bool:
    """Validate request size"""
    if not content_length:
        return True
    
    try:
        size = int(content_length)
        return size <= max_size
    except ValueError:
        return False

def get_endpoint_request_limit(path: str) -> int:
    """Get request size limit for specific endpoint"""
    limits = get_request_limits()
    
    if path.startswith('/api/upload'):
        return limits["file_upload"]
    elif path.startswith('/api/auth'):
        return limits["auth"]
    elif path.startswith('/api/admin'):
        return limits["admin"]
    elif path.startswith('/api/'):
        return limits["api"]
    else:
        return limits["default"] 