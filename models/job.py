#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/job.py
🎯 PURPOSE: Construction job/project database model
🔗 IMPORTS: SQLAlchemy, base model
📤 EXPORTS: Job, JobNote models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Job(Base):
    """Construction job/project model for tracking job profitability"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(100), unique=True, nullable=False, index=True)
    job_name = Column(String(200), nullable=False)
    customer_name = Column(String(200))
    job_address = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    quoted_amount = Column(Numeric(12, 2))
    status = Column(String(50), default="active")  # active, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    notes = relationship("JobNote", back_populates="job", cascade="all, delete-orphan")
    alerts = relationship("JobAlert", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job(id={self.id}, name='{self.job_name}', customer='{self.customer_name}')>"


class JobNote(Base):
    """Notes and changes for construction jobs"""
    __tablename__ = "job_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note_type = Column(String(50))  # change_order, delay, issue, general
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="notes")
    user = relationship("User")
    
    def __repr__(self):
        return f"<JobNote(id={self.id}, type='{self.note_type}', job_id={self.job_id})>"