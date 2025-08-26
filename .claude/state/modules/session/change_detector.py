#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/session/change_detector.py
🎯 PURPOSE: Detect changes between Claude sessions
🔗 IMPORTS: hashlib, logging, pathlib, datetime, collections
📤 EXPORTS: ChangeDetector, Change, ChangeType
🔄 PATTERN: Observer pattern for change detection
📝 TODOS: Add more sophisticated change analysis algorithms

💡 AI HINT: Essential for tracking what changed between sessions
⚠️ NEVER: Miss critical file changes that could affect context
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of changes detected between sessions."""
    FILE_ADDED = "file_added"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    DEPENDENCY_CHANGED = "dependency_changed"
    STRUCTURE_CHANGED = "structure_changed"
    EXTERNAL_CHANGE = "external_change"
    CONFIG_CHANGED = "config_changed"


@dataclass
class Change:
    """Represents a change detected between sessions."""
    change_type: ChangeType
    path: str
    description: str
    timestamp: datetime
    severity: str  # "low", "medium", "high"
    details: Dict[str, Any] = field(default_factory=dict)
    requires_attention: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'change_type': self.change_type.value,
            'path': self.path,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity,
            'details': self.details,
            'requires_attention': self.requires_attention
        }


class ChangeDetector:
    """Detects changes between sessions."""
    
    def __init__(self):
        """Initialize change detector."""
        self.file_hashes: Dict[str, str] = {}
        self.structure_snapshot: Dict[str, Any] = {}
        
    def snapshot_current_state(self, files: List[str], 
                             structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Take a snapshot of current state.
        
        Args:
            files: List of file paths
            structure: Current codebase structure
            
        Returns:
            State snapshot
        """
        snapshot = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'files': {},
            'structure': structure
        }
        
        # Calculate file hashes
        for file_path in files:
            try:
                path = Path(file_path)
                if path.exists():
                    content = path.read_bytes()
                    file_hash = hashlib.sha256(content).hexdigest()
                    snapshot['files'][file_path] = {
                        'hash': file_hash,
                        'size': len(content),
                        'modified': path.stat().st_mtime
                    }
            except Exception as e:
                logger.warning(f"Could not snapshot file {file_path}: {e}")
                
        return snapshot
    
    def detect_changes(self, previous_snapshot: Dict[str, Any],
                      current_snapshot: Dict[str, Any]) -> List[Change]:
        """
        Detect changes between snapshots.
        
        Args:
            previous_snapshot: Previous state snapshot
            current_snapshot: Current state snapshot
            
        Returns:
            List of detected changes
        """
        changes = []
        now = datetime.now(timezone.utc)
        
        # Check file changes
        prev_files = previous_snapshot.get('files', {})
        curr_files = current_snapshot.get('files', {})
        
        # Files added
        for file_path in set(curr_files) - set(prev_files):
            changes.append(Change(
                change_type=ChangeType.FILE_ADDED,
                path=file_path,
                description=f"New file added: {Path(file_path).name}",
                timestamp=now,
                severity="medium",
                details={'size': curr_files[file_path]['size']},
                requires_attention=True
            ))
        
        # Files deleted
        for file_path in set(prev_files) - set(curr_files):
            changes.append(Change(
                change_type=ChangeType.FILE_DELETED,
                path=file_path,
                description=f"File deleted: {Path(file_path).name}",
                timestamp=now,
                severity="high",
                requires_attention=True
            ))
        
        # Files modified
        for file_path in set(prev_files) & set(curr_files):
            if prev_files[file_path]['hash'] != curr_files[file_path]['hash']:
                size_diff = curr_files[file_path]['size'] - prev_files[file_path]['size']
                changes.append(Change(
                    change_type=ChangeType.FILE_MODIFIED,
                    path=file_path,
                    description=f"File modified: {Path(file_path).name}",
                    timestamp=now,
                    severity="medium" if abs(size_diff) < 1000 else "high",
                    details={
                        'size_change': size_diff,
                        'previous_hash': prev_files[file_path]['hash'][:8],
                        'current_hash': curr_files[file_path]['hash'][:8]
                    },
                    requires_attention=True
                ))
        
        # Check structural changes
        if previous_snapshot.get('structure') != current_snapshot.get('structure'):
            changes.append(Change(
                change_type=ChangeType.STRUCTURE_CHANGED,
                path="",
                description="Codebase structure has changed",
                timestamp=now,
                severity="high",
                requires_attention=True
            ))
        
        return changes
    
    def analyze_change_impact(self, changes: List[Change]) -> Dict[str, Any]:
        """
        Analyze the impact of detected changes.
        
        Args:
            changes: List of detected changes
            
        Returns:
            Impact analysis
        """
        impact = {
            'total_changes': len(changes),
            'by_type': defaultdict(int),
            'by_severity': defaultdict(int),
            'critical_changes': [],
            'affected_areas': set(),
            'risk_score': 0.0
        }
        
        for change in changes:
            impact['by_type'][change.change_type.value] += 1
            impact['by_severity'][change.severity] += 1
            
            if change.severity == "high":
                impact['critical_changes'].append({
                    'path': change.path,
                    'description': change.description
                })
            
            # Extract affected area from path
            if change.path:
                parts = Path(change.path).parts
                if len(parts) > 1:
                    impact['affected_areas'].add(parts[1])  # Module/directory
        
        # Calculate risk score
        severity_weights = {'low': 0.1, 'medium': 0.3, 'high': 0.6}
        total_weight = sum(
            count * severity_weights.get(severity, 0)
            for severity, count in impact['by_severity'].items()
        )
        impact['risk_score'] = min(1.0, total_weight / 10)  # Normalize to 0-1
        
        impact['affected_areas'] = list(impact['affected_areas'])
        
        return impact