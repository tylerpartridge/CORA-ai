#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/compression/binary_compression.py
🎯 PURPOSE: Binary compression methods for final stage compression
🔗 IMPORTS: zlib, pickle, gzip, bz2, lzma
📤 EXPORTS: BinaryCompressor, CompressionAlgorithm
🔄 PATTERN: Strategy pattern for compression algorithms
📝 TODOS: Add LZ4 support for faster compression, benchmark algorithms

💡 AI HINT: Final stage compression using various binary algorithms
⚠️ NEVER: Use compression without verifying decompression integrity
"""

"""
CORA - Claude Operational Research Assistant
Binary Compression Module

Implements various binary compression algorithms for the final
stage of the compression pipeline, with support for multiple
compression strategies and benchmarking.

Author: CORA Team
Version: 1.0.0
"""

import zlib
import gzip
import bz2
import lzma
import pickle
from enum import Enum
from typing import Any, Dict, Tuple, Optional
from dataclasses import dataclass
import time


class CompressionAlgorithm(Enum):
    """Available compression algorithms."""
    ZLIB = "zlib"
    GZIP = "gzip"
    BZ2 = "bz2"
    LZMA = "lzma"


@dataclass
class CompressionResult:
    """Result of compression operation."""
    compressed_data: bytes
    algorithm: CompressionAlgorithm
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float


class BinaryCompressor:
    """Handles binary compression with multiple algorithm support."""
    
    def __init__(self, default_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB):
        """
        Initialize binary compressor.
        
        Args:
            default_algorithm: Default compression algorithm to use
        """
        self.default_algorithm = default_algorithm
        self.compression_levels = {
            CompressionAlgorithm.ZLIB: 9,
            CompressionAlgorithm.GZIP: 9,
            CompressionAlgorithm.BZ2: 9,
            CompressionAlgorithm.LZMA: 6  # LZMA is slower, use moderate level
        }
    
    def compress(self, data: Any, 
                 algorithm: Optional[CompressionAlgorithm] = None) -> CompressionResult:
        """
        Compress data using specified algorithm.
        
        Args:
            data: Data to compress (will be pickled if not bytes)
            algorithm: Compression algorithm to use (defaults to self.default_algorithm)
            
        Returns:
            CompressionResult with compressed data and metrics
        """
        algorithm = algorithm or self.default_algorithm
        start_time = time.time()
        
        # Serialize data if needed
        if not isinstance(data, bytes):
            data = pickle.dumps(data)
        
        original_size = len(data)
        
        # Compress based on algorithm
        if algorithm == CompressionAlgorithm.ZLIB:
            compressed = zlib.compress(data, level=self.compression_levels[algorithm])
        elif algorithm == CompressionAlgorithm.GZIP:
            compressed = gzip.compress(data, compresslevel=self.compression_levels[algorithm])
        elif algorithm == CompressionAlgorithm.BZ2:
            compressed = bz2.compress(data, compresslevel=self.compression_levels[algorithm])
        elif algorithm == CompressionAlgorithm.LZMA:
            compressed = lzma.compress(data, preset=self.compression_levels[algorithm])
        else:
            raise ValueError(f"Unknown compression algorithm: {algorithm}")
        
        compressed_size = len(compressed)
        compression_time = time.time() - start_time
        compression_ratio = 1 - (compressed_size / original_size)
        
        return CompressionResult(
            compressed_data=compressed,
            algorithm=algorithm,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compression_time=compression_time
        )
    
    def decompress(self, compressed_data: bytes, 
                   algorithm: CompressionAlgorithm) -> bytes:
        """
        Decompress data using specified algorithm.
        
        Args:
            compressed_data: Compressed data bytes
            algorithm: Algorithm used for compression
            
        Returns:
            Decompressed data bytes
        """
        if algorithm == CompressionAlgorithm.ZLIB:
            return zlib.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.BZ2:
            return bz2.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.LZMA:
            return lzma.decompress(compressed_data)
        else:
            raise ValueError(f"Unknown compression algorithm: {algorithm}")
    
    def benchmark_algorithms(self, data: Any) -> Dict[str, CompressionResult]:
        """
        Benchmark all available compression algorithms on data.
        
        Args:
            data: Data to compress
            
        Returns:
            Dictionary mapping algorithm names to compression results
        """
        results = {}
        
        for algorithm in CompressionAlgorithm:
            try:
                result = self.compress(data, algorithm)
                results[algorithm.value] = result
            except Exception as e:
                # Log error but continue benchmarking
                results[algorithm.value] = f"Error: {str(e)}"
        
        return results
    
    def select_best_algorithm(self, data: Any, 
                            optimize_for: str = "ratio") -> CompressionAlgorithm:
        """
        Select best algorithm based on optimization criteria.
        
        Args:
            data: Data to compress
            optimize_for: Optimization criteria ("ratio", "speed", "balanced")
            
        Returns:
            Best algorithm for the criteria
        """
        results = self.benchmark_algorithms(data)
        
        # Filter out errors
        valid_results = {
            alg: res for alg, res in results.items() 
            if isinstance(res, CompressionResult)
        }
        
        if not valid_results:
            return self.default_algorithm
        
        if optimize_for == "ratio":
            # Best compression ratio
            best = max(valid_results.items(), 
                      key=lambda x: x[1].compression_ratio)
        elif optimize_for == "speed":
            # Fastest compression
            best = min(valid_results.items(), 
                      key=lambda x: x[1].compression_time)
        else:  # balanced
            # Balance between ratio and speed
            best = max(valid_results.items(),
                      key=lambda x: x[1].compression_ratio / (1 + x[1].compression_time))
        
        return CompressionAlgorithm(best[0])