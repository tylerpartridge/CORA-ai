#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/models/user_activity.py
🎯 PURPOSE: Track user actions for comprehensive analytics
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class UserActivity(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    category = Column(String, nullable=True, index=True)  # e.g., 'navigation', 'feature_usage', 'engagement'
    details = Column(String, nullable=True)
    activity_metadata = Column(JSON, nullable=True)  # Additional structured data
    session_id = Column(String, nullable=True, index=True)
    page_url = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    response_time = Column(Float, nullable=True)  # API response time in seconds
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class UserEngagement(Base):
    __tablename__ = "user_engagement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    session_count = Column(Integer, default=0)
    total_time_spent = Column(Float, default=0.0)  # in minutes
    pages_visited = Column(Integer, default=0)
    features_used = Column(Integer, default=0)
    insights_viewed = Column(Integer, default=0)
    insights_acted_upon = Column(Integer, default=0)
    expenses_added = Column(Integer, default=0)
    jobs_created = Column(Integer, default=0)
    chat_interactions = Column(Integer, default=0)
    voice_interactions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String, nullable=False, unique=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Float, nullable=True)  # in minutes
    device_type = Column(String, nullable=True)  # mobile, desktop, tablet
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    is_active = Column(Boolean, default=True) 