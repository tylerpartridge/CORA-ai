#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/query_optimizer.py
🎯 PURPOSE: Query optimization utilities for CORA's performance bottlenecks
🔗 IMPORTS: SQLAlchemy, Redis, logging, functools
📤 EXPORTS: QueryOptimizer class with optimized query patterns
"""

import logging
import functools
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from redis import Redis
import json

from utils.redis_manager import get_redis_client
from models import Expense, ExpenseCategory, Job

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Optimized query patterns for CORA's performance bottlenecks"""
    
    def __init__(self, db: Session, redis_client: Redis = None):
        self.db = db
        self.redis = redis_client or get_redis_client()
        
    def get_dashboard_summary_optimized(self, user_id: str, cache_ttl: int = 300) -> Dict[str, Any]:
        """
        Optimized dashboard summary with single query and caching
        Replaces multiple separate queries with one efficient query
        """
        cache_key = f"dashboard_summary:{user_id}"
        
        # Try cache first
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Single optimized query for all dashboard data
            now = datetime.utcnow()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            last_30_days = now - timedelta(days=30)
            
            # Single query with conditional aggregation
            dashboard_data = self.db.query(
                # Monthly totals
                func.sum(
                    func.case(
                        (Expense.expense_date >= start_of_month, Expense.amount_cents),
                        else_=0
                    )
                ).label('monthly_expenses'),
                
                # Yearly totals
                func.sum(
                    func.case(
                        (Expense.expense_date >= start_of_year, Expense.amount_cents),
                        else_=0
                    )
                ).label('yearly_expenses'),
                
                # 30-day count
                func.count(
                    func.case(
                        (Expense.expense_date >= last_30_days, Expense.id),
                        else_=None
                    )
                ).label('expense_count_30d'),
                
                # Voice expenses (30 days)
                func.count(
                    func.case(
                        (and_(
                            Expense.expense_date >= last_30_days,
                            Expense.description.like('%voice%')
                        ), Expense.id),
                        else_=None
                    )
                ).label('voice_expense_count'),
                
                # Tax deductions (yearly)
                func.sum(
                    func.case(
                        (and_(
                            Expense.expense_date >= start_of_year,
                            ExpenseCategory.name.in_([
                                'Office Supplies', 'Professional Development', 
                                'Software & Subscriptions', 'Marketing & Advertising',
                                'Travel', 'Meals & Entertainment'
                            ])
                        ), Expense.amount_cents),
                        else_=0
                    )
                ).label('deductions_found')
                
            ).join(
                ExpenseCategory, Expense.category_id == ExpenseCategory.id, isouter=True
            ).filter(
                Expense.user_id == user_id
            ).first()
            
            # Get category breakdown in separate optimized query
            category_data = self.db.query(
                ExpenseCategory.name,
                ExpenseCategory.icon,
                func.sum(Expense.amount_cents).label('total')
            ).join(
                Expense, Expense.category_id == ExpenseCategory.id
            ).filter(
                Expense.user_id == user_id,
                Expense.expense_date >= start_of_month
            ).group_by(
                ExpenseCategory.id, ExpenseCategory.name, ExpenseCategory.icon
            ).all()
            
            # Get recent expenses with eager loading
            recent_expenses = self.db.query(Expense).options(
                joinedload(Expense.category)
            ).filter(
                Expense.user_id == user_id
            ).order_by(
                desc(Expense.expense_date)
            ).limit(10).all()
            
            # Calculate wellness metrics efficiently
            wellness_metrics = self._calculate_wellness_metrics_optimized(user_id)
            
            # Build response
            result = {
                "status": "success",
                "summary": {
                    "total_expenses_this_month": (dashboard_data.monthly_expenses or 0) / 100.0,
                    "total_expenses_this_year": (dashboard_data.yearly_expenses or 0) / 100.0,
                    "deductions_found": (dashboard_data.deductions_found or 0) / 100.0,
                    "time_saved_hours": round((dashboard_data.voice_expense_count or 0) * 3 / 60.0, 1),
                    "expense_count_30d": dashboard_data.expense_count_30d or 0,
                    "categories": [
                        {
                            "name": cat.name,
                            "icon": cat.icon,
                            "total": cat.total / 100.0,
                            "percentage": round(
                                (cat.total / (dashboard_data.monthly_expenses or 1) * 100), 1
                            )
                        }
                        for cat in category_data
                    ],
                    "recent_expenses": [
                        {
                            "id": exp.id,
                            "vendor": exp.vendor or "Unknown",
                            "amount": exp.amount,
                            "category": exp.category.name if exp.category else "Uncategorized",
                            "date": exp.expense_date.isoformat(),
                            "description": exp.description
                        }
                        for exp in recent_expenses
                    ]
                },
                "wellness_metrics": wellness_metrics
            }
            
            # Cache the result
            self._set_cache(cache_key, result, cache_ttl)
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Dashboard summary query failed: {e}")
            return {"status": "error", "message": "Failed to load dashboard data"}
    
    def get_expenses_optimized(self, user_id: str, skip: int = 0, limit: int = 100, 
                             cache_ttl: int = 300) -> List[Dict[str, Any]]:
        """
        Optimized expense listing with eager loading and caching
        """
        cache_key = f"expenses:{user_id}:{skip}:{limit}"
        
        # Try cache first
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Optimized query with eager loading
            expenses = self.db.query(Expense).options(
                joinedload(Expense.category)
            ).filter(
                Expense.user_id == user_id
            ).order_by(
                desc(Expense.expense_date)
            ).offset(skip).limit(limit).all()
            
            # Convert to dict format
            result = [
                {
                    "id": exp.id,
                    "expense_date": exp.expense_date.isoformat(),
                    "description": exp.description,
                    "amount_cents": exp.amount_cents,
                    "currency": exp.currency,
                    "vendor": exp.vendor,
                    "category_id": exp.category_id,
                    "category_name": exp.category.name if exp.category else None,
                    "receipt_url": exp.receipt_url,
                    "payment_method": exp.payment_method,
                    "user_email": exp.user_email,
                    "created_at": exp.created_at.isoformat(),
                    "updated_at": exp.updated_at.isoformat() if exp.updated_at else None,
                    "confidence_score": exp.confidence_score,
                    "auto_categorized": exp.auto_categorized,
                    "job_name": exp.job_name,
                    "job_id": exp.job_id
                }
                for exp in expenses
            ]
            
            # Cache the result
            self._set_cache(cache_key, result, cache_ttl)
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Expenses query failed: {e}")
            return []
    
    def get_job_profitability_optimized(self, user_id: str, job_id: str = None) -> Dict[str, Any]:
        """
        Optimized job profitability calculation with single query
        """
        cache_key = f"job_profitability:{user_id}:{job_id or 'all'}"
        
        # Try cache first
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        try:
            if job_id:
                # Single job profitability
                job_data = self.db.query(
                    Job.job_name,
                    Job.quoted_amount,
                    func.sum(Expense.amount_cents).label('total_expenses'),
                    func.count(Expense.id).label('expense_count')
                ).join(
                    Expense, and_(
                        Expense.job_id == Job.job_id,
                        Expense.user_id == Job.user_id
                    ), isouter=True
                ).filter(
                    Job.user_id == user_id,
                    Job.job_id == job_id
                ).group_by(
                    Job.job_name, Job.quoted_amount
                ).first()
                
                if not job_data:
                    return {"status": "error", "message": "Job not found"}
                
                quoted_amount = job_data.quoted_amount or 0
                total_expenses = job_data.total_expenses or 0
                profit = quoted_amount - total_expenses
                profit_margin = (profit / quoted_amount * 100) if quoted_amount > 0 else 0
                
                result = {
                    "job_name": job_data.job_name,
                    "quoted_amount": quoted_amount / 100.0,
                    "total_expenses": total_expenses / 100.0,
                    "profit": profit / 100.0,
                    "profit_margin": round(profit_margin, 2),
                    "expense_count": job_data.expense_count
                }
            else:
                # All jobs profitability summary
                jobs_data = self.db.query(
                    func.sum(Job.quoted_amount).label('total_quoted'),
                    func.sum(Expense.amount_cents).label('total_expenses'),
                    func.count(Job.id).label('job_count'),
                    func.count(Expense.id).label('expense_count')
                ).outerjoin(
                    Expense, and_(
                        Expense.job_id == Job.job_id,
                        Expense.user_id == Job.user_id
                    )
                ).filter(
                    Job.user_id == user_id
                ).first()
                
                total_quoted = jobs_data.total_quoted or 0
                total_expenses = jobs_data.total_expenses or 0
                profit = total_quoted - total_expenses
                profit_margin = (profit / total_quoted * 100) if total_quoted > 0 else 0
                
                result = {
                    "total_quoted": total_quoted / 100.0,
                    "total_expenses": total_expenses / 100.0,
                    "total_profit": profit / 100.0,
                    "overall_profit_margin": round(profit_margin, 2),
                    "job_count": jobs_data.job_count,
                    "expense_count": jobs_data.expense_count
                }
            
            # Cache the result
            self._set_cache(cache_key, result, cache_ttl)
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Job profitability query failed: {e}")
            return {"status": "error", "message": "Failed to calculate profitability"}
    
    def _calculate_wellness_metrics_optimized(self, user_id: str) -> Dict[str, float]:
        """
        Optimized wellness metrics calculation with single query
        """
        try:
            # Single query for all wellness metrics
            metrics = self.db.query(
                # Tracking consistency (expenses in last 30 days)
                func.count(
                    func.case(
                        (Expense.expense_date >= datetime.utcnow() - timedelta(days=30), Expense.id),
                        else_=None
                    )
                ).label('recent_expenses'),
                
                # Categorization rate
                func.count(
                    func.case(
                        (Expense.category_id.isnot(None), Expense.id),
                        else_=None
                    )
                ).label('categorized_expenses'),
                
                # Receipt capture rate
                func.count(
                    func.case(
                        (Expense.receipt_url.isnot(None), Expense.id),
                        else_=None
                    )
                ).label('receipt_expenses'),
                
                # Total expenses
                func.count(Expense.id).label('total_expenses')
                
            ).filter(
                Expense.user_id == user_id
            ).first()
            
            total_expenses = metrics.total_expenses or 1  # Avoid division by zero
            
            return {
                "tracking_consistency": min(100.0, (metrics.recent_expenses or 0) / 30.0 * 100),
                "categorization_rate": (metrics.categorized_expenses or 0) / total_expenses * 100,
                "receipt_capture_rate": (metrics.receipt_expenses or 0) / total_expenses * 100
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Wellness metrics calculation failed: {e}")
            return {
                "tracking_consistency": 0.0,
                "categorization_rate": 0.0,
                "receipt_capture_rate": 0.0
            }
    
    def _get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache"""
        try:
            if self.redis:
                cached = self.redis.get(key)
                if cached:
                    return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None
    
    def _set_cache(self, key: str, data: Dict[str, Any], ttl: int) -> bool:
        """Set data in cache"""
        try:
            if self.redis:
                self.redis.setex(key, ttl, json.dumps(data))
                return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
        return False
    
    def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cache entries for a user"""
        try:
            if self.redis:
                # Get all keys for this user
                pattern = f"*:{user_id}:*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                return True
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")
        return False

# Convenience functions for easy integration
def get_optimized_dashboard_summary(db: Session, user_id: str) -> Dict[str, Any]:
    """Get optimized dashboard summary"""
    optimizer = QueryOptimizer(db)
    return optimizer.get_dashboard_summary_optimized(user_id)

def get_optimized_expenses(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get optimized expense list"""
    optimizer = QueryOptimizer(db)
    return optimizer.get_expenses_optimized(user_id, skip, limit)

def get_optimized_job_profitability(db: Session, user_id: str, job_id: str = None) -> Dict[str, Any]:
    """Get optimized job profitability"""
    optimizer = QueryOptimizer(db)
    return optimizer.get_job_profitability_optimized(user_id, job_id) 