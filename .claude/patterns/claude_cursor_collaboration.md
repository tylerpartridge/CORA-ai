# Claude-Cursor Collaboration Pattern

## Core Principle
**ALWAYS** decompose tasks into Claude and Cursor components for maximum efficiency.

## Task Decomposition Framework

### 1. When Starting ANY Task:
```
1. Analyze task requirements
2. Identify Claude strengths (multi-agent, analysis, architecture)
3. Identify Cursor strengths (runtime, dependencies, fixes)
4. Create parallel task assignments
5. Use TodoWrite to track both Claude AND Cursor tasks
```

### 2. Task Assignment Guidelines:

**Claude Excels At:**
- Multi-agent parallel execution
- System analysis and architecture
- Pattern recognition and optimization
- Security audits and validation
- Creating comprehensive test suites
- Strategic planning and decomposition

**Cursor Excels At:**
- Installing dependencies (npm, pip)
- Fixing runtime errors
- Debugging import issues
- Server configuration
- Environment setup
- Quick iterations and fixes

### 3. Collaboration Patterns:

#### Pattern A: Parallel Execution
```
Claude: Create test framework
Cursor: Install test dependencies
Both: Execute simultaneously
Result: 70% time reduction
```

#### Pattern B: Sequential Handoff
```
Claude: Analyze and plan
Cursor: Implement fixes
Claude: Validate results
Result: Higher quality outcomes
```

#### Pattern C: Real-time Collaboration
```
Claude: Monitor progress
Cursor: Execute changes
Claude: Provide feedback
Cursor: Iterate quickly
Result: Rapid convergence
```

## Operational Memory Rules

### RULE 1: Always Create Cursor Tasks
When working on ANY feature:
1. Immediately identify what Cursor can do
2. Create explicit Cursor tasks in TodoWrite
3. Mark them with "CURSOR:" prefix

### RULE 2: Communicate Dependencies
```python
# Example task breakdown
claude_tasks = [
    "Design authentication flow",
    "Create security test suite"
]
cursor_tasks = [
    "Install bcrypt, jwt dependencies",
    "Fix any import errors",
    "Start test server"
]
```

### RULE 3: Use Handoff Protocols
```
Claude completes → Create handoff document
Cursor picks up → Executes tasks
Both update → STATUS.md with progress
```

## Implementation Checklist

Before starting any task:
- [ ] Have I identified Cursor tasks?
- [ ] Are dependencies listed for Cursor?
- [ ] Is the handoff clear?
- [ ] Are both sets of tasks in TodoWrite?

## Example Workflow

**Task: Implement new payment feature**

Claude Creates:
```
TodoWrite:
1. [CLAUDE] Design payment architecture
2. [CURSOR] Install stripe, payment dependencies
3. [CLAUDE] Create payment models
4. [CURSOR] Run migrations
5. [CLAUDE] Implement payment logic
6. [CURSOR] Fix any runtime errors
7. [BOTH] Test payment flow
```

## Success Metrics
- Tasks completed 70% faster with collaboration
- Fewer iterations needed
- Higher quality outcomes
- Both systems working at peak efficiency

## Remember
**"Two AI systems working together are exponentially more powerful than one working alone."**

Always think: "What can Cursor do while I'm working on this?"