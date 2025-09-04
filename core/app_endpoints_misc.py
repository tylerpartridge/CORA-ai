#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/app_endpoints_misc.py
🎯 PURPOSE: Misc/user-facing endpoints split from app.py to satisfy size guidelines
🔗 IMPORTS: FastAPI, models, services
📤 EXPORTS: register_misc_endpoints(app)
"""

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from dependencies.database import get_db
from models import User
from services.auth_service import create_email_verification_token, verify_email_token
from services.email_service import send_email_verification, send_email
from utils.logging_config import get_logger

logger = get_logger(__name__)


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str
    phone: Optional[str] = None
    company: Optional[str] = None
    subject: Optional[str] = None


def register_misc_endpoints(app: FastAPI) -> None:
    """Register miscellaneous public endpoints (contact, robots) and auth utilities."""

    @app.get("/robots.txt")
    async def robots():
        content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /dashboard/
Sitemap: https://coraai.tech/sitemap.xml
"""
        return Response(content=content, media_type="text/plain")

    @app.post("/api/contact")
    async def contact_form(request: ContactRequest):
        try:
            if os.getenv("SENDGRID_API_KEY"):
                await send_email(
                    to_email=os.getenv("CONTACT_FORM_EMAIL", "contact@coraai.tech"),
                    subject=f"Contact Form: {request.subject or 'New Inquiry'}",
                    html_content=(
                        f"<h2>New Contact Form Submission</h2>"
                        f"<p><strong>Name:</strong> {request.name}</p>"
                        f"<p><strong>Email:</strong> {request.email}</p>"
                        f"<p><strong>Phone:</strong> {request.phone or 'Not provided'}</p>"
                        f"<p><strong>Company:</strong> {request.company or 'Not provided'}</p>"
                        f"<p><strong>Message:</strong></p>"
                        f"<p>{request.message}</p>"
                    ),
                )
            return JSONResponse(status_code=200, content={"success": True, "message": "Thank you for contacting us! We'll get back to you soon."})
        except Exception as e:
            logger.error(f"Contact form error: {str(e)}")
            return JSONResponse(status_code=500, content={"success": False, "message": "Sorry, there was an error sending your message. Please try again."})

    @app.get("/verify-email")
    async def verify_email_endpoint(token: str, db: Session = Depends(get_db)):
        try:
            email = verify_email_token(token)
            if not email:
                raise HTTPException(status_code=400, detail="Invalid or expired verification token")

            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if user.email_verified == "true":
                return RedirectResponse(url="/login?message=already_verified", status_code=302)

            user.email_verified = "true"
            user.email_verified_at = datetime.utcnow()
            user.is_active = "true"
            db.commit()
            logger.info(f"Email verified for user: {email}")
            return RedirectResponse(url="/login?message=email_verified", status_code=302)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            raise HTTPException(status_code=500, detail="Verification failed")

    @app.get("/resend-verification")
    async def resend_verification_endpoint(email: str, db: Session = Depends(get_db)):
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return JSONResponse(status_code=200, content={"message": "If an account exists, a verification email will be sent."})

            if user.email_verified == "true":
                return JSONResponse(status_code=200, content={"message": "Email is already verified."})

            token = create_email_verification_token(email)
            verification_sent = await send_email_verification(email, token)

            if verification_sent:
                return JSONResponse(status_code=200, content={"message": "Verification email sent successfully."})
            else:
                raise HTTPException(status_code=500, detail="Failed to send verification email")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Resend verification error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to resend verification")


