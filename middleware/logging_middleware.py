#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/logging_middleware.py
🎯 PURPOSE: Request/response logging middleware
🔗 IMPORTS: FastAPI, starlette, logging
📤 EXPORTS: setup_request_logging
"""

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import time
import json
from datetime import datetime

# Configure logger
logger = logging.getLogger("cora.requests")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Log request
        request_log = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "client": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        # Log sensitive paths at lower detail
        sensitive_paths = ["/api/auth/login", "/api/auth/register", "/api/payments"]
        if any(path in request.url.path for path in sensitive_paths):
            logger.info(f"Request: {request.method} {request.url.path}")
        else:
            logger.info(f"Request: {json.dumps(request_log)}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        response_log = {
            "status_code": response.status_code,
            "duration": f"{duration:.3f}s"
        }
        
        logger.info(f"Response: {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
        
        # Add timing header
        response.headers["X-Process-Time"] = str(duration)
        
        return response

def setup_request_logging(app: FastAPI):
    """Setup request logging middleware"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/cora_requests.log'),
            logging.StreamHandler()
        ]
    )
    
    # Add middleware
    app.add_middleware(RequestLoggingMiddleware)
    return app