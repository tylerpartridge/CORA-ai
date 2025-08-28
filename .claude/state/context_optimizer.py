#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/context_optimizer.py
🎯 PURPOSE: Intelligent context optimization with knapsack algorithms and eviction policies
🔗 IMPORTS: json, logging, datetime, dataclasses, modules.optimization
📤 EXPORTS: ContextOptimizer, ContextItem, ItemType, EvictionPolicy
🔄 PATTERN: Strategy pattern for eviction policies, knapsack optimization
📝 TODOS: Add ML-based relevance prediction, implement context compression

💡 AI HINT: Maximizes context window efficiency using dynamic priority scoring
⚠️ NEVER: Evict critical system prompts or current task objectives
"""

"""
CORA - Claude Operational Research Assistant
Context Optimizer Module

Implements intelligent context optimization using knapsack algorithms,
priority scoring, dynamic adjustment, relevance decay, smart eviction
policies, and context window pressure management.

Author: CORA Team
Version: 1.0.0
"""

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from collections import defaultdict, deque
from enum import Enum
import numpy as np

# Import from optimization modules
from .modules.optimization import (
    KnapsackOptimizer,
    OptimizationResult,
    PriorityScorer,
    RelevanceDecayFunction,
    hours_since_access,
    ItemType,
    EvictionStrategy,
    LRUEvictionStrategy,
    PriorityEvictionStrategy,
    AdaptiveEvictionStrategy,
    EvictionPolicy,
    ContextWindowManager,
    DynamicContextAdjuster
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ContextItem:
    """Represents an item in the context window."""
    item_id: str
    item_type: ItemType
    content: str
    token_count: int
    priority: float
    relevance: float
    timestamp: datetime
    last_accessed: datetime
    access_count: int = 0
    decay_rate: float = 0.1
    dependencies: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_current_relevance(self) -> float:
        """Calculate current relevance with decay."""
        hours_since_access = (datetime.now(timezone.utc) - self.last_accessed).total_seconds() / 3600
        decay_factor = math.exp(-self.decay_rate * hours_since_access)
        return self.relevance * decay_factor
    
    def get_value_score(self) -> float:
        """Calculate overall value score for optimization."""
        current_relevance = self.get_current_relevance()
        recency_boost = 1.0 / (1.0 + hours_since_access(self.last_accessed))
        frequency_boost = math.log(1 + self.access_count) / 10
        
        return (
            self.priority * 0.4 +
            current_relevance * 0.3 +
            recency_boost * 0.2 +
            frequency_boost * 0.1
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'item_id': self.item_id,
            'item_type': self.item_type.value,
            'token_count': self.token_count,
            'priority': self.priority,
            'relevance': self.relevance,
            'timestamp': self.timestamp.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count,
            'decay_rate': self.decay_rate,
            'dependencies': list(self.dependencies),
            'metadata': self.metadata
        }


class ContextOptimizer:
    """Main context optimizer combining all strategies."""
    
    def __init__(self, max_context_tokens: int = 200000):
        """
        Initialize context optimizer.
        
        Args:
            max_context_tokens: Maximum context window size
        """
        self.max_context_tokens = max_context_tokens
        
        # Initialize components
        self.priority_scorer = PriorityScorer()
        self.decay_function = RelevanceDecayFunction()
        self.knapsack_optimizer = KnapsackOptimizer(max_context_tokens)
        self.window_manager = ContextWindowManager(max_context_tokens)
        
        # Initialize eviction strategies
        self.eviction_strategies = {
            EvictionPolicy.LRU: LRUEvictionStrategy(),
            EvictionPolicy.PRIORITY: PriorityEvictionStrategy(),
            EvictionPolicy.ADAPTIVE: AdaptiveEvictionStrategy()
        }
        self.current_eviction_policy = EvictionPolicy.ADAPTIVE
        
        # Context storage
        self.context_items: Dict[str, ContextItem] = {}
        self.required_items: Set[str] = set()
        
        # Metrics
        self.optimization_count = 0
        self.total_evictions = 0
        
        logger.info(f"Initialized ContextOptimizer with {max_context_tokens} max tokens")
    
    def add_item(self, item: ContextItem, required: bool = False) -> bool:
        """
        Add item to context.
        
        Args:
            item: Context item to add
            required: Whether item is required
            
        Returns:
            Whether item was added successfully
        """
        # Update priority
        current_objectives = self._get_current_objectives()
        session_context = self._get_session_context()
        item.priority = self.priority_scorer.calculate_priority(
            item, current_objectives, session_context
        )
        
        # Add to storage
        self.context_items[item.item_id] = item
        if required:
            self.required_items.add(item.item_id)
        
        # Check if optimization is needed
        current_tokens = self._calculate_total_tokens()
        pressure = self.window_manager.calculate_pressure(current_tokens)
        
        if self.window_manager.should_optimize(pressure):
            self.optimize()
        
        return item.item_id in self.context_items
    
    def access_item(self, item_id: str) -> Optional[ContextItem]:
        """
        Access a context item, updating its metadata.
        
        Args:
            item_id: ID of item to access
            
        Returns:
            The context item or None
        """
        if item_id not in self.context_items:
            return None
        
        item = self.context_items[item_id]
        item.last_accessed = datetime.now(timezone.utc)
        item.access_count += 1
        
        return item
    
    def optimize(self) -> OptimizationResult:
        """
        Optimize context using current strategy.
        
        Returns:
            Optimization result
        """
        self.optimization_count += 1
        
        # Update relevance for all items
        for item in self.context_items.values():
            self.decay_function.update_relevance(item)
        
        # Get current state
        items = list(self.context_items.values())
        current_tokens = self._calculate_total_tokens()
        
        # Check pressure
        pressure = self.window_manager.calculate_pressure(current_tokens)
        
        if pressure['level'] in ['critical', 'exceeded']:
            # Emergency eviction
            return self._emergency_optimize(items, pressure)
        
        # Run knapsack optimization
        result = self.knapsack_optimizer.optimize(items, self.required_items)
        
        # Update context based on result
        self._apply_optimization_result(result)
        
        return result
    
    def evict_items(self, tokens_to_free: int) -> List[str]:
        """
        Evict items to free tokens.
        
        Args:
            tokens_to_free: Number of tokens to free
            
        Returns:
            List of evicted item IDs
        """
        strategy = self.eviction_strategies[self.current_eviction_policy]
        items = [item for item in self.context_items.values()
                if item.item_id not in self.required_items]
        
        evicted_ids = strategy.select_items_to_evict(items, tokens_to_free)
        
        # Remove evicted items
        for item_id in evicted_ids:
            if item_id in self.context_items:
                del self.context_items[item_id]
                self.total_evictions += 1
        
        # Record reinsertions for adaptive strategy
        if isinstance(strategy, AdaptiveEvictionStrategy):
            for item_id in evicted_ids:
                if item_id in self.context_items:
                    strategy.record_reinsertion(item_id)
        
        return evicted_ids
    
    def get_context_state(self) -> Dict[str, Any]:
        """Get current context state."""
        current_tokens = self._calculate_total_tokens()
        pressure = self.window_manager.calculate_pressure(current_tokens)
        
        # Group items by type
        items_by_type = defaultdict(list)
        for item in self.context_items.values():
            items_by_type[item.item_type.value].append({
                'id': item.item_id,
                'tokens': item.token_count,
                'priority': item.priority,
                'relevance': item.get_current_relevance(),
                'value_score': item.get_value_score()
            })
        
        return {
            'total_items': len(self.context_items),
            'total_tokens': current_tokens,
            'required_items': len(self.required_items),
            'pressure': pressure,
            'items_by_type': dict(items_by_type),
            'eviction_policy': self.current_eviction_policy.value,
            'optimization_count': self.optimization_count,
            'total_evictions': self.total_evictions
        }
    
    def set_eviction_policy(self, policy: EvictionPolicy) -> None:
        """Set the eviction policy."""
        self.current_eviction_policy = policy
        logger.info(f"Changed eviction policy to: {policy.value}")
    
    def clear_context(self, keep_required: bool = True) -> None:
        """
        Clear context.
        
        Args:
            keep_required: Whether to keep required items
        """
        if keep_required:
            self.context_items = {
                k: v for k, v in self.context_items.items()