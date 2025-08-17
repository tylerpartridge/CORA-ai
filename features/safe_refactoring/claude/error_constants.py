#!/usr/bin/env python3
"""
Standardized error messages for CORA
This provides consistent error messaging across all routes
Created: 2025-08-10 by Claude (Safe Refactoring Phase 3)
"""

# 400 Bad Request - Client errors
ERROR_INVALID_INPUT = "Invalid input data"
ERROR_INVALID_TOKEN = "Invalid or expired token"
ERROR_INVALID_FILE = "Invalid file type"
ERROR_FILE_TOO_LARGE = "File too large (max 10MB)"
ERROR_NO_FILE = "No file provided"
ERROR_INVALID_DATE = "Invalid date format"
ERROR_INVALID_ID = "Invalid ID provided"
ERROR_ALREADY_EXISTS = "{} already exists"
ERROR_VALIDATION_FAILED = "{} validation failed"
ERROR_MISSING_REQUIRED = "{} is required"
ERROR_INVALID_RANGE = "{} must be between {} and {}"

# 401 Unauthorized - Authentication errors
ERROR_INVALID_CREDENTIALS = "Invalid email or password"
ERROR_TOKEN_EXPIRED = "Token has expired. Please login again"
ERROR_AUTH_REQUIRED = "Authentication required"

# 403 Forbidden - Permission errors
ERROR_ACCESS_DENIED = "Access denied"
ERROR_ADMIN_REQUIRED = "Admin access required"
ERROR_EMAIL_NOT_VERIFIED = "Please verify your email before continuing"
ERROR_ACCOUNT_INACTIVE = "Account is inactive"

# 404 Not Found - Resource errors
ERROR_NOT_FOUND = "{} not found"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_RESOURCE_NOT_FOUND = "Requested resource not found"
ERROR_NO_ACTIVE_SUBSCRIPTION = "No active subscription found"

# 429 Too Many Requests
ERROR_RATE_LIMIT = "Too many requests. Please try again later"

# 500 Internal Server Error - Server errors
ERROR_PROCESSING_FAILED = "Failed to process {}"
ERROR_GENERATION_FAILED = "Failed to generate {}"
ERROR_RETRIEVAL_FAILED = "Failed to retrieve {}"
ERROR_UPDATE_FAILED = "Failed to update {}"
ERROR_DELETION_FAILED = "Failed to delete {}"
ERROR_SEND_FAILED = "Failed to send {}"
ERROR_CALCULATION_FAILED = "Failed to calculate {}"
ERROR_UNEXPECTED = "An unexpected error occurred"
ERROR_SERVICE_UNAVAILABLE = "Service temporarily unavailable"

# 503 Service Unavailable
ERROR_MAINTENANCE = "Service under maintenance. Please try again later"

class ErrorMessages:
    """Helper class for formatting error messages"""
    
    @staticmethod
    def not_found(resource: str) -> str:
        """Format a not found error message"""
        return ERROR_NOT_FOUND.format(resource.capitalize())
    
    @staticmethod
    def already_exists(resource: str) -> str:
        """Format an already exists error message"""
        return ERROR_ALREADY_EXISTS.format(resource.capitalize())
    
    @staticmethod
    def processing_failed(action: str) -> str:
        """Format a processing failed error message"""
        return ERROR_PROCESSING_FAILED.format(action)
    
    @staticmethod
    def validation_failed(field: str) -> str:
        """Format a validation failed error message"""
        return ERROR_VALIDATION_FAILED.format(field.capitalize())
    
    @staticmethod
    def required_field(field: str) -> str:
        """Format a required field error message"""
        return ERROR_MISSING_REQUIRED.format(field.capitalize())
    
    @staticmethod
    def invalid_range(field: str, min_val: int, max_val: int) -> str:
        """Format an invalid range error message"""
        return ERROR_INVALID_RANGE.format(field.capitalize(), min_val, max_val)

# Common error response templates
def error_response(status_code: int, detail: str, headers: dict = None) -> dict:
    """Create a standardized error response"""
    return {
        "status_code": status_code,
        "detail": detail,
        "headers": headers or {}
    }

# Status code helpers
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_ACCEPTED = 202
STATUS_NO_CONTENT = 204
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_CONFLICT = 409
STATUS_UNPROCESSABLE = 422
STATUS_RATE_LIMITED = 429
STATUS_SERVER_ERROR = 500
STATUS_SERVICE_UNAVAILABLE = 503