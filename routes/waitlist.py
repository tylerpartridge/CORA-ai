"""
Contractor Waitlist API Routes
Handles beta signups and waitlist management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator

from models import get_db
from models.waitlist import ContractorWaitlist
from services.notification_service import NotificationService
from dependencies.auth import get_current_user, User

waitlist_router = APIRouter()

class WaitlistSignupRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company_name: Optional[str] = None
    source: str = "website"  # facebook_group, referral, website
    source_details: Optional[str] = None  # FB group name, referrer email
    signup_keyword: Optional[str] = None  # TRUCK, BETA
    business_type: Optional[str] = None
    team_size: Optional[str] = None
    biggest_pain_point: Optional[str] = None
    referred_by_email: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        """
        Validate and sanitize the name field.
        
        Args:
            v: The name value to validate
            
        Returns:
            str: The validated and trimmed name
            
        Raises:
            ValueError: If name is less than 2 characters after trimming
        """
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()

class WaitlistResponse(BaseModel):
    id: int
    position: int
    message: str
    referral_code: str

@waitlist_router.post("/signup", response_model=WaitlistResponse)
async def signup_for_waitlist(
    request: WaitlistSignupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Add contractor to beta waitlist
    """
    # Check if already on waitlist
    existing = db.query(ContractorWaitlist).filter(
        ContractorWaitlist.email == request.email
    ).first()
    
    if existing:
        # Get their position
        position = db.query(func.count(ContractorWaitlist.id)).filter(
            ContractorWaitlist.id <= existing.id,
            ContractorWaitlist.status == 'pending'
        ).scalar()
        
        return WaitlistResponse(
            id=existing.id,
            position=position,
            message="You're already on the waitlist! We'll reach out soon.",
            referral_code=f"CORA{existing.id}"
        )
    
    # Handle referral
    referred_by = None
    if request.referred_by_email:
        referrer = db.query(ContractorWaitlist).filter(
            ContractorWaitlist.email == request.referred_by_email
        ).first()
        if referrer:
            referred_by = referrer.id
    
    # Create new waitlist entry
    new_signup = ContractorWaitlist(
        name=request.name,
        email=request.email,
        phone=request.phone,
        company_name=request.company_name,
        source=request.source,
        source_details=request.source_details,
        signup_keyword=request.signup_keyword,
        business_type=request.business_type,
        team_size=request.team_size,
        biggest_pain_point=request.biggest_pain_point,
        referred_by_id=referred_by
    )
    
    db.add(new_signup)
    db.commit()
    db.refresh(new_signup)
    
    # Get position in line
    position = db.query(func.count(ContractorWaitlist.id)).filter(
        ContractorWaitlist.status == 'pending'
    ).scalar()
    
    # Send welcome email
    background_tasks.add_task(
        NotificationService.send_waitlist_welcome,
        new_signup.email,
        new_signup.name,
        position,
        f"CORA{new_signup.id}"
    )
    
    # Special handling for first 10 signups
    if position <= 10:
        message = f"🎉 You're #{position} on the list! You'll get access within 24 hours."
    else:
        message = f"You're #{position} on the waitlist. We're adding contractors weekly!"
    
    return WaitlistResponse(
        id=new_signup.id,
        position=position,
        message=message,
        referral_code=f"CORA{new_signup.id}"
    )

@waitlist_router.get("/position/{email}")
async def check_waitlist_position(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Check position on waitlist
    """
    signup = db.query(ContractorWaitlist).filter(
        ContractorWaitlist.email == email
    ).first()
    
    if not signup:
        raise HTTPException(status_code=404, detail="Email not found on waitlist")
    
    position = db.query(func.count(ContractorWaitlist.id)).filter(
        ContractorWaitlist.id <= signup.id,
        ContractorWaitlist.status == 'pending'
    ).scalar()
    
    return {
        "position": position,
        "status": signup.status,
        "referral_code": f"CORA{signup.id}",
        "referral_count": db.query(func.count(ContractorWaitlist.id)).filter(
            ContractorWaitlist.referred_by_id == signup.id
        ).scalar()
    }

# Admin endpoints
@waitlist_router.get("/admin/list")
async def list_waitlist(
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin: List waitlist entries
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(ContractorWaitlist)
    
    if status:
        query = query.filter(ContractorWaitlist.status == status)
    if source:
        query = query.filter(ContractorWaitlist.source == source)
    
    signups = query.order_by(ContractorWaitlist.created_at.desc()).limit(limit).all()
    
    return [{
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "company_name": s.company_name,
        "source": s.source,
        "status": s.status,
        "created_at": s.created_at,
        "biggest_pain_point": s.biggest_pain_point,
        "referral_count": db.query(func.count(ContractorWaitlist.id)).filter(
            ContractorWaitlist.referred_by_id == s.id
        ).scalar()
    } for s in signups]

@waitlist_router.post("/admin/invite/{waitlist_id}")
async def invite_from_waitlist(
    waitlist_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin: Send beta invitation
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    signup = db.query(ContractorWaitlist).filter(
        ContractorWaitlist.id == waitlist_id
    ).first()
    
    if not signup:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    
    # Update status
    signup.status = 'invited'
    signup.invitation_sent_at = datetime.utcnow()
    db.commit()
    
    # Send invitation email
    background_tasks.add_task(
        NotificationService.send_beta_invitation,
        signup.email,
        signup.name
    )
    
    return {"message": f"Invitation sent to {signup.email}"}

@waitlist_router.get("/stats")
async def waitlist_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin: Waitlist statistics
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total = db.query(func.count(ContractorWaitlist.id)).scalar()
    pending = db.query(func.count(ContractorWaitlist.id)).filter(
        ContractorWaitlist.status == 'pending'
    ).scalar()
    invited = db.query(func.count(ContractorWaitlist.id)).filter(
        ContractorWaitlist.status == 'invited'
    ).scalar()
    active = db.query(func.count(ContractorWaitlist.id)).filter(
        ContractorWaitlist.status == 'active'
    ).scalar()
    
    # Source breakdown
    sources = db.query(
        ContractorWaitlist.source,
        func.count(ContractorWaitlist.id).label('count')
    ).group_by(ContractorWaitlist.source).all()
    
    # Business type breakdown
    business_types = db.query(
        ContractorWaitlist.business_type,
        func.count(ContractorWaitlist.id).label('count')
    ).filter(
        ContractorWaitlist.business_type.isnot(None)
    ).group_by(ContractorWaitlist.business_type).all()
    
    # Top referrers
    top_referrers = db.query(
        ContractorWaitlist.id,
        ContractorWaitlist.name,
        ContractorWaitlist.email,
        func.count(ContractorWaitlist.id).label('referral_count')
    ).join(
        ContractorWaitlist.referred_by
    ).group_by(
        ContractorWaitlist.id,
        ContractorWaitlist.name,
        ContractorWaitlist.email
    ).order_by(
        func.count(ContractorWaitlist.id).desc()
    ).limit(5).all()
    
    return {
        "total": total,
        "pending": pending,
        "invited": invited,
        "active": active,
        "sources": {s.source: s.count for s in sources},
        "business_types": {b.business_type: b.count for b in business_types},
        "top_referrers": [{
            "name": r.name,
            "email": r.email,
            "referral_count": r.referral_count
        } for r in top_referrers]
    }