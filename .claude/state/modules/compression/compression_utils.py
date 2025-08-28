#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/compression/compression_utils.py
🎯 PURPOSE: Utility functions and helpers for compression pipeline
🔗 IMPORTS: json, collections, datetime
📤 EXPORTS: DecisionTreeCompressor, CompressionMetrics, CompressionStage
🔄 PATTERN: Helper utilities and data structures
📝 TODOS: Add compression statistics aggregation

💡 AI HINT: Provides shared utilities for compression modules
⚠️ NEVER: Modify compression metrics after creation
"""

"""
CORA - Claude Operational Research Assistant
Compression Utilities Module

Provides utility functions, data structures, and helper classes
for the compression pipeline, including decision tree compression
and metrics tracking.

Author: CORA Team
Version: 1.0.0
"""

import json
from datetime import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple


class CompressionStage(Enum):
    """Stages of the compression pipeline."""
    SEMANTIC_DEDUP = "semantic_deduplication"
    GRAPH_COMPRESS = "graph_compression"
    DECISION_TREE = "decision_tree_compression"
    BINARY_COMPRESS = "binary_compression"


@dataclass
class CompressionMetrics:
    """Metrics for tracking compression performance."""
    original_size: int
    compressed_size: int
    compression_ratio: float
    stage_metrics: Dict[str, Dict[str, Any]]
    compression_time: float
    decompression_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return asdict(self)
    
    def get_stage_summary(self) -> str:
        """Get human-readable summary of stage performance."""
        summary = []
        for stage, metrics in self.stage_metrics.items():
            ratio = metrics.get('ratio', 0) * 100
            time = metrics.get('time', 0)
            summary.append(f"{stage}: {ratio:.1f}% reduction in {time:.3f}s")
        return "\n".join(summary)


class DecisionTreeCompressor:
    """Compresses decision sequences using tree structures."""
    
    def __init__(self):
        """Initialize decision tree compressor."""
        self.decision_patterns = defaultdict(list)
        
    def compress_decisions(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compress decision sequences into tree structure.
        
        Args:
            decisions: List of decisions to compress
            
        Returns:
            Compressed decision tree
        """
        if not decisions:
            return {}
            
        # Group decisions by type and pattern
        decision_groups = defaultdict(list)
        
        for decision in decisions:
            decision_type = decision.get('decision_type', 'unknown')
            decision_groups[decision_type].append(decision)
        
        # Build compressed structure
        compressed = {
            'decision_count': len(decisions),
            'types': {},
            'timeline': []
        }
        
        # Compress each type group
        for decision_type, group in decision_groups.items():
            # Extract common patterns
            pattern = self._extract_pattern(group)
            compressed['types'][decision_type] = {
                'count': len(group),
                'pattern': pattern,
                'instances': self._compress_instances(group, pattern)
            }
        
        # Build timeline index
        for idx, decision in enumerate(decisions):
            compressed['timeline'].append([
                idx,
                decision.get('decision_type', 'unknown'),
                decision.get('timestamp', '')
            ])
        
        return compressed
    
    def _extract_pattern(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common pattern from decision group."""
        if not decisions:
            return {}
        
        # Find common keys
        common_keys = set(decisions[0].keys())
        for decision in decisions[1:]:
            common_keys &= set(decision.keys())
        
        # Find common values
        pattern = {}
        for key in common_keys:
            values = [d.get(key) for d in decisions]
            # If all values are the same, it's part of the pattern
            if len(set(str(v) for v in values)) == 1:
                pattern[key] = values[0]
        
        return pattern
    
    def _compress_instances(self, decisions: List[Dict[str, Any]], 
                          pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compress decision instances by removing pattern data."""
        compressed_instances = []
        
        for decision in decisions:
            instance = {}
            for key, value in decision.items():
                # Only store values that differ from pattern
                if key not in pattern or pattern[key] != value:
                    instance[key] = value
            compressed_instances.append(instance)
        
        return compressed_instances
    
    def decompress_decisions(self, compressed: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decompress decision tree back to list format.
        
        Args:
            compressed: Compressed decision tree
            
        Returns:
            List of decompressed decisions
        """
        if not compressed:
            return []
        
        decisions = []
        timeline = compressed.get('timeline', [])
        types_data = compressed.get('types', {})
        
        # Build decision index
        decision_index = {}
        
        for decision_type, type_data in types_data.items():
            pattern = type_data.get('pattern', {})
            instances = type_data.get('instances', [])
            
            for instance in instances:
                # Merge pattern with instance data
                decision = pattern.copy()
                decision.update(instance)
                decision['decision_type'] = decision_type
                
                # Find position in timeline
                for idx, d_type, timestamp in timeline:
                    if d_type == decision_type and timestamp == decision.get('timestamp'):
                        decision_index[idx] = decision
                        break
        
        # Rebuild ordered list
        for idx in sorted(decision_index.keys()):
            decisions.append(decision_index[idx])
            
        return decisions
    
    def analyze_patterns(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze decision patterns for compression insights.
        
        Args:
            decisions: Decisions to analyze
            
        Returns:
            Pattern analysis results
        """
        if not decisions:
            return {
                'total_decisions': 0,
                'unique_types': 0,
                'pattern_score': 0,
                'recommendations': []
            }
        
        # Count decision types
        type_counts = Counter(d.get('decision_type') for d in decisions)
        total = len(decisions)
        
        # Calculate pattern score (higher = more repetitive)
        pattern_score = 0
        for count in type_counts.values():
            pattern_score += (count / total) ** 2
        
        analysis = {
            'total_decisions': total,
            'unique_types': len(type_counts),
            'pattern_score': pattern_score,
            'type_distribution': dict(type_counts),
            'recommendations': []
        }
        
        # Add recommendations
        if pattern_score > 0.5:
            analysis['recommendations'].append(
                "High pattern score - decision tree compression recommended"
            )
        
        if len(type_counts) < total * 0.1:
            analysis['recommendations'].append(
                "Low type diversity - good compression candidate"
            )
        
        return analysis