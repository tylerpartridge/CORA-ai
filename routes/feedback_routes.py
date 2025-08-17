#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/feedback_routes.py
🎯 PURPOSE: Feedback collection system for beta users
🔗 IMPORTS: FastAPI, SQLAlchemy, Pydantic
📤 EXPORTS: Feedback router with collection endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from dependencies.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from models.feedback import Feedback
from services.email_service import send_feedback_notification

# Create router
feedback_router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Pydantic models
class FeedbackCreate(BaseModel):
    category: str  # "bug", "feature", "improvement", "general"
    title: str
    description: str
    priority: Optional[str] = "medium"  # "low", "medium", "high", "critical"
    user_agent: Optional[str] = None
    page_url: Optional[str] = None
    browser_info: Optional[dict] = None

class FeedbackResponse(BaseModel):
    id: int
    category: str
    title: str
    description: str
    priority: str
    status: str
    created_at: datetime
    user_email: str
    
    class Config:
        from_attributes = True

class FeedbackStats(BaseModel):
    total_feedback: int
    by_category: dict
    by_priority: dict
    by_status: dict
    recent_feedback: List[FeedbackResponse]

@feedback_router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Submit user feedback"""
    
    # Create feedback record
    db_feedback = Feedback(
        user_email=current_user.email,
        category=feedback.category,
        title=feedback.title,
        description=feedback.description,
        priority=feedback.priority,
        status="new",
        user_agent=feedback.user_agent,
        page_url=feedback.page_url,
        browser_info=json.dumps(feedback.browser_info) if feedback.browser_info else None
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    # Send notification to admin in background
    if background_tasks:
        background_tasks.add_task(
            send_feedback_notification,
            feedback=db_feedback,
            user_email=current_user.email
        )
    
    return db_feedback

@feedback_router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's own feedback submissions"""
    
    feedback = db.query(Feedback).filter(
        Feedback.user_email == current_user.email
    ).order_by(Feedback.created_at.desc()).all()
    
    return feedback

@feedback_router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback statistics (admin only)"""
    
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get total feedback count
    total_feedback = db.query(Feedback).count()
    
    # Get feedback by category
    by_category = {}
    categories = db.query(Feedback.category).distinct().all()
    for category in categories:
        count = db.query(Feedback).filter(Feedback.category == category[0]).count()
        by_category[category[0]] = count
    
    # Get feedback by priority
    by_priority = {}
    priorities = db.query(Feedback.priority).distinct().all()
    for priority in priorities:
        count = db.query(Feedback).filter(Feedback.priority == priority[0]).count()
        by_priority[priority[0]] = count
    
    # Get feedback by status
    by_status = {}
    statuses = db.query(Feedback.status).distinct().all()
    for status in statuses:
        count = db.query(Feedback).filter(Feedback.status == status[0]).count()
        by_status[status[0]] = count
    
    # Get recent feedback (last 10)
    recent_feedback = db.query(Feedback).order_by(
        Feedback.created_at.desc()
    ).limit(10).all()
    
    return FeedbackStats(
        total_feedback=total_feedback,
        by_category=by_category,
        by_priority=by_priority,
        by_status=by_status,
        recent_feedback=recent_feedback
    )

@feedback_router.get("/all", response_model=List[FeedbackResponse])
async def get_all_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get all feedback with filters (admin only)"""
    
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(Feedback)
    
    # Apply filters
    if category:
        query = query.filter(Feedback.category == category)
    if priority:
        query = query.filter(Feedback.priority == priority)
    if status:
        query = query.filter(Feedback.status == status)
    
    feedback = query.order_by(Feedback.created_at.desc()).limit(limit).all()
    
    return feedback

@feedback_router.put("/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update feedback status (admin only)"""
    
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate status
    valid_statuses = ["new", "in_progress", "resolved", "closed", "duplicate"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Get feedback
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Update status
    feedback.status = status
    feedback.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(feedback)
    
    return {"message": "Feedback status updated successfully"}

@feedback_router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete feedback (admin only)"""
    
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get feedback
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Delete feedback
    db.delete(feedback)
    db.commit()
    
    return {"message": "Feedback deleted successfully"}

# Quick feedback endpoint for simple feedback
@feedback_router.post("/quick")
async def submit_quick_feedback(
    message: str,
    category: str = "general",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit quick feedback with just a message"""
    
    # Create feedback record
    db_feedback = Feedback(
        user_email=current_user.email,
        category=category,
        title=f"Quick feedback from {current_user.email}",
        description=message,
        priority="medium",
        status="new"
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return {"message": "Feedback submitted successfully", "id": db_feedback.id}

# Feature request endpoint
@feedback_router.post("/feature-request")
async def submit_feature_request(
    title: str,
    description: str,
    use_case: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a feature request"""
    
    # Create feedback record
    db_feedback = Feedback(
        user_email=current_user.email,
        category="feature",
        title=title,
        description=f"{description}\n\nUse Case: {use_case or 'Not specified'}",
        priority="medium",
        status="new"
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return {"message": "Feature request submitted successfully", "id": db_feedback.id}

# Bug report endpoint
@feedback_router.post("/bug-report")
async def submit_bug_report(
    title: str,
    description: str,
    steps_to_reproduce: Optional[str] = None,
    expected_behavior: Optional[str] = None,
    actual_behavior: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a bug report"""
    
    # Create detailed description
    full_description = f"""
Bug Description: {description}

Steps to Reproduce: {steps_to_reproduce or 'Not specified'}

Expected Behavior: {expected_behavior or 'Not specified'}

Actual Behavior: {actual_behavior or 'Not specified'}
    """.strip()
    
    # Create feedback record
    db_feedback = Feedback(
        user_email=current_user.email,
        category="bug",
        title=title,
        description=full_description,
        priority="high",
        status="new"
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return {"message": "Bug report submitted successfully", "id": db_feedback.id} 