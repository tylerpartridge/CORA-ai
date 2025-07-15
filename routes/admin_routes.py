#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/admin_routes.py
🎯 PURPOSE: Admin API routes for beta user management
🔗 IMPORTS: FastAPI router, models
📤 EXPORTS: admin_router
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from models import get_db, User, Expense, Feedback, UserActivity
from dependencies.auth import get_current_user

# Create router
admin_router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

# Response models
class UserStats(BaseModel):
    total_users: int
    active_users: int
    total_expenses: int
    feedback_count: int

class UserInfo(BaseModel):
    email: str
    is_active: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FeedbackInfo(BaseModel):
    id: int
    user_email: str
    category: str
    message: str
    rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class OnboardingStats(BaseModel):
    completed_onboarding: int
    pending_onboarding: int
    onboarding_completion_rate: float

class ActivityLog(BaseModel):
    user_email: str
    action: str
    details: str
    timestamp: str

@admin_router.get("/stats", response_model=UserStats)
async def get_system_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics"""
    try:
        # Check if user is admin (for now, allow all authenticated users)
        # In production, add proper admin role checking
        
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == "true").count()
        total_expenses = db.query(Expense).count()
        feedback_count = db.query(Feedback).count()
        
        return UserStats(
            total_users=total_users,
            active_users=active_users,
            total_expenses=total_expenses,
            feedback_count=feedback_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")

@admin_router.get("/users", response_model=List[UserInfo])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users in the system"""
    try:
        users = db.query(User).all()
        return [
            UserInfo(
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@admin_router.get("/feedback", response_model=List[FeedbackInfo])
async def get_all_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all feedback submitted by users"""
    try:
        feedback = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
        return [
            FeedbackInfo(
                id=f.id,
                user_email=f.user_email,
                category=f.category,
                message=f.message,
                rating=f.rating,
                created_at=f.created_at
            )
            for f in feedback
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@admin_router.get("/onboarding-stats", response_model=OnboardingStats)
async def get_onboarding_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get onboarding completion statistics"""
    try:
        total_users = db.query(User).count()
        users_with_expenses = db.query(User).join(Expense).distinct().count()
        completed_onboarding = users_with_expenses
        pending_onboarding = total_users - completed_onboarding
        onboarding_completion_rate = (completed_onboarding / total_users * 100) if total_users > 0 else 0
        
        return OnboardingStats(
            completed_onboarding=completed_onboarding,
            pending_onboarding=pending_onboarding,
            onboarding_completion_rate=round(onboarding_completion_rate, 1)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding stats: {str(e)}")

@admin_router.get("/user/{email}")
async def get_user_details(
    email: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's expenses
        expenses = db.query(Expense).filter(Expense.user_email == email).all()
        expense_count = len(expenses)
        total_spent = sum(expense.amount for expense in expenses)
        
        # Get user's feedback
        feedback = db.query(Feedback).filter(Feedback.user_email == email).all()
        feedback_count = len(feedback)
        
        return {
            "user": {
                "email": user.email,
                "is_active": user.is_active,
                "created_at": user.created_at
            },
            "stats": {
                "expense_count": expense_count,
                "total_spent": total_spent,
                "feedback_count": feedback_count,
                "days_since_signup": (datetime.utcnow() - user.created_at).days if user.created_at else 0
            },
            "recent_expenses": [
                {
                    "id": exp.id,
                    "description": exp.description,
                    "amount": exp.amount,
                    "category": exp.category,
                    "date": exp.date
                }
                for exp in expenses[:5]  # Last 5 expenses
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user details: {str(e)}") 

@admin_router.get("/activity", response_model=list[ActivityLog])
async def get_activity_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(UserActivity).order_by(UserActivity.timestamp.desc()).limit(100).all()
    return [
        ActivityLog(
            user_email=log.user_email,
            action=log.action,
            details=log.details,
            timestamp=log.timestamp.isoformat()
        ) for log in logs
    ] 