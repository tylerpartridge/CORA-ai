#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/analytics.py
🎯 PURPOSE: User analytics and engagement tracking endpoints
🔗 IMPORTS: FastAPI, SQLAlchemy, services
📤 EXPORTS: Analytics router with comprehensive tracking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import get_db, User
from dependencies.auth import get_current_user
from services.user_analytics import UserAnalyticsService, EngagementTracker

router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/user/engagement")
async def get_user_engagement(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive user engagement metrics"""
    try:
        analytics_service = UserAnalyticsService(db)
        engagement_data = analytics_service.get_user_engagement_summary(
            user_id=str(current_user.id), 
            days=days
        )
        
        return {
            "success": True,
            "user_id": str(current_user.id),
            "engagement": engagement_data,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get engagement data: {str(e)}")

@router.get("/user/retention")
async def get_user_retention(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user retention and churn risk metrics"""
    try:
        analytics_service = UserAnalyticsService(db)
        retention_data = analytics_service.get_user_retention_metrics(
            user_id=str(current_user.id)
        )
        
        return {
            "success": True,
            "user_id": str(current_user.id),
            "retention": retention_data,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get retention data: {str(e)}")

@router.get("/user/feature-adoption")
async def get_feature_adoption(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get feature adoption and usage metrics"""
    try:
        analytics_service = UserAnalyticsService(db)
        adoption_data = analytics_service.get_feature_adoption_metrics(
            user_id=str(current_user.id)
        )
        
        return {
            "success": True,
            "user_id": str(current_user.id),
            "feature_adoption": adoption_data,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature adoption data: {str(e)}")

@router.post("/track/activity")
async def track_activity(
    request: Request,
    action: str,
    category: Optional[str] = None,
    details: Optional[str] = None,
    metadata: Optional[Dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Track a user activity"""
    try:
        analytics_service = UserAnalyticsService(db)
        
        # Get session ID from request headers or generate new one
        session_id = request.headers.get('X-Session-ID')
        
        # Get user agent and IP
        user_agent = request.headers.get('User-Agent')
        ip_address = request.client.host if request.client else None
        
        activity = analytics_service.track_activity(
            user_id=str(current_user.id),
            action=action,
            category=category,
            details=details,
            metadata=metadata,
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return {
            "success": True,
            "activity_id": activity.id,
            "tracked_at": activity.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track activity: {str(e)}")

@router.post("/track/page-view")
async def track_page_view(
    request: Request,
    page_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Track a page view"""
    try:
        tracker = EngagementTracker(db)
        
        session_id = request.headers.get('X-Session-ID')
        user_agent = request.headers.get('User-Agent')
        ip_address = request.client.host if request.client else None
        
        activity = tracker.track_page_view(
            user_id=str(current_user.id),
            page_url=page_url,
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return {
            "success": True,
            "activity_id": activity.id,
            "page_url": page_url,
            "tracked_at": activity.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track page view: {str(e)}")

@router.post("/track/feature-usage")
async def track_feature_usage(
    request: Request,
    feature: str,
    details: Optional[str] = None,
    metadata: Optional[Dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Track feature usage"""
    try:
        tracker = EngagementTracker(db)
        
        session_id = request.headers.get('X-Session-ID')
        
        activity = tracker.track_feature_usage(
            user_id=str(current_user.id),
            feature=feature,
            details=details,
            metadata=metadata,
            session_id=session_id
        )
        
        return {
            "success": True,
            "activity_id": activity.id,
            "feature": feature,
            "tracked_at": activity.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track feature usage: {str(e)}")

@router.post("/track/insight-interaction")
async def track_insight_interaction(
    request: Request,
    insight_id: str,
    action: str,  # 'view', 'click', 'dismiss', 'act_upon'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Track insight interactions"""
    try:
        tracker = EngagementTracker(db)
        
        session_id = request.headers.get('X-Session-ID')
        
        activity = tracker.track_insight_interaction(
            user_id=str(current_user.id),
            insight_id=insight_id,
            action=action,
            session_id=session_id
        )
        
        return {
            "success": True,
            "activity_id": activity.id,
            "insight_id": insight_id,
            "action": action,
            "tracked_at": activity.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track insight interaction: {str(e)}")

@router.post("/session/start")
async def start_session(
    request: Request,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Start a new user session"""
    try:
        analytics_service = UserAnalyticsService(db)
        
        user_agent = request.headers.get('User-Agent')
        ip_address = request.client.host if request.client else None
        
        session = analytics_service.start_session(
            user_id=str(current_user.id),
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return {
            "success": True,
            "session_id": session.session_id,
            "started_at": session.started_at.isoformat(),
            "device_type": session.device_type,
            "browser": session.browser,
            "os": session.os
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/session/end")
async def end_session(
    request: Request,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """End a user session"""
    try:
        analytics_service = UserAnalyticsService(db)
        
        session = analytics_service.end_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_id": session.session_id,
            "ended_at": session.ended_at.isoformat(),
            "duration_minutes": session.duration
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@router.get("/dashboard/summary")
async def get_analytics_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive analytics dashboard summary"""
    try:
        analytics_service = UserAnalyticsService(db)
        
        # Get all metrics
        engagement = analytics_service.get_user_engagement_summary(str(current_user.id), days=30)
        retention = analytics_service.get_user_retention_metrics(str(current_user.id))
        feature_adoption = analytics_service.get_feature_adoption_metrics(str(current_user.id))
        
        # Calculate summary metrics
        total_features_adopted = sum([
            1 for feature in feature_adoption.values() 
            if feature['adoption_status'] in ['adopted', 'highly_adopted']
        ])
        
        summary = {
            "engagement_score": engagement['engagement_score'],
            "retention_score": retention['retention_score'],
            "churn_risk": retention['churn_risk'],
            "total_activities": engagement['total_activities'],
            "total_sessions": engagement['total_sessions'],
            "avg_session_duration": engagement['avg_session_duration'],
            "features_adopted": total_features_adopted,
            "lifecycle_stage": retention['user_lifecycle_stage'],
            "most_active_day": engagement['most_active_day'],
            "most_used_feature": engagement['most_used_feature']
        }
        
        return {
            "success": True,
            "user_id": str(current_user.id),
            "summary": summary,
            "engagement": engagement,
            "retention": retention,
            "feature_adoption": feature_adoption,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics summary: {str(e)}") 