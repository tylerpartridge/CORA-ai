#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/.claude/state/modules/session/memory_bank.py
🎯 PURPOSE: Long-term memory storage and retrieval for sessions
🔗 IMPORTS: json, pathlib, datetime, collections, logging
📤 EXPORTS: MemoryBankManager
🔄 PATTERN: Repository pattern for memory storage
📝 TODOS: Add memory compression, implement similarity search

💡 AI HINT: Stores important context for future sessions
⚠️ NEVER: Exceed memory limits without cleanup
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import defaultdict

import logging
logger = logging.getLogger(__name__)


class MemoryBankManager:
    """Manages long-term memory storage and retrieval."""
    
    def __init__(self, memory_dir: Path, max_memories: int = 1000):
        """
        Initialize memory bank manager.
        
        Args:
            memory_dir: Directory for memory storage
            max_memories: Maximum memories to retain
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.max_memories = max_memories
        
        # Memory index
        self.memory_index: Dict[str, Dict[str, Any]] = {}
        self._load_memory_index()
        
    def store_memory(self, key: str, content: Any, 
                    tags: List[str] = None,
                    importance: float = 0.5) -> None:
        """
        Store a memory in the bank.
        
        Args:
            key: Unique key for the memory
            content: Memory content
            tags: Tags for categorization
            importance: Importance score (0-1)
        """
        memory_data = {
            'key': key,
            'content': content,
            'tags': tags or [],
            'importance': importance,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'access_count': 0,
            'last_accessed': None
        }
        
        # Store in index
        self.memory_index[key] = {
            'tags': tags or [],
            'importance': importance,
            'created_at': memory_data['created_at'],
            'file_path': f"{key}.json"
        }
        
        # Save to file
        memory_path = self.memory_dir / f"{key}.json"
        with open(memory_path, 'w') as f:
            json.dump(memory_data, f, indent=2)
        
        # Manage memory limit
        self._enforce_memory_limit()
        
        logger.debug(f"Stored memory: {key}")
    
    def retrieve_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve a memory by key.
        
        Args:
            key: Memory key
            
        Returns:
            Memory content or None
        """
        if key not in self.memory_index:
            return None
        
        memory_path = self.memory_dir / self.memory_index[key]['file_path']
        
        try:
            with open(memory_path, 'r') as f:
                memory_data = json.load(f)
            
            # Update access info
            memory_data['access_count'] += 1
            memory_data['last_accessed'] = datetime.now(timezone.utc).isoformat()
            
            # Save updated data
            with open(memory_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
            
            return memory_data['content']
            
        except Exception as e:
            logger.error(f"Error retrieving memory {key}: {e}")
            return None
    
    def search_memories(self, tags: List[str] = None,
                       min_importance: float = 0.0,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by criteria.
        
        Args:
            tags: Tags to filter by
            min_importance: Minimum importance threshold
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        matches = []
        
        for key, index_data in self.memory_index.items():
            # Check importance
            if index_data['importance'] < min_importance:
                continue
            
            # Check tags
            if tags:
                if not any(tag in index_data['tags'] for tag in tags):
                    continue
            
            matches.append({
                'key': key,
                'tags': index_data['tags'],
                'importance': index_data['importance'],
                'created_at': index_data['created_at']
            })
        
        # Sort by importance and recency
        matches.sort(key=lambda x: (x['importance'], x['created_at']), reverse=True)
        
        return matches[:limit]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory bank statistics."""
        total_memories = len(self.memory_index)
        
        if not total_memories:
            return {
                'total_memories': 0,
                'avg_importance': 0,
                'top_tags': [],
                'memory_usage': 0
            }
        
        # Calculate stats
        importances = [m['importance'] for m in self.memory_index.values()]
        all_tags = []
        for m in self.memory_index.values():
            all_tags.extend(m['tags'])
        
        tag_counts = defaultdict(int)
        for tag in all_tags:
            tag_counts[tag] += 1
        
        # Calculate storage size
        total_size = sum(
            (self.memory_dir / m['file_path']).stat().st_size
            for m in self.memory_index.values()
            if (self.memory_dir / m['file_path']).exists()
        )
        
        return {
            'total_memories': total_memories,
            'avg_importance': sum(importances) / len(importances),
            'top_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'memory_usage': total_size,
            'capacity_used': total_memories / self.max_memories
        }
    
    def _load_memory_index(self) -> None:
        """Load memory index from disk."""
        index_path = self.memory_dir / "memory_index.json"
        
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    self.memory_index = json.load(f)
            except Exception as e:
                logger.error(f"Error loading memory index: {e}")
                self.memory_index = {}
    
    def _save_memory_index(self) -> None:
        """Save memory index to disk."""
        index_path = self.memory_dir / "memory_index.json"
        
        with open(index_path, 'w') as f:
            json.dump(self.memory_index, f, indent=2)
    
    def _enforce_memory_limit(self) -> None:
        """Enforce memory limit by removing least important memories."""
        if len(self.memory_index) <= self.max_memories:
            return
        
        # Sort by importance and access
        memories = []
        for key, data in self.memory_index.items():
            memory_path = self.memory_dir / data['file_path']
            if memory_path.exists():
                with open(memory_path, 'r') as f:
                    memory_data = json.load(f)
                
                score = (data['importance'] * 0.7 + 
                        min(memory_data.get('access_count', 0) / 10, 0.3))
                memories.append((key, score))
        
        # Sort by score
        memories.sort(key=lambda x: x[1])
        
        # Remove lowest scoring memories
        to_remove = len(memories) - self.max_memories
        
        for key, _ in memories[:to_remove]:
            # Remove file
            memory_path = self.memory_dir / self.memory_index[key]['file_path']
            if memory_path.exists():
                memory_path.unlink()
            
            # Remove from index
            del self.memory_index[key]
        
        self._save_memory_index()
        
        logger.info(f"Removed {to_remove} memories to enforce limit")