#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/optimization/scoring_functions.py
🎯 PURPOSE: Scoring and weighting functions for context items
🔗 IMPORTS: math, datetime, typing, enum
📤 EXPORTS: PriorityScorer, RelevanceDecayFunction, hours_since_access
🔄 PATTERN: Strategy pattern for scoring algorithms
📝 TODOS: Add ML-based relevance scoring
"""

"""
CORA - Claude Operational Research Assistant
Scoring Functions Module

Implements various scoring and weighting functions for context optimization.

Author: CORA Team
Version: 1.0.0
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum


def hours_since_access(last_accessed: datetime) -> float:
    """Calculate hours since last access."""
    return (datetime.now(timezone.utc) - last_accessed).total_seconds() / 3600


class ItemType(Enum):
    """Types of context items."""
    FILE_CONTENT = "file_content"
    DECISION = "decision"
    UNDERSTANDING_NODE = "understanding_node"
    MEMORY = "memory"
    SUMMARY = "summary"
    INSTRUCTION = "instruction"
    ERROR_CONTEXT = "error_context"
    DEPENDENCY = "dependency"


class PriorityScorer:
    """Calculates priority scores for context items."""
    
    def __init__(self):
        """Initialize priority scorer."""
        self.type_weights = {
            ItemType.INSTRUCTION: 1.0,
            ItemType.ERROR_CONTEXT: 0.9,
            ItemType.DECISION: 0.8,
            ItemType.FILE_CONTENT: 0.7,
            ItemType.UNDERSTANDING_NODE: 0.6,
            ItemType.DEPENDENCY: 0.5,
            ItemType.SUMMARY: 0.4,
            ItemType.MEMORY: 0.3
        }
        
        self.recency_weight = 0.3
        self.frequency_weight = 0.2
        self.relevance_weight = 0.5
        
    def calculate_priority(self, item: 'ContextItem',
                          current_objectives: List[str],
                          session_context: Dict[str, Any]) -> float:
        """
        Calculate priority score for an item.
        
        Args:
            item: Context item to score
            current_objectives: Current session objectives
            session_context: Current session context
            
        Returns:
            Priority score (0-1)
        """
        # Base score from item type
        type_score = self.type_weights.get(item.item_type, 0.5)
        
        # Relevance to objectives
        objective_score = self._calculate_objective_relevance(item, current_objectives)
        
        # Recency score
        hours_old = hours_since_access(item.last_accessed)
        recency_score = 1.0 / (1.0 + hours_old / 24)  # Decay over days
        
        # Frequency score
        frequency_score = min(1.0, item.access_count / 10)  # Cap at 10 accesses
        
        # Dependency score
        dependency_score = self._calculate_dependency_score(item, session_context)
        
        # Combine scores
        priority = (
            type_score * 0.3 +
            objective_score * 0.3 +
            recency_score * self.recency_weight * 0.4 +
            frequency_score * self.frequency_weight * 0.4 +
            dependency_score * 0.2
        )
        
        # Apply boosts
        priority = self._apply_contextual_boosts(priority, item, session_context)
        
        return min(1.0, priority)
    
    def _calculate_objective_relevance(self, item: 'ContextItem',
                                     objectives: List[str]) -> float:
        """Calculate relevance to current objectives."""
        if not objectives:
            return 0.5  # Neutral score
        
        # Simple keyword matching (in practice, use embeddings)
        content_lower = item.content.lower()
        matches = sum(1 for obj in objectives if obj.lower() in content_lower)
        
        return min(1.0, matches / len(objectives))
    
    def _calculate_dependency_score(self, item: 'ContextItem',
                                   context: Dict[str, Any]) -> float:
        """Calculate score based on dependencies."""
        if not item.dependencies:
            return 0.5  # No dependencies
        
        # Check how many dependencies are in context
        context_items = set(context.get('item_ids', []))
        satisfied_deps = len(item.dependencies & context_items)
        
        if satisfied_deps == len(item.dependencies):
            return 1.0  # All dependencies satisfied
        else:
            return satisfied_deps / len(item.dependencies)
    
    def _apply_contextual_boosts(self, base_priority: float,
                                item: 'ContextItem',
                                context: Dict[str, Any]) -> float:
        """Apply contextual boosts to priority."""
        priority = base_priority
        
        # Boost for items in active files
        if item.item_type == ItemType.FILE_CONTENT:
            active_files = context.get('active_files', [])
            if item.metadata.get('file_path') in active_files:
                priority *= 1.2
        
        # Boost for recent errors
        if item.item_type == ItemType.ERROR_CONTEXT:
            error_age = hours_since_access(item.timestamp)
            if error_age < 1:  # Within last hour
                priority *= 1.5
        
        # Boost for high-confidence decisions
        if item.item_type == ItemType.DECISION:
            confidence = item.metadata.get('confidence', 0.5)
            if confidence > 0.8:
                priority *= 1.1
        
        return priority


class RelevanceDecayFunction:
    """Manages relevance decay over time."""
    
    def __init__(self, base_decay_rate: float = 0.1):
        """
        Initialize decay function.
        
        Args:
            base_decay_rate: Base decay rate per hour
        """
        self.base_decay_rate = base_decay_rate
        self.type_decay_modifiers = {
            ItemType.INSTRUCTION: 0.0,  # Never decay
            ItemType.ERROR_CONTEXT: 0.5,  # Slow decay
            ItemType.DECISION: 1.0,  # Normal decay
            ItemType.FILE_CONTENT: 1.2,  # Faster decay
            ItemType.UNDERSTANDING_NODE: 0.8,  # Slower decay
            ItemType.MEMORY: 1.5,  # Fast decay
            ItemType.SUMMARY: 0.7,  # Slower decay
            ItemType.DEPENDENCY: 0.9  # Normal decay
        }
        
    def calculate_decay(self, item: 'ContextItem',
                       hours_elapsed: float) -> float:
        """
        Calculate relevance after decay.
        
        Args:
            item: Context item
            hours_elapsed: Hours since last relevance update
            
        Returns:
            Decayed relevance (0-1)
        """
        # Get type-specific decay modifier
        modifier = self.type_decay_modifiers.get(item.item_type, 1.0)
        
        # Calculate effective decay rate
        effective_rate = self.base_decay_rate * modifier
        
        # Apply exponential decay
        decay_factor = math.exp(-effective_rate * hours_elapsed)
        
        # Apply minimum threshold
        min_relevance = 0.1
        decayed_relevance = max(min_relevance, item.relevance * decay_factor)
        
        return decayed_relevance
    
    def update_relevance(self, item: 'ContextItem') -> float:
        """Update item relevance based on decay."""
        hours_elapsed = hours_since_access(item.last_accessed)
        new_relevance = self.calculate_decay(item, hours_elapsed)
        item.relevance = new_relevance
        return new_relevance