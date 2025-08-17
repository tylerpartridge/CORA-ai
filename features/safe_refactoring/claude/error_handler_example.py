#!/usr/bin/env python3
"""
Example: Converting a route to use Smart Error Handler
Shows before and after for clarity
"""

# ============================================
# BEFORE: Generic error handling
# ============================================
"""
@router.get("/user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        print(f"Error: {e}")  # Poor logging
        raise HTTPException(status_code=500, detail="Internal server error")
"""

# ============================================
# AFTER: Smart error handling
# ============================================
from utils.smart_error_handler import error_handler, log_info
from utils.error_constants import STATUS_NOT_FOUND, ErrorMessages

@router.get("/user/{user_id}")
@error_handler.safe_route  # Automatic error handling
async def get_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    # Log the request
    log_info("Fetching user", user_id=user_id, client=request.client.host)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # This will be caught and handled properly
        raise HTTPException(
            status_code=STATUS_NOT_FOUND, 
            detail=ErrorMessages.not_found("user")
        )
    
    log_info("User fetched successfully", user_id=user_id)
    return user
    # Any unexpected error will be automatically handled with context!


# ============================================
# BENEFITS
# ============================================
"""
1. Automatic error handling with context
2. Consistent error responses
3. Better logging with structured data
4. Recovery suggestions for users
5. Error statistics tracking
6. Development vs production modes
7. No more generic "Internal server error"
8. Helps debugging immensely
"""

# ============================================
# ERROR RESPONSE EXAMPLE
# ============================================
"""
Instead of:
{
    "detail": "Internal server error"
}

You get:
{
    "error": {
        "message": "Database connection error",
        "type": "OperationalError",
        "suggestion": "Database connection issue - check if database is running"
    }
}

And in development mode, also:
{
    "debug": {
        "traceback": "...",
        "request": {
            "method": "GET",
            "path": "/api/user/123",
            "client": "192.168.1.1"
        }
    }
}
"""