#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/waitlist.py
🎯 PURPOSE: Contractor waitlist system - integrates with existing user/onboarding
🔗 IMPORTS: SQLAlchemy, existing models
📤 EXPORTS: ContractorWaitlist model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base

class ContractorWaitlist(Base):
    """Contractor waitlist entry - integrates with existing user system"""
    __tablename__ = "contractor_waitlist"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(20))
    company_name = Column(String(200))
    
    # Source tracking
    source = Column(String(100))  # 'facebook_group', 'referral', 'website'
    source_details = Column(Text)  # Which FB group, who referred, etc.
    signup_keyword = Column(String(50))  # 'TRUCK', 'BETA', etc.
    
    # Business info
    business_type = Column(String(100))  # 'general_contractor', 'plumber', 'electrician'
    team_size = Column(String(50))  # '1-5', '6-10', '11-25', '25+'
    biggest_pain_point = Column(Text)  # What problem they want solved
    
    # Status
    status = Column(String(50), default='pending')  # pending, invited, active, declined
    invitation_sent_at = Column(DateTime)
    invitation_accepted_at = Column(DateTime)
    
    # Referral tracking
    referred_by_id = Column(Integer, ForeignKey('contractor_waitlist.id'))
    referred_by = relationship('ContractorWaitlist', remote_side=[id])
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Notes
    admin_notes = Column(Text)
    
    def __repr__(self):
        return f"<ContractorWaitlist {self.name} - {self.company_name}>"