# Generated: 2025-07-11 by SmartHeaderGenerator v1.0
"""
🧭 LOCATION: CORA/.claude/state/claude_state_tracker_part2.py
🎯 PURPOSE: [Auto-generated header - could not analyze file]
🔗 IMPORTS: [Unknown]
📤 EXPORTS: [Unknown]
🔄 PATTERN: [Unknown]
📝 TODOS: [Unknown]
💡 AI HINT: [Unknown]
⚠️ NEVER: [Unknown]
"""

🧭 LOCATION: /CORA/.claude\state\claude_state_tracker_part2.py
🎯 PURPOSE: [To be determined - please update]
🔗 IMPORTS: [To be determined - please update]
📤 EXPORTS: [To be determined - please update]
🔄 PATTERN: [To be determined - please update]
📝 TODOS: [To be determined - please update]
"""

            node: The understanding node to add
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        self.current_session.understanding_graph[node.node_id] = node
        self.current_session.last_activity = datetime.now(timezone.utc)
        
        logger.debug(f"Added understanding node: {node.node_id} ({node.node_type})")
    
    def connect_nodes(self, node_id1: str, node_id2: str, bidirectional: bool = True) -> None:
        """
        Create a connection between two nodes in the understanding graph.
        
        Args:
            node_id1: First node ID
            node_id2: Second node ID
            bidirectional: Whether the connection is bidirectional
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        graph = self.current_session.understanding_graph
        
        if node_id1 in graph and node_id2 in graph:
            graph[node_id1].connections.add(node_id2)
            if bidirectional:
                graph[node_id2].connections.add(node_id1)
            
            logger.debug(f"Connected nodes: {node_id1} <-> {node_id2}")
    
    def update_token_usage(self, context_tokens: int, total_tokens: int) -> None:
        """
        Update token usage statistics.
        
        Args:
            context_tokens: Tokens used in current context
            total_tokens: Total tokens used in session
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        self.current_session.context_tokens_used = context_tokens
        self.current_session.total_tokens_used = total_tokens
        self.current_session.last_activity = datetime.now(timezone.utc)
        
        # Update context utilization metric
        self.metrics.context_utilization = min(1.0, context_tokens / self.max_context_tokens)
        
        logger.debug(f"Updated token usage: context={context_tokens}, total={total_tokens}")
    
    def create_checkpoint(self, checkpoint_name: Optional[str] = None) -> str:
        """
        Create a checkpoint of the current session state.
        
        Args:
            checkpoint_name: Optional name for the checkpoint
            
        Returns:
            The checkpoint ID
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        checkpoint_id = checkpoint_name or f"checkpoint_{int(time.time())}"
        checkpoint_path = self.checkpoint_dir / f"{self.current_session.session_id}_{checkpoint_id}.pkl.gz"
        
        # Serialize and compress the session state
        state_data = pickle.dumps(self.current_session)
        compressed_data = zlib.compress(state_data, level=9)
        
        checkpoint_path.write_bytes(compressed_data)
        
        # Record checkpoint in session
        self.current_session.checkpoints.append(checkpoint_id)
        
        logger.info(f"Created checkpoint: {checkpoint_id}")
        return checkpoint_id
    
    def restore_checkpoint(self, session_id: str, checkpoint_id: str) -> SessionState:
        """
        Restore a session from a checkpoint.
        
        Args:
            session_id: The session ID
            checkpoint_id: The checkpoint ID
            
        Returns:
            The restored session state
        """
        checkpoint_path = self.checkpoint_dir / f"{session_id}_{checkpoint_id}.pkl.gz"
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")
        
        # Decompress and deserialize
        compressed_data = checkpoint_path.read_bytes()
        state_data = zlib.decompress(compressed_data)
        self.current_session = pickle.loads(state_data)
        
        logger.info(f"Restored checkpoint: {checkpoint_id}")
        return self.current_session
    
    def calculate_awareness_metrics(self) -> AwarenessMetrics:
        """
        Calculate current awareness metrics.
        
        Returns:
            Current awareness metrics
        """
        if not self.current_session:
            return self.metrics
        
        # Context utilization already updated in update_token_usage
        
        # Understanding depth: based on graph size and connectivity
        graph = self.current_session.understanding_graph
        if graph:
            avg_connections = sum(len(n.connections) for n in graph.values()) / len(graph)
            self.metrics.understanding_depth = min(1.0, len(graph) / 100)  # Assume 100 nodes is deep
            self.metrics.graph_connectivity = min(1.0, avg_connections / 5)  # Assume 5 connections is well-connected
        
        # Decision confidence: average confidence of all decisions
        if self.current_session.decisions_made:
            total_confidence = sum(d.confidence for d in self.current_session.decisions_made)
            self.metrics.decision_confidence = total_confidence / len(self.current_session.decisions_made)
        
        # File coverage: estimate based on files touched
        # This is a rough estimate - in practice, you'd want to know total relevant files
        self.metrics.file_coverage = min(1.0, len(self.current_session.files_touched) / 50)
        
        # Memory pressure: combination of context utilization and session duration
        session_duration = (datetime.now(timezone.utc) - self.current_session.start_time).total_seconds()
        time_pressure = min(1.0, session_duration / 3600)  # 1 hour = full pressure
        self.metrics.memory_pressure = (self.metrics.context_utilization + time_pressure) / 2
        
        return self.metrics
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session.
        
        Returns:
            Session summary dictionary
        """
        if not self.current_session:
            return {"status": "no_active_session"}
        
        metrics = self.calculate_awareness_metrics()
        
        return {
            "session_id": self.current_session.session_id,
            "duration": (datetime.now(timezone.utc) - self.current_session.start_time).total_seconds(),
            "files_touched": len(self.current_session.files_touched),
            "decisions_made": len(self.current_session.decisions_made),
            "understanding_nodes": len(self.current_session.understanding_graph),
            "tokens_used": self.current_session.total_tokens_used,
            "checkpoints": len(self.current_session.checkpoints),
            "metrics": metrics.to_dict()
        }
    
    def save_session(self, file_path: Optional[Path] = None) -> Path:
        """
        Save the current session to disk.
        
        Args:
            file_path: Optional path to save the session
            
        Returns:
            Path where the session was saved
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        if file_path is None:
            file_path = self.state_dir / f"session_{self.current_session.session_id}.json"
        
        session_data = self.current_session.to_dict()
        
        with open(file_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"Saved session to: {file_path}")
        return file_path
    
    def load_session(self, file_path: Path) -> SessionState:
        """
        Load a session from disk.
        
        Args:
            file_path: Path to the session file
            
        Returns:
            The loaded session state
        """
        with open(file_path, 'r') as f:
            session_data = json.load(f)
        
        self.current_session = SessionState.from_dict(session_data)
        
        logger.info(f"Loaded session from: {file_path}")
        return self.current_session
    
    def browse_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Browse recent session history.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        session_files = sorted(
            self.state_dir.glob("session_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]
        
        sessions = []
        for file_path in session_files:
            try:
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                
                session = SessionState.from_dict(session_data)
                sessions.append({
                    "session_id": session.session_id,
                    "start_time": session.start_time.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "files_touched": len(session.files_touched),
                    "decisions_made": len(session.decisions_made),
                    "file_path": str(file_path)
                })
            except Exception as e:
                logger.error(f"Error loading session {file_path}: {e}")
        
        return sessions
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        hash_input = f"{timestamp}_{id(self)}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:12]


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create tracker
    tracker = ClaudeSessionTracker(Path(".claude/state"))
    
    # Start a session
    session = tracker.start_session()
    print(f"Started session: {session.session_id}")
    
    # Record some activity
    tracker.add_file_touch("/path/to/file.py", "read")
    tracker.add_file_touch("/path/to/another.py", "edit")
    
    # Add a decision
    decision = Decision(
        decision_type=DecisionType.FILE_EDIT,
        description="Refactored authentication module",
        timestamp=datetime.now(timezone.utc),
        context={"reason": "improve code readability"},
        confidence=0.9
    )
    tracker.add_decision(decision)
    
    # Update token usage
    tracker.update_token_usage(50000, 75000)
    
    # Create a checkpoint
    checkpoint_id = tracker.create_checkpoint("after_refactor")
    print(f"Created checkpoint: {checkpoint_id}")