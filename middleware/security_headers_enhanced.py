"""
🧭 LOCATION: /CORA/middleware/security_headers_enhanced.py
🎯 PURPOSE: Enhanced security headers middleware with strict CSP
🔗 IMPORTS: FastAPI, starlette, secrets
📤 EXPORTS: setup_security_headers
"""

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import secrets
import os

class EnhancedSecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add enhanced security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate a unique nonce for this request
        nonce = secrets.token_urlsafe(16)
        
        # Store nonce in request state for use in templates
        request.state.csp_nonce = nonce
        
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        # Disable COEP for Plaid compatibility
        # response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        
        # Enhanced Content Security Policy (development-friendly). Using 'unsafe-inline' for now until all inline scripts carry a nonce.
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://cdn.plaid.com https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' data: https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "connect-src 'self' https://api.stripe.com https://cdn.plaid.com https://production.plaid.com https://sandbox.plaid.com wss://localhost:* ws://localhost:*; "
            "frame-src 'self' https://js.stripe.com https://hooks.stripe.com https://cdn.plaid.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "manifest-src 'self'; "
            "worker-src 'self' blob:; "
            "media-src 'self';"
        )
        
        # Add report-uri in production
        if os.getenv("ENVIRONMENT") == "production":
            csp += " report-uri /api/csp-report;"
            
        response.headers["Content-Security-Policy"] = csp
        
        # Enhanced Permissions Policy
        # Keep to widely supported features only; remove experimental to avoid warnings in dev
        permissions = (
            "geolocation=(), microphone=(), camera=()"
        )
        response.headers["Permissions-Policy"] = permissions
        
        return response

def setup_security_headers(app: FastAPI):
    """Setup enhanced security headers middleware"""
    app.add_middleware(EnhancedSecurityHeadersMiddleware)
    
    # Add CSP report endpoint
    @app.post("/api/csp-report")
    async def csp_report(request: Request):
        """Log CSP violations for monitoring"""
        try:
            violation = await request.json()
            # Log the violation (integrate with your logging system)
            print(f"CSP Violation: {violation}")
            # In production, send to monitoring service
        except:
            pass
        return {"status": "ok"}
    
    return app

def get_nonce_tag(nonce: str) -> str:
    """Generate a script tag with nonce for templates"""
    return f'<script nonce="{nonce}">'

def get_inline_script_with_nonce(nonce: str, script: str) -> str:
    """Wrap inline script with nonce"""
    return f'<script nonce="{nonce}">{script}</script>'