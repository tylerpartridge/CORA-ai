#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/error_handler.py
🎯 PURPOSE: Unified error handling framework with standardized error responses
🔗 IMPORTS: fastapi, logging, typing
📤 EXPORTS: ErrorHandler, custom exceptions, error response models
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Custom Exception Classes
class CORAException(Exception):
    """Base exception for CORA application"""
    def __init__(self, message: str, code: str = "CORA_ERROR", status_code: int = 500, 
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(CORAException):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)
        self.field = field

class AuthenticationException(CORAException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", 401, details)

class AuthorizationException(CORAException):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", 403, details)

class NotFoundException(CORAException):
    """Raised when a resource is not found"""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NOT_FOUND_ERROR", 404, details)

class ConflictException(CORAException):
    """Raised when there's a conflict (e.g., duplicate resource)"""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFLICT_ERROR", 409, details)

class RateLimitException(CORAException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", 429, details)

class DatabaseException(CORAException):
    """Raised when database operations fail"""
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", 500, details)

class ExternalServiceException(CORAException):
    """Raised when external service calls fail"""
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502, details)

# Error Response Models
class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str
    code: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    path: Optional[str] = None
    method: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    """Validation error response format"""
    error: str = "Validation Error"
    code: str = "VALIDATION_ERROR"
    field: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None

class ErrorHandler:
    """Unified error handling service"""
    
    @staticmethod
    def create_error_response(
        exception: CORAException,
        request: Optional[Request] = None,
        include_traceback: bool = False
    ) -> ErrorResponse:
        """Create standardized error response"""
        
        # Get request information if available
        path = None
        method = None
        if request:
            path = str(request.url.path)
            method = request.method
        
        # Create error response
        # Ensure datetime fields are ISO strings for JSON serialization
        error_response = ErrorResponse(
            error=exception.__class__.__name__,
            code=exception.code,
            message=exception.message,
            path=path,
            method=method,
            details=exception.details
        )
        
        # Add traceback in development mode
        if include_traceback:
            error_response.details = error_response.details or {}
            error_response.details["traceback"] = traceback.format_exc()
        
        return error_response
    
    @staticmethod
    def log_error(exception: Exception, request: Optional[Request] = None, 
                  context: Optional[Dict[str, Any]] = None):
        """Log error with context"""
        
        # Avoid reserved LogRecord fields like 'message' in extra
        log_data = {
            "exception_type": exception.__class__.__name__,
            "error_message": str(exception),
            "context": context or {}
        }
        
        if request:
            log_data.update({
                "path": str(request.url.path),
                "method": request.method,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            })
        
        if isinstance(exception, CORAException):
            logger.error(f"CORA Error: {exception.code} - {exception.message}", 
                        extra=log_data)
        else:
            logger.error(f"Unexpected Error: {str(exception)}", 
                        extra=log_data, exc_info=True)
    
    @staticmethod
    def handle_exception(exception: Exception, request: Optional[Request] = None) -> JSONResponse:
        """Handle any exception and return appropriate HTTP response"""
        
        # Log the error
        ErrorHandler.log_error(exception, request)
        
        # Convert to CORAException if needed
        if isinstance(exception, CORAException):
            cora_exception = exception
        elif isinstance(exception, HTTPException):
            # Convert FastAPI HTTPException to CORAException
            cora_exception = CORAException(
                message=exception.detail,
                code="HTTP_ERROR",
                status_code=exception.status_code
            )
        else:
            # Convert unexpected exceptions to generic CORAException
            cora_exception = CORAException(
                message="An unexpected error occurred",
                code="INTERNAL_ERROR",
                status_code=500,
                details={"original_error": str(exception)}
            )
        
        # Create error response
        error_response = ErrorHandler.create_error_response(
            cora_exception, 
            request,
            include_traceback=False  # Don't expose traceback in production
        )
        
        payload = error_response.dict()
        # Convert datetime in payload to ISO string if present
        if isinstance(payload.get("timestamp"), datetime):
            payload["timestamp"] = payload["timestamp"].isoformat()
        return JSONResponse(status_code=cora_exception.status_code, content=payload)

# Convenience functions for common error scenarios
def raise_validation_error(message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
    """Raise validation error with standardized format"""
    raise ValidationException(message, field, details)

def raise_not_found_error(message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
    """Raise not found error"""
    raise NotFoundException(message, details)

def raise_authentication_error(message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
    """Raise authentication error"""
    raise AuthenticationException(message, details)

def raise_authorization_error(message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
    """Raise authorization error"""
    raise AuthorizationException(message, details)

def raise_database_error(message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
    """Raise database error"""
    raise DatabaseException(message, details)

def raise_external_service_error(message: str = "External service error", details: Optional[Dict[str, Any]] = None):
    """Raise external service error"""
    raise ExternalServiceException(message, details)

# Error handling decorator
def handle_errors(func):
    """Decorator to handle errors in route functions"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except CORAException as e:
            # Re-raise CORA exceptions (they're already handled)
            raise
        except Exception as e:
            # Convert unexpected exceptions
            raise CORAException(
                message="An unexpected error occurred",
                code="INTERNAL_ERROR",
                status_code=500,
                details={"original_error": str(e)}
            )
    return wrapper 