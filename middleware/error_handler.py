#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/error_handler.py
🎯 PURPOSE: Global error handling middleware with enhanced validation support
🔗 IMPORTS: FastAPI, starlette, pydantic
📤 EXPORTS: setup_error_handlers
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError as PydanticValidationError
import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from utils.validation import ValidationError, format_validation_error
from utils.api_response import APIResponse, ErrorCodes

logger = logging.getLogger("cora.errors")

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with enhanced error details"""
    error_response = {
        "error": exc.detail,
        "status_code": exc.status_code,
        "path": str(request.url),
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": getattr(request.state, 'request_id', None)
    }
    
    # Log the error with context
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def validation_exception_handler(request: Request, exc: PydanticValidationError):
    """Handle Pydantic validation errors with detailed field information"""
    errors = []
    
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'])
        message = error['msg']
        error_type = error['type']
        
        errors.append({
            "field": field,
            "message": message,
            "type": error_type,
            "value": error.get('input', None)
        })
    
    error_response = {
        "error": "Validation failed",
        "status_code": 422,
        "path": str(request.url),
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": getattr(request.state, 'request_id', None),
        "validation_errors": errors,
        "error_count": len(errors)
    }
    
    # Log validation errors
    logger.warning(f"Validation Error: {len(errors)} errors - Path: {request.url}")
    for error in errors:
        logger.debug(f"  Field: {error['field']}, Message: {error['message']}")
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )

async def custom_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle custom validation errors"""
    error_response = format_validation_error(exc)
    # Don't add fields that don't exist in the response model
    # error_response.path = str(request.url)
    # error_response.timestamp = datetime.utcnow().isoformat()
    # error_response.request_id = getattr(request.state, 'request_id', None)
    
    # Log the validation error
    logger.warning(f"Custom Validation Error: {exc.field} - {exc.message} - Path: {request.url}")
    
    # Convert to dict and ensure JSON serializable
    response_dict = error_response.dict()
    # Convert any datetime objects to strings
    import json
    from datetime import datetime
    
    def serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    return JSONResponse(
        status_code=422,
        content=json.loads(json.dumps(response_dict, default=serialize))
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with enhanced logging and error details"""
    # Suppress logging for certain error types on landing page
    error_str = str(exc).lower()
    if request.url.path == "/" and any(term in error_str for term in [
        "invalid input", "retrying", "unexpected error", "openai", 
        "api key", "authorization", "rate limit"
    ]):
        # Silently handle without logging
        pass
    else:
        # Enhanced error logging
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {exc}",
            extra={
                "path": str(request.url),
                "method": request.method,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_id": getattr(request.state, 'request_id', None),
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
    
    # Determine if we should expose error details
    is_development = getattr(request.app.state, 'debug', False)
    
    error_response = {
        "error": "Internal server error",
        "status_code": 500,
        "path": str(request.url),
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": getattr(request.state, 'request_id', None)
    }
    
    # Add debug information in development
    if is_development:
        error_response.update({
            "debug_info": {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc().split('\n')
            }
        })
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

def setup_error_handlers(app: FastAPI):
    """Setup error handlers for the app with enhanced validation support"""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, custom_validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    return app