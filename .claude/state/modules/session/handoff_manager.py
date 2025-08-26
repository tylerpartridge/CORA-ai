#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/session/handoff_manager.py
🎯 PURPOSE: Manage session handoff protocols between Claude sessions
🔗 IMPORTS: dataclasses, datetime, pathlib, logging
📤 EXPORTS: HandoffManager, HandoffProtocol
🔄 PATTERN: Chain of responsibility for handoff steps
📝 TODOS: Add handoff validation and rollback capabilities

💡 AI HINT: Ensures smooth transitions between sessions
⚠️ NEVER: Drop critical context during handoff
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

import logging
logger = logging.getLogger(__name__)


@dataclass
class HandoffProtocol:
    """Protocol for session handoff."""
    from_session: str
    to_session: str
    handoff_time: datetime
    critical_context: Dict[str, Any]
    pending_actions: List[Dict[str, Any]]
    warnings: List[str]
    recommended_next_steps: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class HandoffManager:
    """Manages session handoff protocols."""
    
    def __init__(self):
        """Initialize handoff manager."""
        self.handoff_history: List[HandoffProtocol] = []
        
    def prepare_handoff(self, from_session: Dict[str, Any],
                       to_session_id: str) -> HandoffProtocol:
        """
        Prepare handoff protocol between sessions.
        
        Args:
            from_session: Source session data
            to_session_id: Target session ID
            
        Returns:
            Handoff protocol
        """
        # Extract critical context
        critical_context = self._extract_critical_context(from_session)
        
        # Identify pending actions
        pending_actions = self._identify_pending_actions(from_session)
        
        # Generate warnings
        warnings = self._generate_handoff_warnings(from_session)
        
        # Recommend next steps
        next_steps = self._recommend_next_steps(from_session, pending_actions)
        
        protocol = HandoffProtocol(
            from_session=from_session.get('session_id', 'unknown'),
            to_session=to_session_id,
            handoff_time=datetime.now(timezone.utc),
            critical_context=critical_context,
            pending_actions=pending_actions,
            warnings=warnings,
            recommended_next_steps=next_steps
        )
        
        self.handoff_history.append(protocol)
        
        return protocol
    
    def execute_handoff(self, protocol: HandoffProtocol,
                       new_session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute handoff protocol for new session.
        
        Args:
            protocol: Handoff protocol
            new_session: New session data
            
        Returns:
            Updated session data
        """
        # Inject critical context
        if 'metadata' not in new_session:
            new_session['metadata'] = {}
        
        new_session['metadata']['handoff'] = {
            'from_session': protocol.from_session,
            'received_at': datetime.now(timezone.utc).isoformat(),
            'critical_context': protocol.critical_context,
            'pending_actions': protocol.pending_actions
        }
        
        # Add previous session reference
        new_session['metadata']['previous_session'] = protocol.from_session
        
        # Log handoff
        logger.info(f"Executed handoff from {protocol.from_session} to {protocol.to_session}")
        
        return new_session
    
    def _extract_critical_context(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Extract critical context for handoff."""
        context = {
            'active_files': list(session.get('files_touched', []))[-10:],  # Last 10 files
            'working_directory': session.get('metadata', {}).get('working_directory'),
            'key_understanding': self._extract_key_understanding(session),
            'active_patterns': self._extract_active_patterns(session)
        }
        
        # Add any error states
        if 'errors' in session.get('metadata', {}):
            context['unresolved_errors'] = session['metadata']['errors']
        
        return context
    
    def _identify_pending_actions(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify pending actions from session."""
        pending = []
        
        # Check for incomplete decisions
        for decision in session.get('decisions_made', []):
            if decision.get('confidence', 1.0) < 0.7:
                pending.append({
                    'type': 'incomplete_decision',
                    'description': decision.get('description'),
                    'reason': 'Low confidence',
                    'priority': 'medium'
                })
        
        # Check metadata for explicit pending items
        metadata = session.get('metadata', {})
        if 'pending_tasks' in metadata:
            for task in metadata['pending_tasks']:
                pending.append({
                    'type': 'pending_task',
                    'description': task,
                    'priority': 'high'
                })
        
        return pending
    
    def _generate_handoff_warnings(self, session: Dict[str, Any]) -> List[str]:
        """Generate warnings for handoff."""
        warnings = []
        
        # Check token usage
        tokens_used = session.get('context_tokens_used', 0)
        max_tokens = session.get('metadata', {}).get('max_context_tokens', 200000)
        
        if tokens_used > max_tokens * 0.8:
            warnings.append(f"High context usage: {tokens_used/max_tokens:.0%} of maximum")
        
        # Check session duration
        if 'start_time' in session:
            duration = (datetime.now(timezone.utc) - 
                       datetime.fromisoformat(session['start_time'])).total_seconds() / 3600
            if duration > 2:
                warnings.append(f"Long session duration: {duration:.1f} hours")
        
        # Check for error patterns
        decisions = session.get('decisions_made', [])
        error_count = sum(1 for d in decisions if 'error' in d.get('description', '').lower())
        if error_count > 3:
            warnings.append(f"Multiple errors encountered: {error_count} error-related decisions")
        
        return warnings
    
    def _recommend_next_steps(self, session: Dict[str, Any],
                            pending_actions: List[Dict[str, Any]]) -> List[str]:
        """Recommend next steps based on session state."""
        recommendations = []
        
        # Based on pending actions
        high_priority = [a for a in pending_actions if a.get('priority') == 'high']
        if high_priority:
            recommendations.append(f"Address {len(high_priority)} high-priority pending actions")
        
        # Based on file patterns
        files = session.get('files_touched', [])
        if files:
            # Group by directory
            directories = defaultdict(int)
            for file_path in files:
                parts = Path(file_path).parts
                if len(parts) > 1:
                    directories[parts[1]] += 1
            
            # Recommend based on concentration
            most_active = max(directories.items(), key=lambda x: x[1]) if directories else None
            if most_active and most_active[1] > 3:
                recommendations.append(f"Continue work in {most_active[0]} module")
        
        # Based on decision patterns
        decisions = session.get('decisions_made', [])
        if decisions:
            recent_types = [d.get('decision_type') for d in decisions[-5:]]
            if recent_types.count('analysis') > 2:
                recommendations.append("Complete analysis and move to implementation")
            elif recent_types.count('file_edit') > 3:
                recommendations.append("Consider running tests on recent changes")
        
        return recommendations[:5]
    
    def _extract_key_understanding(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key understanding from session."""
        graph = session.get('understanding_graph', {})
        
        if not graph:
            return {}
        
        # Find most connected nodes (hubs)
        node_connections = {}
        for node_id, node_data in graph.items():
            connections = len(node_data.get('connections', []))
            if connections > 2:  # Only include well-connected nodes
                node_connections[node_id] = connections
        
        # Get top 5 hubs
        top_hubs = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:5]
        
        key_understanding = {
            'central_concepts': [
                {
                    'id': hub[0],
                    'name': graph[hub[0]].get('name', 'unknown'),
                    'type': graph[hub[0]].get('node_type', 'unknown'),
                    'connections': hub[1]
                }
                for hub in top_hubs
            ],
            'total_concepts': len(graph),
            'graph_density': sum(len(n.get('connections', [])) for n in graph.values()) / (len(graph) + 1)
        }
        
        return key_understanding
    
    def _extract_active_patterns(self, session: Dict[str, Any]) -> List[str]:
        """Extract active working patterns from session."""
        patterns = []
        
        decisions = session.get('decisions_made', [])
        if len(decisions) > 5:
            # Look for decision sequences
            recent_types = [d.get('decision_type') for d in decisions[-10:]]
            
            # Detect patterns
            if recent_types.count('file_edit') > 5:
                patterns.append("Heavy editing mode")
            if recent_types.count('analysis') > 3:
                patterns.append("Deep analysis phase")
            if 'test_create' in recent_types:
                patterns.append("Test development active")
        
        return patterns