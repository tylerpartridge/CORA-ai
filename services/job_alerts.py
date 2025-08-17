#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/job_alerts.py
🎯 PURPOSE: Job profitability alert system
🔗 IMPORTS: SQLAlchemy, datetime, typing
📤 EXPORTS: JobAlertService, Alert types and severity levels
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from models import Job, Expense, JobAlert

# Alert types
ALERT_TYPES = {
    "low_margin": "Low Profit Margin",
    "over_budget": "Over Budget",
    "no_activity": "No Recent Activity",
    "high_spending": "High Spending Rate",
    "approaching_deadline": "Approaching Deadline"
}

# Alert severity levels
SEVERITY_LEVELS = {
    "info": "Info",
    "warning": "Warning", 
    "urgent": "Urgent",
    "critical": "Critical"
}

class JobAlertService:
    """Service for managing job profitability alerts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_job_alerts(self, job: Job, user_id: int) -> List[Dict]:
        """Check a job for potential alerts and return alert objects"""
        alerts = []
        
        # Get job expenses
        expenses = self.db.query(Expense).filter(
            Expense.user_id == user_id,
            func.lower(Expense.job_name) == func.lower(job.job_name)
        ).all()
        
        # Calculate metrics
        total_spent = sum(e.amount_cents for e in expenses) / 100
        quoted = job.quoted_amount or 0
        remaining = quoted - total_spent
        margin_percent = ((quoted - total_spent) / quoted * 100) if quoted > 0 else 0
        
        # Check for low margin alerts
        if margin_percent < 10:
            alerts.append({
                "type": "low_margin",
                "severity": "critical",
                "message": f"CRITICAL: {job.job_name} margin is {margin_percent:.1f}%",
                "details": {
                    "margin_percent": margin_percent,
                    "quoted_amount": quoted,
                    "total_spent": total_spent,
                    "remaining": remaining
                }
            })
        elif margin_percent < 20:
            alerts.append({
                "type": "low_margin",
                "severity": "urgent",
                "message": f"URGENT: {job.job_name} margin is {margin_percent:.1f}%",
                "details": {
                    "margin_percent": margin_percent,
                    "quoted_amount": quoted,
                    "total_spent": total_spent,
                    "remaining": remaining
                }
            })
        elif margin_percent < 30:
            alerts.append({
                "type": "low_margin",
                "severity": "warning",
                "message": f"WARNING: {job.job_name} margin is {margin_percent:.1f}%",
                "details": {
                    "margin_percent": margin_percent,
                    "quoted_amount": quoted,
                    "total_spent": total_spent,
                    "remaining": remaining
                }
            })
        
        # Check for over budget alerts
        if remaining < 0:
            alerts.append({
                "type": "over_budget",
                "severity": "critical",
                "message": f"CRITICAL: {job.job_name} is over budget by ${abs(remaining):,.2f}",
                "details": {
                    "over_budget_amount": abs(remaining),
                    "quoted_amount": quoted,
                    "total_spent": total_spent
                }
            })
        
        # Check for no recent activity (if job is active)
        if job.status == "active" and expenses:
            latest_expense = max(expenses, key=lambda e: e.created_at)
            days_since_last = (datetime.now() - latest_expense.created_at).days
            
            if days_since_last > 7:
                alerts.append({
                    "type": "no_activity",
                    "severity": "warning",
                    "message": f"WARNING: No expenses on {job.job_name} for {days_since_last} days",
                    "details": {
                        "days_since_last_expense": days_since_last,
                        "last_expense_date": latest_expense.created_at.isoformat()
                    }
                })
        
        # Check for high spending rate
        if job.start_date and expenses:
            days_active = (datetime.now() - job.start_date).days
            if days_active > 0:
                daily_spending = total_spent / days_active
                if daily_spending > (quoted / 30):  # Spending faster than 30-day completion
                    alerts.append({
                        "type": "high_spending",
                        "severity": "warning",
                        "message": f"WARNING: {job.job_name} spending rate is high",
                        "details": {
                            "daily_spending": daily_spending,
                            "projected_completion_days": quoted / daily_spending if daily_spending > 0 else 0
                        }
                    })
        
        return alerts
    
    def create_alert(self, user_id: int, job_id: int, alert_data: Dict) -> JobAlert:
        """Create a new alert in the database"""
        alert = JobAlert(
            user_id=user_id,
            job_id=job_id,
            alert_type=alert_data["type"],
            severity=alert_data["severity"],
            message=alert_data["message"],
            details=alert_data.get("details", {})
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def get_user_alerts(self, user_id: int, unread_only: bool = False, limit: int = 50) -> List[JobAlert]:
        """Get alerts for a user"""
        query = self.db.query(JobAlert).filter(JobAlert.user_id == user_id)
        
        if unread_only:
            query = query.filter(JobAlert.read == False)
        
        return query.order_by(JobAlert.created_at.desc()).limit(limit).all()
    
    def mark_alert_read(self, alert_id: int, user_id: int) -> bool:
        """Mark an alert as read"""
        alert = self.db.query(JobAlert).filter(
            JobAlert.id == alert_id,
            JobAlert.user_id == user_id
        ).first()
        
        if alert:
            alert.read = True
            self.db.commit()
            return True
        
        return False
    
    def mark_all_alerts_read(self, user_id: int) -> int:
        """Mark all alerts as read for a user"""
        result = self.db.query(JobAlert).filter(
            JobAlert.user_id == user_id,
            JobAlert.read == False
        ).update({"read": True})
        
        self.db.commit()
        return result
    
    def resolve_alert(self, alert_id: int, user_id: int) -> bool:
        """Mark an alert as resolved"""
        alert = self.db.query(JobAlert).filter(
            JobAlert.id == alert_id,
            JobAlert.user_id == user_id
        ).first()
        
        if alert:
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def get_alert_summary(self, user_id: int) -> Dict:
        """Get alert summary for dashboard"""
        total_alerts = self.db.query(JobAlert).filter(JobAlert.user_id == user_id).count()
        unread_alerts = self.db.query(JobAlert).filter(
            JobAlert.user_id == user_id,
            JobAlert.read == False
        ).count()
        
        critical_alerts = self.db.query(JobAlert).filter(
            JobAlert.user_id == user_id,
            JobAlert.severity == "critical",
            JobAlert.read == False
        ).count()
        
        urgent_alerts = self.db.query(JobAlert).filter(
            JobAlert.user_id == user_id,
            JobAlert.severity == "urgent",
            JobAlert.read == False
        ).count()
        
        return {
            "total_alerts": total_alerts,
            "unread_alerts": unread_alerts,
            "critical_alerts": critical_alerts,
            "urgent_alerts": urgent_alerts,
            "has_alerts": unread_alerts > 0
        }
    
    def cleanup_old_alerts(self, days_old: int = 30) -> int:
        """Clean up old resolved alerts"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        result = self.db.query(JobAlert).filter(
            JobAlert.resolved_at < cutoff_date
        ).delete()
        
        self.db.commit()
        return result

# Import statements for SQLAlchemy
