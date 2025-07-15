#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/email_service.py
🎯 PURPOSE: Email service using SendGrid for password reset and notifications
🔗 IMPORTS: requests, os
📤 EXPORTS: send_email, send_password_reset_email, send_welcome_email
"""

import requests
import os
from typing import Optional

# SendGrid API key - TODO: Move to environment variable
SENDGRID_API_KEY = "ALxDBEHhSR2DWekJ_Bf-qw"
FROM_EMAIL = "noreply@coraai.tech"

def send_email(to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
    """Send email using SendGrid API"""
    try:
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": FROM_EMAIL},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }
        
        if html_body:
            payload["content"].append({"type": "text/html", "value": html_body})
        
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )
        
        return response.status_code == 202
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def send_password_reset_email(to_email: str, reset_token: str, reset_url: str) -> bool:
    """Send password reset email"""
    subject = "Reset Your CORA Password"
    body = f"""
Hello!

You requested a password reset for your CORA account.

Click this link to reset your password: {reset_url}

If you didn't request this, please ignore this email.

This link will expire in 24 hours.

Best regards,
The CORA Team
"""
    
    html_body = f"""
    <html>
    <body>
        <h2>Reset Your CORA Password</h2>
        <p>Hello!</p>
        <p>You requested a password reset for your CORA account.</p>
        <p><a href="{reset_url}" style="background: #8B00FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>If you didn't request this, please ignore this email.</p>
        <p>This link will expire in 24 hours.</p>
        <br>
        <p>Best regards,<br>The CORA Team</p>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, body, html_body)

def send_welcome_email(to_email: str, user_name: str = None) -> bool:
    """Send welcome email to new users"""
    subject = "Welcome to CORA - Your AI Bookkeeping Assistant"
    
    greeting = f"Hello {user_name}!" if user_name else "Hello!"
    
    body = f"""
{greeting}

Welcome to CORA! We're excited to have you on board.

CORA is your AI-powered bookkeeping assistant designed specifically for introverted founders who want to focus on their business, not paperwork.

Here's what you can do with CORA:
• Track expenses with AI-powered categorization
• Generate expense reports and insights
• Connect with your bank accounts (coming soon)
• Export data for tax time

Get started by adding your first expense at: https://coraai.tech/dashboard

If you have any questions, just reply to this email.

Best regards,
The CORA Team
"""
    
    html_body = f"""
    <html>
    <body>
        <h2>Welcome to CORA!</h2>
        <p>{greeting}</p>
        <p>Welcome to CORA! We're excited to have you on board.</p>
        <p>CORA is your AI-powered bookkeeping assistant designed specifically for introverted founders who want to focus on their business, not paperwork.</p>
        
        <h3>Here's what you can do with CORA:</h3>
        <ul>
            <li>Track expenses with AI-powered categorization</li>
            <li>Generate expense reports and insights</li>
            <li>Connect with your bank accounts (coming soon)</li>
            <li>Export data for tax time</li>
        </ul>
        
        <p><a href="https://coraai.tech/dashboard" style="background: #8B00FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Get Started</a></p>
        
        <p>If you have any questions, just reply to this email.</p>
        <br>
        <p>Best regards,<br>The CORA Team</p>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, body, html_body)

def send_feedback_confirmation(to_email: str, feedback_id: int) -> bool:
    """Send confirmation email when user submits feedback"""
    subject = "Thank You for Your Feedback - CORA"
    body = f"""
Thank you for your feedback!

We've received your feedback (ID: {feedback_id}) and our team will review it shortly.

Your input helps us make CORA better for all users.

Best regards,
The CORA Team
"""
    
    return send_email(to_email, subject, body) 