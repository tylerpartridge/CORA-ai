#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/snapshot_compressor.py
🎯 PURPOSE: Multi-stage compression pipeline for state snapshots
🔗 IMPORTS: json, logging, pathlib, typing, compression modules
📤 EXPORTS: SnapshotCompressor, integrate_with_state_tracker
🔄 PATTERN: Pipeline pattern for compression stages
📝 TODOS: Add parallel compression support

💡 AI HINT: Orchestrates multi-stage compression pipeline
⚠️ NEVER: Skip compression integrity verification
"""

"""
CORA - Claude Operational Research Assistant
Snapshot Compressor Module

Main orchestrator for the multi-stage compression pipeline,
coordinating semantic deduplication, graph compression,
decision tree compression, and binary compression.

Author: CORA Team
Version: 1.0.0
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone

# Import compression modules
from modules.compression.semantic_dedup import SemanticDeduplicator
from modules.compression.graph_compression import GraphCompressor
from modules.compression.binary_compression import (
    BinaryCompressor, CompressionAlgorithm
)
from modules.compression.compression_utils import (
    DecisionTreeCompressor, CompressionMetrics, CompressionStage
)

# Configure logging
logger = logging.getLogger(__name__)


class SnapshotCompressor:
    """Main snapshot compression orchestrator."""
    
    def __init__(self, target_ratio: float = 0.7,
                 compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB):
        """
        Initialize snapshot compressor.
        
        Args:
            target_ratio: Target compression ratio (0.7 = 70% compression)
            compression_algorithm: Binary compression algorithm to use
        """
        self.target_ratio = target_ratio
        self.semantic_dedup = SemanticDeduplicator()
        self.graph_compressor = GraphCompressor()
        self.decision_compressor = DecisionTreeCompressor()
        self.binary_compressor = BinaryCompressor(compression_algorithm)
        
        logger.info(f"Initialized SnapshotCompressor with target ratio: {target_ratio}")
    
    def compress(self, session_state: Dict[str, Any]) -> Tuple[bytes, CompressionMetrics]:
        """
        Compress session state through multi-stage pipeline.
        
        Args:
            session_state: Session state dictionary to compress
            
        Returns:
            Tuple of (compressed_bytes, metrics)
        """
        start_time = time.time()
        
        # Track metrics
        original_size = len(json.dumps(session_state).encode())
        stage_metrics = {}
        
        # Stage 1: Semantic deduplication
        stage1_start = time.time()
        deduplicated, ref_map = self.semantic_dedup.deduplicate(
            session_state.get('metadata', {})
        )
        stage1_size = len(json.dumps({'dedup': deduplicated, 'refs': ref_map}).encode())
        stage_metrics[CompressionStage.SEMANTIC_DEDUP.value] = {
            'size': stage1_size,
            'ratio': 1 - (stage1_size / original_size) if original_size > 0 else 0,
            'time': time.time() - stage1_start
        }
        
        # Stage 2: Graph compression
        stage2_start = time.time()
        compressed_graph = self.graph_compressor.compress_graph(
            session_state.get('understanding_graph', {})
        )
        graph_original = len(json.dumps(session_state.get('understanding_graph', {})).encode())
        stage2_size = len(json.dumps(compressed_graph).encode())
        stage_metrics[CompressionStage.GRAPH_COMPRESS.value] = {
            'size': stage2_size,
            'ratio': 1 - (stage2_size / graph_original) if graph_original > 0 else 0,
            'time': time.time() - stage2_start
        }
        
        # Stage 3: Decision tree compression
        stage3_start = time.time()
        compressed_decisions = self.decision_compressor.compress_decisions(
            session_state.get('decisions_made', [])
        )
        decisions_original = len(json.dumps(session_state.get('decisions_made', [])).encode())
        stage3_size = len(json.dumps(compressed_decisions).encode())
        stage_metrics[CompressionStage.DECISION_TREE.value] = {
            'size': stage3_size,
            'ratio': 1 - (stage3_size / decisions_original) if decisions_original > 0 else 0,
            'time': time.time() - stage3_start
        }
        
        # Build compressed state
        compressed_state = {
            'session_id': session_state.get('session_id'),
            'start_time': session_state.get('start_time'),
            'last_activity': session_state.get('last_activity'),
            'files_touched': list(session_state.get('files_touched', [])),
            'compressed_graph': compressed_graph,
            'compressed_decisions': compressed_decisions,
            'deduplicated_metadata': deduplicated,
            'reference_map': ref_map,
            'context_tokens_used': session_state.get('context_tokens_used', 0),
            'total_tokens_used': session_state.get('total_tokens_used', 0),
            'checkpoints': session_state.get('checkpoints', [])
        }
        
        # Stage 4: Binary compression
        stage4_start = time.time()
        compression_result = self.binary_compressor.compress(compressed_state)
        compressed_bytes = compression_result.compressed_data
        compressed_size = compression_result.compressed_size
        stage_metrics[CompressionStage.BINARY_COMPRESS.value] = {
            'size': compressed_size,
            'ratio': compression_result.compression_ratio,
            'time': time.time() - stage4_start,
            'algorithm': compression_result.algorithm.value
        }
        
        # Calculate overall metrics
        compression_ratio = 1 - (compressed_size / original_size) if original_size > 0 else 0
        compression_time = time.time() - start_time
        
        metrics = CompressionMetrics(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            stage_metrics=stage_metrics,
            compression_time=compression_time,
            decompression_time=0.0  # Will be set during decompression
        )
        
        logger.info(f"Compression complete: {compression_ratio:.2%} ratio, "
                   f"{original_size} -> {compressed_size} bytes")
        
        return compressed_bytes, metrics
    
    def decompress(self, compressed_bytes: bytes) -> Tuple[Dict[str, Any], CompressionMetrics]:
        """
        Decompress session state from compressed bytes.
        
        Args:
            compressed_bytes: Compressed state bytes
            
        Returns:
            Tuple of (decompressed_state, metrics)
        """
        start_time = time.time()
        
        # Stage 4 reverse: Binary decompression
        # Try each algorithm if we don't know which was used
        decompressed = None
        for algorithm in CompressionAlgorithm:
            try:
                decompressed = self.binary_compressor.decompress(compressed_bytes, algorithm)
                break
            except:
                continue
        
        if decompressed is None:
            raise ValueError("Failed to decompress data with any known algorithm")
        
        import pickle
        compressed_state = pickle.loads(decompressed)
        
        # Stage 3 reverse: Decision tree decompression
        decisions = self.decision_compressor.decompress_decisions(
            compressed_state.get('compressed_decisions', {})
        )
        
        # Stage 2 reverse: Graph decompression
        graph = self.graph_compressor.decompress_graph(
            compressed_state.get('compressed_graph', {})
        )
        
        # Stage 1 reverse: Semantic deduplication restoration
        metadata = self.semantic_dedup.restore(
            compressed_state.get('deduplicated_metadata', {}),
            compressed_state.get('reference_map', {})
        )
        
        # Rebuild full state
        session_state = {
            'session_id': compressed_state.get('session_id'),
            'start_time': compressed_state.get('start_time'),
            'last_activity': compressed_state.get('last_activity'),
            'files_touched': set(compressed_state.get('files_touched', [])),
            'decisions_made': decisions,
            'understanding_graph': graph,
            'metadata': metadata,
            'context_tokens_used': compressed_state.get('context_tokens_used', 0),
            'total_tokens_used': compressed_state.get('total_tokens_used', 0),
            'checkpoints': compressed_state.get('checkpoints', [])
        }
        
        decompression_time = time.time() - start_time
        
        # Create metrics (convert sets to lists for JSON serialization)
        session_state_serializable = session_state.copy()
        if 'files_touched' in session_state_serializable and isinstance(session_state_serializable['files_touched'], set):
            session_state_serializable['files_touched'] = list(session_state_serializable['files_touched'])
        original_size = len(json.dumps(session_state_serializable).encode())
        metrics = CompressionMetrics(
            original_size=original_size,
            compressed_size=len(compressed_bytes),
            compression_ratio=1 - (len(compressed_bytes) / original_size) if original_size > 0 else 0,
            stage_metrics={},
            compression_time=0.0,
            decompression_time=decompression_time
        )
        
        logger.info(f"Decompression complete in {decompression_time:.2f}s")
        
        return session_state, metrics
    
    def compress_to_file(self, session_state: Dict[str, Any], 
                        output_path: Path) -> CompressionMetrics:
        """
        Compress session state and save to file.
        
        Args:
            session_state: Session state to compress
            output_path: Path to save compressed file
            
        Returns:
            Compression metrics
        """
        compressed_bytes, metrics = self.compress(session_state)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(compressed_bytes)
        
        logger.info(f"Saved compressed snapshot to: {output_path}")
        return metrics
    
    def decompress_from_file(self, input_path: Path) -> Tuple[Dict[str, Any], CompressionMetrics]:
        """
        Load and decompress session state from file.
        
        Args:
            input_path: Path to compressed file
            
        Returns:
            Tuple of (session_state, metrics)
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Compressed file not found: {input_path}")
        
        compressed_bytes = input_path.read_bytes()
        return self.decompress(compressed_bytes)
    
    def analyze_compression_potential(self, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze potential compression gains for session state.
        
        Args:
            session_state: Session state to analyze
            
        Returns:
            Analysis results with recommendations
        """
        from collections import Counter
        
        analysis = {
            'total_size': len(json.dumps(session_state).encode()),
            'component_sizes': {},
            'redundancy_score': 0.0,
            'recommendations': []
        }
        
        # Analyze each component
        for component in ['metadata', 'understanding_graph', 'decisions_made', 'files_touched']: