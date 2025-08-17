#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/account_lockout.py
🎯 PURPOSE: Account lockout middleware to prevent brute force attacks
🔗 IMPORTS: FastAPI, time, datetime
📤 EXPORTS: setup_account_lockout, check_account_lockout, record_failed_attempt
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

# Account lockout storage (in production, use Redis)
failed_attempts: Dict[str, Dict[str, any]] = {}

# Configuration
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes
RESET_WINDOW = 3600  # 1 hour - reset counter after this time

def record_failed_attempt(email: str, ip_address: str = None):
    """Record a failed login attempt"""
    current_time = time.time()
    
    if email not in failed_attempts:
        failed_attempts[email] = {
            'attempts': [],
            'locked_until': None,
            'last_attempt': None
        }
    
    user_data = failed_attempts[email]
    
    # Clean old attempts outside the reset window
    user_data['attempts'] = [
        attempt for attempt in user_data['attempts']
        if current_time - attempt['timestamp'] < RESET_WINDOW
    ]
    
    # Add new failed attempt
    user_data['attempts'].append({
        'timestamp': current_time,
        'ip_address': ip_address
    })
    
    user_data['last_attempt'] = current_time
    
    # Check if account should be locked
    if len(user_data['attempts']) >= MAX_FAILED_ATTEMPTS:
        user_data['locked_until'] = current_time + LOCKOUT_DURATION

def record_successful_attempt(email: str):
    """Record a successful login attempt and reset counter"""
    if email in failed_attempts:
        failed_attempts[email] = {
            'attempts': [],
            'locked_until': None,
            'last_attempt': None
        }

def check_account_lockout(email: str) -> Optional[str]:
    """Check if account is locked and return lockout message if so"""
    if email not in failed_attempts:
        return None
    
    user_data = failed_attempts[email]
    current_time = time.time()
    
    # Check if account is currently locked
    if user_data['locked_until'] and current_time < user_data['locked_until']:
        remaining_time = int(user_data['locked_until'] - current_time)
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        return f"Account locked due to too many failed attempts. Try again in {minutes}m {seconds}s."
    
    # If lockout period has expired, clear the lock
    if user_data['locked_until'] and current_time >= user_data['locked_until']:
        user_data['locked_until'] = None
    
    return None

def get_remaining_attempts(email: str) -> int:
    """Get number of remaining login attempts before lockout"""
    if email not in failed_attempts:
        return MAX_FAILED_ATTEMPTS
    
    user_data = failed_attempts[email]
    current_time = time.time()
    
    # Clean old attempts
    user_data['attempts'] = [
        attempt for attempt in user_data['attempts']
        if current_time - attempt['timestamp'] < RESET_WINDOW
    ]
    
    return max(0, MAX_FAILED_ATTEMPTS - len(user_data['attempts']))

async def account_lockout_middleware(request: Request, call_next):
    """Account lockout middleware"""
    
    # Only apply to login endpoint
    if request.url.path != "/api/auth/login":
        response = await call_next(request)
        return response
    
    # For GET requests, just pass through
    if request.method == "GET":
        response = await call_next(request)
        return response
    
    # For POST requests, check lockout status
    if request.method == "POST":
        try:
            # Parse form data to get email
            form_data = await request.form()
            email = form_data.get("username")  # OAuth2 form uses "username" for email
            
            if email:
                # Check if account is locked
                lockout_message = check_account_lockout(email)
                if lockout_message:
                    return JSONResponse(
                        status_code=423,  # Locked
                        content={
                            "error": "Account locked",
                            "message": lockout_message,
                            "remaining_attempts": 0
                        }
                    )
                
                # Get remaining attempts
                remaining_attempts = get_remaining_attempts(email)
                
                # Add remaining attempts to response headers
                response = await call_next(request)
                response.headers["X-Remaining-Attempts"] = str(remaining_attempts)
                
                return response
            else:
                # No email provided, pass through
                response = await call_next(request)
                return response
                
        except Exception as e:
            # If parsing fails, pass through
            response = await call_next(request)
            return response
    
    response = await call_next(request)
    return response

def setup_account_lockout(app):
    """Setup account lockout for the FastAPI app"""
    app.middleware("http")(account_lockout_middleware)
    
    # Clean up old data periodically
    def cleanup_old_data():
        current_time = time.time()
        expired_users = []
        
        for email, user_data in failed_attempts.items():
            # Remove attempts older than reset window
            user_data['attempts'] = [
                attempt for attempt in user_data['attempts']
                if current_time - attempt['timestamp'] < RESET_WINDOW
            ]
            
            # Clear expired lockouts
            if user_data['locked_until'] and current_time >= user_data['locked_until']:
                user_data['locked_until'] = None
            
            # Remove users with no recent activity
            if not user_data['attempts'] and not user_data['locked_until']:
                expired_users.append(email)
        
        for email in expired_users:
            del failed_attempts[email]
    
    # Note: Periodic cleanup is disabled for now to avoid asyncio issues
    # In production, use a proper task scheduler or background worker 