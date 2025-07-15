#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/onboarding_routes.py
🎯 PURPOSE: Onboarding routes for beta user experience
🔗 IMPORTS: FastAPI router, models
📤 EXPORTS: onboarding_router
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from models import get_db, User, Expense, Feedback
from dependencies.auth import get_current_user

# Create router
onboarding_router = APIRouter(
    prefix="/api/onboarding",
    tags=["Onboarding"],
    responses={404: {"description": "Not found"}},
)

# Request/Response models
class OnboardingStep(BaseModel):
    id: str
    title: str
    description: str
    completed: bool
    required: bool
    order: int

class OnboardingProgress(BaseModel):
    user_email: str
    steps: List[OnboardingStep]
    completed_count: int
    total_count: int
    progress_percentage: float
    is_complete: bool

class CompleteStepRequest(BaseModel):
    step_id: str

class FeedbackRequest(BaseModel):
    category: str
    message: str
    rating: Optional[int] = None

class FeedbackResponse(BaseModel):
    id: int
    user_email: str
    category: str
    message: str
    rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Onboarding steps definition
ONBOARDING_STEPS = [
    {
        "id": "welcome",
        "title": "Welcome to CORA",
        "description": "Get started with your expense tracking journey",
        "required": True,
        "order": 1
    },
    {
        "id": "profile_setup",
        "title": "Complete Your Profile",
        "description": "Add your name and basic information",
        "required": True,
        "order": 2
    },
    {
        "id": "first_expense",
        "title": "Add Your First Expense",
        "description": "Track your first expense to see how it works",
        "required": True,
        "order": 3
    },
    {
        "id": "categories",
        "title": "Explore Categories",
        "description": "Browse expense categories and understand organization",
        "required": False,
        "order": 4
    },
    {
        "id": "dashboard",
        "title": "View Your Dashboard",
        "description": "Check out your expense summary and analytics",
        "required": True,
        "order": 5
    },
    {
        "id": "integrations",
        "title": "Connect Integrations (Optional)",
        "description": "Link your bank accounts or payment methods",
        "required": False,
        "order": 6
    },
    {
        "id": "feedback",
        "title": "Share Your Feedback",
        "description": "Help us improve CORA with your thoughts",
        "required": False,
        "order": 7
    }
]

@onboarding_router.get("/checklist", response_model=OnboardingProgress)
async def get_onboarding_checklist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get onboarding checklist for the current user"""
    try:
        user_email = current_user.email
        completed_steps = []
        has_expenses = db.query(Expense).filter(Expense.user_email == user_email).first() is not None
        if has_expenses:
            completed_steps.extend(["first_expense", "dashboard"])
        if has_expenses:
            completed_steps.append("categories")
        steps = []
        for step_data in ONBOARDING_STEPS:
            step = OnboardingStep(
                id=step_data["id"],
                title=step_data["title"],
                description=step_data["description"],
                completed=step_data["id"] in completed_steps,
                required=step_data["required"],
                order=step_data["order"]
            )
            steps.append(step)
        completed_count = len(completed_steps)
        total_count = len([s for s in ONBOARDING_STEPS if s["required"]])
        progress_percentage = (completed_count / total_count * 100) if total_count > 0 else 0
        is_complete = completed_count >= total_count
        return OnboardingProgress(
            user_email=user_email,
            steps=steps,
            completed_count=completed_count,
            total_count=total_count,
            progress_percentage=progress_percentage,
            is_complete=is_complete
        )
    except Exception as e:
        print(f"Onboarding checklist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding checklist: {str(e)}")

@onboarding_router.post("/complete-step")
async def complete_onboarding_step(
    request: CompleteStepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user_email = current_user.email
        step_exists = any(step["id"] == request.step_id for step in ONBOARDING_STEPS)
        if not step_exists:
            raise HTTPException(status_code=400, detail="Invalid step ID")
        return {
            "message": f"Step '{request.step_id}' marked as completed",
            "step_id": request.step_id,
            "user_email": user_email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete step: {str(e)}")

@onboarding_router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user_email = current_user.email
        if not request.message or len(request.message.strip()) < 10:
            raise HTTPException(status_code=400, detail="Feedback message must be at least 10 characters")
        if request.rating and (request.rating < 1 or request.rating > 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        feedback = Feedback(
            user_email=user_email,
            category=request.category,
            message=request.message,
            rating=request.rating,
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        response = FeedbackResponse(
            id=feedback.id,
            user_email=feedback.user_email,
            category=feedback.category,
            message=feedback.message,
            rating=feedback.rating,
            created_at=feedback.created_at
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@onboarding_router.get("/stats")
async def get_onboarding_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user_email = current_user.email
        expense_count = db.query(Expense).filter(Expense.user_email == user_email).count()
        user = db.query(User).filter(User.email == user_email).first()
        days_since_signup = (datetime.utcnow() - user.created_at).days if user and user.created_at else 0
        return {
            "user_email": user_email,
            "expense_count": expense_count,
            "days_since_signup": days_since_signup,
            "onboarding_complete": expense_count > 0,
            "last_activity": user.updated_at if user and hasattr(user, 'updated_at') else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding stats: {str(e)}")