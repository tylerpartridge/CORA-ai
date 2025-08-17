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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SendGrid API key - Get from environment variable
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@coraai.tech")

def send_email(to_email: str, subject: str, body: str, html_body: Optional[str] = None, attachment_path: Optional[str] = None) -> bool:
    """Send email using SendGrid API with optional PDF attachment"""
    print(f"[SEND_EMAIL] Called for {to_email} with subject: {subject}")
    try:
        # Check if API key is configured
        if not SENDGRID_API_KEY:
            print("[SEND_EMAIL] ERROR: SendGrid API key not configured")
            return False
        print(f"[SEND_EMAIL] API key present: {SENDGRID_API_KEY[:10]}...")
            
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {
                "email": FROM_EMAIL,
                "name": "CORA Support"  # Add sender name for better reputation
            },
            "reply_to": {
                "email": FROM_EMAIL,
                "name": "CORA Support"
            },
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}]
        }
        
        if html_body:
            payload["content"].append({"type": "text/html", "value": html_body})
        
        # Add PDF attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as f:
                    attachment_content = f.read()
                    import base64
                    encoded_content = base64.b64encode(attachment_content).decode('utf-8')
                    
                    attachment = {
                        "content": encoded_content,
                        "type": "application/pdf",
                        "filename": os.path.basename(attachment_path),
                        "disposition": "attachment"
                    }
                    
                    payload["attachments"] = [attachment]
                    print(f"Added PDF attachment: {os.path.basename(attachment_path)}")
            except Exception as e:
                print(f"Failed to add attachment: {str(e)}")
                # Continue without attachment rather than failing the email
        
        print(f"[SEND_EMAIL] Sending request to SendGrid...")
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )
        
        success = response.status_code == 202
        print(f"[SEND_EMAIL] SendGrid response: {response.status_code}")
        if not success:
            print(f"[SEND_EMAIL] ERROR: SendGrid returned status {response.status_code}: {response.text}")
        else:
            print(f"[SEND_EMAIL] SUCCESS: Email queued for delivery to {to_email}")
        return success
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

def send_email_verification(to_email: str, verification_token: str, user_name: str = None) -> bool:
    """Send email verification email to new users"""
    print(f"[EMAIL SERVICE] send_email_verification called for {to_email}")
    subject = "Welcome to CORA - Please verify your email"  # Remove emoji from subject (spam trigger)
    
    greeting = f"Hello {user_name}!" if user_name else "Hello!"
    # Get base URL from environment for production
    base_url = os.getenv("BASE_URL", "http://localhost:8001")
    verification_url = f"{base_url}/verify-email?token={verification_token}"
    resend_url = f"{base_url}/resend-verification?email={to_email}"
    print(f"[EMAIL SERVICE] URLs generated - verify: {verification_url[:50]}...")
    
    body = f"""
{greeting}

Thank you for signing up for CORA! We're excited to help you manage your construction business finances with AI.

Please verify your email address to activate your account:
{verification_url}

This link will expire in 24 hours for security reasons.

If you don't see the verification email, check your spam folder or request a new one at:
{resend_url}

If you didn't create an account with CORA, please ignore this email.

Best regards,
The CORA Team
"""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333; margin: 0; padding: 0; background-color: #f4f4f4;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f4f4f4; padding: 20px 0;">
            <tr>
                <td align="center">
                    <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background-color: #FF9800; padding: 40px 30px; text-align: center;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Welcome to CORA!</h1>
                                <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px;">Your AI Financial Assistant</p>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <p style="font-size: 18px; margin: 0 0 20px 0; color: #333333;"><strong>{greeting}</strong></p>
                                
                                <p style="font-size: 16px; margin: 0 0 25px 0; color: #555555;">
                                    Thank you for signing up for CORA! We're excited to help you manage your business finances with AI-powered insights and automation.
                                </p>
                                
                                <!-- Features Box -->
                                <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #FFF3E0; border: 1px solid #FFB74D; border-radius: 8px; margin: 0 0 30px 0;">
                                    <tr>
                                        <td style="padding: 20px;">
                                            <h3 style="margin: 0 0 15px 0; color: #FF9800; font-size: 18px;">What you'll get with CORA:</h3>
                                            <ul style="margin: 0; padding-left: 20px; color: #555555;">
                                                <li style="margin-bottom: 8px;"><strong>AI Expense Tracking</strong> - Smart categorization</li>
                                                <li style="margin-bottom: 8px;"><strong>Real-time Insights</strong> - See profitability instantly</li>
                                                <li style="margin-bottom: 8px;"><strong>Voice Entry</strong> - Add expenses by talking</li>
                                                <li style="margin-bottom: 8px;"><strong>Smart Reports</strong> - AI-powered recommendations</li>
                                            </ul>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="font-size: 16px; margin: 0 0 25px 0; color: #333333;">
                                    <strong>Please verify your email address to activate your account:</strong>
                                </p>
                                
                                <!-- CTA Button -->
                                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                    <tr>
                                        <td align="center" style="padding: 20px 0;">
                                            <a href="{verification_url}" 
                                               style="background-color: #FF9800; color: #ffffff; padding: 15px 35px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px; display: inline-block;">
                                                Verify My Email Address
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Security Notice -->
                                <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 30px 0;">
                                    <tr>
                                        <td style="background-color: #f7f7f7; padding: 20px; border-left: 4px solid #FF9800;">
                                            <p style="margin: 0 0 10px 0; font-weight: bold; color: #333333;">Security Notice:</p>
                                            <p style="margin: 0; font-size: 14px; color: #666666; line-height: 1.8;">
                                                • This verification link expires in 24 hours<br>
                                                • If the button doesn't work, copy and paste this link:<br>
                                                <a href="{verification_url}" style="color: #FF9800; word-break: break-all;">{verification_url}</a>
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Help Section -->
                                <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 20px 0;">
                                    <tr>
                                        <td style="background-color: #E3F2FD; padding: 15px; border-radius: 5px;">
                                            <p style="margin: 0; font-size: 14px; color: #1976D2;">
                                                <strong>Need Help?</strong> Check your spam folder first. If you still don't see the email, 
                                                <a href="{resend_url}" style="color: #1976D2;">click here to request a new verification email</a>.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f7f7f7; padding: 25px 30px; text-align: center; border-top: 1px solid #e0e0e0;">
                                <p style="margin: 0 0 10px 0; font-size: 14px; color: #666666;">
                                    If you didn't create an account with CORA, please ignore this email.
                                </p>
                                <p style="margin: 0; font-size: 12px; color: #999999;">
                                    © 2025 CORA AI. Built to help you succeed.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    result = send_email(to_email, subject, body, html_body)
    print(f"[EMAIL SERVICE] send_email_verification result: {result}")
    return result

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

def send_feedback_notification(feedback, user_email: str) -> bool:
    """Send notification to admin when user submits feedback"""
    subject = f"New Feedback: {feedback.title} - CORA"
    
    body = f"""
New feedback submitted by {user_email}

Category: {feedback.category}
Priority: {feedback.priority}
Title: {feedback.title}
Description: {feedback.description}

Page URL: {feedback.page_url or 'N/A'}
User Agent: {feedback.user_agent or 'N/A'}

Review at: https://coraai.tech/admin/feedback

Best regards,
CORA System
"""
    
    # Send to admin email (you can configure this)
    admin_email = os.getenv("ADMIN_EMAIL", "admin@coraai.tech")
    
    return send_email(admin_email, subject, body) 