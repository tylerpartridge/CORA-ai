#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/test_weekly_insights_validation.py
🎯 PURPOSE: Comprehensive tests for weekly insights validation logic
🔗 IMPORTS: pytest, SQLAlchemy, test utilities
📤 EXPORTS: Test cases for validation thresholds
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

# Import models and services
from models.base import Base
from models.user import User
from models.expense import Expense
from models.job import Job
from services.weekly_report_service import WeeklyReportService, DataValidationReason


@pytest.fixture
def test_db():
    """Create a test database session"""
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_test_password",
        timezone="UTC"
    )
    test_db.add(user)
    test_db.commit()
    return user


class TestWeeklyInsightsValidation:
    """Test suite for weekly insights data validation"""
    
    def test_no_expenses_fails_validation(self, test_db, test_user):
        """Test that validation fails when user has no expenses"""
        # Act
        is_valid, reason, context = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="7d"
        )
        
        # Assert
        assert is_valid is False
        assert reason == DataValidationReason.INSUFFICIENT_EXPENSES
        assert context["expense_count"] == 0
        assert context["needed"] == 5
        assert "message" in context
    
    def test_insufficient_recent_expenses_fails_validation(self, test_db, test_user):
        """Test that validation fails with less than 3 recent expenses"""
        # Arrange - Add only 2 recent expenses
        for i in range(2):
            expense = Expense(
                user_id=test_user.id,
                amount_cents=1000 + (i * 100),
                expense_date=datetime.utcnow() - timedelta(days=i),
                description=f"Test expense {i}",
                currency="USD"
            )
            test_db.add(expense)
        
        # Add old expenses (outside window)
        for i in range(5):
            expense = Expense(
                user_id=test_user.id,
                amount_cents=2000 + (i * 100),
                expense_date=datetime.utcnow() - timedelta(days=30 + i),
                description=f"Old expense {i}",
                currency="USD"
            )
            test_db.add(expense)
        
        test_db.commit()
        
        # Act
        is_valid, reason, context = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="7d"
        )
        
        # Assert
        assert is_valid is False
        assert reason == DataValidationReason.NO_RECENT_ACTIVITY
        assert context["recent_count"] == 2
        assert context["needed"] == 3
        assert context["total_expenses"] == 7
    
    def test_insufficient_total_expenses_fails_validation(self, test_db, test_user):
        """Test that validation fails with less than 5 total expenses"""
        # Arrange - Add only 4 expenses total
        for i in range(4):
            expense = Expense(
                user_id=test_user.id,
                amount_cents=1000 + (i * 100),
                expense_date=datetime.utcnow() - timedelta(days=i),
                description=f"Test expense {i}",
                currency="USD"
            )
            test_db.add(expense)
        
        test_db.commit()
        
        # Act
        is_valid, reason, context = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="7d"
        )
        
        # Assert
        assert is_valid is False
        assert reason == DataValidationReason.INSUFFICIENT_EXPENSES
        assert context["expense_count"] == 4
        assert context["needed"] == 5
    
    def test_insufficient_time_range_fails_validation(self, test_db, test_user):
        """Test that validation fails with less than 3 days of expense history"""
        # Arrange - Add 5 expenses all on the same day
        for i in range(5):
            expense = Expense(
                user_id=test_user.id,
                amount_cents=1000 + (i * 100),
                expense_date=datetime.utcnow(),  # All same day
                description=f"Test expense {i}",
                currency="USD"
            )
            test_db.add(expense)
        
        test_db.commit()
        
        # Act
        is_valid, reason, context = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="7d"
        )
        
        # Assert
        assert is_valid is False
        assert reason == DataValidationReason.NO_TIME_RANGE
        assert context["days_active"] == 1  # All expenses on same day
        assert context["needed_days"] == 3
    
    def test_validation_passes_with_sufficient_data(self, test_db, test_user):
        """Test that validation passes when all thresholds are met"""
        # Arrange - Add sufficient expenses over multiple days
        for i in range(6):  # 6 expenses
            expense = Expense(
                user_id=test_user.id,
                amount_cents=1000 + (i * 100),
                expense_date=datetime.utcnow() - timedelta(days=i % 4),  # Spread over 4 days
                description=f"Test expense {i}",
                currency="USD",
                category_id=i % 3 + 1  # Use different categories
            )
            test_db.add(expense)
        
        # Add a job for extra context
        job = Job(
            user_id=test_user.id,
            job_name="Test Job",
            status="active",
            quoted_amount=5000.00
        )
        test_db.add(job)
        
        test_db.commit()
        
        # Act
        is_valid, reason, context = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="7d"
        )
        
        # Assert
        assert is_valid is True
        assert reason == DataValidationReason.VALID
        assert context["expense_count"] == 6
        assert context["recent_count"] >= 3
        assert context["days_active"] >= 3
        assert context["categories_used"] == 3
        assert context["jobs_count"] == 1
        assert "message" in context
    
    def test_different_window_periods(self, test_db, test_user):
        """Test validation with different window periods (7d, 14d, 30d)"""
        # Arrange - Add expenses spread over 20 days
        for i in range(10):
            expense = Expense(
                user_id=test_user.id,
                amount_cents=1000,
                expense_date=datetime.utcnow() - timedelta(days=i * 2),
                description=f"Test expense {i}",
                currency="USD"
            )
            test_db.add(expense)
        
        test_db.commit()
        
        # Test 7 day window
        is_valid_7d, _, context_7d = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="7d"
        )
        
        # Test 14 day window
        is_valid_14d, _, context_14d = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="14d"
        )
        
        # Test 30 day window
        is_valid_30d, _, context_30d = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="30d"
        )
        
        # Assert - More expenses should be in larger windows
        assert context_7d["recent_count"] <= context_14d["recent_count"]
        assert context_14d["recent_count"] <= context_30d["recent_count"]
        assert is_valid_30d is True  # Should have enough data in 30 day window
    
    def test_invalid_window_format_defaults_to_7_days(self, test_db, test_user):
        """Test that invalid window format defaults to 7 days"""
        # Arrange - Add minimal valid data
        for i in range(5):
            expense = Expense(
                user_id=test_user.id,
                amount_cents=1000,
                expense_date=datetime.utcnow() - timedelta(days=i),
                description=f"Test expense {i}",
                currency="USD"
            )
            test_db.add(expense)
        
        test_db.commit()
        
        # Act - Use invalid window format
        is_valid, reason, context = WeeklyReportService.meets_minimum_data(
            user_id=test_user.id,
            db=test_db,
            window="invalid"
        )
        
        # Assert - Should default to 7 days
        assert context["window_days"] == 7
    
    def test_validation_message_generation(self):
        """Test that validation messages are generated correctly"""
        # Test insufficient expenses message
        message = WeeklyReportService.get_validation_message(
            DataValidationReason.INSUFFICIENT_EXPENSES,
            {"needed": 5, "expense_count": 2}
        )
        assert "5 expenses" in message
        assert "currently have 2" in message
        
        # Test no recent activity message
        message = WeeklyReportService.get_validation_message(
            DataValidationReason.NO_RECENT_ACTIVITY,
            {"window_days": 7, "needed": 3}
        )
        assert "last 7 days" in message
        assert "3 expenses" in message
        
        # Test no time range message
        message = WeeklyReportService.get_validation_message(
            DataValidationReason.NO_TIME_RANGE,
            {"needed_days": 3, "days_active": 1}
        )
        assert "3 days" in message
        assert "tracking for 1 days" in message
        
        # Test valid message
        message = WeeklyReportService.get_validation_message(
            DataValidationReason.VALID,
            {}
        )
        assert "enough data" in message.lower()
    
    def test_email_validation_message_generation(self):
        """Test that email validation messages are generated correctly"""
        # Test insufficient expenses email message
        message = WeeklyReportService.get_email_validation_message(
            DataValidationReason.INSUFFICIENT_EXPENSES,
            {"needed": 5}
        )
        assert "5 total" in message
        assert "Keep tracking" in message
        
        # Test no recent activity email message
        message = WeeklyReportService.get_email_validation_message(
            DataValidationReason.NO_RECENT_ACTIVITY,
            {}
        )
        assert "paused" in message
        assert "resume" in message
        
        # Test valid email message
        message = WeeklyReportService.get_email_validation_message(
            DataValidationReason.VALID,
            {}
        )
        assert "ready" in message.lower()
    
    def test_scheduler_integration_skips_invalid_users(self, test_db, test_user):
        """Test that scheduler skips users without sufficient data"""
        from services.business_task_automation import BusinessTaskAutomation
        
        # Create automation service with test user
        automation = BusinessTaskAutomation(test_user, test_db)
        
        # Mock the logger to capture log messages
        with patch('services.business_task_automation.logger') as mock_logger:
            # Run financial report generation
            result = automation._generate_financial_report()
            
            # Assert - Should skip and log
            assert result.get("skipped") is True
            assert result.get("reason") == DataValidationReason.INSUFFICIENT_EXPENSES.value
            assert "message" in result
            
            # Verify logging was called
            mock_logger.info.assert_called()
            log_message = mock_logger.info.call_args[0][0]
            assert "Skipping" in log_message
            assert test_user.email in log_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])