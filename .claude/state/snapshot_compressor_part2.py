# Generated: 2025-07-11 by SmartHeaderGenerator v1.0
"""
🧭 LOCATION: CORA/.claude/state/snapshot_compressor_part2.py
🎯 PURPOSE: [Auto-generated header - could not analyze file]
🔗 IMPORTS: [Unknown]
📤 EXPORTS: [Unknown]
🔄 PATTERN: [Unknown]
📝 TODOS: [Unknown]
💡 AI HINT: [Unknown]
⚠️ NEVER: [Unknown]
"""

🧭 LOCATION: /CORA/.claude\state\snapshot_compressor_part2.py
🎯 PURPOSE: [To be determined - please update]
🔗 IMPORTS: [To be determined - please update]
📤 EXPORTS: [To be determined - please update]
🔄 PATTERN: [To be determined - please update]
📝 TODOS: [To be determined - please update]
"""

            if component in session_state:
                component_data = session_state[component]
                component_size = len(json.dumps(component_data).encode())
                analysis['component_sizes'][component] = {
                    'size': component_size,
                    'percentage': (component_size / analysis['total_size'] * 100) if analysis['total_size'] > 0 else 0
                }
        
        # Analyze graph structure
        if 'understanding_graph' in session_state:
            graph_analysis = self.graph_compressor.analyze_graph_structure(
                session_state['understanding_graph']
            )
            if graph_analysis.get('compression_suitable'):
                analysis['recommendations'].append(
                    f"Graph structure suitable for compression (connectivity: {graph_analysis['connectivity']:.2%})"
                )
        
        # Analyze decision patterns
        if 'decisions_made' in session_state:
            pattern_analysis = self.decision_compressor.analyze_patterns(
                session_state['decisions_made']
            )
            if pattern_analysis['pattern_score'] > 0.3:
                analysis['recommendations'].append(
                    f"Decision patterns detected (score: {pattern_analysis['pattern_score']:.2f}) - compression recommended"
                )
        
        # Overall recommendation
        if analysis['total_size'] > 100000:  # 100KB
            analysis['recommendations'].append(
                f"Large state size ({analysis['total_size']} bytes) - compression highly recommended"
            )
        
        return analysis


def integrate_with_state_tracker():
    """
    Factory function to create CompressedSessionTracker class.
    
    Returns:
        CompressedSessionTracker class for integration
    """
    try:
        from claude_state_tracker import ClaudeSessionTracker, SessionState
    except ImportError:
        logger.warning("ClaudeSessionTracker not available for integration")
        return None
    
    class CompressedSessionTracker(ClaudeSessionTracker):
        """Extended session tracker with compression support."""
        
        def __init__(self, state_dir: Path, max_context_tokens: int = 200000):
            super().__init__(state_dir, max_context_tokens)
            self.compressor = SnapshotCompressor()
            self.compressed_dir = self.state_dir / "compressed"
            self.compressed_dir.mkdir(exist_ok=True)
        
        def create_compressed_checkpoint(self, checkpoint_name: Optional[str] = None) -> Tuple[str, CompressionMetrics]:
            """Create a compressed checkpoint."""
            if not self.current_session:
                raise RuntimeError("No active session")
            
            checkpoint_id = checkpoint_name or f"compressed_{int(time.time())}"
            checkpoint_path = self.compressed_dir / f"{self.current_session.session_id}_{checkpoint_id}.cmp"
            
            # Convert session to dict and compress
            session_dict = self.current_session.to_dict()
            metrics = self.compressor.compress_to_file(session_dict, checkpoint_path)
            
            # Record checkpoint
            self.current_session.checkpoints.append(checkpoint_id)
            
            logger.info(f"Created compressed checkpoint: {checkpoint_id} "
                       f"(compression ratio: {metrics.compression_ratio:.2%})")
            
            return checkpoint_id, metrics
        
        def restore_compressed_checkpoint(self, session_id: str, checkpoint_id: str) -> SessionState:
            """Restore from compressed checkpoint."""
            checkpoint_path = self.compressed_dir / f"{session_id}_{checkpoint_id}.cmp"
            
            # Decompress and restore
            session_dict, metrics = self.compressor.decompress_from_file(checkpoint_path)
            self.current_session = SessionState.from_dict(session_dict)
            
            logger.info(f"Restored compressed checkpoint: {checkpoint_id}")
            return self.current_session
    
    return CompressedSessionTracker


# Simplified interface for direct usage
def compress_snapshot(snapshot_data: Dict[str, Any]) -> bytes:
    """Simple interface to compress a snapshot."""
    compressor = SnapshotCompressor()
    compressed_bytes, _ = compressor.compress(snapshot_data)
    return compressed_bytes


def decompress_snapshot(compressed_data: bytes) -> Dict[str, Any]:
    """Simple interface to decompress a snapshot."""
    compressor = SnapshotCompressor()
    decompressed_data, _ = compressor.decompress(compressed_data)
    return decompressed_data