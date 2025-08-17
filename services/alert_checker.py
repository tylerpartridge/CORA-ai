#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/alert_checker.py
🎯 PURPOSE: Automatic alert checking service
🔗 IMPORTS: Models, database, monitoring
📤 EXPORTS: Alert checking functions
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from models import Job, JobAlert, Expense, User
from middleware.monitoring import ALERTS_CREATED
from routes.websocket import broadcast_alert


class AlertChecker:
    """Service for checking and creating alerts based on business rules"""
    
    # Alert thresholds
    COST_OVERRUN_PERCENT = 20  # Alert if costs exceed budget by 20%
    PROFIT_MARGIN_WARNING = 10  # Alert if profit margin drops below 10%
    EXPENSE_SPIKE_PERCENT = 50  # Alert if daily expenses spike by 50%
    
    @staticmethod
    def check_job_cost_overrun(job: Job, db: Session) -> Optional[JobAlert]:
        """Check if job costs exceed budget threshold"""
        if not job.quoted_amount:
            return None
            
        # Calculate total expenses for this job
        total_expenses = db.query(func.sum(Expense.amount_cents)).filter(
            Expense.job_id == str(job.id)
        ).scalar() or 0
        
        budget_cents = int(job.quoted_amount * 100)
        overrun_threshold = budget_cents * (1 + AlertChecker.COST_OVERRUN_PERCENT / 100)
        
        if total_expenses > overrun_threshold:
            # Check if alert already exists
            existing = db.query(JobAlert).filter(
                JobAlert.job_id == job.id,
                JobAlert.alert_type == "cost_overrun",
                JobAlert.resolved_at.is_(None)
            ).first()
            
            if not existing:
                overrun_percent = ((total_expenses - budget_cents) / budget_cents) * 100
                alert = JobAlert(
                    user_id=job.user_id,
                    job_id=job.id,
                    alert_type="cost_overrun",
                    severity="critical",
                    message=f"Job costs exceed budget by {overrun_percent:.1f}%",
                    details={
                        "quoted_amount": job.quoted_amount,
                        "total_expenses": total_expenses / 100,
                        "overrun_percent": overrun_percent
                    }
                )
                return alert
        
        return None
    
    @staticmethod
    def check_job_profit_margin(job: Job, db: Session) -> Optional[JobAlert]:
        """Check if job profit margin is too low"""
        if not job.quoted_amount or job.status != "completed":
            return None
            
        # Calculate total expenses
        total_expenses = db.query(func.sum(Expense.amount_cents)).filter(
            Expense.job_id == str(job.id)
        ).scalar() or 0
        
        revenue_cents = int(job.quoted_amount * 100)
        profit_cents = revenue_cents - total_expenses
        profit_margin = (profit_cents / revenue_cents * 100) if revenue_cents > 0 else 0
        
        if profit_margin < AlertChecker.PROFIT_MARGIN_WARNING:
            # Check if alert already exists
            existing = db.query(JobAlert).filter(
                JobAlert.job_id == job.id,
                JobAlert.alert_type == "low_profit_margin",
                JobAlert.resolved_at.is_(None)
            ).first()
            
            if not existing:
                alert = JobAlert(
                    user_id=job.user_id,
                    job_id=job.id,
                    alert_type="low_profit_margin",
                    severity="warning",
                    message=f"Job profit margin is only {profit_margin:.1f}%",
                    details={
                        "quoted_amount": job.quoted_amount,
                        "total_expenses": total_expenses / 100,
                        "profit_margin": profit_margin
                    }
                )
                return alert
        
        return None
    
    @staticmethod
    def check_expense_spike(user: User, db: Session) -> Optional[JobAlert]:
        """Check for unusual expense spikes"""
        # Get today's expenses
        today = datetime.utcnow().date()
        today_expenses = db.query(func.sum(Expense.amount_cents)).filter(
            Expense.user_id == user.id,
            func.date(Expense.expense_date) == today
        ).scalar() or 0
        
        # Get average daily expenses for last 30 days
        thirty_days_ago = today - timedelta(days=30)
        avg_daily = db.query(func.avg(func.sum(Expense.amount_cents))).filter(
            Expense.user_id == user.id,
            func.date(Expense.expense_date) >= thirty_days_ago,
            func.date(Expense.expense_date) < today
        ).group_by(func.date(Expense.expense_date)).scalar() or 0
        
        if avg_daily > 0 and today_expenses > avg_daily * (1 + AlertChecker.EXPENSE_SPIKE_PERCENT / 100):
            # Check if alert already exists for today
            existing = db.query(JobAlert).filter(
                JobAlert.user_id == user.id,
                JobAlert.alert_type == "expense_spike",
                func.date(JobAlert.created_at) == today,
                JobAlert.resolved_at.is_(None)
            ).first()
            
            if not existing:
                spike_percent = ((today_expenses - avg_daily) / avg_daily) * 100
                alert = JobAlert(
                    user_id=user.id,
                    job_id=None,  # Not job-specific
                    alert_type="expense_spike",
                    severity="info",
                    message=f"Today's expenses are {spike_percent:.0f}% higher than average",
                    details={
                        "today_total": today_expenses / 100,
                        "daily_average": avg_daily / 100,
                        "spike_percent": spike_percent
                    }
                )
                return alert
        
        return None
    
    @staticmethod
    async def check_and_create_alerts(user_id: int, job_id: Optional[int], db: Session):
        """Run all alert checks and create alerts as needed"""
        alerts_created = []
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        
        # Check specific job if provided
        if job_id:
            job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
            if job:
                # Check job-specific alerts
                if alert := AlertChecker.check_job_cost_overrun(job, db):
                    db.add(alert)
                    alerts_created.append(alert)
                    ALERTS_CREATED.labels(severity=alert.severity).inc()
                
                if alert := AlertChecker.check_job_profit_margin(job, db):
                    db.add(alert)
                    alerts_created.append(alert)
                    ALERTS_CREATED.labels(severity=alert.severity).inc()
        
        # Check user-wide alerts
        if alert := AlertChecker.check_expense_spike(user, db):
            db.add(alert)
            alerts_created.append(alert)
            ALERTS_CREATED.labels(severity=alert.severity).inc()
        
        # Commit all alerts
        if alerts_created:
            db.commit()
            
            # Broadcast via WebSocket
            for alert in alerts_created:
                alert_data = {
                    "id": alert.id,
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "job_id": alert.job_id,
                    "created_at": alert.created_at.isoformat()
                }
                await broadcast_alert(user.email, alert_data)