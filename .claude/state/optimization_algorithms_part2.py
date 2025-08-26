# Generated: 2025-07-11 by SmartHeaderGenerator v1.0
"""
🧭 LOCATION: CORA/.claude/state/optimization_algorithms_part2.py
🎯 PURPOSE: [Auto-generated header - could not analyze file]
🔗 IMPORTS: [Unknown]
📤 EXPORTS: [Unknown]
🔄 PATTERN: [Unknown]
📝 TODOS: [Unknown]
💡 AI HINT: [Unknown]
⚠️ NEVER: [Unknown]
"""

🧭 LOCATION: /CORA/.claude\state\optimization_algorithms_part2.py
🎯 PURPOSE: [To be determined - please update]
🔗 IMPORTS: [To be determined - please update]
📤 EXPORTS: [To be determined - please update]
🔄 PATTERN: [To be determined - please update]
📝 TODOS: [To be determined - please update]
"""

        return new_relevance


class EvictionStrategy(ABC):
    """Abstract base class for eviction strategies."""
    
    @abstractmethod
    def select_items_to_evict(self, items: List[ContextItem],
                             tokens_to_free: int) -> List[str]:
        """Select items to evict from context."""
        pass


class LRUEvictionStrategy(EvictionStrategy):
    """Least Recently Used eviction strategy."""
    
    def select_items_to_evict(self, items: List[ContextItem],
                             tokens_to_free: int) -> List[str]:
        """Select least recently used items to evict."""
        # Sort by last accessed time (oldest first)
        sorted_items = sorted(items, key=lambda x: x.last_accessed)
        
        evicted_ids = []
        freed_tokens = 0
        
        for item in sorted_items:
            if freed_tokens >= tokens_to_free:
                break
            evicted_ids.append(item.item_id)
            freed_tokens += item.token_count
        
        return evicted_ids


class PriorityEvictionStrategy(EvictionStrategy):
    """Priority-based eviction strategy."""
    
    def select_items_to_evict(self, items: List[ContextItem],
                             tokens_to_free: int) -> List[str]:
        """Select lowest priority items to evict."""
        # Sort by value score (lowest first)
        sorted_items = sorted(items, key=lambda x: x.get_value_score())
        
        evicted_ids = []
        freed_tokens = 0
        
        for item in sorted_items:
            # Never evict instructions
            if item.item_type == ItemType.INSTRUCTION:
                continue
                
            if freed_tokens >= tokens_to_free:
                break
                
            evicted_ids.append(item.item_id)
            freed_tokens += item.token_count
        
        return evicted_ids


class AdaptiveEvictionStrategy(EvictionStrategy):
    """Adaptive eviction strategy that learns from patterns."""
    
    def __init__(self):
        """Initialize adaptive strategy."""
        self.eviction_history = deque(maxlen=100)
        self.reinsertion_penalty = defaultdict(float)
        
    def select_items_to_evict(self, items: List[ContextItem],
                             tokens_to_free: int) -> List[str]:
        """Select items using adaptive strategy."""
        # Calculate scores including penalties
        scored_items = []
        for item in items:
            # Skip protected items
            if item.item_type == ItemType.INSTRUCTION:
                continue
                
            base_score = item.get_value_score()
            penalty = self.reinsertion_penalty.get(item.item_id, 0)
            adjusted_score = base_score - penalty
            
            scored_items.append((adjusted_score, item))
        
        # Sort by adjusted score (lowest first)
        scored_items.sort(key=lambda x: x[0])
        
        evicted_ids = []
        freed_tokens = 0
        
        for score, item in scored_items:
            if freed_tokens >= tokens_to_free:
                break
                
            evicted_ids.append(item.item_id)
            freed_tokens += item.token_count
            
            # Record eviction
            self.eviction_history.append({
                'item_id': item.item_id,
                'timestamp': datetime.now(timezone.utc),
                'score': score
            })
        
        return evicted_ids
    
    def record_reinsertion(self, item_id: str) -> None:
        """Record that an item was reinserted after eviction."""
        # Increase penalty for items that get reinserted
        self.reinsertion_penalty[item_id] += 0.1
        
        # Decay penalties over time
        for key in list(self.reinsertion_penalty.keys()):
            self.reinsertion_penalty[key] *= 0.95
            if self.reinsertion_penalty[key] < 0.01:
                del self.reinsertion_penalty[key]


class KnapsackOptimizer:
    """Implements knapsack algorithm for optimal context packing."""
    
    def __init__(self, max_tokens: int):
        """
        Initialize knapsack optimizer.
        
        Args:
            max_tokens: Maximum tokens in context window
        """
        self.max_tokens = max_tokens
        
    def optimize(self, items: List[ContextItem],
                required_items: Optional[Set[str]] = None) -> OptimizationResult:
        """
        Optimize context using dynamic programming knapsack.
        
        Args:
            items: List of context items
            required_items: Set of item IDs that must be included
            
        Returns:
            Optimization result
        """
        start_time = datetime.now(timezone.utc)
        required_items = required_items or set()
        
        # Separate required and optional items
        required = [item for item in items if item.item_id in required_items]
        optional = [item for item in items if item.item_id not in required_items]
        
        # Calculate space used by required items
        required_tokens = sum(item.token_count for item in required)
        
        if required_tokens > self.max_tokens:
            # Cannot fit all required items
            logger.warning(f"Required items exceed max tokens: {required_tokens} > {self.max_tokens}")
            # Return just the highest priority required items that fit
            required.sort(key=lambda x: x.get_value_score(), reverse=True)
            selected = []
            total_tokens = 0
            
            for item in required:
                if total_tokens + item.token_count <= self.max_tokens:
                    selected.append(item.item_id)
                    total_tokens += item.token_count
            
            excluded = [item.item_id for item in items if item.item_id not in selected]
            
            return OptimizationResult(
                selected_items=selected,
                total_tokens=total_tokens,
                total_value=sum(i.get_value_score() for i in items if i.item_id in selected),
                excluded_items=excluded,
                optimization_time_ms=self._elapsed_ms(start_time),
                pressure_level=1.0  # Maximum pressure
            )
        
        # Space available for optional items
        available_tokens = self.max_tokens - required_tokens
        
        # Run knapsack on optional items
        selected_optional = self._knapsack_dp(optional, available_tokens)
        
        # Combine results
        selected_items = [item.item_id for item in required] + selected_optional
        total_tokens = required_tokens + sum(
            item.token_count for item in optional if item.item_id in selected_optional
        )
        total_value = sum(
            item.get_value_score() for item in items if item.item_id in selected_items
        )
        excluded_items = [item.item_id for item in items if item.item_id not in selected_items]
        
        # Calculate pressure level
        pressure_level = total_tokens / self.max_tokens
        
        return OptimizationResult(
            selected_items=selected_items,
            total_tokens=total_tokens,
            total_value=total_value,
            excluded_items=excluded_items,
            optimization_time_ms=self._elapsed_ms(start_time),
            pressure_level=pressure_level
        )
    
    def _knapsack_dp(self, items: List[ContextItem], capacity: int) -> List[str]:
        """
        Dynamic programming knapsack implementation.
        
        Args:
            items: Items to consider
            capacity: Token capacity
            
        Returns:
            List of selected item IDs
        """
        n = len(items)
        if n == 0 or capacity == 0:
            return []
        
        # Scale down for efficiency if needed
        scale_factor = 1
        if capacity > 10000:
            scale_factor = capacity // 10000
            capacity = capacity // scale_factor
            scaled_items = []
            for item in items:
                scaled_item = ContextItem(
                    item_id=item.item_id,
                    item_type=item.item_type,
                    content=item.content,
                    token_count=max(1, item.token_count // scale_factor),
                    priority=item.priority,
                    relevance=item.relevance,
                    timestamp=item.timestamp,
                    last_accessed=item.last_accessed,
                    access_count=item.access_count,
                    decay_rate=item.decay_rate,
                    dependencies=item.dependencies,
                    metadata=item.metadata
                )
                scaled_items.append(scaled_item)
            items = scaled_items
        
        # Initialize DP table
        dp = [[0.0 for _ in range(capacity + 1)] for _ in range(n + 1)]
        
        # Fill DP table
        for i in range(1, n + 1):
            item = items[i - 1]
            value = item.get_value_score()
            weight = item.token_count
            
            for w in range(capacity + 1):
                if weight <= w:
                    dp[i][w] = max(
                        dp[i - 1][w],
                        dp[i - 1][w - weight] + value
                    )
                else:
                    dp[i][w] = dp[i - 1][w]
        
        # Backtrack to find selected items
        selected = []
        w = capacity
        
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                selected.append(items[i - 1].item_id)
                w -= items[i - 1].token_count
        
        return selected
    
    def _elapsed_ms(self, start_time: datetime) -> float:
        """Calculate elapsed time in milliseconds."""
        elapsed = datetime.now(timezone.utc) - start_time
        return elapsed.total_seconds() * 1000

