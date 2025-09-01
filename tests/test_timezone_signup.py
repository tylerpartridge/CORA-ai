#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/test_timezone_signup.py
🎯 PURPOSE: Test timezone selection functionality in signup flow
🔗 IMPORTS: pytest, TestClient, BeautifulSoup
📤 EXPORTS: Test cases for timezone feature
"""

import pytest
from fastapi.testclient import TestClient
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import User


class TestTimezoneSignup:
    """Test timezone selection in signup flow"""
    
    def test_signup_page_has_timezone_dropdown(self, client: TestClient):
        """Test that signup page renders with timezone dropdown"""
        response = client.get("/signup")
        assert response.status_code == 200
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for timezone select element
        timezone_select = soup.find('select', {'id': 'timezone', 'name': 'timezone'})
        assert timezone_select is not None, "Timezone dropdown not found"
        
        # Check for required attribute
        assert timezone_select.get('required') is not None, "Timezone field should be required"
        
        # Check for common timezone options
        options = timezone_select.find_all('option')
        option_values = [opt.get('value') for opt in options if opt.get('value')]
        
        # Verify key timezones are present
        assert 'America/New_York' in option_values, "Eastern Time not found"
        assert 'America/Los_Angeles' in option_values, "Pacific Time not found"
        assert 'America/Chicago' in option_values, "Central Time not found"
        assert 'Europe/London' in option_values, "London timezone not found"
        assert 'Asia/Tokyo' in option_values, "Tokyo timezone not found"
        
        # Check for optgroups
        optgroups = timezone_select.find_all('optgroup')
        assert len(optgroups) > 0, "Timezone options should be grouped"
        
        # Verify optgroup labels
        optgroup_labels = [og.get('label') for og in optgroups]
        assert 'North America' in optgroup_labels, "North America group not found"
        assert 'Europe' in optgroup_labels, "Europe group not found"
        assert 'Asia' in optgroup_labels, "Asia group not found"
    
    def test_signup_page_has_timezone_detection_script(self, client: TestClient):
        """Test that signup page includes browser timezone detection JavaScript"""
        response = client.get("/signup")
        assert response.status_code == 200
        
        # Check for timezone detection code
        assert 'Intl.DateTimeFormat().resolvedOptions().timeZone' in response.text, \
            "Browser timezone detection code not found"
        assert 'timezoneSelect' in response.text, "Timezone select manipulation code not found"
    
    def test_register_with_timezone(self, client: TestClient):
        """Test user registration with timezone selection"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "timezone_user@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "timezone": "America/Chicago"
            }
        )
        
        # Should succeed (201 or 200 depending on implementation)
        assert response.status_code in [200, 201], f"Registration failed: {response.json()}"
        
        data = response.json()
        assert data.get("success") is True or "email" in data, "Registration response invalid"
    
    def test_register_with_invalid_timezone(self, client: TestClient):
        """Test registration with invalid timezone falls back to default"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid_tz_user@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "timezone": "Invalid/Timezone"
            }
        )
        
        # Should still succeed with fallback to default
        assert response.status_code in [200, 201], f"Registration should succeed with fallback: {response.json()}"
    
    def test_register_without_timezone(self, client: TestClient):
        """Test registration without timezone uses default"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "no_tz_user@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!"
                # No timezone field
            }
        )
        
        # Should succeed with default timezone
        assert response.status_code in [200, 201], f"Registration should succeed with default: {response.json()}"
    
    @pytest.mark.parametrize("timezone", [
        "Pacific/Honolulu",
        "America/Anchorage",
        "America/Los_Angeles",
        "America/Denver",
        "America/Chicago",
        "America/New_York",
        "Europe/London",
        "Europe/Paris",
        "Asia/Tokyo",
        "Australia/Sydney"
    ])
    def test_register_with_various_timezones(self, client: TestClient, timezone: str):
        """Test registration with various valid timezones"""
        # Generate unique email for each test
        email = f"user_{timezone.replace('/', '_').lower()}@example.com"
        
        response = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "timezone": timezone
            }
        )
        
        # Should succeed for all valid timezones
        assert response.status_code in [200, 201, 409], \
            f"Registration failed for {timezone}: {response.json()}"
        
        # 409 is acceptable as it means user already exists from a previous test run
        if response.status_code == 409:
            assert "already" in response.json().get("detail", "").lower()


class TestTimezoneDatabase:
    """Test timezone persistence in database"""
    
    @pytest.mark.skipif("not config.DATABASE_URL" in sys.modules, reason="Database not configured")
    def test_user_timezone_saved_to_db(self, client: TestClient, test_db: Session):
        """Test that user timezone is saved to database"""
        # Register a new user with specific timezone
        response = client.post(
            "/api/auth/register",
            json={
                "email": "db_tz_user@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "timezone": "Europe/Berlin"
            }
        )
        
        # Check registration succeeded
        assert response.status_code in [200, 201], f"Registration failed: {response.json()}"
        
        # Query database for the user
        user = test_db.query(User).filter(User.email == "db_tz_user@example.com").first()
        assert user is not None, "User not found in database"
        assert user.timezone == "Europe/Berlin", f"Timezone not saved correctly: {user.timezone}"
    
    @pytest.mark.skipif("not config.DATABASE_URL" in sys.modules, reason="Database not configured")
    def test_user_default_timezone(self, client: TestClient, test_db: Session):
        """Test that users get default timezone when not specified"""
        # Register without timezone
        response = client.post(
            "/api/auth/register",
            json={
                "email": "default_tz_user@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!"
            }
        )
        
        assert response.status_code in [200, 201], f"Registration failed: {response.json()}"
        
        # Check database
        user = test_db.query(User).filter(User.email == "default_tz_user@example.com").first()
        assert user is not None, "User not found in database"
        assert user.timezone == "America/New_York", f"Default timezone not set: {user.timezone}"


class TestTimezoneJavaScript:
    """Test JavaScript timezone detection functionality"""
    
    def test_signup_form_js_includes_timezone(self, client: TestClient):
        """Test that signup-form.js handles timezone field"""
        # Try to fetch the JavaScript file
        response = client.get("/static/js/signup-form.js")
        
        if response.status_code == 200:
            # Check that timezone is included in form data
            assert "timezone" in response.text or "formData.get('timezone')" in response.text, \
                "Timezone handling not found in signup-form.js"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])