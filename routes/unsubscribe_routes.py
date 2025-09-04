#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/unsubscribe_routes.py
🎯 PURPOSE: Public unsubscribe endpoints split from settings to reduce file size
🔗 IMPORTS: FastAPI, models, dependencies
📤 EXPORTS: unsubscribe_router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import logging

from models import get_db, User
from dependencies.auth import verify_unsubscribe_token

logger = logging.getLogger(__name__)


# Public unsubscribe route (no auth required, uses token)
unsubscribe_router = APIRouter(
    tags=["Unsubscribe"],
    responses={404: {"description": "Not found"}},
)


@unsubscribe_router.get("/unsubscribe")
async def unsubscribe_via_link(
    token: str = Query(..., description="Unsubscribe token from email"),
    db: Session = Depends(get_db)
):
    """
    Unsubscribe from weekly insights via email link.
    """
    try:
        # Verify and decode the token
        user_id = verify_unsubscribe_token(token)

        # Get the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update opt-in preference
        user.weekly_insights_opt_in = "false"
        db.commit()

        logger.info(f"User {user.email} unsubscribed via email link")

        # Return a simple confirmation page
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unsubscribed - CORA</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 400px;
                }
                h1 {
                    color: #9B6EC8;
                    margin-bottom: 20px;
                }
                p {
                    color: #666;
                    line-height: 1.6;
                }
                .success-icon {
                    font-size: 48px;
                    margin-bottom: 20px;
                }
                a {
                    color: #9B6EC8;
                    text-decoration: none;
                    font-weight: bold;
                }
                a:hover {
                    text-decoration: underline;
                }
                .button {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: #9B6EC8;
                    color: white;
                    border-radius: 6px;
                    text-decoration: none;
                    transition: background 0.2s;
                }
                .button:hover {
                    background: #7C3AED;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>Successfully Unsubscribed</h1>
                <p>
                    You've been unsubscribed from weekly insights emails.
                    You won't receive these reports anymore.
                </p>
                <p style="margin-top: 30px; font-size: 14px;">
                    Changed your mind? You can re-enable weekly insights
                    anytime from your account settings.
                </p>
                <a href="/" class="button">Go to Dashboard</a>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except ValueError as e:
        # Invalid or expired token
        logger.warning(f"Invalid unsubscribe token: {str(e)}")

        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invalid Link - CORA</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 400px;
                }
                h1 {
                    color: #ef4444;
                    margin-bottom: 20px;
                }
                p {
                    color: #666;
                    line-height: 1.6;
                }
                .error-icon {
                    font-size: 48px;
                    margin-bottom: 20px;
                }
                a {
                    color: #9B6EC8;
                    text-decoration: none;
                    font-weight: bold;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Invalid or Expired Link</h1>
                <p>
                    This unsubscribe link is invalid or has expired.
                    Links are valid for 7 days after being sent.
                </p>
                <p style="margin-top: 30px; font-size: 14px;">
                    To manage your email preferences, please
                    <a href="/login">log in to your account</a>
                    and visit the settings page.
                </p>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=error_html, status_code=400)
    except Exception as e:
        logger.error(f"Error processing unsubscribe link: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process unsubscribe request")


