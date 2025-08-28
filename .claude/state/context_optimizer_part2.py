# Generated: 2025-07-11 by SmartHeaderGenerator v1.0
"""
🧭 LOCATION: CORA/.claude/state/context_optimizer_part2.py
🎯 PURPOSE: [Auto-generated header - could not analyze file]
🔗 IMPORTS: [Unknown]
📤 EXPORTS: [Unknown]
🔄 PATTERN: [Unknown]
📝 TODOS: [Unknown]
💡 AI HINT: [Unknown]
⚠️ NEVER: [Unknown]
"""

🧭 LOCATION: /CORA/.claude\state\context_optimizer_part2.py
🎯 PURPOSE: [To be determined - please update]
🔗 IMPORTS: [To be determined - please update]
📤 EXPORTS: [To be determined - please update]
🔄 PATTERN: [To be determined - please update]
📝 TODOS: [To be determined - please update]
"""

                if k in self.required_items
            }
        else:
            self.context_items.clear()
            self.required_items.clear()
    
    def _emergency_optimize(self, items: List[ContextItem],
                           pressure: Dict[str, Any]) -> OptimizationResult:
        """Emergency optimization for critical pressure."""
        logger.warning(f"Emergency optimization triggered: {pressure['level']} pressure")
        
        # Calculate tokens to free
        tokens_to_free = self.window_manager.calculate_tokens_to_free(
            pressure['current_tokens']
        )
        
        # Use aggressive eviction
        evicted_ids = self.evict_items(tokens_to_free)
        
        # Recalculate after eviction
        remaining_items = [i for i in items if i.item_id not in evicted_ids]
        total_tokens = sum(i.token_count for i in remaining_items)
        total_value = sum(i.get_value_score() for i in remaining_items)
        
        return OptimizationResult(
            selected_items=[i.item_id for i in remaining_items],
            total_tokens=total_tokens,
            total_value=total_value,
            excluded_items=evicted_ids,
            optimization_time_ms=0,  # Emergency, no time tracking
            pressure_level=total_tokens / self.max_context_tokens
        )
    
    def _apply_optimization_result(self, result: OptimizationResult) -> None:
        """Apply optimization result to context."""
        # Remove excluded items
        for item_id in result.excluded_items:
            if item_id in self.context_items and item_id not in self.required_items:
                del self.context_items[item_id]
                self.total_evictions += 1
    
    def _calculate_total_tokens(self) -> int:
        """Calculate total tokens in context."""
        return sum(item.token_count for item in self.context_items.values())
    
    def _get_current_objectives(self) -> List[str]:
        """Get current session objectives."""
        # In practice, this would come from session state
        return []
    
    def _get_session_context(self) -> Dict[str, Any]:
        """Get current session context."""
        # In practice, this would come from session state
        return {
            'item_ids': list(self.context_items.keys()),
            'active_files': []
        }


# Integration with existing components
def integrate_with_state_tracker(optimizer: ContextOptimizer):
    """
    Example integration with ClaudeSessionTracker.
    
    Args:
        optimizer: Context optimizer instance
    """
    from claude_state_tracker import ClaudeSessionTracker, Decision, DecisionType
    
    class ContextAwareTracker(ClaudeSessionTracker):
        """Session tracker with context optimization."""
        
        def __init__(self, state_dir: Path, max_context_tokens: int = 200000):
            super().__init__(state_dir, max_context_tokens)
            self.context_optimizer = optimizer
            
        def add_file_touch(self, file_path: str, operation: str = "read") -> None:
            """Override to add file to context."""
            super().add_file_touch(file_path, operation)
            
            # Add file content to context
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                item = ContextItem(
                    item_id=f"file:{file_path}",
                    item_type=ItemType.FILE_CONTENT,
                    content=content[:1000],  # Truncate for example
                    token_count=len(content.split()),
                    priority=0.7,
                    relevance=0.8,
                    timestamp=datetime.now(timezone.utc),
                    last_accessed=datetime.now(timezone.utc),
                    metadata={'file_path': file_path}
                )
                
                self.context_optimizer.add_item(item)
                
            except Exception as e:
                logger.error(f"Could not add file to context: {e}")
        
        def add_decision(self, decision: Decision) -> None:
            """Override to add decision to context."""
            super().add_decision(decision)
            
            # Add decision to context
            item = ContextItem(
                item_id=f"decision:{decision.timestamp.timestamp()}",
                item_type=ItemType.DECISION,
                content=decision.description,
                token_count=len(decision.description.split()),
                priority=0.8,
                relevance=0.9,
                timestamp=decision.timestamp,
                last_accessed=datetime.now(timezone.utc),
                metadata={
                    'type': decision.decision_type.value,
                    'confidence': decision.confidence
                }
            )
            
            # High-confidence decisions are required
            required = decision.confidence > 0.9
            self.context_optimizer.add_item(item, required=required)
        
        def get_optimized_context(self) -> Dict[str, Any]:
            """Get optimized context for Claude."""
            # Optimize context
            result = self.context_optimizer.optimize()
            
            # Build context string
            context_parts = []
            
            for item_id in result.selected_items:
                item = self.context_optimizer.access_item(item_id)
                if item:
                    context_parts.append(f"=== {item.item_type.value}: {item_id} ===")
                    context_parts.append(item.content)
                    context_parts.append("")
            
            return {
                'context': "\n".join(context_parts),
                'tokens_used': result.total_tokens,
                'pressure_level': result.pressure_level,
                'excluded_count': len(result.excluded_items)
            }
    
    return ContextAwareTracker


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create optimizer
    optimizer = ContextOptimizer(max_context_tokens=50000)
    
    # Add some test items
    print("=== Adding Context Items ===")
    
    # Add instruction (high priority, required)
    instruction = ContextItem(
        item_id="inst_1",
        item_type=ItemType.INSTRUCTION,
        content="Refactor the authentication module to improve security",
        token_count=10,
        priority=1.0,
        relevance=1.0,
        timestamp=datetime.now(timezone.utc),
        last_accessed=datetime.now(timezone.utc)
    )
    optimizer.add_item(instruction, required=True)
    
    # Add file contents
    for i in range(5):
        file_item = ContextItem(
            item_id=f"file_{i}",
            item_type=ItemType.FILE_CONTENT,
            content=f"File content for module_{i}.py" * 100,
            token_count=1000,
            priority=0.7 - i * 0.1,
            relevance=0.8,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
            last_accessed=datetime.now(timezone.utc) - timedelta(hours=i)
        )
        optimizer.add_item(file_item)
    
    # Add decisions
    for i in range(3):
        decision = ContextItem(
            item_id=f"decision_{i}",
            item_type=ItemType.DECISION,
            content=f"Decision {i}: Implemented feature X",
            token_count=50,
            priority=0.8,
            relevance=0.9 - i * 0.1,
            timestamp=datetime.now(timezone.utc) - timedelta(hours=i*2),
            last_accessed=datetime.now(timezone.utc) - timedelta(hours=i)
        )
        optimizer.add_item(decision)
    
    # Check state
    print("\n=== Initial Context State ===")
    state = optimizer.get_context_state()
    print(f"Total items: {state['total_items']}")
    print(f"Total tokens: {state['total_tokens']}")
    print(f"Pressure: {state['pressure']['level']} ({state['pressure']['utilization']:.1%})")
    
    # Simulate access patterns
    print("\n=== Simulating Access Patterns ===")
    optimizer.access_item("file_0")
    optimizer.access_item("file_0")
    optimizer.access_item("decision_0")
    
    # Run optimization
    print("\n=== Running Optimization ===")
    result = optimizer.optimize()
    print(f"Selected items: {len(result.selected_items)}")
    print(f"Excluded items: {len(result.excluded_items)}")
    print(f"Total value: {result.total_value:.2f}")
    print(f"Optimization time: {result.optimization_time_ms:.1f}ms")
    
    # Test dynamic adjustment
    print("\n=== Dynamic Adjustment ===")
    adjuster = DynamicContextAdjuster(optimizer)
    
    # Record some patterns
    adjuster.record_access_pattern(["file_0", "file_1"], "analysis", 150)
    adjuster.record_access_pattern(["file_0", "file_1"], "analysis", 160)
    adjuster.record_access_pattern(["file_0", "file_1"], "analysis", 155)
    
    suggestions = adjuster.suggest_adjustments()
    print(f"Suggestions: {suggestions}")
    
    # Final state
    print("\n=== Final Context State ===")
    final_state = optimizer.get_context_state()
    print(f"Total items: {final_state['total_items']}")
    print(f"Total tokens: {final_state['total_tokens']}")
    print(f"Optimization count: {final_state['optimization_count']}")
    print(f"Total evictions: {final_state['total_evictions']}")