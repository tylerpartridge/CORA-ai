#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/services/user_analytics.py
🎯 PURPOSE: Comprehensive user analytics and engagement tracking
🔗 IMPORTS: SQLAlchemy, datetime, statistics
📤 EXPORTS: UserAnalyticsService, EngagementTracker
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc
import uuid
from statistics import mean

from models.user_activity import UserActivity, UserSession
from models.user import User

class UserAnalyticsService:
    """Comprehensive user analytics service"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def track_activity(self, user_id: str, action: str, category: str = None, 
                      details: str = None, metadata: Dict = None, 
                      session_id: str = None, page_url: str = None,
                      user_agent: str = None, ip_address: str = None,
                      response_time: float = None, success: bool = True) -> UserActivity:
        """Track a user activity"""
        
        activity = UserActivity(
            user_id=user_id,
            action=action,
            category=category,
            details=details,
            activity_metadata=metadata,
            session_id=session_id,
            page_url=page_url,
            user_agent=user_agent,
            ip_address=ip_address,
            response_time=response_time,
            success=success
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    def start_session(self, user_id: str, session_id: str = None, 
                     user_agent: str = None, ip_address: str = None) -> UserSession:
        """Start a new user session"""
        
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # End any existing active sessions for this user
        self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({"is_active": False, "ended_at": datetime.now()})
        
        # Create new session
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address,
            device_type=self._detect_device_type(user_agent),
            browser=self._detect_browser(user_agent),
            os=self._detect_os(user_agent)
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def end_session(self, session_id: str) -> UserSession:
        """End a user session"""
        
        session = self.db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.ended_at = datetime.now()
            session.is_active = False
            session.duration = (session.ended_at - session.started_at).total_seconds() / 60
            
            self.db.commit()
            self.db.refresh(session)
            
        return session
    
    def get_user_engagement_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive engagement summary for a user"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Get activity counts
        activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.timestamp >= start_date
        ).all()
        
        # Get session data
        sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.started_at >= start_date
        ).all()
        
        # Calculate engagement metrics
        engagement_metrics = {
            'total_activities': len(activities),
            'total_sessions': len(sessions),
            'avg_session_duration': mean([s.duration for s in sessions if s.duration]) if sessions else 0,
            'total_time_spent': sum([s.duration for s in sessions if s.duration]) if sessions else 0,
            'most_active_day': self._get_most_active_day(activities),
            'most_used_feature': self._get_most_used_feature(activities),
            'engagement_score': self._calculate_engagement_score(activities, sessions),
            'activity_trend': self._get_activity_trend(activities, days),
            'feature_usage': self._get_feature_usage_breakdown(activities),
            'device_usage': self._get_device_usage_breakdown(sessions)
        }
        
        return engagement_metrics
    
    def get_user_retention_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get user retention and churn risk metrics"""
        
        # Get user's first activity
        first_activity = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(UserActivity.timestamp.asc()).first()
        
        if not first_activity:
            return {'error': 'No activity found for user'}
        
        # Calculate days since first activity
        days_since_first = (datetime.now() - first_activity.timestamp).days
        
        # Get recent activity (last 7 days)
        recent_activity = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.timestamp >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Get activity frequency
        total_activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).count()
        
        avg_activities_per_day = total_activities / max(days_since_first, 1)
        
        # Calculate churn risk
        churn_risk = self._calculate_churn_risk(recent_activity, avg_activities_per_day, days_since_first)
        
        return {
            'days_since_first_activity': days_since_first,
            'total_activities': total_activities,
            'recent_activity_count': recent_activity,
            'avg_activities_per_day': avg_activities_per_day,
            'churn_risk': churn_risk,
            'retention_score': 100 - churn_risk,
            'user_lifecycle_stage': self._determine_lifecycle_stage(days_since_first, total_activities)
        }
    
    def get_feature_adoption_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get feature adoption and usage metrics"""
        
        # Get all activities for the user
        activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).all()
        
        # Define feature categories
        feature_categories = {
            'expense_tracking': ['create_expense', 'update_expense', 'delete_expense', 'upload_receipt'],
            'profit_intelligence': ['view_profit_intelligence', 'view_insights', 'dismiss_insight'],
            'chat_interactions': ['chat_message', 'voice_input', 'ai_response'],
            'job_management': ['create_job', 'update_job', 'view_job'],
            'analytics': ['view_dashboard', 'view_reports', 'export_data'],
            'onboarding': ['complete_onboarding', 'update_profile', 'connect_bank']
        }
        
        adoption_metrics = {}
        
        for category, actions in feature_categories.items():
            category_activities = [a for a in activities if a.action in actions]
            adoption_metrics[category] = {
                'total_uses': len(category_activities),
                'last_used': max([a.timestamp for a in category_activities]) if category_activities else None,
                'adoption_status': self._determine_adoption_status(category_activities),
                'usage_frequency': self._calculate_usage_frequency(category_activities)
            }
        
        return adoption_metrics
    
    def _detect_device_type(self, user_agent: str) -> str:
        """Detect device type from user agent"""
        if not user_agent:
            return 'unknown'
        
        user_agent_lower = user_agent.lower()
        
        if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
            return 'mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            return 'tablet'
        else:
            return 'desktop'
    
    def _detect_browser(self, user_agent: str) -> str:
        """Detect browser from user agent"""
        if not user_agent:
            return 'unknown'
        
        user_agent_lower = user_agent.lower()
        
        if 'chrome' in user_agent_lower:
            return 'chrome'
        elif 'firefox' in user_agent_lower:
            return 'firefox'
        elif 'safari' in user_agent_lower:
            return 'safari'
        elif 'edge' in user_agent_lower:
            return 'edge'
        else:
            return 'other'
    
    def _detect_os(self, user_agent: str) -> str:
        """Detect operating system from user agent"""
        if not user_agent:
            return 'unknown'
        
        user_agent_lower = user_agent.lower()
        
        if 'windows' in user_agent_lower:
            return 'windows'
        elif 'mac' in user_agent_lower or 'os x' in user_agent_lower:
            return 'macos'
        elif 'linux' in user_agent_lower:
            return 'linux'
        elif 'android' in user_agent_lower:
            return 'android'
        elif 'ios' in user_agent_lower or 'iphone' in user_agent_lower:
            return 'ios'
        else:
            return 'other'
    
    def _get_most_active_day(self, activities: List[UserActivity]) -> str:
        """Get the day of week with most activity"""
        if not activities:
            return 'unknown'
        
        day_counts = {}
        for activity in activities:
            day = activity.timestamp.strftime('%A')
            day_counts[day] = day_counts.get(day, 0) + 1
        
        return max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else 'unknown'
    
    def _get_most_used_feature(self, activities: List[UserActivity]) -> str:
        """Get the most used feature"""
        if not activities:
            return 'unknown'
        
        feature_counts = {}
        for activity in activities:
            feature_counts[activity.action] = feature_counts.get(activity.action, 0) + 1
        
        return max(feature_counts.items(), key=lambda x: x[1])[0] if feature_counts else 'unknown'
    
    def _calculate_engagement_score(self, activities: List[UserActivity], sessions: List[UserSession]) -> float:
        """Calculate engagement score (0-100)"""
        if not activities:
            return 0.0
        
        # Base score from activity count
        activity_score = min(len(activities) * 2, 40)  # Max 40 points for activities
        
        # Session duration score
        total_duration = sum([s.duration for s in sessions if s.duration]) if sessions else 0
        duration_score = min(total_duration / 10, 30)  # Max 30 points for time spent
        
        # Feature diversity score
        unique_features = len(set([a.action for a in activities]))
        diversity_score = min(unique_features * 3, 30)  # Max 30 points for feature diversity
        
        return min(activity_score + duration_score + diversity_score, 100)
    
    def _get_activity_trend(self, activities: List[UserActivity], days: int) -> List[Dict[str, Any]]:
        """Get activity trend over time"""
        if not activities:
            return []
        
        # Group activities by date
        date_activity = {}
        for activity in activities:
            date = activity.timestamp.date()
            date_activity[date] = date_activity.get(date, 0) + 1
        
        # Create trend data
        trend = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            trend.append({
                'date': date.isoformat(),
                'activity_count': date_activity.get(date, 0)
            })
        
        return list(reversed(trend))
    
    def _get_feature_usage_breakdown(self, activities: List[UserActivity]) -> Dict[str, int]:
        """Get breakdown of feature usage"""
        if not activities:
            return {}
        
        feature_counts = {}
        for activity in activities:
            feature_counts[activity.action] = feature_counts.get(activity.action, 0) + 1
        
        return feature_counts
    
    def _get_device_usage_breakdown(self, sessions: List[UserSession]) -> Dict[str, int]:
        """Get breakdown of device usage"""
        if not sessions:
            return {}
        
        device_counts = {}
        for session in sessions:
            device = session.device_type or 'unknown'
            device_counts[device] = device_counts.get(device, 0) + 1
        
        return device_counts
    
    def _calculate_churn_risk(self, recent_activity: int, avg_activity: float, days_since_first: int) -> float:
        """Calculate churn risk percentage"""
        if days_since_first < 7:
            return 0.0  # New user, no churn risk yet
        
        # Factors that increase churn risk
        risk_factors = []
        
        # Low recent activity
        if recent_activity == 0:
            risk_factors.append(40)
        elif recent_activity < avg_activity * 0.5:
            risk_factors.append(20)
        
        # Declining activity
        if avg_activity < 1:
            risk_factors.append(30)
        
        # Long time since first activity with low engagement
        if days_since_first > 30 and avg_activity < 2:
            risk_factors.append(25)
        
        return min(sum(risk_factors), 100)
    
    def _determine_lifecycle_stage(self, days_since_first: int, total_activities: int) -> str:
        """Determine user lifecycle stage"""
        if days_since_first < 7:
            return 'new_user'
        elif days_since_first < 30:
            return 'active_user'
        elif total_activities > 50:
            return 'power_user'
        elif days_since_first > 90:
            return 'at_risk'
        else:
            return 'regular_user'
    
    def _determine_adoption_status(self, activities: List[UserActivity]) -> str:
        """Determine feature adoption status"""
        if not activities:
            return 'not_adopted'
        
        recent_activity = [a for a in activities if a.timestamp >= datetime.now() - timedelta(days=7)]
        
        if len(recent_activity) >= 3:
            return 'highly_adopted'
        elif len(recent_activity) >= 1:
            return 'adopted'
        elif len(activities) >= 5:
            return 'tried'
        else:
            return 'not_adopted'
    
    def _calculate_usage_frequency(self, activities: List[UserActivity]) -> str:
        """Calculate usage frequency"""
        if not activities:
            return 'never'
        
        days_with_activity = len(set([a.timestamp.date() for a in activities]))
        total_days = (datetime.now() - min([a.timestamp for a in activities])).days + 1
        
        frequency = days_with_activity / max(total_days, 1)
        
        if frequency >= 0.7:
            return 'daily'
        elif frequency >= 0.3:
            return 'weekly'
        elif frequency >= 0.1:
            return 'monthly'
        else:
            return 'rarely'


class EngagementTracker:
    """Real-time engagement tracking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = UserAnalyticsService(db)
    
    def track_page_view(self, user_id: str, page_url: str, session_id: str = None,
                       user_agent: str = None, ip_address: str = None) -> UserActivity:
        """Track a page view"""
        
        return self.analytics_service.track_activity(
            user_id=user_id,
            action='page_view',
            category='navigation',
            details=f'Viewed {page_url}',
            page_url=page_url,
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
    
    def track_feature_usage(self, user_id: str, feature: str, details: str = None,
                          metadata: Dict = None, session_id: str = None) -> UserActivity:
        """Track feature usage"""
        
        return self.analytics_service.track_activity(
            user_id=user_id,
            action=feature,
            category='feature_usage',
            details=details,
            activity_metadata=metadata,
            session_id=session_id
        )
    
    def track_insight_interaction(self, user_id: str, insight_id: str, action: str,
                                session_id: str = None) -> UserActivity:
        """Track insight interactions"""
        
        return self.analytics_service.track_activity(
            user_id=user_id,
            action=f'insight_{action}',
            category='engagement',
            details=f'Interacted with insight {insight_id}',
            metadata={'insight_id': insight_id, 'action': action},
            session_id=session_id
        ) 