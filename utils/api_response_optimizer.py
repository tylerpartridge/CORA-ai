#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/utils/api_response_optimizer.py
🎯 PURPOSE: API response optimization utilities for improved performance
🔗 IMPORTS: FastAPI, Redis, gzip, json, time
📤 EXPORTS: ResponseOptimizer, optimized response utilities
"""

import json
import gzip
import time
import logging
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
from functools import wraps
import hashlib

from fastapi import Response, Request
from fastapi.responses import JSONResponse
from redis import Redis

from utils.redis_manager import get_redis_client
from utils.api_response import APIResponse

logger = logging.getLogger(__name__)

class ResponseOptimizer:
    """Optimized API response utilities for improved performance"""
    
    def __init__(self, redis_client: Redis = None):
        self.redis = redis_client or get_redis_client()
        self.compression_threshold = 1024  # Compress responses > 1KB
        self.cache_ttl = 300  # 5 minutes default cache TTL
        
    def optimize_response(
        self,
        data: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        compress: bool = True,
        cache: bool = False,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None
    ) -> Response:
        """
        Create an optimized API response with compression and caching
        
        Args:
            data: Response data
            status_code: HTTP status code
            headers: Additional headers
            compress: Whether to compress response
            cache: Whether to cache response
            cache_key: Custom cache key
            cache_ttl: Custom cache TTL
            
        Returns:
            Optimized FastAPI Response
        """
        # Serialize data efficiently
        if isinstance(data, dict) and 'success' in data:
            # Already formatted response
            json_data = data
        else:
            # Format as standard response
            json_data = APIResponse.success(data=data)
        
        # Convert to JSON string
        json_str = json.dumps(json_data, separators=(',', ':'), default=str)
        
        # Determine if compression should be applied
        should_compress = compress and len(json_str) > self.compression_threshold
        
        # Prepare headers
        response_headers = {
            'Content-Type': 'application/json',
            'X-Response-Optimized': 'true',
            'X-Response-Size': str(len(json_str)),
            'X-Response-Compressed': str(should_compress).lower()
        }
        
        if headers:
            response_headers.update(headers)
        
        # Apply compression if needed
        if should_compress:
            compressed_data = gzip.compress(json_str.encode('utf-8'))
            response_headers.update({
                'Content-Encoding': 'gzip',
                'Content-Length': str(len(compressed_data)),
                'X-Compression-Ratio': f"{len(compressed_data) / len(json_str):.2f}"
            })
            return Response(
                content=compressed_data,
                status_code=status_code,
                headers=response_headers
            )
        else:
            response_headers['Content-Length'] = str(len(json_str))
            return Response(
                content=json_str,
                status_code=status_code,
                headers=response_headers
            )
    
    def cache_response(
        self,
        key: str,
        data: Any,
        ttl: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Cache response data in Redis
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
            user_id: User ID for user-specific caching
            
        Returns:
            True if cached successfully
        """
        try:
            if user_id:
                key = f"response_cache:{user_id}:{key}"
            else:
                key = f"response_cache:{key}"
            
            # Serialize data efficiently
            if isinstance(data, dict):
                cache_data = {
                    'data': data,
                    'timestamp': datetime.utcnow().isoformat(),
                    'ttl': ttl or self.cache_ttl
                }
            else:
                cache_data = {
                    'data': APIResponse.success(data=data),
                    'timestamp': datetime.utcnow().isoformat(),
                    'ttl': ttl or self.cache_ttl
                }
            
            # Compress cache data
            compressed_data = gzip.compress(
                json.dumps(cache_data, separators=(',', ':'), default=str).encode('utf-8')
            )
            
            return self.redis.setex(
                key,
                ttl or self.cache_ttl,
                compressed_data
            )
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
            return False
    
    def get_cached_response(
        self,
        key: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response data from Redis
        
        Args:
            key: Cache key
            user_id: User ID for user-specific caching
            
        Returns:
            Cached data or None
        """
        try:
            if user_id:
                key = f"response_cache:{user_id}:{key}"
            else:
                key = f"response_cache:{key}"
            
            cached_data = self.redis.get(key)
            if not cached_data:
                return None
            
            # Decompress and deserialize
            decompressed = gzip.decompress(cached_data)
            cache_data = json.loads(decompressed.decode('utf-8'))
            
            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.utcnow() - cache_time > timedelta(seconds=cache_data['ttl']):
                self.redis.delete(key)
                return None
            
            return cache_data['data']
        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
            return None
    
    def invalidate_cache(
        self,
        pattern: str,
        user_id: Optional[str] = None
    ) -> int:
        """
        Invalidate cached responses matching pattern
        
        Args:
            pattern: Cache key pattern to match
            user_id: User ID for user-specific invalidation
            
        Returns:
            Number of keys invalidated
        """
        try:
            if user_id:
                search_pattern = f"response_cache:{user_id}:{pattern}"
            else:
                search_pattern = f"response_cache:{pattern}"
            
            keys = self.redis.keys(search_pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return 0
    
    def generate_cache_key(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate a consistent cache key for an endpoint
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            user_id: User ID
            
        Returns:
            Cache key string
        """
        key_parts = [endpoint]
        
        if params:
            # Sort parameters for consistent keys
            sorted_params = sorted(params.items())
            param_str = json.dumps(sorted_params, separators=(',', ':'))
            key_parts.append(hashlib.md5(param_str.encode()).hexdigest()[:8])
        
        if user_id:
            key_parts.append(user_id)
        
        return ':'.join(key_parts)

# Global response optimizer instance
response_optimizer = ResponseOptimizer()

def optimize_api_response(
    compress: bool = True,
    cache: bool = False,
    cache_ttl: Optional[int] = None
):
    """
    Decorator to optimize API responses with compression and caching
    
    Args:
        compress: Whether to compress response
        cache: Whether to cache response
        cache_ttl: Cache TTL in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and user info for caching
            request = None
            user_id = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            for key, value in kwargs.items():
                if key == 'current_user' and hasattr(value, 'id'):
                    user_id = value.id
                    break
            
            # Generate cache key if caching is enabled
            cache_key = None
            if cache and request:
                # Extract query parameters
                params = dict(request.query_params)
                if user_id:
                    params['user_id'] = user_id
                
                cache_key = response_optimizer.generate_cache_key(
                    request.url.path,
                    params,
                    user_id
                )
                
                # Try to get cached response
                cached_response = response_optimizer.get_cached_response(cache_key, user_id)
                if cached_response:
                    return JSONResponse(
                        content=cached_response,
                        headers={'X-Cache-Hit': 'true'}
                    )
            
            # Execute original function
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache result if enabled
            if cache and cache_key:
                response_optimizer.cache_response(
                    cache_key,
                    result,
                    cache_ttl,
                    user_id
                )
            
            # Add performance headers
            headers = {
                'X-Execution-Time': f"{execution_time:.3f}",
                'X-Cache-Key': cache_key or 'none'
            }
            
            # Return optimized response
            return response_optimizer.optimize_response(
                data=result,
                headers=headers,
                compress=compress
            )
        
        return wrapper
    return decorator

def batch_optimize_responses(
    responses: List[Dict[str, Any]],
    compress: bool = True
) -> List[Response]:
    """
    Optimize multiple responses in batch
    
    Args:
        responses: List of response data
        compress: Whether to compress responses
        
    Returns:
        List of optimized responses
    """
    optimized_responses = []
    
    for response_data in responses:
        optimized = response_optimizer.optimize_response(
            data=response_data,
            compress=compress
        )
        optimized_responses.append(optimized)
    
    return optimized_responses

# Performance monitoring utilities
class ResponsePerformanceMonitor:
    """Monitor and track response performance metrics"""
    
    def __init__(self, redis_client: Redis = None):
        self.redis = redis_client or get_redis_client()
    
    def record_response_time(
        self,
        endpoint: str,
        response_time: float,
        status_code: int,
        user_id: Optional[str] = None
    ):
        """Record response time for performance tracking"""
        try:
            key = f"response_performance:{endpoint}"
            data = {
                'endpoint': endpoint,
                'response_time': response_time,
                'status_code': status_code,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id
            }
            
            # Store in Redis with TTL
            self.redis.lpush(key, json.dumps(data, separators=(',', ':')))
            self.redis.expire(key, 3600)  # Keep for 1 hour
            
            # Trim list to keep only last 100 entries
            self.redis.ltrim(key, 0, 99)
        except Exception as e:
            logger.error(f"Failed to record response time: {e}")
    
    def get_performance_stats(
        self,
        endpoint: Optional[str] = None,
        hours: int = 1
    ) -> Dict[str, Any]:
        """Get performance statistics for endpoints"""
        try:
            if endpoint:
                keys = [f"response_performance:{endpoint}"]
            else:
                keys = self.redis.keys("response_performance:*")
            
            all_times = []
            status_codes = {}
            
            for key in keys:
                data_list = self.redis.lrange(key, 0, -1)
                for data_str in data_list:
                    try:
                        data = json.loads(data_str)
                        response_time = data.get('response_time', 0)
                        status_code = data.get('status_code', 200)
                        
                        all_times.append(response_time)
                        status_codes[status_code] = status_codes.get(status_code, 0) + 1
                    except:
                        continue
            
            if not all_times:
                return {
                    'count': 0,
                    'avg_response_time': 0,
                    'min_response_time': 0,
                    'max_response_time': 0,
                    'p95_response_time': 0,
                    'status_codes': {}
                }
            
            all_times.sort()
            count = len(all_times)
            
            return {
                'count': count,
                'avg_response_time': sum(all_times) / count,
                'min_response_time': min(all_times),
                'max_response_time': max(all_times),
                'p95_response_time': all_times[int(count * 0.95)] if count > 0 else 0,
                'status_codes': status_codes
            }
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {}

# Global performance monitor instance
performance_monitor = ResponsePerformanceMonitor()

# Global response optimizer instance
response_optimizer = ResponseOptimizer() 