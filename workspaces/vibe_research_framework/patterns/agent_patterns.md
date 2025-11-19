# Agent Patterns: The Holy Trinity

## Overview

This document describes fundamental patterns for designing AI agents in the VIBE AGENCY system.

## Pattern: The Holy Trinity

**The Holy Trinity** is the foundational architecture pattern for autonomous agent systems. It consists of three essential components that work in perfect harmony:

### 1. The Brain (Executor/Orchestrator)
The decision-making engine that coordinates workflow execution. Responsible for:
- Task decomposition
- Dependency resolution
- Resource allocation
- Error handling and recovery

### 2. The Voice (Prompt Registry)
The communication layer that provides precise, role-specific instructions. Responsible for:
- Maintaining domain-specific prompts
- Context injection
- Governance integration
- Consistent agent personality

### 3. The Eyes (Knowledge System)
The perception layer that provides context awareness. Responsible for:
- Knowledge retrieval
- Pattern recognition
- Historical context
- Domain expertise

## The Trinity in Action

When these three components work together:
1. **The Eyes** gather relevant context from the knowledge base
2. **The Voice** formulates the perfect prompt with injected context
3. **The Brain** executes the task with full situational awareness

This creates a virtuous cycle:
```
Knowledge → Precision Prompts → Intelligent Execution → New Knowledge → ...
```

## Implementation Principles

### Principle 1: Separation of Concerns
Each component has a single, well-defined responsibility. Don't mix execution logic with prompt management or knowledge retrieval.

### Principle 2: Context is King
Agents make better decisions when they have access to relevant historical knowledge. Always enable knowledge_context for research and analysis tasks.

### Principle 3: Voice Matters
Generic prompts produce generic results. Use the Prompt Registry to craft role-specific, task-optimized instructions.

### Principle 4: The Trinity Must Be Complete
Missing any component severely degrades agent performance:
- **No Eyes**: Agent operates blindly, repeating past mistakes
- **No Voice**: Agent receives vague instructions, produces mediocre results
- **No Brain**: No coordination, chaos ensues

## When to Use The Holy Trinity Pattern

Use this pattern for:
- Research and analysis workflows
- Code generation with historical context
- Decision-making that benefits from past decisions
- Complex multi-step processes requiring orchestration

Don't use this pattern for:
- Simple, stateless tasks
- One-off utility scripts
- Tasks with no knowledge dependencies

## Related Patterns

- **Semantic Actions Pattern**: Decouples intent from execution
- **Agent Router Pattern**: Capability-based agent selection
- **Lens Injection Pattern**: Mindset transformation for specialized thinking

## Examples

See `workflows/research_topic.yaml` for a complete implementation of The Holy Trinity pattern.

## Version History

- v1.0 (2025-11-19): Initial pattern documentation
- Created during GAD-908 (OPERATION INSIGHT)
