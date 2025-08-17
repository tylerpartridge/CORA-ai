#!/usr/bin/env python3
"""
Notification Service Activation Script
Configures and tests email/SMS notifications
"""

import os
import sys
from dotenv import load_dotenv, set_key

# Load existing .env
load_dotenv()

def check_current_status():
    """Check current notification configuration"""
    print("=== Notification Service Status ===")
    print("-" * 50)
    
    # Email configuration
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    
    print("[EMAIL CONFIGURATION]")
    print(f"SendGrid API Key: {'Configured' if sendgrid_key else 'Missing'}")
    print(f"From Email: {from_email if from_email else 'Missing'}")
    
    # SMS configuration
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_FROM_NUMBER')
    
    print("\n[SMS CONFIGURATION]")
    print(f"Twilio Account SID: {'Configured' if twilio_sid else 'Missing'}")
    print(f"Twilio Auth Token: {'Configured' if twilio_token else 'Missing'}")
    print(f"Twilio Phone Number: {twilio_number if twilio_number else 'Missing'}")
    
    return {
        'email_ready': bool(sendgrid_key and from_email),
        'sms_ready': bool(twilio_sid and twilio_token and twilio_number)
    }

def add_twilio_config():
    """Add Twilio configuration to .env"""
    print("\n=== Adding Twilio Configuration ===")
    print("To enable SMS notifications, you need:")
    print("1. Twilio Account SID")
    print("2. Twilio Auth Token") 
    print("3. Twilio Phone Number")
    print("\nGet these from: https://console.twilio.com")
    print("-" * 50)
    
    if '--demo' in sys.argv:
        # Add demo values
        env_file = '.env'
        set_key(env_file, 'TWILIO_ACCOUNT_SID', 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        set_key(env_file, 'TWILIO_AUTH_TOKEN', 'your-twilio-auth-token')
        set_key(env_file, 'TWILIO_FROM_NUMBER', '+1234567890')
        print("\n[DEMO] Added placeholder Twilio configuration to .env")
        print("Replace with real values to enable SMS notifications")
    else:
        print("\nTo add Twilio credentials, edit .env and add:")
        print("TWILIO_ACCOUNT_SID=your-account-sid")
        print("TWILIO_AUTH_TOKEN=your-auth-token")
        print("TWILIO_FROM_NUMBER=+1234567890")

def test_email_notification():
    """Test sending an email notification"""
    print("\n=== Testing Email Notification ===")
    
    try:
        from services.notification_service import NotificationService
        from database import SessionLocal
        
        db = SessionLocal()
        service = NotificationService(db)
        
        if service.sendgrid_client:
            # Test with a job alert
            test_data = {
                'name': 'Test Job',
                'id': '123',
                'quoted_amount': 10000,
                'total_costs': 8500,
                'margin_percent': 15,
                'over_budget': False
            }
            
            # Send to test email if provided
            test_email = sys.argv[2] if len(sys.argv) > 2 else None
            if test_email and '--test-email' in sys.argv:
                result = service._send_email_alert(
                    to_email=test_email,
                    alert_type='margin_warning',
                    severity='warning',
                    job_data=test_data,
                    message='Margin below 20% target'
                )
                
                if result:
                    print(f"[SUCCESS] Test email sent to {test_email}")
                else:
                    print(f"[ERROR] Failed to send test email")
            else:
                print("[INFO] Email service is configured and ready")
                print("To test, run: python activate_notifications.py --test-email your@email.com")
        else:
            print("[ERROR] SendGrid client not initialized")
            
        db.close()
        
    except Exception as e:
        print(f"[ERROR] Failed to test email: {e}")

def create_notification_test_endpoint():
    """Create a test endpoint for notifications"""
    test_code = '''
# Add this to your routes to test notifications
@router.post("/test-notifications")
async def test_notifications(
    email: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test notification sending"""
    from services.notification_service import NotificationService
    
    service = NotificationService(db)
    
    # Test job data
    job_data = {
        'name': 'Wilson Renovation',
        'id': 'test-123',
        'quoted_amount': 25000,
        'total_costs': 23000,
        'margin_percent': 8,  # Low margin to trigger alert
        'over_budget': True,
        'over_budget_amount': 2000
    }
    
    results = {}
    
    # Test email if provided
    if email:
        results['email'] = service._send_email_alert(
            to_email=email,
            alert_type='margin_critical',
            severity='critical',
            job_data=job_data,
            message='Job margin critically low - immediate action needed'
        )
    
    # Test SMS if provided
    if phone:
        results['sms'] = service._send_sms_alert(
            to_phone=phone,
            alert_type='margin_critical', 
            severity='critical',
            job_data=job_data,
            message='Low margin alert'
        )
    
    return {
        "success": True,
        "results": results,
        "message": "Test notifications sent"
    }
'''
    
    print("\n=== Test Endpoint Code ===")
    print(test_code)

def main():
    print("CORA Notification Service Activation")
    print("=" * 50)
    
    # Check current status
    status = check_current_status()
    
    # Summary
    print("\n=== Summary ===")
    if status['email_ready']:
        print("[OK] Email notifications are READY (SendGrid configured)")
    else:
        print("[MISSING] Email notifications need SendGrid configuration")
    
    if status['sms_ready']:
        print("[OK] SMS notifications are READY (Twilio configured)")
    else:
        print("[MISSING] SMS notifications need Twilio configuration")
        add_twilio_config()
    
    # Test if requested
    if '--test-email' in sys.argv:
        test_email_notification()
    
    if '--test-endpoint' in sys.argv:
        create_notification_test_endpoint()
    
    print("\n=== Next Steps ===")
    if not status['sms_ready']:
        print("1. Add Twilio credentials to .env file")
        print("2. Restart the server")
        print("3. Test with: python activate_notifications.py --test-email your@email.com")
    else:
        print("1. Notifications are fully configured!")
        print("2. Job alerts will be sent automatically when margins drop below 20%")
        print("3. Users can configure preferences in their settings")

if __name__ == "__main__":
    main()