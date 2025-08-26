#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/metrics/understanding_analyzer.py
🎯 PURPOSE: Analyze depth and quality of Claude's understanding
🔗 IMPORTS: collections, dataclasses, datetime, numpy
📤 EXPORTS: UnderstandingDepthAnalyzer, UnderstandingMetrics
🔄 PATTERN: Graph analysis for understanding connections
📝 TODOS: Add semantic similarity analysis

💡 AI HINT: Measures how well Claude understands the codebase
⚠️ NEVER: Overestimate understanding depth
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Any, Set, Optional
from collections import defaultdict
import numpy as np

import logging
logger = logging.getLogger(__name__)


@dataclass
class UnderstandingMetrics:
    """Metrics for understanding depth analysis."""
    depth_score: float
    breadth_score: float
    connection_density: float
    concept_count: int
    hub_nodes: List[Dict[str, Any]]
    isolated_nodes: List[str]
    understanding_gaps: List[str]
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'depth_score': self.depth_score,
            'breadth_score': self.breadth_score,
            'connection_density': self.connection_density,
            'concept_count': self.concept_count,
            'hub_nodes': self.hub_nodes,
            'isolated_nodes': self.isolated_nodes,
            'understanding_gaps': self.understanding_gaps,
            'confidence': self.confidence
        }


class UnderstandingDepthAnalyzer:
    """Analyzes depth and quality of understanding."""
    
    def __init__(self):
        """Initialize understanding analyzer."""
        self.min_connections_for_hub = 3
        self.depth_weights = {
            'module': 1.0,
            'class': 0.8,
            'function': 0.6,
            'variable': 0.4,
            'concept': 0.7
        }
    
    def analyze_understanding(self, understanding_graph: Dict[str, Any]) -> UnderstandingMetrics:
        """
        Analyze understanding depth from graph.
        
        Args:
            understanding_graph: Graph of understanding nodes
            
        Returns:
            Understanding metrics
        """
        if not understanding_graph:
            return UnderstandingMetrics(
                depth_score=0.0,
                breadth_score=0.0,
                connection_density=0.0,
                concept_count=0,
                hub_nodes=[],
                isolated_nodes=[],
                understanding_gaps=['No understanding graph available'],
                confidence=0.0
            )
        
        # Calculate basic metrics
        concept_count = len(understanding_graph)
        
        # Analyze connectivity
        connectivity_analysis = self._analyze_connectivity(understanding_graph)
        
        # Calculate depth score
        depth_score = self._calculate_depth_score(understanding_graph)
        
        # Calculate breadth score
        breadth_score = self._calculate_breadth_score(understanding_graph)
        
        # Identify understanding gaps
        understanding_gaps = self._identify_gaps(understanding_graph, connectivity_analysis)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            concept_count,
            connectivity_analysis['density'],
            len(understanding_gaps)
        )
        
        return UnderstandingMetrics(
            depth_score=depth_score,
            breadth_score=breadth_score,
            connection_density=connectivity_analysis['density'],
            concept_count=concept_count,
            hub_nodes=connectivity_analysis['hubs'],
            isolated_nodes=connectivity_analysis['isolated'],
            understanding_gaps=understanding_gaps,
            confidence=confidence
        )
    
    def _analyze_connectivity(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze graph connectivity."""
        connection_counts = defaultdict(int)
        all_connections = set()
        
        # Count connections
        for node_id, node_data in graph.items():
            connections = node_data.get('connections', [])
            connection_counts[node_id] = len(connections)
            
            for target in connections:
                all_connections.add((node_id, target))
        
        # Find hubs (highly connected nodes)
        hubs = []
        for node_id, count in connection_counts.items():
            if count >= self.min_connections_for_hub:
                hubs.append({
                    'id': node_id,
                    'name': graph[node_id].get('name', 'unknown'),
                    'type': graph[node_id].get('node_type', 'unknown'),
                    'connections': count
                })
        
        # Sort hubs by connection count
        hubs.sort(key=lambda x: x['connections'], reverse=True)
        
        # Find isolated nodes
        isolated = [
            node_id for node_id, count in connection_counts.items()
            if count == 0
        ]
        
        # Calculate density
        max_connections = len(graph) * (len(graph) - 1)
        density = len(all_connections) / max_connections if max_connections > 0 else 0
        
        return {
            'density': density,
            'hubs': hubs[:10],  # Top 10 hubs
            'isolated': isolated,
            'total_connections': len(all_connections)
        }
    
    def _calculate_depth_score(self, graph: Dict[str, Any]) -> float:
        """Calculate understanding depth score."""
        if not graph:
            return 0.0
        
        depth_scores = []
        
        for node_data in graph.values():
            node_type = node_data.get('node_type', 'unknown')
            base_weight = self.depth_weights.get(node_type, 0.5)
            
            # Adjust weight based on node attributes
            understanding_level = node_data.get('understanding_level', 0.5)
            confidence = node_data.get('confidence', 0.5)
            connections = len(node_data.get('connections', []))
            
            # More connections indicate deeper understanding
            connection_factor = min(1.0, connections / 5)
            
            node_score = base_weight * understanding_level * confidence * (0.7 + 0.3 * connection_factor)
            depth_scores.append(node_score)
        
        return np.mean(depth_scores) if depth_scores else 0.0
    
    def _calculate_breadth_score(self, graph: Dict[str, Any]) -> float:
        """Calculate understanding breadth score."""
        if not graph:
            return 0.0
        
        # Count different types of nodes
        type_counts = defaultdict(int)
        for node_data in graph.values():
            node_type = node_data.get('node_type', 'unknown')
            type_counts[node_type] += 1
        
        # Breadth is about diversity
        type_diversity = len(type_counts) / 10  # Assume 10 possible types
        
        # Also consider coverage across different modules/areas
        module_set = set()
        for node_data in graph.values():
            if 'module' in node_data:
                module_set.add(node_data['module'])
        
        module_diversity = min(1.0, len(module_set) / 20)  # Assume 20 modules is good coverage
        
        # Consider total number of concepts
        size_factor = min(1.0, len(graph) / 100)  # 100 concepts is good breadth
        
        breadth_score = (type_diversity * 0.3 + module_diversity * 0.4 + size_factor * 0.3)
        
        return breadth_score
    
    def _identify_gaps(self, graph: Dict[str, Any], 
                      connectivity: Dict[str, Any]) -> List[str]:
        """Identify gaps in understanding."""
        gaps = []
        
        # Isolated nodes indicate gaps
        if connectivity['isolated']:
            gaps.append(f"{len(connectivity['isolated'])} isolated concepts need connection")
        
        # Low density indicates missing connections
        if connectivity['density'] < 0.1:
            gaps.append("Low connection density - many relationships missing")
        
        # Check for missing node types
        existing_types = {node.get('node_type') for node in graph.values()}
        expected_types = {'module', 'class', 'function', 'variable', 'concept'}
        missing_types = expected_types - existing_types
        
        if missing_types:
            gaps.append(f"Missing understanding of: {', '.join(missing_types)}")
        
        # Check for nodes with low confidence
        low_confidence = [
            node_id for node_id, node_data in graph.items()
            if node_data.get('confidence', 1.0) < 0.5
        ]
        
        if low_confidence:
            gaps.append(f"{len(low_confidence)} concepts have low confidence")
        
        return gaps
    
    def _calculate_confidence(self, concept_count: int, density: float,
                            gap_count: int) -> float:
        """Calculate confidence in understanding assessment."""
        # More concepts = higher confidence
        count_factor = min(1.0, concept_count / 50)
        
        # Good density = higher confidence
        density_factor = min(1.0, density * 5)  # 0.2 density is good
        
        # Fewer gaps = higher confidence
        gap_factor = max(0.0, 1.0 - (gap_count / 5))
        
        confidence = (count_factor * 0.4 + density_factor * 0.3 + gap_factor * 0.3)
        
        return confidence
    
    def compare_understanding(self, before: Dict[str, Any], 
                            after: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare understanding between two states.
        
        Args:
            before: Previous understanding graph
            after: Current understanding graph
            
        Returns:
            Comparison results
        """
        before_metrics = self.analyze_understanding(before)
        after_metrics = self.analyze_understanding(after)
        
        return {
            'depth_change': after_metrics.depth_score - before_metrics.depth_score,
            'breadth_change': after_metrics.breadth_score - before_metrics.breadth_score,
            'density_change': after_metrics.connection_density - before_metrics.connection_density,
            'concept_growth': after_metrics.concept_count - before_metrics.concept_count,
            'new_hubs': [
                hub for hub in after_metrics.hub_nodes
                if hub['id'] not in {h['id'] for h in before_metrics.hub_nodes}
            ],
            'resolved_gaps': [
                gap for gap in before_metrics.understanding_gaps
                if gap not in after_metrics.understanding_gaps
            ],
            'improvement_score': (
                (after_metrics.depth_score - before_metrics.depth_score) * 0.5 +
                (after_metrics.breadth_score - before_metrics.breadth_score) * 0.3 +
                (after_metrics.connection_density - before_metrics.connection_density) * 0.2
            )
        }