#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/auth_security_enhanced.py
🎯 PURPOSE: Enhanced authentication security middleware for session management and rate limiting
🔗 IMPORTS: FastAPI, time, hashlib, secrets
📤 EXPORTS: AuthSecurityMiddleware, SessionManager, RateLimitManager
"""

import time
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logging_config import get_logger
from utils.error_handler import AuthenticationException, RateLimitException

logger = get_logger(__name__)

class SessionManager:
    """Enhanced session management with security features"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_user = 3
        self.session_rotation_interval = 1800  # 30 minutes
    
    def create_session(self, user_email: str, user_data: Dict[str, Any]) -> str:
        """Create a new secure session"""
        # Clean up old sessions for this user
        self._cleanup_user_sessions(user_email)
        
        # Check session limit
        user_sessions = [s for s in self.sessions.values() if s.get('user_email') == user_email]
        if len(user_sessions) >= self.max_sessions_per_user:
            # Remove oldest session
            oldest_session = min(user_sessions, key=lambda x: x.get('created_at', 0))
            session_id = oldest_session.get('session_id')
            if session_id:
                self.sessions.pop(session_id, None)
        
        # Generate secure session ID
        session_id = self._generate_session_id()
        
        # Create session data
        session_data = {
            'session_id': session_id,
            'user_email': user_email,
            'user_data': user_data,
            'created_at': time.time(),
            'last_activity': time.time(),
            'ip_address': None,  # Will be set by middleware
            'user_agent': None,  # Will be set by middleware
            'is_active': True
        }
        
        self.sessions[session_id] = session_data
        logger.info(f"Session created for user: {user_email}")
        
        return session_id
    
    def validate_session(self, session_id: str, request: Request) -> Optional[Dict[str, Any]]:
        """Validate session and update activity"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if not session.get('is_active'):
            return None
        
        # Check session timeout
        if time.time() - session.get('last_activity', 0) > self.session_timeout:
            self.sessions.pop(session_id, None)
            return None
        
        # Update last activity
        session['last_activity'] = time.time()
        
        # Check for session rotation
        if time.time() - session.get('created_at', 0) > self.session_rotation_interval:
            session['created_at'] = time.time()
            logger.info(f"Session rotated for user: {session.get('user_email')}")
        
        return session.get('user_data')
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session"""
        if session_id in self.sessions:
            self.sessions.pop(session_id, None)
            logger.info(f"Session invalidated: {session_id}")
            return True
        return False
    
    def invalidate_user_sessions(self, user_email: str) -> int:
        """Invalidate all sessions for a user"""
        count = 0
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.get('user_email') == user_email:
                sessions_to_remove.append(session_id)
                count += 1
        
        for session_id in sessions_to_remove:
            self.sessions.pop(session_id, None)
        
        logger.info(f"Invalidated {count} sessions for user: {user_email}")
        return count
    
    def _generate_session_id(self) -> str:
        """Generate a secure session ID"""
        return secrets.token_urlsafe(32)
    
    def _cleanup_user_sessions(self, user_email: str) -> None:
        """Clean up expired sessions for a user"""
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if (session.get('user_email') == user_email and 
                time.time() - session.get('last_activity', 0) > self.session_timeout):
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.sessions.pop(session_id, None)

class RateLimitManager:
    """Enhanced rate limiting with adaptive limits"""
    
    def __init__(self):
        self.attempts: Dict[str, Dict[str, Any]] = {}
        self.base_limits = {
            'login': {'max_attempts': 5, 'window': 300, 'lockout_duration': 900},
            'password_reset': {'max_attempts': 3, 'window': 3600, 'lockout_duration': 3600},
            'api': {'max_attempts': 100, 'window': 60, 'lockout_duration': 300},
            'file_upload': {'max_attempts': 10, 'window': 60, 'lockout_duration': 300}
        }
    
    def check_rate_limit(self, key: str, limit_type: str = 'api') -> Tuple[bool, Optional[str]]:
        """Check if request is within rate limits"""
        current_time = time.time()
        limits = self.base_limits.get(limit_type, self.base_limits['api'])
        
        if key not in self.attempts:
            self.attempts[key] = {
                'count': 0,
                'first_attempt': current_time,
                'last_attempt': current_time,
                'lockout_until': 0
            }
        
        attempt_data = self.attempts[key]
        
        # Check if currently locked out
        if current_time < attempt_data['lockout_until']:
            remaining_lockout = int(attempt_data['lockout_until'] - current_time)
            return False, f"Rate limit exceeded. Try again in {remaining_lockout} seconds."
        
        # Reset if window has passed
        if current_time - attempt_data['first_attempt'] > limits['window']:
            attempt_data['count'] = 0
            attempt_data['first_attempt'] = current_time
        
        # Check if limit exceeded
        if attempt_data['count'] >= limits['max_attempts']:
            # Apply lockout
            attempt_data['lockout_until'] = current_time + limits['lockout_duration']
            return False, f"Rate limit exceeded. Account locked for {limits['lockout_duration']} seconds."
        
        # Update attempt data
        attempt_data['count'] += 1
        attempt_data['last_attempt'] = current_time
        
        return True, None
    
    def get_remaining_attempts(self, key: str, limit_type: str = 'api') -> int:
        """Get remaining attempts for a key"""
        if key not in self.attempts:
            limits = self.base_limits.get(limit_type, self.base_limits['api'])
            return limits['max_attempts']
        
        attempt_data = self.attempts[key]
        limits = self.base_limits.get(limit_type, self.base_limits['api'])
        
        # Reset if window has passed
        if time.time() - attempt_data['first_attempt'] > limits['window']:
            return limits['max_attempts']
        
        return max(0, limits['max_attempts'] - attempt_data['count'])

class AuthSecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced authentication security middleware"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.session_manager = SessionManager()
        self.rate_limit_manager = RateLimitManager()
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get('user-agent', 'unknown')
        
        # Create rate limit key
        rate_limit_key = f"{client_ip}:{request.url.path}"
        
        # Check rate limits for sensitive endpoints
        if self._is_sensitive_endpoint(request.url.path):
            limit_type = self._get_limit_type(request.url.path)
            allowed, message = self.rate_limit_manager.check_rate_limit(rate_limit_key, limit_type)
            
            if not allowed:
                logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": message,
                        "retry_after": 60
                    },
                    headers={"Retry-After": "60"}
                )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add rate limit headers
        if self._is_sensitive_endpoint(request.url.path):
            remaining = self.rate_limit_manager.get_remaining_attempts(rate_limit_key, self._get_limit_type(request.url.path))
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, handling proxies"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_sensitive_endpoint(self, path: str) -> bool:
        """Check if endpoint is sensitive and needs rate limiting"""
        sensitive_paths = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/auth/password-reset',
            '/api/auth/forgot-password',
            '/login',
            '/signup',
            '/api/upload',
            '/api/admin'
        ]
        
        return any(path.startswith(sensitive_path) for sensitive_path in sensitive_paths)
    
    def _get_limit_type(self, path: str) -> str:
        """Get rate limit type for endpoint"""
        if path.startswith('/api/auth/login'):
            return 'login'
        elif path.startswith('/api/auth/password-reset') or path.startswith('/api/auth/forgot-password'):
            return 'password_reset'
        elif path.startswith('/api/upload'):
            return 'file_upload'
        elif path.startswith('/api/admin'):
            return 'api'
        else:
            return 'api'

# Global instances
session_manager = SessionManager()
rate_limit_manager = RateLimitManager()

def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    return session_manager

def get_rate_limit_manager() -> RateLimitManager:
    """Get global rate limit manager instance"""
    return rate_limit_manager 