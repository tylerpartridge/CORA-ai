"""
🧭 LOCATION: /CORA/.claude/state/modules/compression/__init__.py
🎯 PURPOSE: Compression modules for state snapshot optimization
🔗 IMPORTS: SemanticDeduplicator, GraphCompressor, BinaryCompressor, CompressionAlgorithm, CompressionResult, DecisionTreeCompressor, CompressionMetrics, CompressionStage
📤 EXPORTS: All compression-related classes and utilities
🔄 PATTERN: Modular compression system with multiple strategies
📝 TODOS: None

💡 AI HINT: These modules compress Claude's state snapshots for efficiency
⚠️ NEVER: Don't use compression that loses critical semantic information

CORA Compression Modules Package

Provides modular compression components for state snapshot compression.
"""

from .semantic_dedup import SemanticDeduplicator
from .graph_compression import GraphCompressor
from .binary_compression import BinaryCompressor, CompressionAlgorithm, CompressionResult
from .compression_utils import (
    DecisionTreeCompressor, 
    CompressionMetrics, 
    CompressionStage
)

__all__ = [
    'SemanticDeduplicator',
    'GraphCompressor',
    'BinaryCompressor',
    'CompressionAlgorithm',
    'CompressionResult',
    'DecisionTreeCompressor',
    'CompressionMetrics',
    'CompressionStage'
]