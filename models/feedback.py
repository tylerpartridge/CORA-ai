#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/feedback.py
🎯 PURPOSE: Feedback model for user feedback and bug reports
🔗 IMPORTS: SQLAlchemy
📤 EXPORTS: Feedback model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from models.base import Base

class Feedback(Base):
    """Feedback model for user feedback and bug reports"""
    
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)  # "bug", "feature", "improvement", "general"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium", index=True)  # "low", "medium", "high", "critical"
    status = Column(String, default="new", index=True)  # "new", "in_progress", "resolved", "closed", "duplicate"
    user_agent = Column(Text, nullable=True)
    page_url = Column(String, nullable=True)
    browser_info = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, category='{self.category}', title='{self.title}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_email": self.user_email,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "user_agent": self.user_agent,
            "page_url": self.page_url,
            "browser_info": self.browser_info,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 