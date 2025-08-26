#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/session/summary_generator.py
🎯 PURPOSE: Generate session summaries and "Previously on CORA" content
🔗 IMPORTS: json, datetime, pathlib, collections
📤 EXPORTS: SummaryGenerator, SessionSummary
🔄 PATTERN: Template pattern for different summary types
📝 TODOS: Add NLP-based summary extraction

💡 AI HINT: Creates concise summaries for session continuity
⚠️ NEVER: Lose critical context in summarization
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

import logging
logger = logging.getLogger(__name__)


@dataclass
class SessionSummary:
    """Summary of a session for continuity purposes."""
    session_id: str
    start_time: datetime
    end_time: datetime
    primary_focus: str
    key_decisions: List[str]
    files_modified: List[str]
    unfinished_tasks: List[str]
    context_snapshot: Dict[str, Any]
    achievements: List[str]
    blockers: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'primary_focus': self.primary_focus,
            'key_decisions': self.key_decisions,
            'files_modified': self.files_modified,
            'unfinished_tasks': self.unfinished_tasks,
            'context_snapshot': self.context_snapshot,
            'achievements': self.achievements,
            'blockers': self.blockers
        }


class SummaryGenerator:
    """Generates session summaries and "Previously on CORA" content."""
    
    def __init__(self):
        """Initialize summary generator."""
        self.summary_templates = {
            'brief': self._generate_brief_summary,
            'detailed': self._generate_detailed_summary,
            'technical': self._generate_technical_summary
        }
        
    def generate_session_summary(self, session_data: Dict[str, Any],
                               summary_type: str = "brief") -> SessionSummary:
        """
        Generate a session summary.
        
        Args:
            session_data: Raw session data
            summary_type: Type of summary to generate
            
        Returns:
            Session summary
        """
        # Extract key information
        decisions = session_data.get('decisions_made', [])
        files = list(session_data.get('files_touched', []))
        
        # Determine primary focus
        primary_focus = self._determine_primary_focus(decisions, files)
        
        # Extract key decisions
        key_decisions = self._extract_key_decisions(decisions)
        
        # Identify unfinished tasks
        unfinished_tasks = self._identify_unfinished_tasks(session_data)
        
        # Create context snapshot
        context_snapshot = {
            'understanding_depth': len(session_data.get('understanding_graph', {})),
            'tokens_used': session_data.get('total_tokens_used', 0),
            'last_checkpoint': session_data.get('checkpoints', [])[-1] if session_data.get('checkpoints') else None
        }
        
        # Extract achievements and blockers
        achievements = self._extract_achievements(decisions)
        blockers = self._extract_blockers(session_data)
        
        return SessionSummary(
            session_id=session_data.get('session_id', 'unknown'),
            start_time=datetime.fromisoformat(session_data.get('start_time', datetime.now(timezone.utc).isoformat())),
            end_time=datetime.fromisoformat(session_data.get('last_activity', datetime.now(timezone.utc).isoformat())),
            primary_focus=primary_focus,
            key_decisions=key_decisions,
            files_modified=files,
            unfinished_tasks=unfinished_tasks,
            context_snapshot=context_snapshot,
            achievements=achievements,
            blockers=blockers
        )
    
    def generate_previously_on(self, summaries: List[SessionSummary],
                             max_sessions: int = 3) -> str:
        """
        Generate "Previously on CORA" summary.
        
        Args:
            summaries: List of session summaries
            max_sessions: Maximum sessions to include
            
        Returns:
            Previously-on narrative
        """
        if not summaries:
            return "This is the beginning of our journey with CORA."
        
        # Take most recent sessions
        recent_summaries = summaries[-max_sessions:]
        
        narrative = ["Previously on CORA:\n"]
        
        for summary in recent_summaries:
            duration = (summary.end_time - summary.start_time).total_seconds() / 3600
            narrative.append(f"\n## Session {summary.session_id[:8]} ({duration:.1f} hours ago)")
            narrative.append(f"Focus: {summary.primary_focus}")
            
            if summary.achievements:
                narrative.append("\nAchievements:")
                for achievement in summary.achievements[:3]:
                    narrative.append(f"  ✓ {achievement}")
            
            if summary.key_decisions:
                narrative.append("\nKey decisions:")
                for decision in summary.key_decisions[:3]:
                    narrative.append(f"  • {decision}")
            
            if summary.unfinished_tasks:
                narrative.append("\nPending tasks:")
                for task in summary.unfinished_tasks[:3]:
                    narrative.append(f"  ⟳ {task}")
        
        # Add overall context
        total_files = len(set(f for s in recent_summaries for f in s.files_modified))
        narrative.append(f"\n\nOverall: Modified {total_files} files across {len(recent_summaries)} sessions.")
        
        return "\n".join(narrative)
    
    def _determine_primary_focus(self, decisions: List[Dict[str, Any]], 
                               files: List[str]) -> str:
        """Determine primary focus of session."""
        if not decisions:
            return "Exploration and analysis"
        
        # Count decision types
        decision_types = defaultdict(int)
        for decision in decisions:
            decision_types[decision.get('decision_type', 'unknown')] += 1
        
        # Find most common type
        most_common = max(decision_types.items(), key=lambda x: x[1])
        
        focus_map = {
            'file_edit': 'Code modification and refactoring',
            'file_create': 'New feature implementation',
            'bug_fix': 'Bug fixing and issue resolution',
            'analysis': 'Code analysis and understanding',
            'test_create': 'Test development and coverage',
            'documentation': 'Documentation improvements'
        }
        
        return focus_map.get(most_common[0], f"Working on {most_common[0]}")
    
    def _extract_key_decisions(self, decisions: List[Dict[str, Any]]) -> List[str]:
        """Extract key decisions from session."""
        # Filter high-confidence decisions
        key_decisions = []
        
        for decision in decisions:
            if decision.get('confidence', 0) >= 0.8:
                desc = decision.get('description', '')
                if len(desc) > 10:  # Skip trivial descriptions
                    key_decisions.append(desc)
        
        # Return top 5 decisions
        return key_decisions[:5]
    
    def _identify_unfinished_tasks(self, session_data: Dict[str, Any]) -> List[str]:
        """Identify unfinished tasks from session."""
        unfinished = []
        
        # Check for TODO markers in decisions
        for decision in session_data.get('decisions_made', []):
            if 'TODO' in decision.get('description', ''):
                unfinished.append(decision['description'])
        
        # Check metadata for explicit unfinished tasks
        metadata = session_data.get('metadata', {})
        if 'unfinished_tasks' in metadata:
            unfinished.extend(metadata['unfinished_tasks'])
        
        return list(set(unfinished))[:5]  # Deduplicate and limit
    
    def _extract_achievements(self, decisions: List[Dict[str, Any]]) -> List[str]:
        """Extract achievements from decisions."""
        achievements = []
        
        achievement_keywords = ['completed', 'fixed', 'implemented', 'resolved', 'added']
        
        for decision in decisions:
            desc = decision.get('description', '').lower()
            if any(keyword in desc for keyword in achievement_keywords):
                achievements.append(decision['description'])
        
        return achievements[:5]
    
    def _extract_blockers(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract blockers from session."""
        blockers = []
        
        # Check for low-confidence decisions
        for decision in session_data.get('decisions_made', []):
            if decision.get('confidence', 1.0) < 0.5:
                blockers.append(f"Uncertain about: {decision.get('description', 'unknown')}")
        
        # Check metadata for explicit blockers
        metadata = session_data.get('metadata', {})
        if 'blockers' in metadata:
            blockers.extend(metadata['blockers'])
        
        return blockers[:3]
    
    def _generate_brief_summary(self, session_data: Dict[str, Any]) -> str:
        """Generate brief summary."""
        summary = self.generate_session_summary(session_data, "brief")
        return f"{summary.primary_focus}. Modified {len(summary.files_modified)} files."
    
    def _generate_detailed_summary(self, session_data: Dict[str, Any]) -> str:
        """Generate detailed summary."""
        summary = self.generate_session_summary(session_data, "detailed")
        return json.dumps(summary.to_dict(), indent=2)
    
    def _generate_technical_summary(self, session_data: Dict[str, Any]) -> str:
        """Generate technical summary."""
        summary = self.generate_session_summary(session_data, "technical")
        
        technical = {
            'metrics': {
                'files_touched': len(summary.files_modified),
                'decisions_made': len(session_data.get('decisions_made', [])),
                'tokens_used': summary.context_snapshot.get('tokens_used', 0),
                'understanding_nodes': summary.context_snapshot.get('understanding_depth', 0)
            },
            'primary_operations': summary.key_decisions[:3],
            'incomplete_work': summary.unfinished_tasks
        }
        
        return json.dumps(technical, indent=2)