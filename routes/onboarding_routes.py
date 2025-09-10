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
import json

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


class OnboardingProgressPayload(BaseModel):
    data: dict

class CompleteStepRequest(BaseModel):
    step_id: str

class FeedbackRequest(BaseModel):
    category: str
    message: str
    rating: Optional[int] = None

class OnboardingCompleteRequest(BaseModel):
    userData: dict
    completedAt: str

class FeedbackResponse(BaseModel):
    id: int
    user_email: str
    category: str
    message: str
    rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


@onboarding_router.get("/progress")
async def get_onboarding_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return user's onboarding_progress JSON (empty dict if none)."""
    try:
        # SQLAlchemy JSON returns dict or None
        data = getattr(current_user, 'onboarding_progress', None) or {}
        # Ensure dict
        if not isinstance(data, dict):
            try:
                data = json.loads(data)
            except Exception:
                data = {}
        return {"user": current_user.email, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch onboarding progress")


@onboarding_router.put("/progress")
async def put_onboarding_progress(
    payload: OnboardingProgressPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Persist user's onboarding_progress JSON (overwrite)."""
    try:
        data = payload.data or {}
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="data must be an object")
        current_user.onboarding_progress = data
        db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save onboarding progress")

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

@onboarding_router.get("/prefill-data")
async def get_prefill_data(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pre-fill data from waitlist for onboarding"""
    try:
        from models.waitlist import ContractorWaitlist
        
        waitlist_entry = db.query(ContractorWaitlist).filter(
            ContractorWaitlist.email == current_user.email
        ).first()
        
        if waitlist_entry:
            return {
                "businessName": waitlist_entry.company_name,
                "businessType": waitlist_entry.business_type,
                "teamSize": waitlist_entry.team_size
            }
        return {}
    except Exception:
        return {}

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

@onboarding_router.post("/complete")
async def complete_onboarding(
    request: OnboardingCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Complete onboarding and send welcome profit report.
    Can work with or without authentication.
    """
    try:
        # Extract user data
        user_data = request.userData
        
        # Extract email from user data
        user_email = user_data.get('email')
        if not user_email:
            return {
                "success": False,
                "message": "Email address required to send profit report",
                "error": "No email provided in user data"
            }
        
        print(f"[ONBOARDING COMPLETE] Received data: {json.dumps(user_data, indent=2)}")
        
        # Save to lead file (consulting mode)
        import os
        from pathlib import Path
        
        # Create data directory if it doesn't exist
        data_dir = Path(__file__).parent.parent / "data" / "onboarding_leads"
        data_dir.mkdir(exist_ok=True)
        
        # Save to timestamped file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = data_dir / f"lead_{timestamp}_{user_data.get('name', 'unknown').lower().replace(' ', '_')}.json"
        
        lead_data = {
            "userData": user_data,
            "completedAt": request.completedAt,
            "savedAt": datetime.utcnow().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(lead_data, f, indent=2)
        
        # Generate and send welcome profit report
        from services.onboarding_report_service import onboarding_report_service
        
        report_result = onboarding_report_service.process_onboarding_completion(user_data, user_email)
        
        if report_result["success"]:
            print(f"[ONBOARDING SUCCESS] Welcome report sent to {user_email}")
            return {
                "success": True,
                "message": "Onboarding complete! Check your email for your personalized profit report.",
                "leadId": filename.stem,
                "report_sent": True,
                "email": user_email
            }
        else:
            print(f"[ONBOARDING WARNING] Report generation failed: {report_result.get('error', 'Unknown error')}")
            return {
                "success": True,
                "message": "Onboarding data saved successfully, but report delivery failed",
                "leadId": filename.stem,
                "report_sent": False,
                "report_error": report_result.get('error', 'Unknown error')
            }
        
    except Exception as e:
        print(f"[ONBOARDING ERROR] Failed to complete: {str(e)}")
        return {
            "success": False,
            "message": "Onboarding completion failed",
            "error": str(e)
        }

class BusinessProfileRequest(BaseModel):
    businessName: str
    businessType: str
    industry: str
    monthlyRevenueRange: str
    onboardingData: dict

@onboarding_router.post("/create-business-profile")
async def create_business_profile(
    request: BusinessProfileRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create business profile from onboarding data"""
    try:
        # Import here to avoid circular imports
        from models.business_profile import BusinessProfile
        from models.waitlist import ContractorWaitlist
        
        # Pre-fill from waitlist if available and not provided
        waitlist_entry = db.query(ContractorWaitlist).filter(
            ContractorWaitlist.email == current_user.email
        ).first()
        if waitlist_entry:
            # Use waitlist data as defaults if not provided
            if not request.businessName and waitlist_entry.company_name:
                request.businessName = waitlist_entry.company_name
            if not request.businessType and waitlist_entry.business_type:
                request.businessType = waitlist_entry.business_type
        
        # Check if business profile already exists
        existing_profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_email == current_user.email
        ).first()
        
        if existing_profile:
            # Update existing profile
            existing_profile.business_name = request.businessName
            existing_profile.business_type = request.businessType
            existing_profile.industry = request.industry
            existing_profile.monthly_revenue_range = request.monthlyRevenueRange
            existing_profile.updated_at = datetime.utcnow()
        else:
            # Create new profile
            business_profile = BusinessProfile(
                user_email=current_user.email,
                business_name=request.businessName,
                business_type=request.businessType,
                industry=request.industry,
                monthly_revenue_range=request.monthlyRevenueRange
            )
            db.add(business_profile)
        
        db.commit()
        
        # Also save the detailed onboarding data to a file for analysis
        try:
            from pathlib import Path
            data_dir = Path(__file__).parent.parent / "data" / "business_profiles"
            data_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = data_dir / f"profile_{timestamp}_{current_user.email.replace('@', '_').replace('.', '_')}.json"
            
            profile_data = {
                "userEmail": current_user.email,
                "businessProfile": {
                    "businessName": request.businessName,
                    "businessType": request.businessType,
                    "industry": request.industry,
                    "monthlyRevenueRange": request.monthlyRevenueRange
                },
                "detailedOnboardingData": request.onboardingData,
                "createdAt": datetime.utcnow().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(profile_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save detailed profile data: {str(e)}")
            # Don't fail the request if file save fails
        
        return {
            "success": True,
            "message": "Business profile created successfully"
        }
        
    except Exception as e:
        print(f"[BUSINESS PROFILE ERROR] Failed to create: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create business profile: {str(e)}")

class OnboardingBusinessProfileRequest(BaseModel):
    businessName: str
    businessType: str
    industry: str
    monthlyRevenueRange: str
    onboardingData: dict
    userEmail: str  # Email from onboarding data

@onboarding_router.post("/create-business-profile-onboarding")
async def create_business_profile_onboarding(
    request: OnboardingBusinessProfileRequest,
    db: Session = Depends(get_db)
):
    """Create business profile during onboarding (no auth required)"""
    try:
        # Import here to avoid circular imports
        from models.business_profile import BusinessProfile
        
        # Check if business profile already exists
        existing_profile = db.query(BusinessProfile).filter(
            BusinessProfile.user_email == request.userEmail
        ).first()
        
        if existing_profile:
            # Update existing profile
            existing_profile.business_name = request.businessName
            existing_profile.business_type = request.businessType
            existing_profile.industry = request.industry
            existing_profile.monthly_revenue_range = request.monthlyRevenueRange
            existing_profile.updated_at = datetime.utcnow()
        else:
            # Create new profile
            business_profile = BusinessProfile(
                user_email=request.userEmail,
                business_name=request.businessName,
                business_type=request.businessType,
                industry=request.industry,
                monthly_revenue_range=request.monthlyRevenueRange
            )
            db.add(business_profile)
        
        db.commit()
        
        # Also save the detailed onboarding data to a file for analysis
        try:
            from pathlib import Path
            data_dir = Path(__file__).parent.parent / "data" / "business_profiles"
            data_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = data_dir / f"profile_{timestamp}_{request.userEmail.replace('@', '_').replace('.', '_')}.json"
            
            profile_data = {
                "userEmail": request.userEmail,
                "businessProfile": {
                    "businessName": request.businessName,
                    "businessType": request.businessType,
                    "industry": request.industry,
                    "monthlyRevenueRange": request.monthlyRevenueRange
                },
                "detailedOnboardingData": request.onboardingData,
                "createdAt": datetime.utcnow().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(profile_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save detailed profile data: {str(e)}")
            # Don't fail the request if file save fails
        
        return {
            "success": True,
            "message": "Business profile created successfully during onboarding"
        }
        
    except Exception as e:
        print(f"[ONBOARDING BUSINESS PROFILE ERROR] Failed to create: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create business profile: {str(e)}")

# ---------------------------------------------------------------------------
# Save/Resume: Onboarding Progress (server-side JSON)
# ---------------------------------------------------------------------------

class ProgressPayload(BaseModel):
    progress: dict


@onboarding_router.get("/progress")
async def get_onboarding_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        progress = getattr(current_user, 'onboarding_progress', None) or {}
        if not isinstance(progress, dict):
            progress = {}
        return {"progress": progress}
    except Exception:
        return {"progress": {}}


@onboarding_router.put("/progress")
async def put_onboarding_progress(
    payload: ProgressPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        data = payload.progress or {}
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="progress must be an object")
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.onboarding_progress = data
        db.commit()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save progress: {str(e)}")

# ---------------------------------------------------------------------------
# Typical Job Types: list + custom + selection (store in onboarding_progress)
# ---------------------------------------------------------------------------

class JobTypeCreate(BaseModel):
    name: str


@onboarding_router.get("/job-types")
async def list_job_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from models import JobType
    # Global (user_id is null) + user custom
    types = db.query(JobType).filter((JobType.user_id == None) | (JobType.user_id == current_user.id)).all()  # noqa: E711
    return {"items": [{"id": t.id, "name": t.name, "custom": bool(t.user_id)} for t in types]}


@onboarding_router.post("/job-types/custom")
async def create_custom_job_type(
    payload: JobTypeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from models import JobType
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    # Upsert-like behavior: return existing if present
    existing = db.query(JobType).filter(JobType.name == name, JobType.user_id == current_user.id).first()
    if existing:
        return {"id": existing.id, "name": existing.name, "custom": True}
    jt = JobType(name=name, user_id=current_user.id)
    db.add(jt)
    db.commit()
    db.refresh(jt)
    return {"id": jt.id, "name": jt.name, "custom": True}


class JobTypeSelect(BaseModel):
    selected: list[str]


@onboarding_router.put("/job-types/select")
async def select_job_types(
    payload: JobTypeSelect,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Store selection in onboarding_progress
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    progress = getattr(user, 'onboarding_progress', None) or {}
    if not isinstance(progress, dict):
        progress = {}
    progress['job_types'] = list(payload.selected or [])
    user.onboarding_progress = progress
    db.commit()
    return {"success": True, "selected": progress['job_types']}
