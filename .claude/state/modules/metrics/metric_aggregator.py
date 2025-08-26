#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/metrics/metric_aggregator.py
🎯 PURPOSE: Aggregate and manage all awareness metrics
🔗 IMPORTS: dataclasses, datetime, enum, collections
📤 EXPORTS: MetricAggregator, MetricSnapshot, MetricType, AggregatedMetrics
🔄 PATTERN: Facade pattern for metric collection
📝 TODOS: Add trend analysis, implement alerting

💡 AI HINT: Central hub for all awareness metrics
⚠️ NEVER: Mix metric types without proper normalization
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from collections import deque
from enum import Enum

import logging
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of awareness metrics."""
    CONTEXT_QUALITY = "context_quality"
    UNDERSTANDING_DEPTH = "understanding_depth"
    CONNECTION_STRENGTH = "connection_strength"
    RESPONSE_TIME = "response_time"
    ACCURACY = "accuracy"
    MEMORY_EFFICIENCY = "memory_efficiency"
    FOCUS_CLARITY = "focus_clarity"
    DECISION_CONFIDENCE = "decision_confidence"


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time."""
    timestamp: datetime
    metric_type: MetricType
    value: float
    dimensions: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_type': self.metric_type.value,
            'value': self.value,
            'dimensions': self.dimensions,
            'metadata': self.metadata
        }


@dataclass
class AggregatedMetrics:
    """Aggregated metrics across all dimensions."""
    overall_health: float
    metric_scores: Dict[MetricType, float]
    alerts: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'overall_health': self.overall_health,
            'metric_scores': {k.value: v for k, v in self.metric_scores.items()},
            'alerts': self.alerts,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }


class MetricAggregator:
    """Aggregates and manages all awareness metrics."""
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize metric aggregator.
        
        Args:
            history_size: Size of metric history to maintain
        """
        self.history_size = history_size
        self.metric_history: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=history_size)
            for metric_type in MetricType
        }
        
        # Metric weights for overall health calculation
        self.metric_weights = {
            MetricType.CONTEXT_QUALITY: 0.25,
            MetricType.UNDERSTANDING_DEPTH: 0.20,
            MetricType.CONNECTION_STRENGTH: 0.15,
            MetricType.RESPONSE_TIME: 0.10,
            MetricType.ACCURACY: 0.10,
            MetricType.MEMORY_EFFICIENCY: 0.10,
            MetricType.FOCUS_CLARITY: 0.05,
            MetricType.DECISION_CONFIDENCE: 0.05
        }
        
        # Thresholds for alerts
        self.alert_thresholds = {
            MetricType.CONTEXT_QUALITY: 0.6,
            MetricType.UNDERSTANDING_DEPTH: 0.5,
            MetricType.CONNECTION_STRENGTH: 0.4,
            MetricType.RESPONSE_TIME: 2000,  # ms
            MetricType.ACCURACY: 0.7,
            MetricType.MEMORY_EFFICIENCY: 0.5,
            MetricType.FOCUS_CLARITY: 0.6,
            MetricType.DECISION_CONFIDENCE: 0.6
        }
    
    def record_metric(self, metric_type: MetricType, value: float,
                     dimensions: Optional[Dict[str, float]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a metric snapshot.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            dimensions: Additional dimensions
            metadata: Additional metadata
        """
        snapshot = MetricSnapshot(
            timestamp=datetime.now(timezone.utc),
            metric_type=metric_type,
            value=value,
            dimensions=dimensions or {},
            metadata=metadata or {}
        )
        
        self.metric_history[metric_type].append(snapshot)
        
        # Check for alerts
        self._check_alerts(metric_type, value)
    
    def get_current_metrics(self) -> AggregatedMetrics:
        """Get current aggregated metrics."""
        metric_scores = {}
        alerts = []
        recommendations = []
        
        # Get latest value for each metric type
        for metric_type in MetricType:
            history = self.metric_history[metric_type]
            if history:
                latest = history[-1]
                metric_scores[metric_type] = latest.value
                
                # Check thresholds
                threshold = self.alert_thresholds.get(metric_type)
                if threshold:
                    if metric_type == MetricType.RESPONSE_TIME:
                        # Higher is worse for response time
                        if latest.value > threshold:
                            alerts.append(f"{metric_type.value} above threshold: {latest.value:.0f}ms")
                    else:
                        # Lower is worse for other metrics
                        if latest.value < threshold:
                            alerts.append(f"{metric_type.value} below threshold: {latest.value:.2f}")
            else:
                metric_scores[metric_type] = 0.0
        
        # Calculate overall health
        overall_health = self._calculate_overall_health(metric_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metric_scores, alerts)
        
        return AggregatedMetrics(
            overall_health=overall_health,
            metric_scores=metric_scores,
            alerts=alerts,
            recommendations=recommendations
        )
    
    def get_metric_trends(self, metric_type: MetricType, 
                         window_size: int = 10) -> Dict[str, Any]:
        """
        Get trend analysis for a metric.
        
        Args:
            metric_type: Type of metric
            window_size: Size of analysis window
            
        Returns:
            Trend analysis
        """
        history = list(self.metric_history[metric_type])
        
        if len(history) < 2:
            return {
                'trend': 'insufficient_data',
                'change': 0.0,
                'volatility': 0.0
            }
        
        # Get recent values
        recent_values = [s.value for s in history[-window_size:]]
        
        # Calculate trend
        if len(recent_values) >= 2:
            change = recent_values[-1] - recent_values[0]
            avg_change = change / len(recent_values)
            
            # Determine trend direction
            if abs(avg_change) < 0.01:
                trend = 'stable'
            elif avg_change > 0:
                trend = 'improving' if metric_type != MetricType.RESPONSE_TIME else 'degrading'
            else:
                trend = 'degrading' if metric_type != MetricType.RESPONSE_TIME else 'improving'
            
            # Calculate volatility
            if len(recent_values) > 2:
                differences = [abs(recent_values[i] - recent_values[i-1]) 
                             for i in range(1, len(recent_values))]
                volatility = sum(differences) / len(differences)
            else:
                volatility = 0.0
            
            return {
                'trend': trend,
                'change': change,
                'volatility': volatility,
                'recent_values': recent_values
            }
        
        return {
            'trend': 'insufficient_data',
            'change': 0.0,
            'volatility': 0.0
        }
    
    def _calculate_overall_health(self, metric_scores: Dict[MetricType, float]) -> float:
        """Calculate overall system health."""
        if not metric_scores:
            return 0.0
        
        # Normalize response time (inverse since lower is better)
        if MetricType.RESPONSE_TIME in metric_scores:
            # Normalize to 0-1 where 1 is good (fast)
            response_time = metric_scores[MetricType.RESPONSE_TIME]
            normalized_response = max(0, min(1, 2000 / (response_time + 1)))
            metric_scores[MetricType.RESPONSE_TIME] = normalized_response
        
        # Weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        for metric_type, score in metric_scores.items():
            weight = self.metric_weights.get(metric_type, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        overall_health = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return overall_health
    
    def _check_alerts(self, metric_type: MetricType, value: float) -> None:
        """Check if metric value triggers alerts."""
        threshold = self.alert_thresholds.get(metric_type)
        if not threshold:
            return
        
        if metric_type == MetricType.RESPONSE_TIME:
            if value > threshold:
                logger.warning(f"High {metric_type.value}: {value:.0f}ms > {threshold}ms")
        else:
            if value < threshold:
                logger.warning(f"Low {metric_type.value}: {value:.2f} < {threshold}")
    
    def _generate_recommendations(self, metric_scores: Dict[MetricType, float],
                                alerts: List[str]) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        # Context quality recommendations
        if MetricType.CONTEXT_QUALITY in metric_scores:
            if metric_scores[MetricType.CONTEXT_QUALITY] < 0.7:
                recommendations.append("Refresh context to improve quality")
        
        # Understanding depth recommendations
        if MetricType.UNDERSTANDING_DEPTH in metric_scores:
            if metric_scores[MetricType.UNDERSTANDING_DEPTH] < 0.6:
                recommendations.append("Analyze more code relationships to deepen understanding")
        
        # Memory efficiency recommendations
        if MetricType.MEMORY_EFFICIENCY in metric_scores:
            if metric_scores[MetricType.MEMORY_EFFICIENCY] < 0.6:
                recommendations.append("Compress or evict low-priority context items")
        
        # Response time recommendations
        if MetricType.RESPONSE_TIME in metric_scores:
            if metric_scores[MetricType.RESPONSE_TIME] > 1500:
                recommendations.append("Optimize context size to improve response time")