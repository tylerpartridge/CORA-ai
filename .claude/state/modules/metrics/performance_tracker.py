#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/metrics/performance_tracker.py
🎯 PURPOSE: Track performance metrics for Claude sessions
🔗 IMPORTS: time, dataclasses, collections, threading
📤 EXPORTS: PerformanceTracker, PerformanceMetrics
🔄 PATTERN: Observer pattern for metric collection
📝 TODOS: Add performance anomaly detection

💡 AI HINT: Monitors system performance to optimize resource usage
⚠️ NEVER: Let performance tracking impact actual performance
"""

import time
from dataclasses import dataclass, asdict
from collections import deque
from threading import Lock
from typing import Dict, List, Any, Optional

import logging
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics."""
    response_time_ms: float
    token_throughput: float
    memory_usage_mb: float
    cpu_usage_percent: float
    cache_hit_rate: float
    error_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PerformanceTracker:
    """Tracks performance metrics for Claude sessions."""
    
    def __init__(self, window_size: int = 100):
        """
        Initialize performance tracker.
        
        Args:
            window_size: Size of sliding window for metrics
        """
        self.window_size = window_size
        self._lock = Lock()
        
        # Metric windows
        self.response_times: deque = deque(maxlen=window_size)
        self.token_counts: deque = deque(maxlen=window_size)
        self.memory_readings: deque = deque(maxlen=window_size)
        self.cpu_readings: deque = deque(maxlen=window_size)
        self.cache_hits: deque = deque(maxlen=window_size)
        self.cache_misses: deque = deque(maxlen=window_size)
        self.errors: deque = deque(maxlen=window_size)
        self.requests: deque = deque(maxlen=window_size)
        
        # Timing
        self._request_start_time: Optional[float] = None
        self._last_update = time.time()
    
    def start_request(self) -> None:
        """Mark the start of a request."""
        self._request_start_time = time.time()
    
    def end_request(self, tokens_used: int, cache_hit: bool = False, 
                   error: bool = False) -> None:
        """
        Mark the end of a request.
        
        Args:
            tokens_used: Number of tokens used
            cache_hit: Whether this was a cache hit
            error: Whether an error occurred
        """
        if self._request_start_time is None:
            return
        
        response_time = (time.time() - self._request_start_time) * 1000  # ms
        
        with self._lock:
            self.response_times.append(response_time)
            self.token_counts.append(tokens_used)
            self.cache_hits.append(1 if cache_hit else 0)
            self.cache_misses.append(0 if cache_hit else 1)
            self.errors.append(1 if error else 0)
            self.requests.append(1)
        
        self._request_start_time = None
    
    def record_memory_usage(self, memory_mb: float) -> None:
        """Record memory usage."""
        with self._lock:
            self.memory_readings.append(memory_mb)
    
    def record_cpu_usage(self, cpu_percent: float) -> None:
        """Record CPU usage."""
        with self._lock:
            self.cpu_readings.append(cpu_percent)
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        with self._lock:
            # Response time
            response_time_ms = (
                sum(self.response_times) / len(self.response_times)
                if self.response_times else 0.0
            )
            
            # Token throughput (tokens per second)
            time_window = time.time() - self._last_update
            total_tokens = sum(self.token_counts)
            token_throughput = total_tokens / time_window if time_window > 0 else 0.0
            
            # Memory usage
            memory_usage_mb = (
                sum(self.memory_readings) / len(self.memory_readings)
                if self.memory_readings else 0.0
            )
            
            # CPU usage
            cpu_usage_percent = (
                sum(self.cpu_readings) / len(self.cpu_readings)
                if self.cpu_readings else 0.0
            )
            
            # Cache hit rate
            total_cache_checks = len(self.cache_hits) + len(self.cache_misses)
            cache_hit_rate = (
                sum(self.cache_hits) / total_cache_checks
                if total_cache_checks > 0 else 0.0
            )
            
            # Error rate
            total_requests = len(self.requests)
            error_rate = (
                sum(self.errors) / total_requests
                if total_requests > 0 else 0.0
            )
        
        return PerformanceMetrics(
            response_time_ms=response_time_ms,
            token_throughput=token_throughput,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        metrics = self.get_current_metrics()
        
        with self._lock:
            summary = {
                'current_metrics': metrics.to_dict(),
                'statistics': {
                    'response_time': {
                        'min': min(self.response_times) if self.response_times else 0,
                        'max': max(self.response_times) if self.response_times else 0,
                        'avg': metrics.response_time_ms
                    },
                    'token_throughput': {
                        'current': metrics.token_throughput,
                        'total_tokens': sum(self.token_counts)
                    },
                    'cache_performance': {
                        'hit_rate': metrics.cache_hit_rate,
                        'total_hits': sum(self.cache_hits),
                        'total_misses': sum(self.cache_misses)
                    },
                    'reliability': {
                        'error_rate': metrics.error_rate,
                        'total_errors': sum(self.errors),
                        'total_requests': len(self.requests)
                    }
                },
                'window_size': self.window_size,
                'samples_collected': len(self.response_times)
            }
        
        return summary
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self.response_times.clear()
            self.token_counts.clear()
            self.memory_readings.clear()
            self.cpu_readings.clear()
            self.cache_hits.clear()
            self.cache_misses.clear()
            self.errors.clear()
            self.requests.clear()
            self._last_update = time.time()
        
        logger.info("Performance metrics reset")