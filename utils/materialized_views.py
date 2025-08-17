#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/materialized_views.py
🎯 PURPOSE: Materialized view implementation for SQLite with caching
🔗 IMPORTS: SQLAlchemy, Redis, logging
📤 EXPORTS: MaterializedViewManager, JobProfitabilityView
"""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
import json

from models.base import engine
from utils.redis_manager import get_redis_client

logger = logging.getLogger(__name__)

class MaterializedViewManager:
    """Manages materialized view-like functionality for SQLite with Redis caching"""
    
    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis = redis_client or get_redis_client()
        self.cache_ttl = 300  # 5 minutes default
    
    def _get_cache_key(self, view_name: str, user_id: str = None, **kwargs) -> str:
        """Generate cache key for materialized view data"""
        key_parts = [f"mv:{view_name}"]
        if user_id:
            key_parts.append(f"user:{user_id}")
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached materialized view data"""
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Failed to get cached data for {cache_key}: {e}")
        return None
    
    def _set_cached_data(self, cache_key: str, data: Dict[str, Any], ttl: int = None) -> bool:
        """Cache materialized view data"""
        try:
            ttl = ttl or self.cache_ttl
            self.redis.setex(cache_key, ttl, json.dumps(data))
            return True
        except Exception as e:
            logger.warning(f"Failed to cache data for {cache_key}: {e}")
            return False
    
    def _invalidate_user_cache(self, user_id: str, view_name: str = None):
        """Invalidate cache for a specific user"""
        try:
            if view_name:
                pattern = f"mv:{view_name}:user:{user_id}:*"
            else:
                pattern = f"mv:*:user:{user_id}:*"
            
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")

class JobProfitabilityView(MaterializedViewManager):
    """Materialized view for job profitability calculations"""
    
    def get_job_profitability(self, user_id: str, job_id: str = None, 
                             use_cache: bool = True) -> Dict[str, Any]:
        """Get job profitability data with caching"""
        
        cache_key = self._get_cache_key("job_profitability", user_id, job_id=job_id)
        
        # Try cache first
        if use_cache:
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
        
        try:
            # Build the query
            if job_id:
                # Single job query
                query = text("""
                    SELECT 
                        j.id as job_id,
                        j.user_id,
                        j.job_name,
                        j.customer_name,
                        j.quoted_amount,
                        j.status,
                        j.start_date,
                        j.end_date,
                        COALESCE(expense_summary.total_costs_cents, 0) as total_costs_cents,
                        COALESCE(expense_summary.total_costs_cents / 100.0, 0) as total_costs,
                        COALESCE(expense_summary.expense_count, 0) as expense_count,
                        COALESCE(expense_summary.last_expense_date, j.created_at) as last_expense_date,
                        
                        -- Profit calculations
                        CASE 
                            WHEN j.quoted_amount IS NOT NULL AND j.quoted_amount > 0 
                            THEN j.quoted_amount - COALESCE(expense_summary.total_costs_cents / 100.0, 0)
                            ELSE NULL 
                        END as profit,
                        
                        -- Profit margin percentage
                        CASE 
                            WHEN j.quoted_amount IS NOT NULL AND j.quoted_amount > 0 
                            THEN ROUND(((j.quoted_amount - COALESCE(expense_summary.total_costs_cents / 100.0, 0)) / j.quoted_amount * 100), 2)
                            ELSE NULL 
                        END as profit_margin_percent,
                        
                        -- Completion percentage
                        CASE 
                            WHEN j.quoted_amount IS NOT NULL AND j.quoted_amount > 0 
                            THEN MIN(ROUND((COALESCE(expense_summary.total_costs_cents / 100.0, 0) / j.quoted_amount * 100), 2), 100)
                            ELSE NULL 
                        END as completion_percent_estimate
                        
                    FROM jobs j
                    LEFT JOIN (
                        SELECT 
                            e.user_id,
                            e.job_name,
                            SUM(e.amount_cents) as total_costs_cents,
                            COUNT(*) as expense_count,
                            MAX(e.expense_date) as last_expense_date
                        FROM expenses e 
                        WHERE e.job_name IS NOT NULL
                        GROUP BY e.user_id, e.job_name
                    ) expense_summary ON j.user_id = expense_summary.user_id AND j.job_name = expense_summary.job_name
                    WHERE j.user_id = :user_id AND j.id = :job_id
                """)
                result = self.db.execute(query, {"user_id": user_id, "job_id": job_id})
                row = result.fetchone()
                
                if row:
                    data = {
                        "status": "success",
                        "job_id": row.job_id,
                        "job_name": row.job_name,
                        "customer_name": row.customer_name,
                        "quoted_amount": row.quoted_amount,
                        "status": row.status,
                        "total_costs": row.total_costs,
                        "profit": row.profit,
                        "profit_margin_percent": row.profit_margin_percent,
                        "completion_percent_estimate": row.completion_percent_estimate,
                        "expense_count": row.expense_count,
                        "calculated_at": datetime.now().isoformat()
                    }
                else:
                    data = {"status": "error", "message": "Job not found"}
            else:
                # All jobs for user
                query = text("""
                    SELECT 
                        j.id as job_id,
                        j.job_name,
                        j.customer_name,
                        j.quoted_amount,
                        j.status,
                        j.start_date,
                        j.end_date,
                        COALESCE(expense_summary.total_costs_cents, 0) as total_costs_cents,
                        COALESCE(expense_summary.total_costs_cents / 100.0, 0) as total_costs,
                        COALESCE(expense_summary.expense_count, 0) as expense_count,
                        COALESCE(expense_summary.last_expense_date, j.created_at) as last_expense_date,
                        
                        -- Profit calculations
                        CASE 
                            WHEN j.quoted_amount IS NOT NULL AND j.quoted_amount > 0 
                            THEN j.quoted_amount - COALESCE(expense_summary.total_costs_cents / 100.0, 0)
                            ELSE NULL 
                        END as profit,
                        
                        -- Profit margin percentage
                        CASE 
                            WHEN j.quoted_amount IS NOT NULL AND j.quoted_amount > 0 
                            THEN ROUND(((j.quoted_amount - COALESCE(expense_summary.total_costs_cents / 100.0, 0)) / j.quoted_amount * 100), 2)
                            ELSE NULL 
                        END as profit_margin_percent,
                        
                        -- Completion percentage
                        CASE 
                            WHEN j.quoted_amount IS NOT NULL AND j.quoted_amount > 0 
                            THEN MIN(ROUND((COALESCE(expense_summary.total_costs_cents / 100.0, 0) / j.quoted_amount * 100), 2), 100)
                            ELSE NULL 
                        END as completion_percent_estimate
                        
                    FROM jobs j
                    LEFT JOIN (
                        SELECT 
                            e.user_id,
                            e.job_name,
                            SUM(e.amount_cents) as total_costs_cents,
                            COUNT(*) as expense_count,
                            MAX(e.expense_date) as last_expense_date
                        FROM expenses e 
                        WHERE e.job_name IS NOT NULL
                        GROUP BY e.user_id, e.job_name
                    ) expense_summary ON j.user_id = expense_summary.user_id AND j.job_name = expense_summary.job_name
                    WHERE j.user_id = :user_id
                    ORDER BY j.created_at DESC
                """)
                result = self.db.execute(query, {"user_id": user_id})
                rows = result.fetchall()
                
                data = {
                    "status": "success",
                    "jobs": [
                        {
                            "job_id": row.job_id,
                            "job_name": row.job_name,
                            "customer_name": row.customer_name,
                            "quoted_amount": row.quoted_amount,
                            "status": row.status,
                            "total_costs": row.total_costs,
                            "profit": row.profit,
                            "profit_margin_percent": row.profit_margin_percent,
                            "completion_percent_estimate": row.completion_percent_estimate,
                            "expense_count": row.expense_count
                        }
                        for row in rows
                    ],
                    "calculated_at": datetime.now().isoformat()
                }
            
            # Cache the result
            if use_cache and data.get("status") == "success":
                self._set_cached_data(cache_key, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error calculating job profitability: {e}")
            return {"status": "error", "message": str(e)}
    
    def refresh_job_profitability(self, user_id: str = None):
        """Refresh job profitability cache"""
        try:
            if user_id:
                self._invalidate_user_cache(user_id, "job_profitability")
            else:
                # Invalidate all job profitability cache
                pattern = "mv:job_profitability:*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                    logger.info(f"Refreshed job profitability cache: {len(keys)} keys")
        except Exception as e:
            logger.error(f"Error refreshing job profitability cache: {e}")

def get_job_profitability_optimized(db: Session, user_id: str, job_id: str = None) -> Dict[str, Any]:
    """Optimized job profitability calculation using materialized view"""
    view = JobProfitabilityView(db)
    return view.get_job_profitability(user_id, job_id)

def refresh_job_profitability_cache(user_id: str = None):
    """Refresh job profitability cache"""
    view = JobProfitabilityView(None)  # No DB session needed for cache operations
    view.refresh_job_profitability(user_id) 