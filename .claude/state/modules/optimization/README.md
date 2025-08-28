# Context Optimization Modules

This directory contains the modularized components of the context optimization system.

## Module Structure

### knapsack_solver.py (208 lines)
- **Purpose**: Implements the knapsack algorithm for optimal context packing
- **Exports**: `KnapsackOptimizer`, `OptimizationResult`
- **Key Features**:
  - Dynamic programming knapsack implementation
  - Handles required vs optional items
  - Automatic scaling for large contexts

### scoring_functions.py (215 lines)
- **Purpose**: Scoring and weighting functions for context items
- **Exports**: `PriorityScorer`, `RelevanceDecayFunction`, `hours_since_access`, `ItemType`
- **Key Features**:
  - Priority calculation based on multiple factors
  - Time-based relevance decay
  - Type-specific scoring weights

### optimization_strategies.py (294 lines)
- **Purpose**: Eviction and optimization strategies
- **Exports**: `EvictionStrategy`, `LRUEvictionStrategy`, `PriorityEvictionStrategy`, `AdaptiveEvictionStrategy`, `EvictionPolicy`, `ContextWindowManager`
- **Key Features**:
  - Multiple eviction policies (LRU, Priority, Adaptive)
  - Context window pressure management
  - Adaptive learning from eviction patterns

### context_analyzer.py (219 lines)
- **Purpose**: Context analysis and pattern detection
- **Exports**: `DynamicContextAdjuster`
- **Key Features**:
  - Access pattern analysis
  - Performance tracking
  - Dynamic adjustment suggestions
  - Frequent itemset mining

## Integration

All modules are imported through the main `context_optimizer.py` file, which now contains only:
- The core `ContextOptimizer` class
- The `ContextItem` dataclass
- Integration examples

## Results

- **Original file**: 1,276 lines
- **New main file**: 542 lines (57.5% reduction)
- **Total modular code**: 992 lines
- **All modules**: <300 lines each as required
- **Main file**: <600 lines as required