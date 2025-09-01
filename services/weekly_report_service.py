#!/usr/bin/env python3
"""
Weekly Report Validation Service

Validates if user has sufficient data for meaningful weekly insights.
Thresholds: 3 recent expenses, 5 total expenses, 3 active days.
"""

from enum import Enum
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import logging

from models import User, Expense

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status codes for weekly report validation."""
    OK = "OK"
    INSUFFICIENT_RECENT = "INSUFFICIENT_RECENT"
    INSUFFICIENT_TOTAL = "INSUFFICIENT_TOTAL"
    INSUFFICIENT_DAYS = "INSUFFICIENT_DAYS"


class DataValidationReason(Enum):
    """Legacy enum for backward compatibility"""
    INSUFFICIENT_EXPENSES = "need_more_expenses"
    NO_TIME_RANGE = "need_time_range"
    NO_RECENT_ACTIVITY = "no_recent_activity"
    VALID = "sufficient_data"


def validate_weekly_report(
    user_id: int, 
    db: Session,
    window_days: int = 7
) -> Tuple[ValidationStatus, Dict[str, Any]]:
    """
    Validate if user has sufficient data for weekly insights.
    
    Args:
        user_id: User ID to validate
        db: Database session
        window_days: Number of days to look back (default 7)
    
    Returns:
        Tuple of (ValidationStatus, details dict)
        Details include counts and threshold info for UI messaging
    
    Thresholds:
        - recent_count >= 3 (expenses in last window_days)
        - total_count >= 5 (all-time expenses)
        - active_days >= 3 (distinct days with expenses in window)
    """
    # Calculate date window
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=window_days)
    
    # Get recent expense count (last 7 days)
    recent_count = db.query(func.count(Expense.id)).filter(
        Expense.user_id == user_id,
        Expense.expense_date >= window_start.date()
    ).scalar() or 0
    
    # Get total expense count (all-time)
    total_count = db.query(func.count(Expense.id)).filter(
        Expense.user_id == user_id
    ).scalar() or 0
    
    # Get distinct active days in window
    active_days = db.query(func.count(distinct(Expense.expense_date))).filter(
        Expense.user_id == user_id,
        Expense.expense_date >= window_start.date()
    ).scalar() or 0
    
    # Prepare details for response
    details = {
        "recent_count": recent_count,
        "total_count": total_count,
        "active_days": active_days,
        "window_days": window_days,
        "thresholds": {
            "recent_minimum": 3,
            "total_minimum": 5,
            "days_minimum": 3
        }
    }
    
    # Check thresholds in order of importance
    if total_count < 5:
        details["message"] = f"You need at least 5 total expenses to generate insights (you have {total_count})"
        return (ValidationStatus.INSUFFICIENT_TOTAL, details)
    
    if recent_count < 3:
        details["message"] = f"You need at least 3 expenses in the last {window_days} days for weekly insights (you have {recent_count})"
        return (ValidationStatus.INSUFFICIENT_RECENT, details)
    
    if active_days < 3:
        details["message"] = f"You need expenses on at least 3 different days in the last {window_days} days (you have {active_days})"
        return (ValidationStatus.INSUFFICIENT_DAYS, details)
    
    # All validations passed
    details["message"] = "Sufficient data for weekly insights"
    return (ValidationStatus.OK, details)


def get_validation_message(status: ValidationStatus, details: Dict[str, Any]) -> str:
    """
    Get user-friendly message based on validation status.
    
    Args:
        status: ValidationStatus enum value
        details: Details dict from validate_weekly_report
    
    Returns:
        User-friendly message string
    """
    if status == ValidationStatus.OK:
        return "Your weekly insights are ready!"
    
    # Use the message from details if available
    if "message" in details:
        return details["message"]
    
    # Fallback messages
    if status == ValidationStatus.INSUFFICIENT_TOTAL:
        return "Keep tracking expenses to unlock weekly insights. You need at least 5 expenses total."
    elif status == ValidationStatus.INSUFFICIENT_RECENT:
        return f"Add more recent expenses to get weekly insights. You need at least 3 in the last {details.get('window_days', 7)} days."
    elif status == ValidationStatus.INSUFFICIENT_DAYS:
        return f"Track expenses on more days to get insights. You need at least 3 active days in the last {details.get('window_days', 7)} days."
    
    return "Unable to generate weekly insights at this time."


class WeeklyReportService:
    """Legacy service class for backward compatibility"""
    
    # Validation thresholds
    MIN_RECENT_EXPENSES = 3  # Minimum expenses in the window period
    MIN_TOTAL_EXPENSES = 5   # Minimum total expenses overall
    MIN_DAYS_ACTIVE = 3      # Minimum days of expense history
    
    @classmethod
    def meets_minimum_data(
        cls,
        user_id: int,
        db: Session,
        window: str = "7d"
    ) -> Tuple[bool, DataValidationReason, Dict]:
        """
        Check if user has sufficient data for meaningful weekly insights.
        
        Args:
            user_id: ID of the user to validate
            db: Database session
            window: Time window string (e.g., "7d", "14d", "30d")
            
        Returns:
            Tuple of (is_valid: bool, reason: DataValidationReason, context: Dict)
            Context dict contains details about the validation failure/success
        """
        try:
            # Parse window to get number of days
            window_days = cls._parse_window(window)
            cutoff_date = datetime.utcnow() - timedelta(days=window_days)
            
            # Get recent expense count (within window)
            recent_expense_count = db.query(Expense).filter(
                and_(
                    Expense.user_id == user_id,
                    Expense.expense_date >= cutoff_date
                )
            ).count()
            
            # Get total expense count
            total_expense_count = db.query(Expense).filter(
                Expense.user_id == user_id
            ).count()
            
            # If no expenses at all, return early
            if total_expense_count == 0:
                return False, DataValidationReason.INSUFFICIENT_EXPENSES, {
                    "expense_count": 0,
                    "recent_count": 0,
                    "needed": cls.MIN_TOTAL_EXPENSES,
                    "window_days": window_days,
                    "message": f"You need at least {cls.MIN_TOTAL_EXPENSES} expenses to generate insights"
                }
            
            # Get first and last expense dates to calculate active days
            first_expense = db.query(Expense.expense_date).filter(
                Expense.user_id == user_id
            ).order_by(Expense.expense_date.asc()).first()
            
            last_expense = db.query(Expense.expense_date).filter(
                Expense.user_id == user_id
            ).order_by(Expense.expense_date.desc()).first()
            
            if first_expense and last_expense:
                days_of_data = (last_expense[0] - first_expense[0]).days + 1
            else:
                days_of_data = 0
            
            # Check if there's insufficient total expenses
            if total_expense_count < cls.MIN_TOTAL_EXPENSES:
                return False, DataValidationReason.INSUFFICIENT_EXPENSES, {
                    "expense_count": total_expense_count,
                    "recent_count": recent_expense_count,
                    "needed": cls.MIN_TOTAL_EXPENSES,
                    "window_days": window_days,
                    "days_active": days_of_data,
                    "message": f"You need {cls.MIN_TOTAL_EXPENSES - total_expense_count} more expenses to generate insights"
                }
            
            # Check if there's no recent activity
            if recent_expense_count < cls.MIN_RECENT_EXPENSES:
                return False, DataValidationReason.NO_RECENT_ACTIVITY, {
                    "expense_count": total_expense_count,
                    "recent_count": recent_expense_count,
                    "needed": cls.MIN_RECENT_EXPENSES,
                    "window_days": window_days,
                    "days_active": days_of_data,
                    "message": f"Add {cls.MIN_RECENT_EXPENSES - recent_expense_count} more expenses in the last {window_days} days"
                }
            
            # Check if there's insufficient time range
            if days_of_data < cls.MIN_DAYS_ACTIVE:
                return False, DataValidationReason.NO_TIME_RANGE, {
                    "expense_count": total_expense_count,
                    "recent_count": recent_expense_count,
                    "days_active": days_of_data,
                    "needed_days": cls.MIN_DAYS_ACTIVE,
                    "window_days": window_days,
                    "message": f"Track expenses for {cls.MIN_DAYS_ACTIVE - days_of_data} more days to see trends"
                }
            
            # All validations passed - get additional context for report generation
            categories_used = db.query(Expense.category_id).filter(
                Expense.user_id == user_id
            ).distinct().count()
            
            jobs_count = db.query(Job).filter(
                Job.user_id == user_id
            ).count()
            
            return True, DataValidationReason.VALID, {
                "expense_count": total_expense_count,
                "recent_count": recent_expense_count,
                "days_active": days_of_data,
                "window_days": window_days,
                "categories_used": categories_used,
                "jobs_count": jobs_count,
                "message": "Sufficient data for meaningful insights"
            }
            
        except Exception as e:
            logger.error(f"Error validating data for user {user_id}: {str(e)}")
            # Return a safe default that prevents report generation
            return False, DataValidationReason.INSUFFICIENT_EXPENSES, {
                "error": str(e),
                "message": "Unable to validate data at this time"
            }
    
    @staticmethod
    def _parse_window(window: str) -> int:
        """
        Parse window string to number of days.
        
        Args:
            window: Window string like "7d", "14d", "30d"
            
        Returns:
            Number of days as integer
        """
        if window.endswith('d'):
            try:
                return int(window[:-1])
            except ValueError:
                logger.warning(f"Invalid window format: {window}, defaulting to 7 days")
                return 7
        else:
            logger.warning(f"Unknown window format: {window}, defaulting to 7 days")
            return 7
    
    @classmethod
    def get_validation_message(cls, reason: DataValidationReason, context: Dict) -> str:
        """
        Get user-friendly validation message based on reason and context.
        
        Args:
            reason: The validation failure reason
            context: Context dictionary with details
            
        Returns:
            User-friendly message string
        """
        if "message" in context:
            return context["message"]
        
        messages = {
            DataValidationReason.INSUFFICIENT_EXPENSES: 
                f"You need at least {context.get('needed', cls.MIN_TOTAL_EXPENSES)} expenses to generate insights. "
                f"You currently have {context.get('expense_count', 0)}.",
            
            DataValidationReason.NO_RECENT_ACTIVITY:
                f"No recent expense activity in the last {context.get('window_days', 7)} days. "
                f"Add at least {context.get('needed', cls.MIN_RECENT_EXPENSES)} expenses to generate insights.",
            
            DataValidationReason.NO_TIME_RANGE:
                f"We need at least {context.get('needed_days', cls.MIN_DAYS_ACTIVE)} days of expense data to spot trends. "
                f"You've been tracking for {context.get('days_active', 0)} days.",
            
            DataValidationReason.VALID:
                "Great! You have enough data for meaningful insights."
        }
        
        return messages.get(reason, "Unable to generate insights at this time.")
    
    @classmethod
    def get_email_validation_message(cls, reason: DataValidationReason, context: Dict) -> str:
        """
        Get email-friendly validation message.
        
        Args:
            reason: The validation failure reason
            context: Context dictionary with details
            
        Returns:
            Email-friendly message string
        """
        messages = {
            DataValidationReason.INSUFFICIENT_EXPENSES:
                f"We need a few more expenses ({context.get('needed', cls.MIN_TOTAL_EXPENSES)} total) "
                f"to create your weekly insights report. Keep tracking!",
            
            DataValidationReason.NO_RECENT_ACTIVITY:
                "Your weekly insights report is paused due to no recent expense activity. "
                "Add some expenses and we'll resume your reports automatically.",
            
            DataValidationReason.NO_TIME_RANGE:
                f"Keep tracking! We need {context.get('needed_days', cls.MIN_DAYS_ACTIVE)} days of data "
                f"to spot meaningful trends in your spending.",
            
            DataValidationReason.VALID:
                "Your weekly insights report is ready!"
        }
        
        return messages.get(reason, "Your weekly insights report will resume once you have enough data.")