# Generated: 2025-07-11 by SmartHeaderGenerator v1.0
"""
🧭 LOCATION: CORA/.claude/state/modules/session/drift_detector_part2.py
🎯 PURPOSE: [Auto-generated header - could not analyze file]
🔗 IMPORTS: [Unknown]
📤 EXPORTS: [Unknown]
🔄 PATTERN: [Unknown]
📝 TODOS: [Unknown]
💡 AI HINT: [Unknown]
⚠️ NEVER: [Unknown]
"""

🧭 LOCATION: /CORA/.claude\state\modules\session\drift_detector_part2.py
🎯 PURPOSE: [To be determined - please update]
🔗 IMPORTS: [To be determined - please update]
📤 EXPORTS: [To be determined - please update]
🔄 PATTERN: [To be determined - please update]
📝 TODOS: [To be determined - please update]
"""

    def _calculate_decision_distribution(self, session: Dict[str, Any]) -> Dict[str, int]:
        """Calculate distribution of decision types."""
        distribution = defaultdict(int)
        
        for decision in session.get('decisions_made', []):
            decision_type = decision.get('decision_type', 'unknown')
            distribution[decision_type] += 1
        
        return dict(distribution)
    
    def _calculate_understanding_signature(self, session: Dict[str, Any]) -> Dict[str, int]:
        """Calculate understanding graph signature."""
        signature = defaultdict(int)
        
        graph = session.get('understanding_graph', {})
        for node in graph.values():
            node_type = node.get('node_type', 'unknown')
            signature[node_type] += 1
        
        return dict(signature)
    
    def _extract_objective_keywords(self, session: Dict[str, Any]) -> Set[str]:
        """Extract keywords representing session objectives."""
        keywords = set()
        
        # Extract from decisions
        for decision in session.get('decisions_made', []):
            desc = decision.get('description', '').lower()
            # Simple keyword extraction - in practice, use NLP
            words = desc.split()
            keywords.update(w for w in words if len(w) > 4)
        
        # Extract from metadata
        metadata = session.get('metadata', {})
        if 'objectives' in metadata:
            keywords.update(metadata['objectives'])
        
        return keywords