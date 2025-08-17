#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/admin_routes.py
🎯 PURPOSE: Admin API routes for beta user management
🔗 IMPORTS: FastAPI router, models
📤 EXPORTS: admin_router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from models import get_db, User, Expense, Feedback, UserActivity
from dependencies.auth import require_admin
from services.email_service import send_welcome_email

# Create router
admin_router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

# Response models
class UserStats(BaseModel):
    """Response model for user statistics in admin dashboard"""
    total_users: int
    active_users: int
    total_expenses: int
    feedback_count: int

class UserInfo(BaseModel):
    """Response model for user information in admin views"""
    email: str
    is_active: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FeedbackInfo(BaseModel):
    """Response model for user feedback data"""
    id: int
    user_email: str
    category: str
    message: str
    rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class OnboardingStats(BaseModel):
    """Response model for onboarding completion statistics"""
    completed_onboarding: int
    pending_onboarding: int
    onboarding_completion_rate: float

class ActivityLog(BaseModel):
    """Response model for user activity log entries"""
    user_email: str
    action: str
    details: str
    timestamp: str

class EmailRequest(BaseModel):
    """Request model for admin email sending"""
    to_email: str
    user_name: Optional[str] = None
    email_type: str = "welcome"  # welcome, password_reset, feedback_confirmation

@admin_router.post("/send-email")
async def send_email(
    request: EmailRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Send email to a user (Admin only)"""
    try:
        # Verify user exists
        user = db.query(User).filter(User.email == request.to_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Send email based on type
        if request.email_type == "welcome":
            success = send_welcome_email(request.to_email, request.user_name)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported email type: {request.email_type}")
        
        if success:
            return {
                "message": f"Email sent successfully to {request.to_email}",
                "email_type": request.email_type,
                "success": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

@admin_router.get("/stats", response_model=UserStats)
async def get_system_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics (Admin only)"""
    try:
        
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == "true").count()
        total_expenses = db.query(Expense).count()
        feedback_count = db.query(Feedback).count()
        
        return UserStats(
            total_users=total_users,
            active_users=active_users,
            total_expenses=total_expenses,
            feedback_count=feedback_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")

@admin_router.get("/users", response_model=List[UserInfo])
async def get_all_users(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users in the system (Admin only)"""
    try:
        users = db.query(User).all()
        return [
            UserInfo(
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@admin_router.get("/feedback", response_model=List[FeedbackInfo])
async def get_all_feedback(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all feedback submitted by users (Admin only)"""
    try:
        feedback = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
        return [
            FeedbackInfo(
                id=f.id,
                user_email=f.user_email,
                category=f.category,
                message=f.message,
                rating=f.rating,
                created_at=f.created_at
            )
            for f in feedback
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@admin_router.get("/onboarding-stats", response_model=OnboardingStats)
async def get_onboarding_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get onboarding completion statistics (Admin only)"""
    try:
        total_users = db.query(User).count()
        users_with_expenses = db.query(User).join(Expense).distinct().count()
        completed_onboarding = users_with_expenses
        pending_onboarding = total_users - completed_onboarding
        onboarding_completion_rate = (completed_onboarding / total_users * 100) if total_users > 0 else 0
        
        return OnboardingStats(
            completed_onboarding=completed_onboarding,
            pending_onboarding=pending_onboarding,
            onboarding_completion_rate=round(onboarding_completion_rate, 1)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding stats: {str(e)}")

@admin_router.get("/user/{email}")
async def get_user_details(
    email: str,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user (Admin only)"""
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's expenses (optimized - single query instead of loading all records)
        expense_stats = db.query(
            func.count(Expense.id).label('count'),
            func.coalesce(func.sum(Expense.amount), 0).label('total')
        ).filter(Expense.user_email == email).first()
        
        # Get user's feedback count (optimized)
        feedback_count = db.query(func.count(Feedback.id)).filter(Feedback.user_email == email).scalar()
        
        return {
            "user": {
                "email": user.email,
                "is_active": user.is_active,
                "created_at": user.created_at
            },
            "stats": {
                "expense_count": expense_stats.count,
                "total_spent": float(expense_stats.total),
                "feedback_count": feedback_count,
                "days_since_signup": (datetime.utcnow() - user.created_at).days if user.created_at else 0
            },
            "recent_expenses": [
                {
                    "id": exp.id,
                    "description": exp.description,
                    "amount": exp.amount,
                    "category": exp.category,
                    "date": exp.date
                }
                for exp in expenses[:5]  # Last 5 expenses
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user details: {str(e)}") 

@admin_router.get("/activity", response_model=list[ActivityLog])
async def get_activity_logs(admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    logs = db.query(UserActivity).order_by(UserActivity.timestamp.desc()).limit(100).all()
    return [
        ActivityLog(
            user_email=log.user_email,
            action=log.action,
            details=log.details,
            timestamp=log.timestamp.isoformat()
        ) for log in logs
    ] 

@admin_router.get("/query-monitoring/stats")
async def get_query_monitoring_stats(
    current_user: User = Depends(require_admin)
):
    """Get query monitoring statistics"""
    from middleware.query_monitoring import query_monitor
    
    stats = query_monitor.get_query_statistics()
    slow_queries = query_monitor.get_slow_queries(limit=50)
    
    return {
        "status": "success",
        "statistics": stats,
        "slow_queries": slow_queries,
        "timestamp": datetime.now().isoformat()
    }

@admin_router.post("/query-monitoring/clear")
async def clear_query_monitoring_stats(
    current_user: User = Depends(require_admin)
):
    """Clear query monitoring statistics"""
    from middleware.query_monitoring import query_monitor
    
    query_monitor.clear_statistics()
    
    return {
        "status": "success",
        "message": "Query monitoring statistics cleared",
        "timestamp": datetime.now().isoformat()
    }

@admin_router.get("/materialized-views/refresh")
async def refresh_materialized_views(
    user_id: Optional[str] = Query(None),
    current_user: User = Depends(require_admin)
):
    """Refresh materialized view caches"""
    from utils.materialized_views import refresh_job_profitability_cache
    
    try:
        refresh_job_profitability_cache(user_id)
        
        return {
            "status": "success",
            "message": f"Materialized views refreshed for user: {user_id or 'all users'}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh materialized views: {str(e)}")

@admin_router.get("/performance/health")
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive system health metrics"""
    from utils.performance_monitor import get_performance_metrics
    
    try:
        metrics = get_performance_metrics(db)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

@admin_router.get("/performance/recommendations")
async def get_performance_recommendations(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get performance improvement recommendations"""
    from utils.performance_monitor import get_performance_recommendations
    
    try:
        recommendations = get_performance_recommendations(db)
        return {
            "status": "success",
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@admin_router.get("/response-performance/stats")
async def get_response_performance_stats(
    endpoint: Optional[str] = Query(None),
    hours: int = Query(1, ge=1, le=24),
    current_user: User = Depends(require_admin)
):
    """Get response performance statistics"""
    from utils.api_response_optimizer import performance_monitor
    
    try:
        stats = performance_monitor.get_performance_stats(endpoint, hours)
        return {
            "status": "success",
            "statistics": stats,
            "endpoint": endpoint,
            "hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get response performance stats: {str(e)}")

@admin_router.get("/response-optimization/status")
async def get_response_optimization_status(
    current_user: User = Depends(require_admin)
):
    """Get response optimization status and metrics"""
    from utils.api_response_optimizer import response_optimizer
    from utils.redis_manager import get_redis_client
    
    try:
        redis_client = get_redis_client()
        
        # Get cache statistics
        cache_keys = redis_client.keys("response_cache:*")
        cache_hits = len([k for k in cache_keys if b"hit" in k])
        cache_misses = len([k for k in cache_keys if b"miss" in k])
        
        # Get compression statistics
        compressed_responses = redis_client.keys("response_performance:*")
        
        return {
            "status": "success",
            "optimization_enabled": True,
            "compression_enabled": True,
            "caching_enabled": True,
            "cache_stats": {
                "total_keys": len(cache_keys),
                "cache_hits": cache_hits,
                "cache_misses": cache_misses,
                "hit_rate": cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0
            },
            "compression_stats": {
                "compressed_responses": len(compressed_responses),
                "compression_threshold": response_optimizer.compression_threshold
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimization status: {str(e)}") 