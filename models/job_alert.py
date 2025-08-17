#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/job_alert.py
🎯 PURPOSE: Job alert database model
🔗 IMPORTS: SQLAlchemy base and types
📤 EXPORTS: JobAlert model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class JobAlert(Base):
    """Database model for job alerts"""
    __tablename__ = "job_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False, default="warning")
    message = Column(String(500), nullable=False)
    details = Column(JSON, nullable=True)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    job = relationship("Job", back_populates="alerts")
    
    def __repr__(self):
        return f"<JobAlert {self.id}: {self.alert_type} - {self.severity}>"