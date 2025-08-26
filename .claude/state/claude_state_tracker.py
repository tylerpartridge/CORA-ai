#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/claude_state_tracker.py
🎯 PURPOSE: Track Claude's working memory and session state with checkpointing
🔗 IMPORTS: json, logging, pickle, zlib, dataclasses, datetime, pathlib, hashlib
📤 EXPORTS: ClaudeStateTracker, SessionState, Decision, DecisionType
🔄 PATTERN: State management with compression and checkpointing
📝 TODOS: Add state diffing, implement state migration between versions

💡 AI HINT: Critical for maintaining context across interactions and crashes
⚠️ NEVER: Load pickled state from untrusted sources
"""

"""
CORA - Claude Operational Research Assistant
Claude State Tracker Module

Tracks Claude's working memory, session state, and provides checkpoint functionality
for maintaining context awareness across interactions.

Author: CORA Team
Version: 1.0.0
"""

import json
import logging
import pickle
import zlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
import hashlib
import time

# Configure logging
logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions Claude can make during a session."""
    FILE_EDIT = "file_edit"
    FILE_CREATE = "file_create"
    FILE_DELETE = "file_delete"
    ANALYSIS = "analysis"
    REFACTOR = "refactor"
    BUG_FIX = "bug_fix"
    FEATURE_ADD = "feature_add"
    DOCUMENTATION = "documentation"
    TEST_CREATE = "test_create"
    DEPENDENCY_UPDATE = "dependency_update"


@dataclass
class Decision:
    """Represents a decision made by Claude during a session."""
    decision_type: DecisionType
    description: str
    timestamp: datetime
    context: Dict[str, Any]
    confidence: float = 1.0
    rationale: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary for serialization."""
        return {
            "decision_type": self.decision_type.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "confidence": self.confidence,
            "rationale": self.rationale
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Decision':
        """Create Decision from dictionary."""
        return cls(
            decision_type=DecisionType(data["decision_type"]),
            description=data["description"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=data["context"],
            confidence=data.get("confidence", 1.0),
            rationale=data.get("rationale")
        )


@dataclass
class UnderstandingNode:
    """Node in the understanding graph representing a concept or relationship."""
    node_id: str
    node_type: str  # e.g., "file", "function", "class", "concept"
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    connections: Set[str] = field(default_factory=set)
    confidence: float = 1.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "properties": self.properties,
            "connections": list(self.connections),
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnderstandingNode':
        """Create UnderstandingNode from dictionary."""
        return cls(
            node_id=data["node_id"],
            node_type=data["node_type"],
            name=data["name"],
            properties=data.get("properties", {}),
            connections=set(data.get("connections", [])),
            confidence=data.get("confidence", 1.0),
            last_updated=datetime.fromisoformat(data["last_updated"])
        )


@dataclass
class SessionState:
    """Current session data including context and working memory."""
    session_id: str
    start_time: datetime
    last_activity: datetime
    files_touched: Set[str] = field(default_factory=set)
    decisions_made: List[Decision] = field(default_factory=list)
    understanding_graph: Dict[str, UnderstandingNode] = field(default_factory=dict)
    context_tokens_used: int = 0
    total_tokens_used: int = 0
    checkpoints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session state to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "files_touched": list(self.files_touched),
            "decisions_made": [d.to_dict() for d in self.decisions_made],
            "understanding_graph": {k: v.to_dict() for k, v in self.understanding_graph.items()},
            "context_tokens_used": self.context_tokens_used,
            "total_tokens_used": self.total_tokens_used,
            "checkpoints": self.checkpoints,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionState':
        """Create SessionState from dictionary."""
        return cls(
            session_id=data["session_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            files_touched=set(data.get("files_touched", [])),
            decisions_made=[Decision.from_dict(d) for d in data.get("decisions_made", [])],
            understanding_graph={
                k: UnderstandingNode.from_dict(v) 
                for k, v in data.get("understanding_graph", {}).items()
            },
            context_tokens_used=data.get("context_tokens_used", 0),
            total_tokens_used=data.get("total_tokens_used", 0),
            checkpoints=data.get("checkpoints", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class AwarenessMetrics:
    """Metrics tracking Claude's awareness and context pressure."""
    context_utilization: float  # 0-1, how much of context window is used
    understanding_depth: float  # 0-1, how well Claude understands the codebase
    decision_confidence: float  # 0-1, average confidence in decisions
    file_coverage: float  # 0-1, percentage of relevant files touched
    graph_connectivity: float  # 0-1, how connected the understanding graph is
    memory_pressure: float  # 0-1, how much memory pressure exists
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AwarenessMetrics':
        """Create AwarenessMetrics from dictionary."""
        return cls(**data)


class ClaudeSessionTracker:
    """Tracks Claude's working memory and session state."""
    
    def __init__(self, state_dir: Path, max_context_tokens: int = 200000):
        """
        Initialize the session tracker.
        
        Args:
            state_dir: Directory to store state files
            max_context_tokens: Maximum context window size
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.max_context_tokens = max_context_tokens
        
        self.current_session: Optional[SessionState] = None
        self.checkpoint_dir = self.state_dir / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Initialize metrics
        self.metrics = AwarenessMetrics(
            context_utilization=0.0,
            understanding_depth=0.0,
            decision_confidence=0.0,
            file_coverage=0.0,
            graph_connectivity=0.0,
            memory_pressure=0.0
        )
        
        logger.info(f"Initialized ClaudeSessionTracker with state_dir: {state_dir}")
    
    def start_session(self, session_id: Optional[str] = None) -> SessionState:
        """
        Start a new session.
        
        Args:
            session_id: Optional session ID, will be generated if not provided
            
        Returns:
            The new session state
        """
        if session_id is None:
            session_id = self._generate_session_id()
        
        now = datetime.now(timezone.utc)
        self.current_session = SessionState(
            session_id=session_id,
            start_time=now,
            last_activity=now
        )
        
        logger.info(f"Started new session: {session_id}")
        return self.current_session
    
    def add_file_touch(self, file_path: str, operation: str = "read") -> None:
        """
        Record that a file was touched during the session.
        
        Args:
            file_path: Path to the file
            operation: Type of operation performed
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        self.current_session.files_touched.add(file_path)
        self.current_session.last_activity = datetime.now(timezone.utc)
        
        # Update understanding graph
        node_id = f"file:{file_path}"
        if node_id not in self.current_session.understanding_graph:
            self.current_session.understanding_graph[node_id] = UnderstandingNode(
                node_id=node_id,
                node_type="file",
                name=Path(file_path).name,
                properties={"full_path": file_path, "operations": [operation]}
            )
        else:
            node = self.current_session.understanding_graph[node_id]
            if "operations" not in node.properties:
                node.properties["operations"] = []
            node.properties["operations"].append(operation)
            node.last_updated = datetime.now(timezone.utc)
        
        logger.debug(f"Recorded file touch: {file_path} ({operation})")
    
    def add_decision(self, decision: Decision) -> None:
        """
        Record a decision made during the session.
        
        Args:
            decision: The decision to record
        """
        if not self.current_session:
            raise RuntimeError("No active session")
        
        self.current_session.decisions_made.append(decision)
        self.current_session.last_activity = datetime.now(timezone.utc)
        
        logger.debug(f"Recorded decision: {decision.decision_type.value} - {decision.description}")
    
    def add_understanding_node(self, node: UnderstandingNode) -> None:
        """
        Add or update a node in the understanding graph.
        
        Args: