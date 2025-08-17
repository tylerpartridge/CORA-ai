#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/alert_routes.py
🎯 PURPOSE: Job alert API endpoints
🔗 IMPORTS: FastAPI, SQLAlchemy, alert service
📤 EXPORTS: alert_router
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models import get_db, Job, User
from dependencies.auth import get_current_user
from services.job_alerts import JobAlertService, JobAlert

# Create router
alert_router = APIRouter(
    prefix="/api/alerts",
    tags=["alerts"]
)

# Request/Response models
class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    details: Optional[dict] = None
    read: bool
    created_at: datetime
    job_name: str
    job_id: int

class AlertSummary(BaseModel):
    total_alerts: int
    unread_alerts: int
    critical_alerts: int
    urgent_alerts: int
    has_alerts: bool

@alert_router.get("/summary", response_model=AlertSummary)
async def get_alert_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert summary for dashboard"""
    alert_service = JobAlertService(db)
    return alert_service.get_alert_summary(current_user.id)

@alert_router.get("/", response_model=List[AlertResponse])
async def get_user_alerts(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts for current user"""
    alert_service = JobAlertService(db)
    alerts = alert_service.get_user_alerts(current_user.id, unread_only, limit)
    
    # Convert to response format
    alert_responses = []
    for alert in alerts:
        job = db.query(Job).filter(Job.id == alert.job_id).first()
        alert_responses.append(AlertResponse(
            id=alert.id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            details=alert.details,
            read=alert.read,
            created_at=alert.created_at,
            job_name=job.job_name if job else "Unknown Job",
            job_id=alert.job_id
        ))
    
    return alert_responses

@alert_router.post("/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as read"""
    alert_service = JobAlertService(db)
    success = alert_service.mark_alert_read(alert_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert marked as read"}

@alert_router.post("/read-all")
async def mark_all_alerts_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all alerts as read for current user"""
    alert_service = JobAlertService(db)
    count = alert_service.mark_all_alerts_read(current_user.id)
    
    return {"message": f"Marked {count} alerts as read"}

@alert_router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as resolved"""
    alert_service = JobAlertService(db)
    success = alert_service.resolve_alert(alert_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved"}

@alert_router.post("/check-jobs")
async def check_all_jobs_for_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check all user jobs for new alerts"""
    alert_service = JobAlertService(db)
    
    # Get all user jobs (ordered for consistent processing)
    jobs = db.query(Job).filter(Job.user_id == current_user.id).order_by(Job.created_at.desc()).all()
    
    new_alerts = []
    for job in jobs:
        alerts = alert_service.check_job_alerts(job, current_user.id)
        
        # Create alerts in database
        for alert_data in alerts:
            # Check if similar alert already exists (avoid duplicates)
            existing = db.query(JobAlert).filter(
                JobAlert.user_id == current_user.id,
                JobAlert.job_id == job.id,
                JobAlert.alert_type == alert_data["type"],
                JobAlert.read == False
            ).first()
            
            if not existing:
                alert = alert_service.create_alert(current_user.id, job.id, alert_data)
                new_alerts.append({
                    "id": alert.id,
                    "message": alert.message,
                    "severity": alert.severity,
                    "job_name": job.job_name
                })
    
    return {
        "message": f"Checked {len(jobs)} jobs",
        "new_alerts": len(new_alerts),
        "alerts": new_alerts
    }

@alert_router.delete("/cleanup")
async def cleanup_old_alerts(
    days_old: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up old resolved alerts (admin only)"""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    alert_service = JobAlertService(db)
    deleted_count = alert_service.cleanup_old_alerts(days_old)
    
    return {"message": f"Deleted {deleted_count} old alerts"} 