#!/usr/bin/env python3
"""
Smart Error Handler for CORA
Provides intelligent error handling, logging, and recovery suggestions
Created: 2025-08-10 by Claude (Phase 18)
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from functools import wraps
import json
import sys

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from pydantic import ValidationError

# Import our error constants
from utils.error_constants import (
    STATUS_BAD_REQUEST, STATUS_UNAUTHORIZED, STATUS_FORBIDDEN,
    STATUS_NOT_FOUND, STATUS_CONFLICT, STATUS_SERVER_ERROR,
    STATUS_SERVICE_UNAVAILABLE, ErrorMessages
)

class SmartErrorHandler:
    """Intelligent error handling with context and recovery suggestions"""
    
    def __init__(self, logger_name: str = "CORA"):
        self.logger = logging.getLogger(logger_name)
        self.error_stats = {}
        self.recovery_suggestions = self._load_recovery_suggestions()
        
    def _load_recovery_suggestions(self) -> Dict[str, str]:
        """Load recovery suggestions for common errors"""
        return {
            # Database errors
            "IntegrityError": "Check for duplicate entries or missing foreign key references",
            "OperationalError": "Database connection issue - check if database is running",
            "DataError": "Invalid data format for database field",
            
            # Validation errors
            "ValidationError": "Check input data format and required fields",
            "ValueError": "Invalid value provided - check data types and ranges",
            "TypeError": "Incorrect data type - verify API documentation",
            
            # Authentication errors
            "InvalidCredentialsError": "Verify username and password",
            "TokenExpiredError": "Login again to get a new token",
            "PermissionError": "User doesn't have required permissions",
            
            # External service errors
            "ConnectionError": "External service unavailable - check network/service status",
            "TimeoutError": "Request timed out - try again or check service status",
            "APIError": "External API error - check API limits and credentials",
            
            # File errors
            "FileNotFoundError": "File doesn't exist - check file path",
            "PermissionError": "No permission to access file",
            "OSError": "Operating system error - check disk space and permissions",
            
            # Business logic errors
            "InsufficientFundsError": "Not enough funds for this operation",
            "DuplicateEntryError": "This entry already exists",
            "ResourceNotFoundError": "Requested resource not found",
            "RateLimitError": "Too many requests - please wait",
            
            # Generic
            "Exception": "An unexpected error occurred - please try again"
        }
    
    def get_error_context(self, error: Exception, request: Optional[Request] = None) -> Dict[str, Any]:
        """Get detailed context about the error"""
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }
        
        # Add request context if available
        if request:
            context["request"] = {
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else None,
            }
        
        # Add recovery suggestion
        error_type = error.__class__.__name__
        context["recovery_suggestion"] = self.recovery_suggestions.get(
            error_type, 
            self.recovery_suggestions["Exception"]
        )
        
        # Track error statistics
        self._track_error(error_type)
        
        return context
    
    def _track_error(self, error_type: str) -> None:
        """Track error statistics for monitoring"""
        if error_type not in self.error_stats:
            self.error_stats[error_type] = {
                "count": 0,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": None
            }
        
        self.error_stats[error_type]["count"] += 1
        self.error_stats[error_type]["last_seen"] = datetime.utcnow().isoformat()
    
    def handle_error(self, error: Exception, request: Optional[Request] = None, 
                    user_message: Optional[str] = None) -> JSONResponse:
        """Handle an error and return appropriate response"""
        
        # Get error context
        context = self.get_error_context(error, request)
        
        # Determine status code and message
        status_code = STATUS_SERVER_ERROR
        message = user_message or "An error occurred"
        details = {}
        
        # Handle specific error types
        if isinstance(error, ValidationError):
            status_code = STATUS_BAD_REQUEST
            message = "Validation error"
            details = {"validation_errors": error.errors()}
            
        elif isinstance(error, IntegrityError):
            status_code = STATUS_CONFLICT
            message = "Database constraint violation"
            
        elif isinstance(error, OperationalError):
            status_code = STATUS_SERVICE_UNAVAILABLE
            message = "Database connection error"
            
        elif isinstance(error, HTTPException):
            status_code = error.status_code
            message = error.detail
            
        elif isinstance(error, PermissionError):
            status_code = STATUS_FORBIDDEN
            message = "Permission denied"
            
        elif isinstance(error, FileNotFoundError):
            status_code = STATUS_NOT_FOUND
            message = "Resource not found"
            
        elif isinstance(error, ConnectionError):
            status_code = STATUS_SERVICE_UNAVAILABLE
            message = "External service unavailable"
            
        elif isinstance(error, TimeoutError):
            status_code = STATUS_SERVICE_UNAVAILABLE
            message = "Request timeout"
        
        # Log the error with context
        if status_code >= 500:
            self.logger.error(f"{message}: {context}")
        else:
            self.logger.warning(f"{message}: {context}")
        
        # Prepare response
        response_data = {
            "error": {
                "message": message,
                "type": error.__class__.__name__,
                "suggestion": context["recovery_suggestion"]
            }
        }
        
        # Add details if available
        if details:
            response_data["error"]["details"] = details
        
        # In development, include more context
        if self._is_development():
            response_data["debug"] = {
                "traceback": context["traceback"],
                "request": context.get("request")
            }
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    def _is_development(self) -> bool:
        """Check if running in development mode"""
        import os
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    def log_with_context(self, level: str, message: str, **kwargs) -> None:
        """Log a message with additional context"""
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        log_message = json.dumps({"level": level, "message": message, "context": context})
        with open('error_log.json', 'a') as f:
            f.write(log_message + '\n')
        
        if level == "error":
            self.logger.error(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "info":
            self.logger.info(log_message)
        else:
            self.logger.debug(log_message)
    
    def safe_route(self, func: Callable) -> Callable:
        """Decorator to wrap routes with smart error handling"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Get request from kwargs if available
                request = kwargs.get('request') or kwargs.get('req')
                
                # Execute the route function
                result = await func(*args, **kwargs)
                return result
                
            except Exception as e:
                # Handle the error smartly
                return self.handle_error(e, request)
        
        return wrapper
    
    def get_error_report(self) -> Dict[str, Any]:
        """Get a report of all errors encountered"""
        return {
            "total_errors": sum(stat["count"] for stat in self.error_stats.values()),
            "error_types": len(self.error_stats),
            "most_common": sorted(
                self.error_stats.items(), 
                key=lambda x: x[1]["count"], 
                reverse=True
            )[:10],
            "full_stats": self.error_stats
        }


class ErrorRecovery:
    """Provides automatic recovery strategies for common errors"""
    
    @staticmethod
    def retry_with_backoff(func: Callable, max_retries: int = 3, 
                          initial_delay: float = 1.0) -> Callable:
        """Decorator to retry failed operations with exponential backoff"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError, OperationalError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                    continue
                except Exception as e:
                    # Don't retry for other errors
                    raise e
            
            # If all retries failed, raise the last exception
            raise last_exception
        
        return wrapper
    
    @staticmethod
    def fallback_value(default_value: Any) -> Callable:
        """Decorator to provide fallback value on error"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Using fallback value due to error: {e}")
                    return default_value
            return wrapper
        return decorator
    
    @staticmethod
    def circuit_breaker(failure_threshold: int = 5, 
                       timeout: int = 60) -> Callable:
        """Decorator to implement circuit breaker pattern"""
        def decorator(func: Callable) -> Callable:
            func._failures = 0
            func._last_failure = None
            func._is_open = False
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Check if circuit is open
                if func._is_open:
                    if func._last_failure:
                        time_since_failure = (datetime.utcnow() - func._last_failure).seconds
                        if time_since_failure < timeout:
                            raise Exception("Circuit breaker is open")
                        else:
                            # Try to close the circuit
                            func._is_open = False
                            func._failures = 0
                
                try:
                    result = await func(*args, **kwargs)
                    # Reset failures on success
                    func._failures = 0
                    return result
                except Exception as e:
                    func._failures += 1
                    func._last_failure = datetime.utcnow()
                    
                    if func._failures >= failure_threshold:
                        func._is_open = True
                        logging.error(f"Circuit breaker opened for {func.__name__}")
                    
                    raise e
            
            return wrapper
        return decorator


# Global error handler instance
error_handler = SmartErrorHandler()

# Convenience functions
def handle_route_error(error: Exception, request: Optional[Request] = None) -> JSONResponse:
    """Convenience function to handle route errors"""
    return error_handler.handle_error(error, request)

def log_error(message: str, **context) -> None:
    """Convenience function to log errors with context"""
    error_handler.log_with_context("error", message, **context)

def log_warning(message: str, **context) -> None:
    """Convenience function to log warnings with context"""
    error_handler.log_with_context("warning", message, **context)

def log_info(message: str, **context) -> None:
    """Convenience function to log info with context"""
    error_handler.log_with_context("info", message, **context)


# Example usage for routes
"""
from utils.smart_error_handler import error_handler, ErrorRecovery

@router.get("/example")
@error_handler.safe_route
async def example_route(request: Request, db: Session = Depends(get_db)):
    # Your route logic here
    # Any exception will be automatically handled
    pass

@router.get("/with-retry")
@ErrorRecovery.retry_with_backoff
async def route_with_retry():
    # This will retry on connection errors
    pass

@router.get("/with-fallback")
@ErrorRecovery.fallback_value({"status": "default"})
async def route_with_fallback():
    # Returns fallback value on error
    pass
"""