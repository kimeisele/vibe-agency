# ADR-003: Delegated Execution Architecture

**Status:** ✅ Implemented
**Date:** 2025-11-14
**Author:** System Architect (Claude Code)
**Related:** GAD-002 (Hybrid Orchestrator Architecture)

---

## Context

### The Problem: Regression in `core_orchestrator.py`

The original vision for Agency OS was a **hybrid system**:
- **Claude Code** (the "Brain") = Central intelligence, makes all LLM calls
- **core_orchestrator.py** (the "Arm") = Deterministic state manager, no intelligence

However, during implementation of GAD-002, a **regression** occurred:

```python
# core_orchestrator.py (REGRESSION - The "Arm" started "thinking")
def execute_agent(self, agent_name, task_id, inputs, manifest):
    prompt = self.prompt_runtime.execute_task(agent_name, task_id, inputs)

    # 🚨 REGRESSION: The orchestrator makes LLM calls directly!
    response = self.llm_client.invoke(
        prompt=prompt,
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096
    )

    return json.loads(response.content)
```

**Why this is a problem:**
1. ❌ **Architecture violation:** The "Arm" (orchestrator) usurped the "Brain" (Claude Code)
2. ❌ **Loss of stability:** State management got mixed with intelligence execution
3. ❌ **No visibility:** Claude Code doesn't see what prompts are being executed
4. ❌ **Hard to debug:** Workflow runs autonomously, bypassing the operator

### The Vision: "Fließband" Architecture

The correct architecture is:

```
┌──────────────────────────────────────────────┐
│  CLAUDE CODE (The Brain - Central AI)       │
│  • All LLM calls                             │
│  • All intelligence operations               │
│  • Full visibility into workflow             │
└──────────────────────────────────────────────┘
           │ calls                    ▲ returns
           ▼                          │ prompt
┌──────────────────────────────────────────────┐
│  core_orchestrator.py (The Arm - Manager)    │
│  • State management                          │
│  • Prompt composition                        │
│  • Artifact management                       │
│  • NO LLM calls!                             │
└──────────────────────────────────────────────┘
           │                          ▲
           ▼                          │
     ┌──────────┐              ┌──────────┐
     │ prompt   │              │ explore  │
     │ registry │              │ agent    │
     └──────────┘              └──────────┘
     (Dumb helpers - no intelligence)
```

This is called the **"Fließband" (Conveyor Belt)** architecture:
- The "Arm" composes prompts and places them on the "conveyor belt"
- The "Brain" picks up prompts, executes them, and returns results
- The "Arm" takes results and updates state

---

## Decision

We implement a **Delegated Execution Protocol** via STDOUT/STDIN handoff.

### Components

#### 1. Execution Modes in `core_orchestrator.py`

```python
class CoreOrchestrator:
    def __init__(self, repo_root, execution_mode="delegated"):
        self.execution_mode = execution_mode
        # "delegated" = Claude Code integration (default)
        # "autonomous" = Legacy direct LLM calls (for testing)
```

#### 2. Intelligence Request Protocol (STDOUT)

When the orchestrator needs intelligence:

```python
def _request_intelligence(self, agent_name, task_id, prompt, manifest):
    request = {
        "type": "INTELLIGENCE_REQUEST",
        "agent": agent_name,
        "task_id": task_id,
        "prompt": prompt,  # Composed prompt, ready for LLM
        "context": {
            "project_id": manifest.project_id,
            "phase": manifest.current_phase.value
        },
        "wait_for_response": True
    }

    print("---INTELLIGENCE_REQUEST_START---", file=sys.stderr)
    print(json.dumps(request, indent=2))
    print("---INTELLIGENCE_REQUEST_END---", file=sys.stderr)
    sys.stdout.flush()

    # Wait for response on STDIN
    response_line = sys.stdin.readline()
    response = json.loads(response_line)

    return response["result"]
```

#### 3. Intelligence Response Protocol (STDIN)

Claude Code (or vibe-cli) responds:

```json
{
  "type": "INTELLIGENCE_RESPONSE",
  "agent": "VIBE_ALIGNER",
  "task_id": "scope_negotiation",
  "result": {
    "features": [...],
    "scope_negotiation": {...}
  },
  "metadata": {
    "executor": "claude-code",
    "model": "claude-sonnet-4-5"
  }
}
```

#### 4. `vibe-cli` Wrapper Tool

A Python wrapper that:
1. Launches `core_orchestrator.py` with `--mode=delegated`
2. Monitors STDOUT for `INTELLIGENCE_REQUEST`s
3. Executes prompts via Anthropic API (or delegates to Claude Code)
4. Sends `INTELLIGENCE_RESPONSE`s back via STDIN

---

## Implementation

### Changes to `core_orchestrator.py`

#### Added execution mode parameter:

```python
def __init__(
    self,
    repo_root: Path,
    execution_mode: str = "delegated"  # NEW
):
    self.execution_mode = execution_mode
```

#### Refactored `execute_agent()`:

```python
def execute_agent(self, agent_name, task_id, inputs, manifest):
    # 1. Compose prompt (ALWAYS - this is the "Arm's" job)
    prompt = self.prompt_runtime.execute_task(agent_name, task_id, inputs)

    # 2. Route based on execution mode
    if self.execution_mode == "delegated":
        return self._request_intelligence(agent_name, task_id, prompt, manifest)
    elif self.execution_mode == "autonomous":
        return self._execute_autonomous(agent_name, prompt, manifest)
```

#### Added `_request_intelligence()`:

Implements STDOUT/STDIN handoff protocol (see above).

#### Added `_execute_autonomous()`:

Legacy behavior preserved for testing and backward compatibility.

### New Tool: `vibe-cli`

```bash
# Delegated mode (default)
vibe-cli run my-project-123

# Autonomous mode (legacy)
vibe-cli run my-project-123 --mode=autonomous
```

---

## Consequences

### Positive

✅ **Architectural purity restored:**
- Orchestrator is now a pure state manager (the "Arm")
- All intelligence operations go through Claude Code (the "Brain")

✅ **Workflow stability:**
- State management is deterministic
- No mixing of concerns

✅ **Full visibility:**
- Claude Code sees all prompts
- Easy to debug and understand workflow

✅ **Testability:**
- Can mock intelligence responses
- Can test state machine independently

✅ **Backward compatibility:**
- `--mode=autonomous` preserves old behavior for testing

### Negative

⚠️ **Additional complexity:**
- STDIN/STDOUT protocol adds communication layer
- Requires wrapper tool (vibe-cli)

⚠️ **Not fully tested yet:**
- Need to create integration tests
- Need to verify prompt_runtime works correctly

### Mitigation

- Keep autonomous mode as fallback
- Add comprehensive logging
- Create test suite for handoff protocol

---

## Testing Strategy

### Unit Tests

Test each component independently:
- `core_orchestrator.py` in delegated mode (mock STDIN/STDOUT)
- `vibe-cli` handoff logic (mock subprocess)

### Integration Tests

Test full workflow:
1. Start vibe-cli with test project
2. Verify INTELLIGENCE_REQUEST is sent
3. Send mock INTELLIGENCE_RESPONSE
4. Verify state transitions work

### Manual Tests

Use actual Claude Code session:
1. Run orchestrator in delegated mode
2. Claude Code intercepts INTELLIGENCE_REQUESTs
3. Claude Code executes prompts
4. Verify workflow completes successfully

---

## Related Decisions

- **GAD-001:** Hybrid Architecture (Python + Prompts)
- **GAD-002:** Hierarchical Orchestrator Architecture
- **ADR-003:** This decision (Delegated Execution)

---

## Notes

### Why STDOUT/STDIN instead of API?

We considered several options:
1. ❌ **REST API:** Too heavyweight, requires server
2. ❌ **Message Queue:** Adds infrastructure dependency
3. ✅ **STDOUT/STDIN:** Simplest, works everywhere, no dependencies

STDOUT/STDIN is the Unix philosophy: tools communicate via pipes.

### Why not just run everything in Claude Code?

We **could** run the orchestrator logic in Claude Code, but:
- ❌ State management in LLM context is unreliable (token limits)
- ❌ Complex state machines are hard to maintain in prompts
- ✅ Python is better for deterministic workflows
- ✅ Prompts are better for intelligence operations

**The hybrid approach gives us the best of both worlds.**

---

## Future Work

1. Add integration tests for handoff protocol
2. Create Python library for Claude Code integration
3. Explore Claude MCP (Model Context Protocol) for richer integration
4. Add streaming support for long-running agents
5. Add telemetry/observability

---

## Approval

**Approved by:** User (via conversation)
**Implemented by:** Claude Code (System Architect)
**Review status:** Pending integration testing
**Rollout plan:** Gradual (keep autonomous mode available)
