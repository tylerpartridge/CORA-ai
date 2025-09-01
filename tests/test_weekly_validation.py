#!/usr/bin/env python3
"""
Test Weekly Report Validation Service

Tests the 3/5/3 validation thresholds for weekly insights.
"""

import pytest
from datetime import datetime, date, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.weekly_report_service import validate_weekly_report, ValidationStatus, get_validation_message
from models import User, Expense


class TestWeeklyValidation:
    """Test weekly report validation with 3/5/3 thresholds"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.user_id = 1
        self.mock_db = Mock(spec=Session)
        
    def test_ok_with_3_5_3(self):
        """Test validation passes with exactly 3 recent, 5 total, 3 days"""
        # Mock: 5 total expenses
        total_query = Mock()
        total_query.scalar.return_value = 5
        
        # Mock: 3 recent expenses
        recent_query = Mock()
        recent_query.scalar.return_value = 3
        
        # Mock: 3 distinct days
        days_query = Mock()
        days_query.scalar.return_value = 3
        
        # Setup query chain mocking
        self.mock_db.query.return_value.filter.return_value = total_query
        
        # Use side_effect to return different mocks for different queries
        query_call_count = 0
        def query_side_effect(*args):
            nonlocal query_call_count
            query_call_count += 1
            mock = Mock()
            if query_call_count == 1:  # Recent count
                mock.filter.return_value.scalar.return_value = 3
            elif query_call_count == 2:  # Total count
                mock.filter.return_value.scalar.return_value = 5
            elif query_call_count == 3:  # Active days
                mock.filter.return_value.scalar.return_value = 3
            return mock
        
        self.mock_db.query.side_effect = query_side_effect
        
        # Run validation
        status, details = validate_weekly_report(self.user_id, self.mock_db)
        
        # Assert OK status
        assert status == ValidationStatus.OK
        assert details["recent_count"] == 3
        assert details["total_count"] == 5
        assert details["active_days"] == 3
        assert "Sufficient data" in details["message"]
    
    def test_insufficient_recent(self):
        """Test validation fails with only 2 recent expenses"""
        # Setup mocks: 2 recent, 10 total, 5 days
        query_call_count = 0
        def query_side_effect(*args):
            nonlocal query_call_count
            query_call_count += 1
            mock = Mock()
            if query_call_count == 1:  # Recent count
                mock.filter.return_value.scalar.return_value = 2
            elif query_call_count == 2:  # Total count
                mock.filter.return_value.scalar.return_value = 10
            elif query_call_count == 3:  # Active days
                mock.filter.return_value.scalar.return_value = 5
            return mock
        
        self.mock_db.query.side_effect = query_side_effect
        
        # Run validation
        status, details = validate_weekly_report(self.user_id, self.mock_db)
        
        # Assert insufficient recent status
        assert status == ValidationStatus.INSUFFICIENT_RECENT
        assert details["recent_count"] == 2
        assert details["total_count"] == 10
        assert "at least 3 expenses in the last" in details["message"]
    
    def test_insufficient_total(self):
        """Test validation fails with only 4 total expenses"""
        # Setup mocks: 4 recent, 4 total, 4 days
        query_call_count = 0
        def query_side_effect(*args):
            nonlocal query_call_count
            query_call_count += 1
            mock = Mock()
            if query_call_count == 1:  # Recent count
                mock.filter.return_value.scalar.return_value = 4
            elif query_call_count == 2:  # Total count
                mock.filter.return_value.scalar.return_value = 4
            elif query_call_count == 3:  # Active days
                mock.filter.return_value.scalar.return_value = 4
            return mock
        
        self.mock_db.query.side_effect = query_side_effect
        
        # Run validation
        status, details = validate_weekly_report(self.user_id, self.mock_db)
        
        # Assert insufficient total status
        assert status == ValidationStatus.INSUFFICIENT_TOTAL
        assert details["total_count"] == 4
        assert "at least 5 total expenses" in details["message"]
    
    def test_insufficient_days(self):
        """Test validation fails with only 2 active days"""
        # Setup mocks: 5 recent, 10 total, 2 days
        query_call_count = 0
        def query_side_effect(*args):
            nonlocal query_call_count
            query_call_count += 1
            mock = Mock()
            if query_call_count == 1:  # Recent count
                mock.filter.return_value.scalar.return_value = 5
            elif query_call_count == 2:  # Total count
                mock.filter.return_value.scalar.return_value = 10
            elif query_call_count == 3:  # Active days
                mock.filter.return_value.scalar.return_value = 2
            return mock
        
        self.mock_db.query.side_effect = query_side_effect
        
        # Run validation
        status, details = validate_weekly_report(self.user_id, self.mock_db)
        
        # Assert insufficient days status
        assert status == ValidationStatus.INSUFFICIENT_DAYS
        assert details["active_days"] == 2
        assert "at least 3 different days" in details["message"]
    
    def test_custom_window_days(self):
        """Test validation with custom window (14 days)"""
        # Setup mocks
        query_call_count = 0
        def query_side_effect(*args):
            nonlocal query_call_count
            query_call_count += 1
            mock = Mock()
            if query_call_count == 1:  # Recent count
                mock.filter.return_value.scalar.return_value = 3
            elif query_call_count == 2:  # Total count
                mock.filter.return_value.scalar.return_value = 5
            elif query_call_count == 3:  # Active days
                mock.filter.return_value.scalar.return_value = 3
            return mock
        
        self.mock_db.query.side_effect = query_side_effect
        
        # Run validation with 14-day window
        status, details = validate_weekly_report(self.user_id, self.mock_db, window_days=14)
        
        # Assert window is reflected in details
        assert status == ValidationStatus.OK
        assert details["window_days"] == 14
    
    def test_zero_expenses(self):
        """Test validation with no expenses at all"""
        # Setup mocks: all zeros
        query_call_count = 0
        def query_side_effect(*args):
            nonlocal query_call_count
            query_call_count += 1
            mock = Mock()
            mock.filter.return_value.scalar.return_value = 0
            return mock
        
        self.mock_db.query.side_effect = query_side_effect
        
        # Run validation
        status, details = validate_weekly_report(self.user_id, self.mock_db)
        
        # Assert insufficient total (checked first)
        assert status == ValidationStatus.INSUFFICIENT_TOTAL
        assert details["total_count"] == 0
        assert details["recent_count"] == 0
    
    def test_validation_message_generation(self):
        """Test that validation messages are user-friendly"""
        # Test OK message
        ok_details = {"message": "Custom OK message"}
        message = get_validation_message(ValidationStatus.OK, ok_details)
        assert "ready" in message.lower() or "Custom OK" in message
        
        # Test insufficient total message
        total_details = {"total_count": 3, "window_days": 7}
        message = get_validation_message(ValidationStatus.INSUFFICIENT_TOTAL, total_details)
        assert "5 expenses" in message or "tracking" in message.lower()
        
        # Test insufficient recent message
        recent_details = {"recent_count": 1, "window_days": 7}
        message = get_validation_message(ValidationStatus.INSUFFICIENT_RECENT, recent_details)
        assert "recent" in message.lower() or "3" in message
        
        # Test insufficient days message
        days_details = {"active_days": 1, "window_days": 7}
        message = get_validation_message(ValidationStatus.INSUFFICIENT_DAYS, days_details)
        assert "days" in message.lower() or "3" in message
    
    def test_thresholds_in_details(self):
        """Test that threshold values are included in details"""
        # Setup mocks
        query_call_count = 0
        def query_side_effect(*args):
            nonlocal query_call_count
            query_call_count += 1
            mock = Mock()
            mock.filter.return_value.scalar.return_value = 10
            return mock
        
        self.mock_db.query.side_effect = query_side_effect
        
        # Run validation
        status, details = validate_weekly_report(self.user_id, self.mock_db)
        
        # Check thresholds are present
        assert "thresholds" in details
        assert details["thresholds"]["recent_minimum"] == 3
        assert details["thresholds"]["total_minimum"] == 5
        assert details["thresholds"]["days_minimum"] == 3


def test_validation_priority_order():
    """Test that validations are checked in the correct priority order"""
    # This test verifies the order: total -> recent -> days
    mock_db = Mock(spec=Session)
    
    # Case 1: Fails all checks, should return INSUFFICIENT_TOTAL
    query_call_count = 0
    def all_fail_query(*args):
        nonlocal query_call_count
        query_call_count += 1
        mock = Mock()
        mock.filter.return_value.scalar.return_value = 0
        return mock
    
    mock_db.query.side_effect = all_fail_query
    status, _ = validate_weekly_report(1, mock_db)
    assert status == ValidationStatus.INSUFFICIENT_TOTAL
    
    # Case 2: Passes total, fails recent
    query_call_count = 0
    def pass_total_query(*args):
        nonlocal query_call_count
        query_call_count += 1
        mock = Mock()
        if query_call_count == 2:  # Total count
            mock.filter.return_value.scalar.return_value = 5
        else:
            mock.filter.return_value.scalar.return_value = 0
        return mock
    
    mock_db.query.side_effect = pass_total_query
    status, _ = validate_weekly_report(1, mock_db)
    assert status == ValidationStatus.INSUFFICIENT_RECENT
    
    # Case 3: Passes total and recent, fails days
    query_call_count = 0
    def pass_total_recent_query(*args):
        nonlocal query_call_count
        query_call_count += 1
        mock = Mock()
        if query_call_count == 1:  # Recent
            mock.filter.return_value.scalar.return_value = 3
        elif query_call_count == 2:  # Total
            mock.filter.return_value.scalar.return_value = 5
        else:  # Days
            mock.filter.return_value.scalar.return_value = 1
        return mock
    
    mock_db.query.side_effect = pass_total_recent_query
    status, _ = validate_weekly_report(1, mock_db)
    assert status == ValidationStatus.INSUFFICIENT_DAYS


if __name__ == "__main__":
    print("\nTesting Weekly Report Validation (3/5/3 Thresholds)\n")
    print("-" * 50)
    
    # Run unit tests
    test_validator = TestWeeklyValidation()
    
    print("\n1. Testing OK with 3/5/3...")
    test_validator.setup_method()
    test_validator.test_ok_with_3_5_3()
    print("   OK: Validation passes with minimum thresholds")
    
    print("\n2. Testing insufficient recent expenses...")
    test_validator.setup_method()
    test_validator.test_insufficient_recent()
    print("   OK: Correctly identifies insufficient recent expenses")
    
    print("\n3. Testing insufficient total expenses...")
    test_validator.setup_method()
    test_validator.test_insufficient_total()
    print("   OK: Correctly identifies insufficient total expenses")
    
    print("\n4. Testing insufficient active days...")
    test_validator.setup_method()
    test_validator.test_insufficient_days()
    print("   OK: Correctly identifies insufficient active days")
    
    print("\n5. Testing custom window days...")
    test_validator.setup_method()
    test_validator.test_custom_window_days()
    print("   OK: Custom window days work correctly")
    
    print("\n6. Testing zero expenses...")
    test_validator.setup_method()
    test_validator.test_zero_expenses()
    print("   OK: Handles zero expenses correctly")
    
    print("\n7. Testing validation messages...")
    test_validator.setup_method()
    test_validator.test_validation_message_generation()
    print("   OK: Messages are user-friendly")
    
    print("\n8. Testing thresholds in details...")
    test_validator.setup_method()
    test_validator.test_thresholds_in_details()
    print("   OK: Thresholds included in response details")
    
    print("\n9. Testing validation priority order...")
    test_validation_priority_order()
    print("   OK: Validations checked in correct order")
    
    print("\n" + "=" * 50)
    print("SUCCESS: All weekly validation tests passed!")
    print("=" * 50)