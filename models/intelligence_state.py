#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/intelligence_state.py
🎯 PURPOSE: Shared intelligence models for cross-brain communication
🔗 IMPORTS: SQLAlchemy base and User relationship
📤 EXPORTS: IntelligenceSignal, EmotionalProfile
"""

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class IntelligenceSignal(Base):
    """Stores intelligence signals for cross-brain communication."""
    __tablename__ = "intelligence_signals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    source_component = Column(String(50), nullable=False)  # Which brain generated this
    priority = Column(Float, default=0.5)
    data = Column(JSON)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="intelligence_signals")


class EmotionalProfile(Base):
    """Tracks user emotional state over time."""
    __tablename__ = "emotional_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    current_state = Column(String(50), default="neutral")
    stress_level = Column(Float, default=5.0)  # 0-10 scale
    confidence = Column(Float, default=0.5)  # 0-1 confidence in assessment
    last_crisis_date = Column(DateTime)
    wellness_score = Column(Float, default=7.0)  # 0-10 scale
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="emotional_profile", uselist=False)


