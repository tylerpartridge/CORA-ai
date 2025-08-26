#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/session/drift_detector.py
🎯 PURPOSE: Detect context drift between Claude sessions
🔗 IMPORTS: datetime, math, collections, pathlib, enum
📤 EXPORTS: DriftDetector, DriftMetrics, DriftType
🔄 PATTERN: Strategy pattern for drift detection algorithms
📝 TODOS: Add ML-based drift prediction

💡 AI HINT: Identifies when context has shifted significantly
⚠️ NEVER: Ignore critical drift that could affect performance
"""

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
from enum import Enum

import logging
logger = logging.getLogger(__name__)


class DriftType(Enum):
    """Types of context drift."""
    TEMPORAL = "temporal_drift"  # Time-based drift
    SEMANTIC = "semantic_drift"  # Meaning/understanding drift
    STRUCTURAL = "structural_drift"  # Codebase structure drift
    OBJECTIVE = "objective_drift"  # Goal/purpose drift


@dataclass
class DriftMetrics:
    """Metrics for context drift detection."""
    drift_type: DriftType
    drift_score: float  # 0-1, higher means more drift
    confidence: float
    indicators: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'drift_type': self.drift_type.value,
            'drift_score': self.drift_score,
            'confidence': self.confidence,
            'indicators': self.indicators,
            'recommendations': self.recommendations
        }


class DriftDetector:
    """Detects context drift between sessions."""
    
    def __init__(self, sensitivity: float = 0.5):
        """
        Initialize drift detector.
        
        Args:
            sensitivity: Detection sensitivity (0-1)
        """
        self.sensitivity = sensitivity
        self.baseline_metrics: Dict[str, Any] = {}
        
    def establish_baseline(self, session_data: Dict[str, Any]) -> None:
        """
        Establish baseline metrics from session.
        
        Args:
            session_data: Session data to use as baseline
        """
        self.baseline_metrics = {
            'timestamp': datetime.now(timezone.utc),
            'file_patterns': self._extract_file_patterns(session_data),
            'decision_distribution': self._calculate_decision_distribution(session_data),
            'understanding_signature': self._calculate_understanding_signature(session_data),
            'objective_keywords': self._extract_objective_keywords(session_data)
        }
        
        logger.info("Established context drift baseline")
    
    def detect_drift(self, current_session: Dict[str, Any]) -> List[DriftMetrics]:
        """
        Detect context drift from baseline.
        
        Args:
            current_session: Current session data
            
        Returns:
            List of detected drifts
        """
        if not self.baseline_metrics:
            logger.warning("No baseline established for drift detection")
            return []
        
        drifts = []
        
        # Temporal drift
        temporal_drift = self._detect_temporal_drift(current_session)
        if temporal_drift.drift_score > self.sensitivity:
            drifts.append(temporal_drift)
        
        # Semantic drift
        semantic_drift = self._detect_semantic_drift(current_session)
        if semantic_drift.drift_score > self.sensitivity:
            drifts.append(semantic_drift)
        
        # Structural drift
        structural_drift = self._detect_structural_drift(current_session)
        if structural_drift.drift_score > self.sensitivity:
            drifts.append(structural_drift)
        
        # Objective drift
        objective_drift = self._detect_objective_drift(current_session)
        if objective_drift.drift_score > self.sensitivity:
            drifts.append(objective_drift)
        
        return drifts
    
    def _detect_temporal_drift(self, session: Dict[str, Any]) -> DriftMetrics:
        """Detect temporal context drift."""
        indicators = []
        
        # Check time gap
        if 'timestamp' in self.baseline_metrics:
            time_gap = (datetime.now(timezone.utc) - 
                       self.baseline_metrics['timestamp']).total_seconds() / 3600
            
            if time_gap > 24:
                indicators.append(f"Large time gap: {time_gap:.1f} hours")
            
            # Calculate drift score based on time
            drift_score = min(1.0, time_gap / 168)  # 1 week = full drift
        else:
            drift_score = 0.0
        
        recommendations = []
        if drift_score > 0.5:
            recommendations.append("Review recent changes before proceeding")
            recommendations.append("Check for external updates or modifications")
        
        return DriftMetrics(
            drift_type=DriftType.TEMPORAL,
            drift_score=drift_score,
            confidence=0.9,
            indicators=indicators,
            recommendations=recommendations
        )
    
    def _detect_semantic_drift(self, session: Dict[str, Any]) -> DriftMetrics:
        """Detect semantic understanding drift."""
        current_signature = self._calculate_understanding_signature(session)
        baseline_signature = self.baseline_metrics.get('understanding_signature', {})
        
        # Compare signatures
        drift_score = 0.0
        indicators = []
        
        # Check node type distribution
        for node_type in set(list(current_signature.keys()) + list(baseline_signature.keys())):
            current_count = current_signature.get(node_type, 0)
            baseline_count = baseline_signature.get(node_type, 0)
            
            if baseline_count > 0:
                change_ratio = abs(current_count - baseline_count) / baseline_count
                if change_ratio > 0.5:
                    indicators.append(f"{node_type} understanding changed by {change_ratio:.0%}")
                drift_score += change_ratio * 0.2
        
        drift_score = min(1.0, drift_score)
        
        recommendations = []
        if drift_score > 0.5:
            recommendations.append("Re-analyze core concepts to refresh understanding")
            recommendations.append("Verify assumptions about code structure")
        
        return DriftMetrics(
            drift_type=DriftType.SEMANTIC,
            drift_score=drift_score,
            confidence=0.8,
            indicators=indicators,
            recommendations=recommendations
        )
    
    def _detect_structural_drift(self, session: Dict[str, Any]) -> DriftMetrics:
        """Detect structural codebase drift."""
        current_patterns = self._extract_file_patterns(session)
        baseline_patterns = self.baseline_metrics.get('file_patterns', {})
        
        drift_score = 0.0
        indicators = []
        
        # Check directory structure changes
        current_dirs = set(current_patterns.get('directories', []))
        baseline_dirs = set(baseline_patterns.get('directories', []))
        
        added_dirs = current_dirs - baseline_dirs
        removed_dirs = baseline_dirs - current_dirs
        
        if added_dirs:
            indicators.append(f"New directories: {', '.join(added_dirs)}")
            drift_score += 0.3
        
        if removed_dirs:
            indicators.append(f"Missing directories: {', '.join(removed_dirs)}")
            drift_score += 0.4
        
        # Check file type distribution
        current_types = current_patterns.get('file_types', {})
        baseline_types = baseline_patterns.get('file_types', {})
        
        for file_type in set(list(current_types.keys()) + list(baseline_types.keys())):
            current_count = current_types.get(file_type, 0)
            baseline_count = baseline_types.get(file_type, 0)
            
            if baseline_count > 0 and abs(current_count - baseline_count) > 5:
                indicators.append(f"{file_type} file count changed significantly")
                drift_score += 0.1
        
        drift_score = min(1.0, drift_score)
        
        recommendations = []
        if drift_score > 0.5:
            recommendations.append("Scan codebase for structural changes")
            recommendations.append("Update understanding graph with new structure")
        
        return DriftMetrics(
            drift_type=DriftType.STRUCTURAL,
            drift_score=drift_score,
            confidence=0.85,
            indicators=indicators,
            recommendations=recommendations
        )
    
    def _detect_objective_drift(self, session: Dict[str, Any]) -> DriftMetrics:
        """Detect objective/goal drift."""
        current_keywords = self._extract_objective_keywords(session)
        baseline_keywords = self.baseline_metrics.get('objective_keywords', set())
        
        # Calculate keyword overlap
        if baseline_keywords:
            overlap = len(current_keywords & baseline_keywords) / len(baseline_keywords)
            drift_score = 1.0 - overlap
        else:
            drift_score = 0.0
        
        indicators = []
        
        new_keywords = current_keywords - baseline_keywords
        if new_keywords:
            indicators.append(f"New focus areas: {', '.join(list(new_keywords)[:5])}")
        
        lost_keywords = baseline_keywords - current_keywords
        if lost_keywords:
            indicators.append(f"Lost focus areas: {', '.join(list(lost_keywords)[:5])}")
        
        recommendations = []
        if drift_score > 0.5:
            recommendations.append("Clarify current objectives with user")
            recommendations.append("Review original goals and adjust approach")
        
        return DriftMetrics(
            drift_type=DriftType.OBJECTIVE,
            drift_score=drift_score,
            confidence=0.7,
            indicators=indicators,
            recommendations=recommendations
        )
    
    def _extract_file_patterns(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Extract file access patterns."""
        files = session.get('files_touched', [])
        
        patterns = {
            'directories': set(),
            'file_types': defaultdict(int),
            'depth_distribution': defaultdict(int)
        }
        
        for file_path in files:
            path = Path(file_path)
            
            # Extract directory
            if len(path.parts) > 1:
                patterns['directories'].add(path.parts[1])
            
            # Extract file type
            if path.suffix:
                patterns['file_types'][path.suffix] += 1
            
            # Track depth
            patterns['depth_distribution'][len(path.parts)] += 1
        
        # Convert sets to lists for JSON serialization
        patterns['directories'] = list(patterns['directories'])
        
        return patterns
    