#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/user_activity.py
🎯 PURPOSE: Middleware to log user actions for analytics
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from models import UserActivity, get_db
from dependencies.auth import get_current_user
import asyncio

TRACKED_PATHS = [
    ("POST", "/api/auth/login", "login"),
    ("POST", "/api/auth/register", "register"),
    ("POST", "/api/expenses", "create_expense"),
    ("PUT", "/api/expenses/", "update_expense"),
    ("DELETE", "/api/expenses/", "delete_expense"),
    ("POST", "/api/onboarding/feedback", "submit_feedback"),
]

class UserActivityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        method = request.method
        matched = None
        for m, p, action in TRACKED_PATHS:
            if method == m and path.startswith(p):
                matched = action
                break
        if matched:
            try:
                # Try to get user from request.state or JWT
                user_email = None
                try:
                    user = await get_current_user(request)
                    user_email = user.email
                except Exception:
                    # Fallback: try to parse from form or JSON
                    if "username" in await request.form():
                        user_email = (await request.form())["username"]
                if user_email:
                    # Use DB session
                    db_gen = get_db()
                    db = next(db_gen)
                    activity = UserActivity(
                        user_email=user_email,
                        action=matched,
                        details=path
                    )
                    db.add(activity)
                    db.commit()
                    db.close()
            except Exception as e:
                # Don't block request on logging failure
                pass
        return response

def setup_user_activity(app):
    app.add_middleware(UserActivityMiddleware)
    return app 