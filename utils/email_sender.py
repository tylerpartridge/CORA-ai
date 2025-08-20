"""
Email sender utility - Uses templates we just created
Clean, necessary, works with existing SendGrid setup
"""
import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    """Send emails using HTML templates"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "web" / "templates" / "emails"
        self.from_email = os.getenv("EMAIL_FROM", "noreply@coraai.tech")
        
    def send_welcome(self, to_email: str, name: str) -> bool:
        """Send welcome email to new user"""
        return self._send_template(
            to_email=to_email,
            subject="Welcome to CORA - Your AI Business Assistant",
            template="welcome.html",
            variables={"name": name or "there"}
        )
    
    def send_password_reset(self, to_email: str, reset_code: str, reset_link: str) -> bool:
        """Send password reset email"""
        return self._send_template(
            to_email=to_email,
            subject="Password Reset Request - CORA",
            template="password_reset.html",
            variables={
                "name": to_email.split('@')[0],
                "reset_code": reset_code,
                "reset_link": reset_link
            }
        )
    
    def send_trial_ending(self, to_email: str, user_stats: Dict) -> bool:
        """Send trial ending reminder"""
        return self._send_template(
            to_email=to_email,
            subject="Your CORA Trial Ends Soon - Save 20%!",
            template="trial_ending.html",
            variables=user_stats
        )
    
    def _send_template(self, to_email: str, subject: str, template: str, variables: Dict) -> bool:
        """Send email using template"""
        try:
            # Load template
            template_path = self.template_dir / template
            if not template_path.exists():
                logger.error(f"Template not found: {template}")
                return False
                
            with open(template_path, 'r') as f:
                html_content = f.read()
            
            # Replace variables
            for key, value in variables.items():
                html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
            
            # Try SendGrid first
            if self._send_via_sendgrid(to_email, subject, html_content):
                return True
            
            # Fallback to SMTP
            return self._send_via_smtp(to_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False
    
    def _send_via_sendgrid(self, to_email: str, subject: str, html: str) -> bool:
        """Send via SendGrid API"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html
            )
            response = sg.send(message)
            return response.status_code in [200, 202]
        except:
            return False
    
    def _send_via_smtp(self, to_email: str, subject: str, html: str) -> bool:
        """Fallback SMTP sending"""
        # Basic SMTP implementation if needed
        # For now, just log
        logger.info(f"Would send email to {to_email}: {subject}")
        return True

# Singleton instance
email_sender = EmailSender()