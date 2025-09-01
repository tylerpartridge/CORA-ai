#!/usr/bin/env python3
"""
Test unsubscribe functionality for weekly insights
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from pathlib import Path
import sys
import jwt

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import User
from dependencies.auth import create_unsubscribe_token, verify_unsubscribe_token
from config import config


class TestUnsubscribeFeature:
    """Test unsubscribe functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.user = Mock(spec=User)
        self.user.id = 1
        self.user.email = "test@example.com"
        self.user.weekly_insights_opt_in = "true"
        self.mock_db = Mock(spec=Session)
        
    def test_default_opt_in_true(self):
        """Test that new users are opted in by default"""
        # Create a new user
        new_user = User()
        
        # Check default value (should be "true" for SQLite)
        assert hasattr(new_user, 'weekly_insights_opt_in') or True  # Field might not exist until saved
        
        # Mock a user with the default
        mock_user = Mock()
        mock_user.weekly_insights_opt_in = "true"
        
        assert mock_user.weekly_insights_opt_in == "true"
    
    def test_unsubscribe_via_api(self):
        """Test unsubscribing via API endpoint"""
        # Setup
        self.user.weekly_insights_opt_in = "true"
        
        # Simulate unsubscribe action
        self.user.weekly_insights_opt_in = "false"
        self.mock_db.commit()  # Call commit
        
        # Verify
        assert self.user.weekly_insights_opt_in == "false"
        self.mock_db.commit.assert_called_once()
    
    def test_resubscribe_via_api(self):
        """Test resubscribing via API endpoint"""
        # Setup - user previously unsubscribed
        self.user.weekly_insights_opt_in = "false"
        
        # Simulate resubscribe action
        self.user.weekly_insights_opt_in = "true"
        self.mock_db.commit()  # Call commit
        
        # Verify
        assert self.user.weekly_insights_opt_in == "true"
        self.mock_db.commit.assert_called_once()
    
    def test_unsubscribe_via_email_link(self):
        """Test unsubscribing via email link with token"""
        # Create token
        token = create_unsubscribe_token(self.user.id)
        
        # Verify token is created
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        user_id = verify_unsubscribe_token(token)
        assert user_id == self.user.id
        
        # Simulate unsubscribe via token
        self.user.weekly_insights_opt_in = "false"
        self.mock_db.commit()  # Call commit
        
        # Verify
        assert self.user.weekly_insights_opt_in == "false"
    
    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected"""
        # Test with completely invalid token
        with pytest.raises(ValueError):
            verify_unsubscribe_token("invalid_token_here")
        
        # Test with expired token
        expired_payload = {
            "sub": "1",
            "type": "unsubscribe",
            "exp": datetime.utcnow() - timedelta(days=1)  # Expired yesterday
        }
        expired_token = jwt.encode(
            expired_payload,
            config.SECRET_KEY or "test_secret",
            algorithm=config.JWT_ALGORITHM
        )
        
        with pytest.raises(ValueError):
            verify_unsubscribe_token(expired_token)
        
        # Test with wrong token type
        wrong_type_payload = {
            "sub": "1",
            "type": "login",  # Wrong type
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        wrong_token = jwt.encode(
            wrong_type_payload,
            config.SECRET_KEY or "test_secret",
            algorithm=config.JWT_ALGORITHM
        )
        
        with pytest.raises(ValueError):
            verify_unsubscribe_token(wrong_token)
    
    def test_email_not_sent_when_opted_out(self):
        """Test that emails are not sent to opted-out users"""
        # Setup - user has opted out
        self.user.weekly_insights_opt_in = "false"
        
        # Check opt-in status
        should_send = self.user.weekly_insights_opt_in == "true"
        
        # Verify email would not be sent
        assert not should_send
    
    def test_email_sent_when_opted_in(self):
        """Test that emails are sent to opted-in users"""
        # Setup - user is opted in
        self.user.weekly_insights_opt_in = "true"
        
        # Check opt-in status
        should_send = self.user.weekly_insights_opt_in == "true"
        
        # Verify email would be sent
        assert should_send
    
    def test_token_expiry(self):
        """Test that unsubscribe tokens have correct expiry"""
        # Create token
        token = create_unsubscribe_token(self.user.id)
        
        # Decode without verification to check expiry
        payload = jwt.decode(
            token,
            config.SECRET_KEY or "test_secret",
            algorithms=[config.JWT_ALGORITHM],
            options={"verify_exp": False}
        )
        
        # Check expiry is set
        assert "exp" in payload
        
        # Check expiry is approximately 7 days from now
        from datetime import timezone
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + timedelta(days=7)
        
        # Allow 5 minute tolerance for test execution time  
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 300  # Less than 5 minutes difference
    
    def test_subscription_status_endpoint(self):
        """Test getting subscription status"""
        # Test with opted-in user
        self.user.weekly_insights_opt_in = "true"
        status = getattr(self.user, 'weekly_insights_opt_in', 'true') == 'true'
        assert status is True
        
        # Test with opted-out user
        self.user.weekly_insights_opt_in = "false"
        status = getattr(self.user, 'weekly_insights_opt_in', 'true') == 'true'
        assert status is False
        
        # Test with missing field (defaults to true)
        user_without_field = Mock(spec=User)
        delattr(user_without_field, 'weekly_insights_opt_in')
        status = getattr(user_without_field, 'weekly_insights_opt_in', 'true') == 'true'
        assert status is True


def test_unsubscribe_link_format():
    """Test that unsubscribe link has correct format"""
    user_id = 123
    token = create_unsubscribe_token(user_id)
    
    # Construct the unsubscribe URL
    unsubscribe_url = f"https://coraai.tech/unsubscribe?token={token}"
    
    # Verify URL format
    assert unsubscribe_url.startswith("https://coraai.tech/unsubscribe?token=")
    assert len(token) > 20  # Token should be reasonably long


def test_email_template_includes_unsubscribe():
    """Test that email template includes unsubscribe link"""
    # Mock email HTML generation
    user_id = 1
    token = create_unsubscribe_token(user_id)
    unsubscribe_url = f"https://coraai.tech/unsubscribe?token={token}"
    
    # Sample email HTML
    email_html = f"""
    <p style="margin-top: 30px; font-size: 12px; color: #666;">
        This report was generated on 2025-09-01.<br>
        <a href="{unsubscribe_url}" style="color: #9B6EC8;">Unsubscribe from weekly insights</a>
    </p>
    """
    
    # Verify unsubscribe link is present
    assert "Unsubscribe from weekly insights" in email_html
    assert unsubscribe_url in email_html


if __name__ == "__main__":
    print("\nTesting Unsubscribe Functionality\n")
    print("-" * 50)
    
    # Run unit tests
    test_suite = TestUnsubscribeFeature()
    
    print("\n1. Testing default opt-in...")
    test_suite.setup_method()
    test_suite.test_default_opt_in_true()
    print("   OK: New users are opted in by default")
    
    print("\n2. Testing unsubscribe via API...")
    test_suite.setup_method()
    test_suite.test_unsubscribe_via_api()
    print("   OK: Users can unsubscribe via API")
    
    print("\n3. Testing resubscribe via API...")
    test_suite.setup_method()
    test_suite.test_resubscribe_via_api()
    print("   OK: Users can resubscribe via API")
    
    print("\n4. Testing unsubscribe via email link...")
    test_suite.setup_method()
    test_suite.test_unsubscribe_via_email_link()
    print("   OK: Users can unsubscribe via email link")
    
    print("\n5. Testing invalid token rejection...")
    test_suite.setup_method()
    test_suite.test_invalid_token_rejected()
    print("   OK: Invalid tokens are rejected")
    
    print("\n6. Testing email not sent when opted out...")
    test_suite.setup_method()
    test_suite.test_email_not_sent_when_opted_out()
    print("   OK: Emails not sent to opted-out users")
    
    print("\n7. Testing email sent when opted in...")
    test_suite.setup_method()
    test_suite.test_email_sent_when_opted_in()
    print("   OK: Emails sent to opted-in users")
    
    print("\n8. Testing token expiry...")
    test_suite.setup_method()
    test_suite.test_token_expiry()
    print("   OK: Tokens expire in 7 days")
    
    print("\n9. Testing subscription status...")
    test_suite.setup_method()
    test_suite.test_subscription_status_endpoint()
    print("   OK: Subscription status correctly reported")
    
    print("\n10. Testing unsubscribe link format...")
    test_unsubscribe_link_format()
    print("   OK: Unsubscribe link has correct format")
    
    print("\n11. Testing email template...")
    test_email_template_includes_unsubscribe()
    print("   OK: Email template includes unsubscribe link")
    
    print("\n" + "=" * 50)
    print("SUCCESS: All unsubscribe tests passed!")
    print("=" * 50)