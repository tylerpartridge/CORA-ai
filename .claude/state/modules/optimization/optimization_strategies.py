#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/optimization/optimization_strategies.py
🎯 PURPOSE: Eviction and optimization strategies for context management
🔗 IMPORTS: abc, logging, datetime, collections, typing, enum
📤 EXPORTS: EvictionStrategy, LRUEvictionStrategy, PriorityEvictionStrategy, AdaptiveEvictionStrategy, EvictionPolicy
🔄 PATTERN: Strategy pattern for eviction policies
📝 TODOS: Add hybrid eviction strategies
"""

"""
CORA - Claude Operational Research Assistant
Optimization Strategies Module

Implements various eviction and optimization strategies for context management.

Author: CORA Team
Version: 1.0.0
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from collections import defaultdict, deque
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class EvictionPolicy(Enum):
    """Context eviction policies."""
    LRU = "least_recently_used"
    LFU = "least_frequently_used"
    FIFO = "first_in_first_out"
    PRIORITY = "priority_based"
    DECAY = "relevance_decay"
    ADAPTIVE = "adaptive"


class EvictionStrategy(ABC):
    """Abstract base class for eviction strategies."""
    
    @abstractmethod
    def select_items_to_evict(self, items: List['ContextItem'],
                             tokens_to_free: int) -> List[str]:
        """Select items to evict from context."""
        pass


class LRUEvictionStrategy(EvictionStrategy):
    """Least Recently Used eviction strategy."""
    
    def select_items_to_evict(self, items: List['ContextItem'],
                             tokens_to_free: int) -> List[str]:
        """Select least recently used items to evict."""
        # Sort by last accessed time (oldest first)
        sorted_items = sorted(items, key=lambda x: x.last_accessed)
        
        evicted_ids = []
        freed_tokens = 0
        
        for item in sorted_items:
            if freed_tokens >= tokens_to_free:
                break
            evicted_ids.append(item.item_id)
            freed_tokens += item.token_count
        
        return evicted_ids


class PriorityEvictionStrategy(EvictionStrategy):
    """Priority-based eviction strategy."""
    
    def select_items_to_evict(self, items: List['ContextItem'],
                             tokens_to_free: int) -> List[str]:
        """Select lowest priority items to evict."""
        from .scoring_functions import ItemType
        
        # Sort by value score (lowest first)
        sorted_items = sorted(items, key=lambda x: x.get_value_score())
        
        evicted_ids = []
        freed_tokens = 0
        
        for item in sorted_items:
            # Never evict instructions
            if item.item_type == ItemType.INSTRUCTION:
                continue
                
            if freed_tokens >= tokens_to_free:
                break
                
            evicted_ids.append(item.item_id)
            freed_tokens += item.token_count
        
        return evicted_ids


class AdaptiveEvictionStrategy(EvictionStrategy):
    """Adaptive eviction strategy that learns from patterns."""
    
    def __init__(self):
        """Initialize adaptive strategy."""
        self.eviction_history = deque(maxlen=100)
        self.reinsertion_penalty = defaultdict(float)
        
    def select_items_to_evict(self, items: List['ContextItem'],
                             tokens_to_free: int) -> List[str]:
        """Select items using adaptive strategy."""
        from .scoring_functions import ItemType
        
        # Calculate scores including penalties
        scored_items = []
        for item in items:
            # Skip protected items
            if item.item_type == ItemType.INSTRUCTION:
                continue
                
            base_score = item.get_value_score()
            penalty = self.reinsertion_penalty.get(item.item_id, 0)
            adjusted_score = base_score - penalty
            
            scored_items.append((adjusted_score, item))
        
        # Sort by adjusted score (lowest first)
        scored_items.sort(key=lambda x: x[0])
        
        evicted_ids = []
        freed_tokens = 0
        
        for score, item in scored_items:
            if freed_tokens >= tokens_to_free:
                break
                
            evicted_ids.append(item.item_id)
            freed_tokens += item.token_count
            
            # Record eviction
            self.eviction_history.append({
                'item_id': item.item_id,
                'timestamp': datetime.now(timezone.utc),
                'score': score
            })
        
        return evicted_ids
    
    def record_reinsertion(self, item_id: str) -> None:
        """Record that an item was reinserted after eviction."""
        # Increase penalty for items that get reinserted
        self.reinsertion_penalty[item_id] += 0.1
        
        # Decay penalties over time
        for key in list(self.reinsertion_penalty.keys()):
            self.reinsertion_penalty[key] *= 0.95
            if self.reinsertion_penalty[key] < 0.01:
                del self.reinsertion_penalty[key]


class ContextWindowManager:
    """Manages context window pressure and optimization."""
    
    def __init__(self, max_tokens: int, target_utilization: float = 0.8):
        """
        Initialize context window manager.
        
        Args:
            max_tokens: Maximum context window size
            target_utilization: Target utilization (0-1)
        """
        self.max_tokens = max_tokens
        self.target_utilization = target_utilization
        self.pressure_history = deque(maxlen=50)
        self.pressure_thresholds = {
            'low': 0.6,
            'medium': 0.8,
            'high': 0.9,
            'critical': 0.95
        }
        
    def calculate_pressure(self, current_tokens: int) -> Dict[str, Any]:
        """
        Calculate current context window pressure.
        
        Args:
            current_tokens: Current token count
            
        Returns:
            Pressure metrics
        """
        utilization = current_tokens / self.max_tokens
        
        # Determine pressure level
        if utilization < self.pressure_thresholds['low']:
            level = 'low'
        elif utilization < self.pressure_thresholds['medium']:
            level = 'medium'
        elif utilization < self.pressure_thresholds['high']:
            level = 'high'
        elif utilization < self.pressure_thresholds['critical']:
            level = 'critical'
        else:
            level = 'exceeded'
        
        # Calculate headroom
        headroom = self.max_tokens - current_tokens
        headroom_percent = (headroom / self.max_tokens) * 100
        
        # Record in history
        self.pressure_history.append({
            'timestamp': datetime.now(timezone.utc),
            'utilization': utilization,
            'level': level
        })
        
        # Calculate trend
        trend = self._calculate_pressure_trend()
        
        return {
            'current_tokens': current_tokens,
            'max_tokens': self.max_tokens,
            'utilization': utilization,
            'level': level,
            'headroom': headroom,
            'headroom_percent': headroom_percent,
            'trend': trend,
            'recommendation': self._get_pressure_recommendation(level, trend)
        }
    
    def should_optimize(self, current_pressure: Dict[str, Any]) -> bool:
        """Determine if optimization is needed."""
        level = current_pressure['level']
        trend = current_pressure['trend']
        
        # Always optimize if critical or exceeded
        if level in ['critical', 'exceeded']:
            return True
        
        # Optimize if high and trending up
        if level == 'high' and trend == 'increasing':
            return True
        
        # Optimize if above target utilization
        if current_pressure['utilization'] > self.target_utilization:
            return True
        
        return False
    
    def calculate_tokens_to_free(self, current_tokens: int) -> int:
        """Calculate how many tokens to free."""
        target_tokens = int(self.max_tokens * self.target_utilization)
        
        if current_tokens <= target_tokens:
            return 0
        
        # Free enough to get to target, plus buffer
        buffer = int(self.max_tokens * 0.05)  # 5% buffer
        return current_tokens - target_tokens + buffer
    
    def _calculate_pressure_trend(self) -> str:
        """Calculate pressure trend from history."""
        if len(self.pressure_history) < 3:
            return 'stable'
        
        recent = list(self.pressure_history)[-5:]
        utilizations = [p['utilization'] for p in recent]
        
        # Simple trend detection
        if len(utilizations) >= 2:
            avg_change = sum(
                utilizations[i] - utilizations[i-1]
                for i in range(1, len(utilizations))
            ) / (len(utilizations) - 1)
            
            if avg_change > 0.02:  # 2% increase
                return 'increasing'
            elif avg_change < -0.02:  # 2% decrease
                return 'decreasing'
        
        return 'stable'
    
    def _get_pressure_recommendation(self, level: str, trend: str) -> str:
        """Get recommendation based on pressure level and trend."""
        if level == 'exceeded':
            return "Immediate optimization required - context window exceeded"
        elif level == 'critical':
            return "Urgent optimization needed to prevent overflow"
        elif level == 'high' and trend == 'increasing':
            return "Proactive optimization recommended"
        elif level == 'high':
            return "Monitor closely, optimization may be needed soon"
        elif level == 'medium':
            return "Healthy utilization, continue monitoring"
        else:
            return "Low utilization, no action needed"