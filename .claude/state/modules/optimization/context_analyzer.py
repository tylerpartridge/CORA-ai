#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/optimization/context_analyzer.py
🎯 PURPOSE: Context analysis and pattern detection for optimization
🔗 IMPORTS: datetime, collections, typing, logging
📤 EXPORTS: DynamicContextAdjuster
🔄 PATTERN: Observer pattern for access pattern analysis
📝 TODOS: Add predictive analytics for context prefetching
"""

"""
CORA - Claude Operational Research Assistant
Context Analyzer Module

Implements context analysis and dynamic adjustment based on usage patterns.

Author: CORA Team
Version: 1.0.0
"""

import logging
from datetime import datetime, timezone
from collections import defaultdict, deque
from typing import Dict, List, Any, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from .optimization_strategies import EvictionPolicy

logger = logging.getLogger(__name__)


class DynamicContextAdjuster:
    """Dynamically adjusts context based on patterns."""
    
    def __init__(self, optimizer: 'ContextOptimizer'):
        """
        Initialize dynamic adjuster.
        
        Args:
            optimizer: Context optimizer instance
        """
        self.optimizer = optimizer
        self.access_patterns = defaultdict(list)
        self.performance_history = deque(maxlen=100)
        
    def record_access_pattern(self, accessed_items: List[str],
                             operation_type: str,
                             performance_ms: float) -> None:
        """
        Record an access pattern.
        
        Args:
            accessed_items: Items that were accessed
            operation_type: Type of operation
            performance_ms: Operation performance
        """
        pattern = {
            'timestamp': datetime.now(timezone.utc),
            'items': accessed_items,
            'operation': operation_type,
            'performance': performance_ms
        }
        
        self.access_patterns[operation_type].append(pattern)
        self.performance_history.append(performance_ms)
    
    def suggest_adjustments(self) -> Dict[str, Any]:
        """Suggest context adjustments based on patterns."""
        from .optimization_strategies import EvictionPolicy
        
        suggestions = {
            'prefetch': [],
            'evict': [],
            'policy_change': None,
            'priority_adjustments': {}
        }
        
        # Analyze access patterns
        frequent_sets = self._find_frequent_item_sets()
        
        # Suggest prefetching frequently co-accessed items
        for itemset in frequent_sets:
            in_context = [i for i in itemset if i in self.optimizer.context_items]
            not_in_context = [i for i in itemset if i not in self.optimizer.context_items]
            
            if in_context and not_in_context:
                suggestions['prefetch'].extend(not_in_context)
        
        # Analyze performance trends
        if len(self.performance_history) >= 10:
            recent_avg = sum(list(self.performance_history)[-10:]) / 10
            overall_avg = sum(self.performance_history) / len(self.performance_history)
            
            if recent_avg > overall_avg * 1.2:
                # Performance degrading, suggest policy change
                current_policy = self.optimizer.current_eviction_policy
                if current_policy == EvictionPolicy.LRU:
                    suggestions['policy_change'] = EvictionPolicy.PRIORITY
                elif current_policy == EvictionPolicy.PRIORITY:
                    suggestions['policy_change'] = EvictionPolicy.ADAPTIVE
        
        # Suggest priority adjustments for frequently accessed items
        for item_id, item in self.optimizer.context_items.items():
            if item.access_count > 5:
                suggestions['priority_adjustments'][item_id] = min(1.0, item.priority * 1.2)
        
        return suggestions
    
    def apply_suggestions(self, suggestions: Dict[str, Any]) -> None:
        """Apply suggested adjustments."""
        # Apply priority adjustments
        for item_id, new_priority in suggestions.get('priority_adjustments', {}).items():
            if item_id in self.optimizer.context_items:
                self.optimizer.context_items[item_id].priority = new_priority
        
        # Apply policy change
        if suggestions.get('policy_change'):
            self.optimizer.set_eviction_policy(suggestions['policy_change'])
        
        # Note: Prefetch and evict suggestions would be handled by the caller
    
    def _find_frequent_item_sets(self, min_support: int = 3) -> List[Set[str]]:
        """Find frequently co-accessed item sets."""
        # Simple frequent itemset mining
        itemsets = defaultdict(int)
        
        for patterns in self.access_patterns.values():
            for pattern in patterns:
                items = pattern['items']
                # Generate 2-itemsets
                for i in range(len(items)):
                    for j in range(i + 1, len(items)):
                        itemset = frozenset([items[i], items[j]])
                        itemsets[itemset] += 1
        
        # Filter by minimum support
        frequent = [
            set(itemset) for itemset, count in itemsets.items()
            if count >= min_support
        ]
        
        return frequent
    
    def analyze_context_usage(self) -> Dict[str, Any]:
        """Analyze context usage patterns."""
        analysis = {
            'total_operations': sum(len(patterns) for patterns in self.access_patterns.values()),
            'operation_types': list(self.access_patterns.keys()),
            'avg_performance_ms': 0,
            'performance_trend': 'stable',
            'most_accessed_items': [],
            'least_accessed_items': [],
            'co_access_patterns': []
        }
        
        # Calculate average performance
        if self.performance_history:
            analysis['avg_performance_ms'] = sum(self.performance_history) / len(self.performance_history)
            
            # Determine performance trend
            if len(self.performance_history) >= 10:
                recent = list(self.performance_history)[-10:]
                older = list(self.performance_history)[:-10]
                if older:
                    recent_avg = sum(recent) / len(recent)
                    older_avg = sum(older) / len(older)
                    if recent_avg > older_avg * 1.1:
                        analysis['performance_trend'] = 'degrading'
                    elif recent_avg < older_avg * 0.9:
                        analysis['performance_trend'] = 'improving'
        
        # Find most/least accessed items
        access_counts = defaultdict(int)
        for patterns in self.access_patterns.values():
            for pattern in patterns:
                for item in pattern['items']:
                    access_counts[item] += 1
        
        if access_counts:
            sorted_items = sorted(access_counts.items(), key=lambda x: x[1], reverse=True)
            analysis['most_accessed_items'] = sorted_items[:5]
            analysis['least_accessed_items'] = sorted_items[-5:]
        
        # Find co-access patterns
        analysis['co_access_patterns'] = [
            list(itemset) for itemset in self._find_frequent_item_sets()
        ][:10]
        
        return analysis
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get metrics about optimization effectiveness."""
        metrics = {
            'total_patterns_recorded': sum(len(p) for p in self.access_patterns.values()),
            'unique_operations': len(self.access_patterns),
            'performance_percentiles': {},
            'pattern_confidence': {}
        }
        
        # Calculate performance percentiles
        if self.performance_history:
            sorted_perf = sorted(self.performance_history)
            n = len(sorted_perf)
            metrics['performance_percentiles'] = {
                'p50': sorted_perf[n // 2],
                'p90': sorted_perf[int(n * 0.9)],
                'p95': sorted_perf[int(n * 0.95)],
                'p99': sorted_perf[int(n * 0.99)] if n > 100 else sorted_perf[-1]
            }
        
        # Calculate pattern confidence
        for op_type, patterns in self.access_patterns.items():
            if len(patterns) >= 5:
                # Simple confidence based on consistency
                item_sequences = [tuple(p['items']) for p in patterns[-5:]]
                unique_sequences = len(set(item_sequences))
                confidence = 1.0 - (unique_sequences - 1) / 5.0
                metrics['pattern_confidence'][op_type] = confidence
        
        return metrics