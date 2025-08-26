#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/compression/graph_compression.py
🎯 PURPOSE: Graph compression for understanding networks
🔗 IMPORTS: typing
📤 EXPORTS: GraphCompressor
🔄 PATTERN: Adjacency list optimization for graph storage
📝 TODOS: Add graph-specific compression algorithms (e.g., WebGraph)

💡 AI HINT: Compresses graph structures while preserving connectivity
⚠️ NEVER: Lose graph topology information during compression
"""

"""
CORA - Claude Operational Research Assistant
Graph Compression Module

Implements graph compression techniques for efficiently storing
understanding graph networks using adjacency list optimization
and property compression.

Author: CORA Team
Version: 1.0.0
"""

from typing import Dict, Any, List, Set


class GraphCompressor:
    """Compresses understanding graph networks."""
    
    def __init__(self, edge_threshold: float = 0.1):
        """
        Initialize graph compressor.
        
        Args:
            edge_threshold: Minimum edge weight to preserve
        """
        self.edge_threshold = edge_threshold
        
    def compress_graph(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress understanding graph using adjacency list optimization.
        
        Args:
            graph: Understanding graph to compress
            
        Returns:
            Compressed graph representation
        """
        if not graph:
            return {}
            
        # Extract nodes and edges
        nodes = []
        edges = []
        node_index = {}
        
        for idx, (node_id, node_data) in enumerate(graph.items()):
            node_index[node_id] = idx
            nodes.append({
                'id': node_id,
                'type': node_data.get('node_type', ''),
                'name': node_data.get('name', ''),
                'props': self._compress_properties(node_data.get('properties', {}))
            })
        
        # Build edge list
        for node_id, node_data in graph.items():
            src_idx = node_index[node_id]
            for connection in node_data.get('connections', []):
                if connection in node_index:
                    dst_idx = node_index[connection]
                    edges.append([src_idx, dst_idx])
        
        return {
            'nodes': nodes,
            'edges': edges,
            'index': node_index
        }
    
    def _compress_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Compress node properties by removing redundant data."""
        compressed = {}
        
        for key, value in properties.items():
            # Skip large or redundant values
            if isinstance(value, str) and len(value) > 100:
                compressed[key] = value[:100] + f"...[{len(value)}]"
            elif isinstance(value, list) and len(value) > 10:
                compressed[key] = value[:10] + [f"...[+{len(value)-10}]"]
            else:
                compressed[key] = value
                
        return compressed
    
    def decompress_graph(self, compressed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decompress graph back to original format.
        
        Args:
            compressed: Compressed graph representation
            
        Returns:
            Decompressed understanding graph
        """
        if not compressed:
            return {}
            
        graph = {}
        nodes = compressed.get('nodes', [])
        edges = compressed.get('edges', [])
        
        # Rebuild nodes
        for node in nodes:
            node_id = node['id']
            graph[node_id] = {
                'node_id': node_id,
                'node_type': node['type'],
                'name': node['name'],
                'properties': node['props'],
                'connections': set()
            }
        
        # Rebuild edges
        for src_idx, dst_idx in edges:
            if src_idx < len(nodes) and dst_idx < len(nodes):
                src_id = nodes[src_idx]['id']
                dst_id = nodes[dst_idx]['id']
                graph[src_id]['connections'].add(dst_id)
        
        # Convert sets back to lists for serialization
        for node_id in graph:
            graph[node_id]['connections'] = list(graph[node_id]['connections'])
        
        return graph
    
    def analyze_graph_structure(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze graph structure for compression insights.
        
        Args:
            graph: Graph to analyze
            
        Returns:
            Analysis results
        """
        if not graph:
            return {
                'node_count': 0,
                'edge_count': 0,
                'avg_degree': 0,
                'connectivity': 0
            }
        
        node_count = len(graph)
        edge_count = sum(len(node.get('connections', [])) for node in graph.values())
        avg_degree = edge_count / node_count if node_count > 0 else 0
        
        # Calculate connectivity (ratio of actual to possible edges)
        max_edges = node_count * (node_count - 1)
        connectivity = edge_count / max_edges if max_edges > 0 else 0
        
        return {
            'node_count': node_count,
            'edge_count': edge_count,
            'avg_degree': avg_degree,
            'connectivity': connectivity,
            'is_sparse': connectivity < 0.1,
            'compression_suitable': connectivity < 0.3
        }