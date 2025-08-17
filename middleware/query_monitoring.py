#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/middleware/query_monitoring.py
🎯 PURPOSE: Database query monitoring and slow query detection
🔗 IMPORTS: FastAPI, time, logging, sqlalchemy
📤 EXPORTS: QueryMonitoringMiddleware
"""

import time
import logging
from typing import Dict, List, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import event
from sqlalchemy.orm import Session
from models.base import engine

# Configure logging
logger = logging.getLogger(__name__)

class QueryMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring database query performance"""
    
    def __init__(self, app, slow_query_threshold: float = 0.1):
        super().__init__(app)
        self.slow_query_threshold = slow_query_threshold
        self.slow_queries: List[Dict[str, Any]] = []
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        
        # Set up SQLAlchemy event listeners
        self._setup_query_listeners()
    
    def _setup_query_listeners(self):
        """Set up SQLAlchemy event listeners for query monitoring"""
        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
            context._query_statement = statement
            context._query_parameters = parameters
        
        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            query_time = time.time() - context._query_start_time
            
            # Track query statistics
            query_hash = hash(statement)
            if query_hash not in self.query_stats:
                self.query_stats[query_hash] = {
                    'sql': statement,
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0,
                    'last_executed': None
                }
            
            stats = self.query_stats[query_hash]
            stats['count'] += 1
            stats['total_time'] += query_time
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['min_time'] = min(stats['min_time'], query_time)
            stats['max_time'] = max(stats['max_time'], query_time)
            stats['last_executed'] = time.time()
            
            # Log slow queries
            if query_time > self.slow_query_threshold:
                slow_query = {
                    'sql': statement,
                    'parameters': str(parameters)[:200],
                    'execution_time': query_time,
                    'timestamp': time.time(),
                    'connection_id': id(conn)
                }
                self.slow_queries.append(slow_query)
                
                logger.warning(
                    f"Slow query detected: {query_time:.3f}s - {statement[:100]}...",
                    extra={
                        'query_time': query_time,
                        'sql': statement,
                        'parameters': str(parameters)[:200]
                    }
                )
    
    async def dispatch(self, request: Request, call_next):
        """Process request and monitor database queries"""
        start_time = time.time()
        
        # Clear slow queries for this request
        request_slow_queries = []
        
        # Store original query stats
        original_stats = self.query_stats.copy()
        
        try:
            response = await call_next(request)
            
            # Calculate request processing time
            request_time = time.time() - start_time
            
            # Get queries executed during this request
            new_stats = {k: v for k, v in self.query_stats.items() 
                        if k not in original_stats or v['count'] > original_stats[k]['count']}
            
            # Log request summary if it had database queries
            if new_stats:
                total_queries = sum(stats['count'] - original_stats.get(k, {}).get('count', 0) 
                                  for k, stats in new_stats.items())
                total_query_time = sum(stats['total_time'] - original_stats.get(k, {}).get('total_time', 0) 
                                     for k, stats in new_stats.items())
                
                logger.info(
                    f"Request {request.method} {request.url.path} - "
                    f"Total time: {request_time:.3f}s, "
                    f"DB queries: {total_queries}, "
                    f"DB time: {total_query_time:.3f}s",
                    extra={
                        'request_time': request_time,
                        'db_queries': total_queries,
                        'db_time': total_query_time,
                        'method': request.method,
                        'path': request.url.path
                    }
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)}")
            raise
    
    def get_slow_queries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent slow queries"""
        return sorted(self.slow_queries, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        if not self.query_stats:
            return {
                'total_queries': 0,
                'average_query_time': 0,
                'slowest_query_time': 0,
                'fastest_query_time': 0,
                'slow_query_count': len(self.slow_queries)
            }
        
        total_queries = sum(stats['count'] for stats in self.query_stats.values())
        total_time = sum(stats['total_time'] for stats in self.query_stats.values())
        
        return {
            'total_queries': total_queries,
            'average_query_time': total_time / total_queries if total_queries > 0 else 0,
            'slowest_query_time': max(stats['max_time'] for stats in self.query_stats.values()),
            'fastest_query_time': min(stats['min_time'] for stats in self.query_stats.values()),
            'slow_query_count': len(self.slow_queries),
            'unique_queries': len(self.query_stats)
        }
    
    def clear_statistics(self):
        """Clear all query statistics"""
        self.slow_queries.clear()
        self.query_stats.clear()

# Global instance for easy access
query_monitor = QueryMonitoringMiddleware(None) 