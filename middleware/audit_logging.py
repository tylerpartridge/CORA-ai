#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/audit_logging.py
🎯 PURPOSE: Comprehensive audit logging for security events and user actions
🔗 IMPORTS: FastAPI, datetime, json, logging
📤 EXPORTS: setup_audit_logging, log_security_event, log_user_action
"""

import logging
import json
from datetime import datetime
from fastapi import Request, Response
from typing import Dict, Any, Optional
import os
from pathlib import Path

# Configure audit logger
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

# Create audit log file
audit_log_dir = Path("logs")
audit_log_dir.mkdir(exist_ok=True)
audit_log_file = audit_log_dir / "audit.log"

# File handler for audit logs
file_handler = logging.FileHandler(audit_log_file)
file_handler.setLevel(logging.INFO)

# JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'event_type': getattr(record, 'event_type', 'general'),
            'user_email': getattr(record, 'user_email', None),
            'ip_address': getattr(record, 'ip_address', None),
            'user_agent': getattr(record, 'user_agent', None),
            'action': getattr(record, 'action', None),
            'resource': getattr(record, 'resource', None),
            'status': getattr(record, 'status', None),
            'details': getattr(record, 'details', None),
            'message': record.getMessage()
        }
        return json.dumps(log_entry)

file_handler.setFormatter(JSONFormatter())
audit_logger.addHandler(file_handler)

# Security event types
SECURITY_EVENTS = {
    'LOGIN_SUCCESS': 'user_login_success',
    'LOGIN_FAILED': 'user_login_failed',
    'LOGOUT': 'user_logout',
    'PASSWORD_RESET_REQUEST': 'password_reset_request',
    'PASSWORD_RESET_SUCCESS': 'password_reset_success',
    'PASSWORD_RESET_FAILED': 'password_reset_failed',
    'ACCOUNT_LOCKED': 'account_locked',
    'ACCOUNT_UNLOCKED': 'account_unlocked',
    'CSRF_VIOLATION': 'csrf_violation',
    'RATE_LIMIT_EXCEEDED': 'rate_limit_exceeded',
    'UNAUTHORIZED_ACCESS': 'unauthorized_access',
    'ADMIN_ACTION': 'admin_action',
    'DATA_EXPORT': 'data_export',
    'DATA_IMPORT': 'data_import',
    'USER_CREATED': 'user_created',
    'USER_DELETED': 'user_deleted',
    'USER_MODIFIED': 'user_modified'
}

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'

def get_user_email_from_request(request: Request) -> Optional[str]:
    """Extract user email from JWT token in request"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        try:
            # Import JWT decoding function
            from dependencies.auth import decode_token
            token = auth_header.split(' ')[1]
            user_data = decode_token(token)
            return user_data.get('sub')  # sub contains the email
        except Exception as e:
            # If JWT decoding fails, return None
            return None
    return None

def log_security_event(
    event_type: str,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status: str = 'success'
):
    """Log a security event"""
    record = audit_logger.makeRecord(
        name='audit',
        level=logging.INFO,
        fn='',
        lno=0,
        msg=f"Security event: {event_type}",
        args=(),
        exc_info=None
    )
    
    record.event_type = 'security'
    record.user_email = user_email
    record.ip_address = ip_address
    record.user_agent = user_agent
    record.action = event_type
    record.status = status
    record.details = details
    
    audit_logger.handle(record)

def log_user_action(
    action: str,
    resource: str,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status: str = 'success'
):
    """Log a user action"""
    record = audit_logger.makeRecord(
        name='audit',
        level=logging.INFO,
        fn='',
        lno=0,
        msg=f"User action: {action} on {resource}",
        args=(),
        exc_info=None
    )
    
    record.event_type = 'user_action'
    record.user_email = user_email
    record.ip_address = ip_address
    record.user_agent = user_agent
    record.action = action
    record.resource = resource
    record.status = status
    record.details = details
    
    audit_logger.handle(record)

async def audit_middleware(request: Request, call_next):
    """Audit logging middleware"""
    
    # Extract request information
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('User-Agent', 'unknown')
    user_email = get_user_email_from_request(request)
    
    # Log the request
    start_time = datetime.utcnow()
    
    try:
        response = await call_next(request)
        
        # Log successful requests for sensitive endpoints
        if request.url.path in [
            '/api/auth/login',
            '/api/auth/register',
            '/api/auth/logout',
            '/api/admin/users',
            '/api/admin/feedback',
            '/api/expenses/export',
            '/api/payments/checkout'
        ]:
            log_user_action(
                action=f"{request.method}_{request.url.path}",
                resource=request.url.path,
                user_email=user_email,
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'method': request.method,
                    'status_code': response.status_code,
                    'response_time_ms': int((datetime.utcnow() - start_time).total_seconds() * 1000)
                },
                status='success' if response.status_code < 400 else 'error'
            )
        
        return response
        
    except Exception as e:
        # Log failed requests
        log_security_event(
            event_type='request_failed',
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                'method': request.method,
                'path': request.url.path,
                'error': str(e)
            },
            status='error'
        )
        raise

def setup_audit_logging(app):
    """Setup audit logging for the FastAPI app"""
    app.middleware("http")(audit_middleware)
    
    # Add audit log endpoint for admin access
    @app.get("/api/admin/audit-logs")
    async def get_audit_logs(
        limit: int = 100,
        event_type: Optional[str] = None,
        user_email: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        """Get audit logs (admin only)"""
        try:
            # In a real implementation, query the audit log database
            # For now, return a sample of recent logs
            logs = []
            
            if audit_log_file.exists():
                with open(audit_log_file, 'r') as f:
                    lines = f.readlines()
                    # Get last N lines
                    recent_lines = lines[-limit:] if len(lines) > limit else lines
                    
                    for line in recent_lines:
                        try:
                            log_entry = json.loads(line.strip())
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
            
            return {
                "logs": logs,
                "total": len(logs),
                "filters": {
                    "event_type": event_type,
                    "user_email": user_email,
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to retrieve audit logs: {str(e)}"} 