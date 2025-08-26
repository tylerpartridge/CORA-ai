#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/metrics/quality_analyzer.py
🎯 PURPOSE: Analyze context quality across multiple dimensions
🔗 IMPORTS: dataclasses, datetime, enum, numpy, statistics
📤 EXPORTS: ContextQualityAnalyzer, ContextQualityScore, QualityDimension
🔄 PATTERN: Strategy pattern for quality assessment algorithms
📝 TODOS: Add weighted scoring, implement quality prediction

💡 AI HINT: Measures how good the current context is for decision-making
⚠️ NEVER: Allow quality to drop below critical thresholds silently
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import numpy as np
import statistics

import logging
logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Dimensions of context quality."""
    COVERAGE = "coverage"
    RELEVANCE = "relevance"
    FRESHNESS = "freshness"
    COMPLETENESS = "completeness"
    COHERENCE = "coherence"


@dataclass
class ContextQualityScore:
    """Context quality assessment results."""
    overall_score: float
    dimensions: Dict[QualityDimension, float]
    confidence: float
    issues: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'overall_score': self.overall_score,
            'dimensions': {dim.value: score for dim, score in self.dimensions.items()},
            'confidence': self.confidence,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }


class ContextQualityAnalyzer:
    """Analyzes context quality across multiple dimensions."""
    
    def __init__(self, quality_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize quality analyzer.
        
        Args:
            quality_thresholds: Custom quality thresholds by dimension
        """
        self.quality_thresholds = quality_thresholds or {
            'coverage': 0.7,
            'relevance': 0.8,
            'freshness': 0.6,
            'completeness': 0.75,
            'coherence': 0.85
        }
        
        self.dimension_weights = {
            QualityDimension.COVERAGE: 0.2,
            QualityDimension.RELEVANCE: 0.3,
            QualityDimension.FRESHNESS: 0.15,
            QualityDimension.COMPLETENESS: 0.2,
            QualityDimension.COHERENCE: 0.15
        }
    
    def analyze_quality(self, context_items: List[Dict[str, Any]], 
                       task_requirements: Dict[str, Any]) -> ContextQualityScore:
        """
        Analyze context quality.
        
        Args:
            context_items: List of context items
            task_requirements: Requirements for the current task
            
        Returns:
            Context quality score
        """
        dimensions = {}
        issues = []
        recommendations = []
        
        # Analyze each dimension
        dimensions[QualityDimension.COVERAGE] = self._analyze_coverage(
            context_items, task_requirements
        )
        dimensions[QualityDimension.RELEVANCE] = self._analyze_relevance(
            context_items, task_requirements
        )
        dimensions[QualityDimension.FRESHNESS] = self._analyze_freshness(
            context_items
        )
        dimensions[QualityDimension.COMPLETENESS] = self._analyze_completeness(
            context_items, task_requirements
        )
        dimensions[QualityDimension.COHERENCE] = self._analyze_coherence(
            context_items
        )
        
        # Calculate overall score
        overall_score = sum(
            score * self.dimension_weights[dim]
            for dim, score in dimensions.items()
        )
        
        # Identify issues
        for dim, score in dimensions.items():
            threshold = self.quality_thresholds.get(dim.value, 0.7)
            if score < threshold:
                issues.append(f"Low {dim.value}: {score:.2f} < {threshold}")
                
                # Generate recommendations
                if dim == QualityDimension.COVERAGE:
                    recommendations.append("Load more relevant files to improve coverage")
                elif dim == QualityDimension.RELEVANCE:
                    recommendations.append("Filter out low-relevance context items")
                elif dim == QualityDimension.FRESHNESS:
                    recommendations.append("Refresh stale context information")
                elif dim == QualityDimension.COMPLETENESS:
                    recommendations.append("Add missing context dependencies")
                elif dim == QualityDimension.COHERENCE:
                    recommendations.append("Resolve conflicting context information")
        
        # Calculate confidence
        confidence = self._calculate_confidence(dimensions, len(context_items))
        
        return ContextQualityScore(
            overall_score=overall_score,
            dimensions=dimensions,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations
        )
    
    def _analyze_coverage(self, context_items: List[Dict[str, Any]], 
                         task_requirements: Dict[str, Any]) -> float:
        """Analyze context coverage."""
        if not task_requirements.get('required_files'):
            return 1.0
        
        required_files = set(task_requirements['required_files'])
        covered_files = {
            item['path'] for item in context_items 
            if item.get('type') == 'file' and 'path' in item
        }
        
        if not required_files:
            return 1.0
        
        coverage = len(covered_files & required_files) / len(required_files)
        return coverage
    
    def _analyze_relevance(self, context_items: List[Dict[str, Any]], 
                          task_requirements: Dict[str, Any]) -> float:
        """Analyze context relevance."""
        if not context_items:
            return 0.0
        
        relevance_scores = []
        task_keywords = set(task_requirements.get('keywords', []))
        
        for item in context_items:
            item_relevance = item.get('relevance', 0.5)
            
            # Boost relevance if item contains task keywords
            if task_keywords and 'content' in item:
                content_lower = item['content'].lower()
                keyword_matches = sum(1 for kw in task_keywords if kw.lower() in content_lower)
                keyword_boost = min(0.3, keyword_matches * 0.1)
                item_relevance = min(1.0, item_relevance + keyword_boost)
            
            relevance_scores.append(item_relevance)
        
        return statistics.mean(relevance_scores) if relevance_scores else 0.0
    
    def _analyze_freshness(self, context_items: List[Dict[str, Any]]) -> float:
        """Analyze context freshness."""
        if not context_items:
            return 0.0
        
        now = datetime.now(timezone.utc)
        freshness_scores = []
        
        for item in context_items:
            if 'timestamp' in item:
                item_time = datetime.fromisoformat(item['timestamp'])
                age_hours = (now - item_time).total_seconds() / 3600
                
                # Exponential decay with 24-hour half-life
                freshness = np.exp(-age_hours / 24)
                freshness_scores.append(freshness)
            else:
                freshness_scores.append(0.5)  # Default for items without timestamp
        
        return statistics.mean(freshness_scores) if freshness_scores else 0.0
    
    def _analyze_completeness(self, context_items: List[Dict[str, Any]], 
                             task_requirements: Dict[str, Any]) -> float:
        """Analyze context completeness."""
        required_types = task_requirements.get('required_context_types', [])
        if not required_types:
            return 1.0
        
        available_types = {item.get('type') for item in context_items if 'type' in item}
        completeness = len(available_types & set(required_types)) / len(required_types)
        
        return completeness
    
    def _analyze_coherence(self, context_items: List[Dict[str, Any]]) -> float:
        """Analyze context coherence."""
        if len(context_items) < 2:
            return 1.0
        
        # Check for conflicting information
        conflicts = 0
        comparisons = 0
        
        for i, item1 in enumerate(context_items):
            for item2 in context_items[i+1:]:
                if self._items_overlap(item1, item2):
                    comparisons += 1
                    if self._items_conflict(item1, item2):
                        conflicts += 1
        
        if comparisons == 0:
            return 1.0
        
        coherence = 1.0 - (conflicts / comparisons)
        return coherence
    
    def _items_overlap(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """Check if two items have overlapping scope."""
        # Simple check - items overlap if they refer to the same file or entity
        if item1.get('path') and item1.get('path') == item2.get('path'):
            return True
        if item1.get('entity_id') and item1.get('entity_id') == item2.get('entity_id'):
            return True
        return False
    
    def _items_conflict(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """Check if two items have conflicting information."""
        # Simple conflict detection - could be made more sophisticated
        if 'version' in item1 and 'version' in item2:
            return item1['version'] != item2['version']
        return False
    
    def _calculate_confidence(self, dimensions: Dict[QualityDimension, float], 
                            item_count: int) -> float:
        """Calculate confidence in quality assessment."""
        # Base confidence on number of items and dimension scores
        if item_count == 0:
            return 0.0
        
        # Higher confidence with more items (up to a point)
        count_factor = min(1.0, item_count / 20)
        
        # Higher confidence when dimensions are consistent
        scores = list(dimensions.values())
        consistency = 1.0 - statistics.stdev(scores) if len(scores) > 1 else 1.0
        
        confidence = (count_factor * 0.6 + consistency * 0.4)
        return confidence