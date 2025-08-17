#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/authorization.py
🎯 PURPOSE: Authorization middleware to prevent IDOR vulnerabilities
🔗 IMPORTS: FastAPI, dependencies
📤 EXPORTS: require_ownership, require_admin, check_resource_access
"""

from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from functools import wraps
from typing import Optional, Callable, Any
import re

def get_user_email_from_token(request: Request) -> Optional[str]:
    """Extract user email from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        from dependencies.auth import decode_token
        token = auth_header.split(" ")[1]
        user_data = decode_token(token)
        return user_data.get("sub")  # sub contains the email
    except Exception:
        return None

def get_user_id_from_token(request: Request) -> Optional[int]:
    """Extract user ID from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        from dependencies.auth import decode_token
        token = auth_header.split(" ")[1]
        user_data = decode_token(token)
        return user_data.get("user_id")
    except Exception:
        return None

def require_ownership(resource_type: str, id_param: str = "id"):
    """
    Decorator to ensure user owns the resource they're accessing
    
    Args:
        resource_type: Type of resource (e.g., "expense", "user", "feedback")
        id_param: Name of the ID parameter in the request
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the request object (usually the first argument)
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Get user email from token
            user_email = get_user_email_from_token(request)
            if not user_email:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Get resource ID from path parameters or query parameters
            resource_id = None
            
            # Check path parameters first
            if hasattr(request, 'path_params') and request.path_params:
                resource_id = request.path_params.get(id_param)
            
            # Check query parameters if not found in path
            if not resource_id:
                resource_id = request.query_params.get(id_param)
            
            # Check if resource ID is provided
            if not resource_id:
                raise HTTPException(status_code=400, detail=f"{resource_type} ID required")
            
            # Verify ownership based on resource type
            if not await verify_resource_ownership(resource_type, resource_id, user_email):
                raise HTTPException(status_code=403, detail=f"Access denied to {resource_type}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def verify_resource_ownership(resource_type: str, resource_id: str, user_email: str) -> bool:
    """Verify that the user owns the specified resource"""
    try:
        from dependencies.database import get_db
        from models.expense import Expense
        from models.user import User
        from models.feedback import Feedback
        
        db = get_db()
        
        if resource_type.lower() == "expense":
            # Check if expense belongs to user
            expense = db.query(Expense).filter(
                Expense.id == resource_id,
                Expense.user_email == user_email
            ).first()
            return expense is not None
            
        elif resource_type.lower() == "user":
            # Users can only access their own profile
            return resource_id == user_email
            
        elif resource_type.lower() == "feedback":
            # Check if feedback belongs to user
            feedback = db.query(Feedback).filter(
                Feedback.id == resource_id,
                Feedback.user_email == user_email
            ).first()
            return feedback is not None
            
        elif resource_type.lower() == "business_profile":
            # Check if business profile belongs to user
            from models.business_profile import BusinessProfile
            profile = db.query(BusinessProfile).filter(
                BusinessProfile.id == resource_id,
                BusinessProfile.user_email == user_email
            ).first()
            return profile is not None
            
        else:
            # Unknown resource type - deny access
            return False
            
    except Exception as e:
        # Log the error and deny access for security
        print(f"Error verifying resource ownership: {e}")
        return False

def require_admin(func: Callable) -> Callable:
    """Decorator to require admin privileges"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get the request object
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            raise HTTPException(status_code=500, detail="Request object not found")
        
        # Get user email from token
        user_email = get_user_email_from_token(request)
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if user is admin
        if not await verify_admin_status(user_email):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        return await func(*args, **kwargs)
    return wrapper

async def verify_admin_status(user_email: str) -> bool:
    """Verify that the user has admin privileges"""
    try:
        from dependencies.database import get_db
        from models.user import User
        
        db = get_db()
        user = db.query(User).filter(User.email == user_email).first()
        
        return user and user.is_admin
        
    except Exception as e:
        print(f"Error verifying admin status: {e}")
        return False

def check_resource_access(resource_type: str, resource_id: str, user_email: str) -> bool:
    """Synchronous function to check resource access (for use in route handlers)"""
    try:
        from dependencies.database import get_db
        from models.expense import Expense
        from models.user import User
        from models.feedback import Feedback
        
        db = get_db()
        
        if resource_type.lower() == "expense":
            expense = db.query(Expense).filter(
                Expense.id == resource_id,
                Expense.user_email == user_email
            ).first()
            return expense is not None
            
        elif resource_type.lower() == "user":
            return resource_id == user_email
            
        elif resource_type.lower() == "feedback":
            feedback = db.query(Feedback).filter(
                Feedback.id == resource_id,
                Feedback.user_email == user_email
            ).first()
            return feedback is not None
            
        else:
            return False
            
    except Exception:
        return False

def validate_user_input(input_data: dict, allowed_fields: list) -> dict:
    """Validate and sanitize user input to prevent injection attacks"""
    sanitized_data = {}
    
    for field in allowed_fields:
        if field in input_data:
            value = input_data[field]
            
            # Basic sanitization
            if isinstance(value, str):
                # Remove potentially dangerous characters
                value = re.sub(r'[<>"\']', '', value)
                # Limit length
                value = value[:1000] if len(value) > 1000 else value
            
            sanitized_data[field] = value
    
    return sanitized_data

def require_authentication(func: Callable) -> Callable:
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get the request object
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            raise HTTPException(status_code=500, detail="Request object not found")
        
        # Get user email from token
        user_email = get_user_email_from_token(request)
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return await func(*args, **kwargs)
    return wrapper

# Helper function for route handlers
def get_current_user_email(request: Request) -> str:
    """Get current user email from request (for use in route handlers)"""
    user_email = get_user_email_from_token(request)
    if not user_email:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_email

def get_current_user_id(request: Request) -> int:
    """Get current user ID from request (for use in route handlers)"""
    user_id = get_user_id_from_token(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id

# Routes that don't require authentication
PUBLIC_ROUTES = [
    "/",
    "/health",
    "/api/health/detailed",
    "/api/status",
    "/api/v1/capture-email",
    "/robots.txt",
    "/static",
    "/favicon.ico",
    "/docs",
    "/openapi.json",
    "/redoc",
    # Auth routes
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
    # Landing page routes
    "/api/waitlist",
    "/api/cora-chat"
]

def setup_authorization(app):
    """Setup authorization middleware for the application"""
    
    @app.middleware("http")
    async def authorize_request(request: Request, call_next):
        """Check authorization for protected routes"""
        path = request.url.path
        
        # Allow public routes
        if any(path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)
        
        # Allow OPTIONS requests for CORS
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Check for authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid authorization header"}
            )
        
        # Extract and validate token
        token = auth_header.split(" ")[1]
        try:
            # Decode token and add user info to request state
            from dependencies.auth import decode_token
            user_data = decode_token(token)
            request.state.user_email = user_data.get("email", user_data.get("sub"))
            request.state.user_data = user_data
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"}
            )
        
        # Continue with the request
        response = await call_next(request)
        return response