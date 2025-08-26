#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/optimization/knapsack_solver.py
🎯 PURPOSE: Knapsack algorithm implementation for optimal context packing
🔗 IMPORTS: logging, datetime, dataclasses, typing
📤 EXPORTS: KnapsackOptimizer, OptimizationResult
🔄 PATTERN: Dynamic programming optimization
📝 TODOS: Add approximation algorithms for large contexts
"""

"""
CORA - Claude Operational Research Assistant
Knapsack Solver Module

Implements the knapsack algorithm for optimal context window packing.

Author: CORA Team
Version: 1.0.0
"""

import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of context optimization."""
    selected_items: List[str]
    total_tokens: int
    total_value: float
    excluded_items: List[str]
    optimization_time_ms: float
    pressure_level: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'selected_items': self.selected_items,
            'total_tokens': self.total_tokens,
            'total_value': self.total_value,
            'excluded_items': self.excluded_items,
            'optimization_time_ms': self.optimization_time_ms,
            'pressure_level': self.pressure_level
        }


class KnapsackOptimizer:
    """Implements knapsack algorithm for optimal context packing."""
    
    def __init__(self, max_tokens: int):
        """
        Initialize knapsack optimizer.
        
        Args:
            max_tokens: Maximum tokens in context window
        """
        self.max_tokens = max_tokens
        
    def optimize(self, items: List['ContextItem'],
                required_items: Optional[Set[str]] = None) -> OptimizationResult:
        """
        Optimize context using dynamic programming knapsack.
        
        Args:
            items: List of context items
            required_items: Set of item IDs that must be included
            
        Returns:
            Optimization result
        """
        start_time = datetime.now(timezone.utc)
        required_items = required_items or set()
        
        # Separate required and optional items
        required = [item for item in items if item.item_id in required_items]
        optional = [item for item in items if item.item_id not in required_items]
        
        # Calculate space used by required items
        required_tokens = sum(item.token_count for item in required)
        
        if required_tokens > self.max_tokens:
            # Cannot fit all required items
            logger.warning(f"Required items exceed max tokens: {required_tokens} > {self.max_tokens}")
            # Return just the highest priority required items that fit
            required.sort(key=lambda x: x.get_value_score(), reverse=True)
            selected = []
            total_tokens = 0
            
            for item in required:
                if total_tokens + item.token_count <= self.max_tokens:
                    selected.append(item.item_id)
                    total_tokens += item.token_count
            
            excluded = [item.item_id for item in items if item.item_id not in selected]
            
            return OptimizationResult(
                selected_items=selected,
                total_tokens=total_tokens,
                total_value=sum(i.get_value_score() for i in items if i.item_id in selected),
                excluded_items=excluded,
                optimization_time_ms=self._elapsed_ms(start_time),
                pressure_level=1.0  # Maximum pressure
            )
        
        # Space available for optional items
        available_tokens = self.max_tokens - required_tokens
        
        # Run knapsack on optional items
        selected_optional = self._knapsack_dp(optional, available_tokens)
        
        # Combine results
        selected_items = [item.item_id for item in required] + selected_optional
        total_tokens = required_tokens + sum(
            item.token_count for item in optional if item.item_id in selected_optional
        )
        total_value = sum(
            item.get_value_score() for item in items if item.item_id in selected_items
        )
        excluded_items = [item.item_id for item in items if item.item_id not in selected_items]
        
        # Calculate pressure level
        pressure_level = total_tokens / self.max_tokens
        
        return OptimizationResult(
            selected_items=selected_items,
            total_tokens=total_tokens,
            total_value=total_value,
            excluded_items=excluded_items,
            optimization_time_ms=self._elapsed_ms(start_time),
            pressure_level=pressure_level
        )
    
    def _knapsack_dp(self, items: List['ContextItem'], capacity: int) -> List[str]:
        """
        Dynamic programming knapsack implementation.
        
        Args:
            items: Items to consider
            capacity: Token capacity
            
        Returns:
            List of selected item IDs
        """
        n = len(items)
        if n == 0 or capacity == 0:
            return []
        
        # Scale down for efficiency if needed
        scale_factor = 1
        if capacity > 10000:
            scale_factor = capacity // 10000
            capacity = capacity // scale_factor
            scaled_items = []
            for item in items:
                # Create a new item with scaled token count
                scaled_item = type(item)(
                    item_id=item.item_id,
                    item_type=item.item_type,
                    content=item.content,
                    token_count=max(1, item.token_count // scale_factor),
                    priority=item.priority,
                    relevance=item.relevance,
                    timestamp=item.timestamp,
                    last_accessed=item.last_accessed,
                    access_count=item.access_count,
                    decay_rate=item.decay_rate,
                    dependencies=item.dependencies,
                    metadata=item.metadata
                )
                scaled_items.append(scaled_item)
            items = scaled_items
        
        # Initialize DP table
        dp = [[0.0 for _ in range(capacity + 1)] for _ in range(n + 1)]
        
        # Fill DP table
        for i in range(1, n + 1):
            item = items[i - 1]
            value = item.get_value_score()
            weight = item.token_count
            
            for w in range(capacity + 1):
                if weight <= w:
                    dp[i][w] = max(
                        dp[i - 1][w],
                        dp[i - 1][w - weight] + value
                    )
                else:
                    dp[i][w] = dp[i - 1][w]
        
        # Backtrack to find selected items
        selected = []
        w = capacity
        
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                selected.append(items[i - 1].item_id)
                w -= items[i - 1].token_count
        
        return selected
    
    def _elapsed_ms(self, start_time: datetime) -> float:
        """Calculate elapsed time in milliseconds."""
        elapsed = datetime.now(timezone.utc) - start_time
        return elapsed.total_seconds() * 1000