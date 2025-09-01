#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/weekly_insights.py
🎯 PURPOSE: Weekly insights report generation with validation
🔗 IMPORTS: FastAPI, database models, validation service
📤 EXPORTS: Weekly insights generation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

from models import get_db, User, Expense
from dependencies.auth import get_current_user
from services.weekly_report_service import validate_weekly_report, ValidationStatus, get_validation_message, WeeklyReportService, DataValidationReason
import logging
logger = logging.getLogger("cora.weekly_insights")
try:
    from services.email_service import EmailService  # type: ignore
except Exception as e:
    logger.warning("EmailService unavailable (%s); weekly insights will skip email sending.", e)
    class EmailService:
        @staticmethod
        def send_report(*args, **kwargs):
            return None
from utils.pdf_exporter import PDFExporter

logger = logging.getLogger(__name__)

# Create router
weekly_insights_router = APIRouter(
    prefix="/api/weekly",
    tags=["Weekly Insights"],
    responses={404: {"description": "Not found"}},
)


@weekly_insights_router.post("/generate")
async def generate_weekly_insights(
    background_tasks: BackgroundTasks,
    window: str = "7d",
    send_email: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate weekly insights report for the current user.
    
    Args:
        window: Time window for the report (e.g., "7d", "14d")
        send_email: Whether to send the report via email
        current_user: Authenticated user
        db: Database session
        
    Returns:
        JSON response with report status or error message
    """
    try:
        # Validate user has sufficient data
        window_days = int(window[:-1]) if window.endswith('d') else 7
        status, details = validate_weekly_report(
            user_id=current_user.id,
            db=db,
            window_days=window_days
        )
        
        if status != ValidationStatus.OK:
            # Get user-friendly message
            message = get_validation_message(status, details)
            
            # Return 400 with detailed validation failure
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "insufficient_data",
                    "reason": status.value,
                    "message": message,
                    "context": details
                }
            )
        
        # Data is valid - proceed with report generation
        logger.info(f"Generating weekly insights for user {current_user.email}")
        
        # Get expense data for the report
        window_days = int(window[:-1]) if window.endswith('d') else 7
        cutoff_date = datetime.utcnow() - timedelta(days=window_days)
        
        expenses = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            Expense.expense_date >= cutoff_date
        ).order_by(Expense.expense_date.desc()).all()
        
        # Calculate basic metrics
        total_spent = sum(e.amount_cents for e in expenses) / 100
        expense_count = len(expenses)
        
        # Group by category
        category_breakdown = {}
        for expense in expenses:
            cat_id = expense.category_id or 0
            if cat_id not in category_breakdown:
                category_breakdown[cat_id] = {
                    "count": 0,
                    "total": 0
                }
            category_breakdown[cat_id]["count"] += 1
            category_breakdown[cat_id]["total"] += expense.amount_cents / 100
        
        # Prepare report data
        report_data = {
            "user_email": current_user.email,
            "period": f"Last {window_days} days",
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": {
                "total_spent": total_spent,
                "expense_count": expense_count,
                "daily_average": total_spent / window_days if window_days > 0 else 0,
                "categories_used": len(category_breakdown)
            },
            "category_breakdown": category_breakdown,
            "validation_context": details
        }
        
        # Send email if requested (in background)
        if send_email and current_user.email:
            background_tasks.add_task(
                send_weekly_insights_email,
                current_user.email,
                report_data,
                db
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Weekly insights generated successfully",
                "report": report_data,
                "email_sent": send_email
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating weekly insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "generation_failed",
                "message": "Failed to generate weekly insights report"
            }
        )


@weekly_insights_router.get("/validate")
async def validate_weekly_insights_data(
    window: str = "7d",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user has sufficient data for weekly insights without generating.
    
    Args:
        window: Time window for validation (e.g., "7d", "14d")
        current_user: Authenticated user
        db: Database session
        
    Returns:
        JSON response with validation status and details
    """
    try:
        # Check data sufficiency
        window_days = int(window[:-1]) if window.endswith('d') else 7
        status, details = validate_weekly_report(
            user_id=current_user.id,
            db=db,
            window_days=window_days
        )
        
        # Get appropriate message
        message = get_validation_message(status, details)
        
        return JSONResponse(
            status_code=200,
            content={
                "valid": status == ValidationStatus.OK,
                "reason": status.value,
                "message": message,
                "context": details
            }
        )
        
    except Exception as e:
        logger.error(f"Error validating weekly insights data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "validation_failed",
                "message": "Failed to validate data"
            }
        )


async def send_weekly_insights_email(
    user_email: str,
    report_data: Dict,
    db: Session
):
    """
    Send weekly insights report via email (background task).
    
    Args:
        user_email: Recipient email address
        report_data: Report data dictionary
        db: Database session
    """
    try:
        # Create email content
        email_subject = f"Your Weekly Insights Report - {report_data['period']}"
        
        # Generate HTML email content
        email_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>Your Weekly Insights Report</h2>
            <p>Period: {report_data['period']}</p>
            
            <h3>Summary</h3>
            <ul>
                <li>Total Spent: ${report_data['metrics']['total_spent']:.2f}</li>
                <li>Number of Expenses: {report_data['metrics']['expense_count']}</li>
                <li>Daily Average: ${report_data['metrics']['daily_average']:.2f}</li>
                <li>Categories Used: {report_data['metrics']['categories_used']}</li>
            </ul>
            
            <p style="margin-top: 30px; font-size: 12px; color: #666;">
                This report was generated on {report_data['generated_at']}.
                To unsubscribe from weekly reports, please visit your account settings.
            </p>
        </body>
        </html>
        """
        
        # Send email using EmailService
        email_service = EmailService()
        success = await email_service.send_email(
            to_email=user_email,
            subject=email_subject,
            html_content=email_html
        )
        
        if success:
            logger.info(f"Weekly insights email sent to {user_email}")
        else:
            logger.error(f"Failed to send weekly insights email to {user_email}")
            
    except Exception as e:
        logger.error(f"Error sending weekly insights email: {str(e)}")


# UI messaging constants for frontend
VALIDATION_MESSAGES = {
    "need_more_expenses": "You need at least {needed} expenses to generate insights. You currently have {count}.",
    "need_time_range": "We need at least {needed} days of expense data. You've been tracking for {days} days.",
    "no_recent_activity": "No recent expense activity in the last {window} days. Add some expenses first!",
    "sufficient_data": "Great! You have enough data for meaningful insights."
}

# Email template messages
EMAIL_VALIDATION_MESSAGES = {
    "need_more_expenses": "We need a few more expenses to create your weekly insights report. Keep tracking!",
    "need_time_range": "Keep tracking! We need more days of data to spot trends in your spending.",
    "no_recent_activity": "Your weekly insights report is paused due to no recent activity.",
    "sufficient_data": "Your weekly insights report is ready!"
}
