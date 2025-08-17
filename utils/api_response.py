#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/api_response.py
🎯 PURPOSE: Standardized API response utilities for consistent response formats
🔗 IMPORTS: typing, datetime
📤 EXPORTS: API response helper functions
"""

from typing import Any, Dict, Optional, Union
from datetime import datetime
import uuid

class APIResponse:
    """Standardized API response class for consistent formatting"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized success response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata
            
        Returns:
            Standardized success response dictionary
        """
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": str(uuid.uuid4())
        }
        
        if data is not None:
            response["data"] = data
            
        if meta:
            response["meta"] = meta
            
        return response
    
    @staticmethod
    def error(
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized error response
        
        Args:
            message: Error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error details
            request_id: Request ID for tracking
            
        Returns:
            Standardized error response dictionary
        """
        response = {
            "success": False,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or str(uuid.uuid4())
        }
        
        if error_code:
            response["error_code"] = error_code
            
        if details:
            response["details"] = details
            
        return response
    
    @staticmethod
    def paginated(
        data: list,
        page: int,
        per_page: int,
        total: int,
        message: str = "Data retrieved successfully"
    ) -> Dict[str, Any]:
        """
        Create a standardized paginated response
        
        Args:
            data: List of items
            page: Current page number
            per_page: Items per page
            total: Total number of items
            message: Success message
            
        Returns:
            Standardized paginated response dictionary
        """
        total_pages = (total + per_page - 1) // per_page
        
        return APIResponse.success(
            data=data,
            message=message,
            meta={
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        )

# Legacy compatibility functions
def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """Legacy success response for backward compatibility"""
    return APIResponse.success(data=data, message=message)

def error_response(message: str, error_code: Optional[str] = None) -> Dict[str, Any]:
    """Legacy error response for backward compatibility"""
    return APIResponse.error(message=message, error_code=error_code)

# Common error codes
class ErrorCodes:
    """Standard error codes for consistent error handling"""
    
    # Authentication errors
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    
    # System errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Business logic errors
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"

# Common success messages
class SuccessMessages:
    """Standard success messages for consistency"""
    
    # CRUD operations
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    RETRIEVED = "Data retrieved successfully"
    
    # Authentication
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    PASSWORD_CHANGED = "Password changed successfully"
    EMAIL_VERIFIED = "Email verified successfully"
    
    # Business operations
    PAYMENT_PROCESSED = "Payment processed successfully"
    INTEGRATION_CONNECTED = "Integration connected successfully"
    INTEGRATION_DISCONNECTED = "Integration disconnected successfully"
    EXPORT_COMPLETED = "Export completed successfully"
    
    # Wellness
    WELLNESS_CHECK_COMPLETED = "Wellness check completed"
    SUPPORT_REQUESTED = "Support requested successfully"
    INTERACTION_TRACKED = "Interaction tracked successfully" 