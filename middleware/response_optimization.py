#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/response_optimization.py
🎯 PURPOSE: Response optimization middleware for automatic compression and performance tracking
🔗 IMPORTS: FastAPI, time, logging
📤 EXPORTS: ResponseOptimizationMiddleware
"""

import time
import logging
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from utils.api_response_optimizer import response_optimizer, performance_monitor

logger = logging.getLogger(__name__)

class ResponseOptimizationMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic response optimization and performance monitoring"""
    
    def __init__(
        self,
        app: ASGIApp,
        enable_compression: bool = True,
        enable_monitoring: bool = True,
        compression_threshold: int = 1024,
        excluded_paths: list = None
    ):
        super().__init__(app)
        self.enable_compression = enable_compression
        self.enable_monitoring = enable_monitoring
        self.compression_threshold = compression_threshold
        self.excluded_paths = excluded_paths or [
            '/health',
            '/api/health',
            '/api/health/detailed',
            '/static/',
            '/favicon.ico',
            '/robots.txt'
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and optimize response"""
        start_time = time.time()
        
        # Skip optimization for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Extract user ID if available
        user_id = None
        if hasattr(request.state, 'user'):
            user_id = getattr(request.state.user, 'id', None)
        
        # Record performance metrics
        if self.enable_monitoring:
            try:
                performance_monitor.record_response_time(
                    endpoint=request.url.path,
                    response_time=response_time,
                    status_code=response.status_code,
                    user_id=user_id
                )
            except Exception as e:
                logger.error(f"Failed to record performance metrics: {e}")
        
        # Apply response optimization
        if self.enable_compression and self._should_optimize_response(response):
            try:
                optimized_response = self._optimize_response(response, request)
                if optimized_response:
                    return optimized_response
            except Exception as e:
                logger.error(f"Failed to optimize response: {e}")
        
        # Add performance headers
        response.headers['X-Response-Time'] = f"{response_time:.3f}"
        response.headers['X-Response-Optimized'] = 'false'
        
        return response
    
    def _should_optimize_response(self, response: Response) -> bool:
        """Determine if response should be optimized"""
        # Only optimize JSON responses
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type:
            return False
        
        # Check if response is large enough to benefit from compression
        content_length = response.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                return size > self.compression_threshold
            except ValueError:
                pass
        
        return True
    
    def _optimize_response(self, response: Response, request: Request) -> Response:
        """Optimize the response with compression and caching"""
        try:
            # Get response content
            if hasattr(response, 'body'):
                content = response.body
            else:
                # For streaming responses, we can't optimize
                return response
            
            # Parse JSON content
            try:
                import json
                data = json.loads(content.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON or can't decode, skip optimization
                return response
            
            # Apply optimization
            optimized = response_optimizer.optimize_response(
                data=data,
                status_code=response.status_code,
                headers=dict(response.headers),
                compress=True
            )
            
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing response: {e}")
            return response

def setup_response_optimization(app, **kwargs):
    """Setup response optimization middleware"""
    app.add_middleware(ResponseOptimizationMiddleware, **kwargs)
    logger.info("Response optimization middleware configured") 