#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/test_export_filenames_tz.py
🎯 PURPOSE: Test that export filenames use user's timezone preference
🔗 IMPORTS: pytest, datetime, utils.filenames
📤 EXPORTS: Test cases for timezone-aware filename generation
"""

import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.filenames import generate_filename, get_timezone_aware_date


class TestExportFilenamesTimezone:
    """Test suite for timezone-aware export filename generation"""
    
    def test_filename_uses_user_timezone(self):
        """Test that filename uses user's timezone for date"""
        # Create a fixed datetime for testing
        # UTC time: 2025-09-04 23:30:00 (late evening)
        test_dt = datetime(2025, 9, 4, 23, 30, 0, tzinfo=timezone.utc)
        
        # Test with America/St_Johns timezone
        # This would be 2025-09-04 21:00:00 in St. John's (still same day)
        filename = generate_filename(
            export_type="expenses",
            user_email="test@example.com",
            user_timezone="America/St_Johns",
            when=test_dt
        )
        assert "20250904" in filename  # Still Sept 4th in St. John's
        assert filename == "cora_expenses_test_at_example.com_20250904.csv"
        
        # Test with Asia/Tokyo timezone
        # This would be 2025-09-05 08:30:00 in Tokyo (next day!)
        filename = generate_filename(
            export_type="expenses",
            user_email="test@example.com",
            user_timezone="Asia/Tokyo",
            when=test_dt
        )
        assert "20250905" in filename  # Sept 5th in Tokyo
        assert filename == "cora_expenses_test_at_example.com_20250905.csv"
    
    def test_filename_falls_back_to_utc(self):
        """Test that filename falls back to UTC if timezone is invalid"""
        # Test with invalid timezone
        filename = generate_filename(
            export_type="dashboard",
            user_email="user@example.com",
            user_timezone="Invalid/Timezone"
        )
        # Should still generate a valid filename
        assert filename.startswith("cora_dashboard_user_at_example.com_")
        assert filename.endswith(".csv")
    
    def test_timezone_aware_date_conversion(self):
        """Test timezone-aware date conversion"""
        # Fixed UTC time: 2025-01-01 03:00:00 UTC
        test_dt = datetime(2025, 1, 1, 3, 0, 0, tzinfo=timezone.utc)
        
        # In America/New_York (UTC-5), this is still Dec 31, 2024
        date_str = get_timezone_aware_date("America/New_York", test_dt)
        assert date_str == "20241231"
        
        # In Europe/London (UTC+0), this is Jan 1, 2025
        date_str = get_timezone_aware_date("Europe/London", test_dt)
        assert date_str == "20250101"
        
        # In Asia/Shanghai (UTC+8), this is Jan 1, 2025
        date_str = get_timezone_aware_date("Asia/Shanghai", test_dt)
        assert date_str == "20250101"
    
    def test_current_time_with_timezone(self):
        """Test using current time with user timezone"""
        # Test with current time (no 'when' parameter)
        filename = generate_filename(
            export_type="report",
            user_email="current@test.com",
            user_timezone="America/Chicago"
        )
        
        # Should contain today's date in Chicago timezone
        assert filename.startswith("cora_report_current_at_test.com_")
        assert filename.endswith(".csv")
        # Date should be 8 digits
        date_part = filename.split("_")[-1].replace(".csv", "")
        assert len(date_part) == 8
        assert date_part.isdigit()
    
    def test_edge_case_timezones(self):
        """Test edge case timezones"""
        # Test UTC+14 (earliest timezone)
        test_dt = datetime(2025, 3, 15, 10, 0, 0, tzinfo=timezone.utc)
        
        # Pacific/Kiritimati is UTC+14
        filename = generate_filename(
            export_type="edge",
            user_email="test@example.com",
            user_timezone="Pacific/Kiritimati",
            when=test_dt
        )
        # March 16th in Kiritimati (day ahead)
        assert "20250316" in filename
        
        # Pacific/Niue is UTC-11 (among the latest)
        filename = generate_filename(
            export_type="edge",
            user_email="test@example.com",
            user_timezone="Pacific/Niue",
            when=test_dt
        )
        # March 14th in Niue (day behind)
        assert "20250314" in filename
    
    def test_dst_transition(self):
        """Test handling of daylight saving time transitions"""
        # Test a date during DST in Eastern time
        summer_dt = datetime(2025, 7, 15, 4, 0, 0, tzinfo=timezone.utc)
        filename = generate_filename(
            export_type="summer",
            user_email="test@example.com",
            user_timezone="America/New_York",
            when=summer_dt
        )
        # EDT is UTC-4, so 4:00 UTC is midnight, still July 15
        assert "20250715" in filename
        
        # Test a date during standard time
        winter_dt = datetime(2025, 1, 15, 5, 0, 0, tzinfo=timezone.utc)
        filename = generate_filename(
            export_type="winter",
            user_email="test@example.com",
            user_timezone="America/New_York",
            when=winter_dt
        )
        # EST is UTC-5, so 5:00 UTC is midnight, still Jan 15
        assert "20250115" in filename
    
    def test_email_sanitization_with_timezone(self):
        """Test that email sanitization works with timezone-aware dates"""
        test_dt = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        # Test various email formats
        emails_and_expected = [
            ("user.name@example.com", "user.name_at_example.com"),
            ("user+tag@test.org", "user-tag_at_test.org"),
            ("special!char@domain.co", "special-char_at_domain.co"),
        ]
        
        for email, expected_email_part in emails_and_expected:
            filename = generate_filename(
                export_type="test",
                user_email=email,
                user_timezone="America/Los_Angeles",
                when=test_dt
            )
            assert expected_email_part in filename
            assert "20250601" in filename  # June 1st in LA


if __name__ == "__main__":
    pytest.main([__file__, "-v"])