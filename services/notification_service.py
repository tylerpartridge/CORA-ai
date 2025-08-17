#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/notification_service.py
🎯 PURPOSE: Email and SMS notifications for job alerts
🔗 IMPORTS: SendGrid, Twilio, models
📤 EXPORTS: NotificationService
"""

import os
from typing import Optional, Dict, List
import logging

# Email imports
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logging.warning("SendGrid not installed. Email notifications disabled.")

# SMS imports
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio not installed. SMS notifications disabled.")

from sqlalchemy.orm import Session
from models import User, UserPreference

logger = logging.getLogger(__name__)

class NotificationService:
    """Handle email and SMS notifications for job alerts"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Email configuration
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'alerts@cora.ai')
        self.sendgrid_client = None
        
        if SENDGRID_AVAILABLE and self.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
        
        # SMS configuration
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_from_number = os.getenv('TWILIO_FROM_NUMBER')
        self.twilio_client = None
        
        if TWILIO_AVAILABLE and all([self.twilio_account_sid, self.twilio_auth_token]):
            self.twilio_client = TwilioClient(self.twilio_account_sid, self.twilio_auth_token)
    
    def send_job_alert(
        self,
        user_id: str,
        alert_type: str,
        severity: str,
        job_data: Dict,
        message: str
    ) -> Dict[str, bool]:
        """Send job alert via user's preferred channels"""
        
        # Get user preferences
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User not found: {user_id}")
            return {"email": False, "sms": False}
        
        # Get notification preferences
        prefs = self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
        
        # Default preferences if not set
        email_enabled = True
        sms_enabled = False
        phone_number = None
        
        if prefs:
            email_enabled = prefs.email_notifications
            sms_enabled = prefs.sms_notifications
            phone_number = prefs.phone_number
        
        results = {"email": False, "sms": False}
        
        # Send email if enabled
        if email_enabled and user.email:
            results["email"] = self._send_email_alert(
                to_email=user.email,
                alert_type=alert_type,
                severity=severity,
                job_data=job_data,
                message=message
            )
        
        # Send SMS if enabled and phone available
        if sms_enabled and phone_number:
            results["sms"] = self._send_sms_alert(
                to_phone=phone_number,
                alert_type=alert_type,
                severity=severity,
                job_data=job_data,
                message=message
            )
        
        return results
    
    def _send_email_alert(
        self,
        to_email: str,
        alert_type: str,
        severity: str,
        job_data: Dict,
        message: str
    ) -> bool:
        """Send email alert using SendGrid"""
        
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured. Skipping email.")
            return False
        
        # Determine subject based on severity
        severity_emoji = {
            "critical": "🚨",
            "urgent": "⚠️",
            "warning": "⚡"
        }.get(severity, "📢")
        
        subject = f"{severity_emoji} {job_data.get('name', 'Job')} Alert - {message}"
        
        # Build email content
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #9B6EC8; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">CORA Job Alert</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border: 1px solid #e9ecef;">
                <h2 style="color: #333; margin-top: 0;">{job_data.get('name', 'Unknown Job')}</h2>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="font-size: 18px; color: #dc2626; margin: 0;">
                        <strong>{message}</strong>
                    </p>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                    <div style="background: white; padding: 15px; border-radius: 8px;">
                        <p style="margin: 0; color: #666; font-size: 14px;">Quoted Amount</p>
                        <p style="margin: 5px 0 0 0; font-size: 20px; font-weight: bold;">
                            ${job_data.get('quoted_amount', 0):,.2f}
                        </p>
                    </div>
                    
                    <div style="background: white; padding: 15px; border-radius: 8px;">
                        <p style="margin: 0; color: #666; font-size: 14px;">Current Costs</p>
                        <p style="margin: 5px 0 0 0; font-size: 20px; font-weight: bold;">
                            ${job_data.get('total_costs', 0):,.2f}
                        </p>
                    </div>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;">
                        <strong>Current Margin:</strong> {job_data.get('margin_percent', 0):.1f}%
                        {' (Below 20% target!)' if job_data.get('margin_percent', 0) < 20 else ''}
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{os.getenv('APP_URL', 'https://cora.ai')}/jobs/{job_data.get('id', '')}" 
                       style="background: #9B6EC8; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        View Job Details
                    </a>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                <p>You're receiving this because you have email alerts enabled for job warnings.</p>
                <p><a href="{os.getenv('APP_URL', 'https://cora.ai')}/settings" style="color: #9B6EC8;">
                    Manage notification preferences
                </a></p>
            </div>
        </div>
        """
        
        try:
            message = Mail(
                from_email=Email(self.from_email, "CORA Alerts"),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sendgrid_client.send(message)
            logger.info(f"Email sent to {to_email}. Status: {response.status_code}")
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _send_sms_alert(
        self,
        to_phone: str,
        alert_type: str,
        severity: str,
        job_data: Dict,
        message: str
    ) -> bool:
        """Send SMS alert using Twilio"""
        
        if not self.twilio_client:
            logger.warning("Twilio not configured. Skipping SMS.")
            return False
        
        # Build concise SMS message
        sms_body = f"CORA Alert: {job_data.get('name', 'Job')} - {message}\n"
        sms_body += f"Margin: {job_data.get('margin_percent', 0):.1f}%\n"
        
        if job_data.get('over_budget'):
            sms_body += f"Over budget by ${job_data['over_budget']:,.2f}\n"
        
        sms_body += f"View: {os.getenv('APP_URL', 'cora.ai')}/jobs"
        
        try:
            message = self.twilio_client.messages.create(
                body=sms_body,
                from_=self.twilio_from_number,
                to=to_phone
            )
            
            logger.info(f"SMS sent to {to_phone}. SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: Optional[str] = None) -> bool:
        """Send welcome email to new contractor"""
        
        if not self.sendgrid_client:
            return False
        
        subject = "🚧 Welcome to CORA - Your Construction Financial Assistant"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #9B6EC8; color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">Welcome to CORA!</h1>
                <p style="margin: 10px 0 0 0;">Built by contractors, for contractors</p>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2>Hey {user_name or 'there'}! 👋</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    I'm Tyler, and I built CORA after losing money on jobs for years 
                    because I never knew my real costs until tax time.
                </p>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Here's how to get started in <strong>2 minutes</strong>:
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">1. Add Your First Job (30 seconds)</h3>
                    <p>Click "Add Job" and enter your current project. Just need a name and quoted amount.</p>
                    
                    <h3>2. Try Voice Entry (30 seconds)</h3>
                    <p>Click the 🎤 button and say:<br>
                    <em>"Home Depot receipt [job name] [amount]"</em></p>
                    
                    <h3>3. Check Your Profit (instant)</h3>
                    <p>Ask CORA: <em>"How's the [job name] job doing?"</em></p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.getenv('APP_URL', 'https://cora.ai')}/dashboard" 
                       style="background: #9B6EC8; color: white; padding: 15px 40px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;
                              font-size: 18px;">
                        Start Tracking Jobs
                    </a>
                </div>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
                    <p style="margin: 0;">
                        <strong>🎁 Beta Special:</strong> You're one of our first 10 users! 
                        Free forever if you give us feedback.
                    </p>
                </div>
                
                <p style="margin-top: 30px;">
                    Questions? Just reply to this email. I personally read every one.
                </p>
                
                <p>
                    Happy building,<br>
                    <strong>Tyler</strong><br>
                    <em>Founder, CORA</em>
                </p>
            </div>
        </div>
        """
        
        try:
            message = Mail(
                from_email=Email(self.from_email, "Tyler from CORA"),
                to_emails=To(user_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sendgrid_client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False
    
    @staticmethod
    def send_waitlist_welcome(
        email: str,
        name: str,
        position: int,
        referral_code: str
    ) -> bool:
        """Send welcome email to waitlist signup"""
        
        # Create a temporary notification service
        from database import SessionLocal
        db = SessionLocal()
        service = NotificationService(db)
        
        if not service.sendgrid_client:
            db.close()
            return False
        
        subject = f"🚧 You're #{position} on the CORA waitlist!"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #9B6EC8; color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">Welcome to the CORA Waitlist!</h1>
                <p style="margin: 10px 0 0 0; font-size: 20px;">You're #{position} in line</p>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2>Hey {name}! 👋</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Thanks for signing up! I'm Tyler, the contractor who built CORA after 
                    losing $30k on jobs because I didn't track costs properly.
                </p>
                
                {"<div style='background: #c8e6c9; padding: 15px; border-radius: 8px; margin: 20px 0;'><p style='margin: 0;'><strong>🎉 Great news!</strong> You're in the first 10 - you'll get access within 24 hours!</p></div>" if position <= 10 else f"<p style='font-size: 16px;'>We're adding contractors weekly. You'll be contractor #{position} to get access.</p>"}
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">🚀 Jump the line!</h3>
                    <p>Share your referral code with other contractors:</p>
                    <div style="background: #f0f0f0; padding: 15px; border-radius: 6px; text-align: center;">
                        <code style="font-size: 24px; font-weight: bold;">{referral_code}</code>
                    </div>
                    <p style="margin-top: 10px; color: #666;">
                        Each contractor who signs up with your code moves you up 5 spots!
                    </p>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px;">
                    <h4 style="margin-top: 0;">What to expect:</h4>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Voice expense tracking from your truck</li>
                        <li>Real-time job profitability</li>
                        <li>Know which jobs make money</li>
                        <li>No more spreadsheet hell</li>
                    </ul>
                </div>
                
                <p style="margin-top: 30px;">
                    Questions? Just reply to this email. I read every one personally.
                </p>
                
                <p>
                    See you soon,<br>
                    <strong>Tyler</strong><br>
                    <em>Founder, CORA</em>
                </p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                <p>CORA - Built by contractors, for contractors</p>
            </div>
        </div>
        """
        
        try:
            message = Mail(
                from_email=Email(service.from_email, "Tyler from CORA"),
                to_emails=To(email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = service.sendgrid_client.send(message)
            db.close()
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Failed to send waitlist welcome: {str(e)}")
            db.close()
            return False
    
    @staticmethod
    def send_beta_invitation(email: str, name: str) -> bool:
        """Send beta invitation email"""
        
        from database import SessionLocal
        db = SessionLocal()
        service = NotificationService(db)
        
        if not service.sendgrid_client:
            db.close()
            return False
        
        subject = "🎉 Your CORA Beta Access is Ready!"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #9B6EC8; color: white; padding: 40px; text-align: center;">
                <h1 style="margin: 0; font-size: 32px;">🎉 You're In!</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px;">Welcome to the CORA Beta</p>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2>Congrats {name}! 🚀</h2>
                
                <p style="font-size: 18px; line-height: 1.6;">
                    Your beta access is ready! You're one of the first contractors 
                    to use CORA. Let's get you tracking jobs in 2 minutes.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.getenv('APP_URL', 'https://cora.ai')}/signup?beta=true" 
                       style="background: #10b981; color: white; padding: 20px 50px; 
                              text-decoration: none; border-radius: 8px; display: inline-block;
                              font-size: 20px; font-weight: bold;">
                        Activate Beta Access
                    </a>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Quick Start (2 minutes):</h3>
                    <ol style="line-height: 1.8;">
                        <li><strong>Create your account</strong> - Use this email</li>
                        <li><strong>Add your first job</strong> - Current project name + quote</li>
                        <li><strong>Try voice entry</strong> - "Home Depot receipt [job] [amount]"</li>
                        <li><strong>Check profit</strong> - "How's the [job] doing?"</li>
                    </ol>
                </div>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
                    <p style="margin: 0;">
                        <strong>🎁 Beta Deal:</strong> Free forever if you give us feedback. 
                        Just tell us what works and what doesn't.
                    </p>
                </div>
                
                <p style="margin-top: 30px;">
                    Ready to stop losing money on jobs?
                </p>
                
                <p>
                    Let's do this,<br>
                    <strong>Tyler</strong><br>
                    <em>Founder, CORA</em>
                </p>
                
                <p style="font-size: 14px; color: #666; margin-top: 20px;">
                    P.S. Join our beta contractor Slack channel after you sign up. 
                    Great place to share tips and get help.
                </p>
            </div>
        </div>
        """
        
        try:
            message = Mail(
                from_email=Email(service.from_email, "Tyler from CORA"),
                to_emails=To(email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = service.sendgrid_client.send(message)
            db.close()
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Failed to send beta invitation: {str(e)}")
            db.close()
            return False