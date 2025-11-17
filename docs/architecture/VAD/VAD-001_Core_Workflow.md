# VAD-001: Core Workflow Verification

## Purpose
Tests integration of GAD-2 (SDLC) + GAD-4 (Quality) + GAD-5 (Runtime)

## Question
"Does the state machine respect quality gates?"

## Test Scenarios

### Scenario 1: Quality Gate Blocks Transition
**Given**: Linting status = failing
**When**: Agent tries to transition state
**Then**: Transition blocked, error message shown

### Scenario 2: Quality Gate Allows Transition
**Given**: All quality checks passing
**When**: Agent transitions state
**Then**: Transition succeeds, receipt created

## Implementation
See: `tests/architecture/test_vad001_core_workflow.py`

## Status
- ✅ Layer 2 (Tool-based)
- ✅ Layer 3 (Runtime)
- ❌ Layer 1 (N/A - no automation)
