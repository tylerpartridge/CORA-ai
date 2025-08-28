#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/optimization/__init__.py
🎯 PURPOSE: Optimization module initialization
🔗 IMPORTS: All optimization submodules
📤 EXPORTS: All public classes and functions from submodules
"""

"""
CORA - Claude Operational Research Assistant
Optimization Module

Provides optimized context management components.

Author: CORA Team
Version: 1.0.0
"""

from .knapsack_solver import KnapsackOptimizer, OptimizationResult
from .scoring_functions import (
    PriorityScorer, 
    RelevanceDecayFunction, 
    hours_since_access,
    ItemType
)
from .optimization_strategies import (
    EvictionStrategy,
    LRUEvictionStrategy,
    PriorityEvictionStrategy,
    AdaptiveEvictionStrategy,
    EvictionPolicy,
    ContextWindowManager
)
from .context_analyzer import DynamicContextAdjuster

__all__ = [
    # Knapsack solver
    'KnapsackOptimizer',
    'OptimizationResult',
    
    # Scoring functions
    'PriorityScorer',
    'RelevanceDecayFunction',
    'hours_since_access',
    'ItemType',
    
    # Optimization strategies
    'EvictionStrategy',
    'LRUEvictionStrategy',
    'PriorityEvictionStrategy',
    'AdaptiveEvictionStrategy',
    'EvictionPolicy',
    'ContextWindowManager',
    
    # Context analyzer
    'DynamicContextAdjuster'
]