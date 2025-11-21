# HANDOVER: PHASE 2.6 - HYBRID AGENT INTEGRATION (START)

**Handover Date:** 2025-11-21
**Session ID:** claude/fix-vibe-core-steward-01GaxFiZ5PSAzy9eTXogKyU3
**From:** STEWARD (Documentation Sync & Roadmap Planning)
**To:** STEWARD (Implementation Start)
**Priority:** P0 (Critical Integration)

---

## 📊 SESSION SUMMARY

### What Was Accomplished

1. **✅ Documentation Sync Complete** (Previous session cleanup)
   - Removed stale `ARCHITECTURE_V3_OS.md` (described non-existent agency_os/)
   - Fixed `SPECIALIST_AGENT_CONTRACT.md` imports (agency_os → vibe_core)
   - Updated `ARCHITECTURE_MAP.md` with post-split structure (vibe_core/ + apps/agency/)
   - Created `ARCHITECTURE_CURRENT_STATE.md` reflecting actual codebase

2. **✅ Hybrid Concept Analysis**
   - Identified CRITICAL problem: Two parallel architectures with NO integration
   - **Universe A:** Kernel → SimpleLLMAgent (can think, cannot act - no tool-use)
   - **Universe B:** STEWARD → Specialists (can act, not in Kernel - no audit trail)
   - Root cause: `BaseSpecialist` does NOT implement `VibeAgent` protocol

3. **✅ Roadmap Creation** (JSON + Markdown)
   - Created `docs/roadmap/phase_2_6_hybrid_integration.json` (JSON system integration)
   - Created `docs/architecture/ROADMAP_HYBRID_INTEGRATION.md` (detailed design doc)
   - Updated `CLAUDE.md` to point to Phase 2.6 as active roadmap
   - 10 tasks defined: ARCH-026 to ARCH-033 (3 phases)

### Git Commits

```bash
6421c31 - docs: Remove ARCHITECTURE_V3_OS.md (replaced by ARCHITECTURE_CURRENT_STATE.md)
92b0032 - docs: Add roadmap for Hybrid Agent Integration (Phase 2.6)
<pending> - docs: Integrate Phase 2.6 into roadmap system + CLAUDE.md update
```

---

## 🎯 CURRENT STATE ANALYSIS

### What Exists (Working)

| Component | Status | Location |
|-----------|--------|----------|
| **VibeKernel** | ✅ Working | `vibe_core/kernel.py` (ARCH-022) |
| **VibeScheduler** | ✅ Working | `vibe_core/scheduling/scheduler.py` (ARCH-021) |
| **VibeLedger** | ✅ Working | `vibe_core/ledger.py` (ARCH-024) |
| **VibeAgent Protocol** | ✅ Defined | `vibe_core/agent_protocol.py` (ARCH-023) |
| **SimpleLLMAgent** | ✅ Working | `vibe_core/agents/llm_agent.py` (ARCH-025) |
| **BaseSpecialist** | ✅ Working | `vibe_core/specialists/base_specialist.py` (ARCH-005) |
| **5 Specialists** | ✅ Working | `apps/agency/specialists/*.py` (Planning, Coding, Testing, Deployment, Maintenance) |
| **RouterBridge** | ✅ Working | `vibe_core/playbook/router_bridge.py` (Playbook → Phase mapping) |

### What's Broken (The Gap)

```python
# PROBLEM 1: SimpleLLMAgent has no tool-use
class SimpleLLMAgent(VibeAgent):
    def process(self, task: Task) -> dict:
        # Can only call LLM provider
        response = self.provider.chat(messages)
        # ❌ NO ability to write files, execute code, etc.
        return {"response": response}

# PROBLEM 2: BaseSpecialist does NOT implement VibeAgent
class BaseSpecialist(ABC):  # ❌ Not a VibeAgent!
    def execute(self, context: MissionContext):  # ❌ Different signature!
        ...

# PROBLEM 3: No integration
# - Specialists called directly by STEWARD (bypass Kernel, no Ledger audit)
# - Kernel only used for SimpleLLMAgent (underutilized)
# - Two parallel dispatch systems!
```

---

## 🧠 MENTAL MODEL: THE HYBRID CONCEPT

**The GENIUS Insight:**
"Agent" is an INTERFACE (VibeAgent protocol), not a single type. We need TWO kinds of agents:

### Type 1: LLM-Agents (Intelligent, Non-Deterministic)
```python
SimpleLLMAgent(VibeAgent):
    """
    Powered by LLM, makes intelligent decisions.

    Use cases:
    - Code review
    - Architecture advice
    - Refactoring suggestions
    - Natural language tasks

    Needs: Tool-use capability (ARCH-027)
    """
```

### Type 2: Script-Agents (Rule-Based, Deterministic)
```python
SpecialistAgent(VibeAgent):  # ← NEW! Wrap BaseSpecialist
    """
    Wraps BaseSpecialist, executes playbook workflows.

    Use cases:
    - SDLC workflows (planning, coding, testing, deployment)
    - Pipeline automation
    - Structured processes

    Needs: Adapter to implement VibeAgent protocol (ARCH-026)
    """
```

### Unification via Kernel

```
┌─────────────────────────────────────────┐
│ STEWARD (Claude Code - External)       │
│  - Reads mission from user              │
│  - Submits tasks to Kernel              │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ VibeKernel (Central Dispatch)          │
│  - FIFO/Priority scheduling             │
│  - Agent registry (both types)          │
│  - Ledger audit trail                   │
└─────────────────────────────────────────┘
                 ↓
        ┌────────┴────────┐
        ↓                 ↓
┌──────────────┐  ┌──────────────┐
│ LLM-Agents   │  │ Script-Agents│
│ (Intelligent)│  │ (Workflows)  │
└──────────────┘  └──────────────┘

Both implement VibeAgent protocol!
Both dispatched by Kernel!
Both recorded in Ledger!
```

---

## 🗺️ YOUR MISSION: ARCH-026 (First Task)

### Task: SpecialistAgent Adapter

**Goal:** Create adapter that wraps `BaseSpecialist` to implement `VibeAgent` protocol.

**Why Critical:** This is the bridge between the two parallel universes. Once this exists, Specialists can be dispatched by Kernel (enabling audit trail, resource management, unified scheduling).

### Implementation Guide

**File to create:** `vibe_core/agents/specialist_agent.py`

**Key responsibilities:**
1. Implement `VibeAgent` protocol:
   - `agent_id` property (return `f"specialist-{specialist.role.lower()}"`)
   - `process(task: Task)` method

2. Convert data structures:
   - Task payload → MissionContext (for specialist)
   - SpecialistResult → Task result (for kernel)

3. Call specialist lifecycle hooks:
   - `validate_preconditions(context)`
   - `on_start(context)`
   - `execute(context)` ← The main work
   - `on_complete(context, result)` or `on_error(context, error)`

**Pseudo-code:**
```python
class SpecialistAgent(VibeAgent):
    def __init__(self, specialist: BaseSpecialist):
        self._specialist = specialist
        self._agent_id = f"specialist-{specialist.role.lower()}"

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def process(self, task: Task) -> dict:
        # 1. Extract mission data from task payload
        context = MissionContext(
            mission_id=task.payload["mission_id"],
            mission_uuid=task.payload["mission_uuid"],
            phase=task.payload["phase"],
            project_root=Path(task.payload["project_root"]),
            metadata=task.payload.get("metadata", {})
        )

        # 2. Validate preconditions
        if not self._specialist.validate_preconditions(context):
            return {"success": False, "error": "Preconditions not met"}

        # 3. Execute with lifecycle hooks
        self._specialist.on_start(context)

        try:
            result = self._specialist.execute(context)
            self._specialist.on_complete(context, result)

            # 4. Convert SpecialistResult → Task result
            return {
                "success": result.success,
                "next_phase": result.next_phase,
                "artifacts": result.artifacts,
                "decisions": result.decisions,
                "error": result.error
            }
        except Exception as e:
            error_result = self._specialist.on_error(context, e)
            return {"success": False, "error": str(e)}
```

### Tests to Write

**File:** `tests/agents/test_specialist_agent.py`

**Test scenarios:**
1. ✅ Wrap PlanningSpecialist, register with Kernel
2. ✅ Submit task → Kernel.tick() → SpecialistAgent → PlanningSpecialist
3. ✅ Verify Ledger records execution (input, output, timestamps)
4. ✅ Error handling: precondition failure
5. ✅ Error handling: specialist exception

**Test-First Workflow:**
```bash
# 1. Write tests FIRST
vim tests/agents/test_specialist_agent.py

# 2. Run tests (expect failures)
uv run pytest tests/agents/test_specialist_agent.py -v

# 3. Implement SpecialistAgent
vim vibe_core/agents/specialist_agent.py

# 4. Run tests again (expect passes)
uv run pytest tests/agents/test_specialist_agent.py -v

# 5. Commit when all green
git add vibe_core/agents/specialist_agent.py tests/agents/test_specialist_agent.py
git commit -m "feat(ARCH-026): SpecialistAgent adapter (BaseSpecialist → VibeAgent)"
```

### Acceptance Criteria (from Roadmap)

- [ ] `vibe_core/agents/specialist_agent.py` created
- [ ] `SpecialistAgent` implements `VibeAgent` protocol (agent_id + process())
- [ ] Converts Task payload → MissionContext
- [ ] Converts SpecialistResult → Task result
- [ ] Validates preconditions before execution
- [ ] Calls lifecycle hooks (on_start, on_complete, on_error)
- [ ] All 5 specialists wrapped (Planning, Coding, Testing, Deployment, Maintenance)
- [ ] Tests pass: `uv run pytest tests/agents/test_specialist_agent.py -v`

### Definition of Done

✅ All acceptance criteria met
✅ All tests passing (minimum 80% coverage)
✅ Integration test: Kernel → SpecialistAgent → PlanningSpecialist → Success
✅ Ledger audit trail verified (query DB shows task execution)
✅ Committed to git with clear message

---

## 📁 KEY FILES & REFERENCES

### Code Files to Study

| File | Purpose |
|------|---------|
| `vibe_core/agent_protocol.py` | VibeAgent interface definition |
| `vibe_core/kernel.py` | Kernel dispatch mechanism |
| `vibe_core/specialists/base_specialist.py` | BaseSpecialist interface |
| `apps/agency/specialists/planning.py` | Example specialist implementation |
| `vibe_core/agents/llm_agent.py` | Example VibeAgent implementation |

### Documentation

| Document | Content |
|----------|---------|
| `docs/roadmap/phase_2_6_hybrid_integration.json` | ⭐ YOUR ROADMAP (JSON system) |
| `docs/architecture/ROADMAP_HYBRID_INTEGRATION.md` | Detailed design document |
| `docs/architecture/ARCHITECTURE_CURRENT_STATE.md` | Current architecture state |
| `docs/architecture/SPECIALIST_AGENT_CONTRACT.md` | BaseSpecialist contract |
| `CLAUDE.md` | System snapshot (updated to Phase 2.6) |

### Tests to Reference

| Test File | Learn From |
|-----------|------------|
| `tests/core/test_kernel.py` | How to use Kernel + Ledger |
| `tests/agents/test_llm_agent.py` | How to test VibeAgent implementations |
| `tests/test_planning_workflow.py` | How specialists are currently used |

---

## 🚨 IMPORTANT NOTES

### What NOT to Do

❌ **NO Dirty Hacks**
- No `exec()` or `eval()` for code execution
- No string parsing of LLM responses (proper JSON parsing only)
- No bypassing type safety

❌ **NO Architecture Astronautics**
- Don't build new abstraction layers beyond what's needed
- Don't refactor existing code unnecessarily
- Stick to the roadmap tasks

❌ **NO Breaking Changes**
- Existing tests MUST still pass
- Backward compatibility required
- Specialists should work standalone AND via Kernel

### What TO Do

✅ **Test-First Development**
- Write tests BEFORE implementation
- Aim for 80%+ coverage
- Run tests after every change

✅ **Clean Architecture**
- Follow existing patterns (VibeAgent protocol)
- Clear separation of concerns
- Proper type hints

✅ **Incremental Progress**
- One task at a time (ARCH-026, then ARCH-027, etc.)
- Commit after each task completion
- Update roadmap JSON progress_tracking

---

## 🔍 TROUBLESHOOTING

### If Tests Fail

1. **Check imports:** vibe_core paths, not agency_os paths
2. **Check signatures:** Task.payload structure, MissionContext fields
3. **Check mocks:** Use MockLLMProvider for LLM tests, real DB for Specialists
4. **Check Ledger:** SQLite file path (use `:memory:` for tests)

### If Integration Breaks

1. **Verify VibeAgent protocol:** Does SpecialistAgent have `agent_id` + `process()`?
2. **Verify Kernel registration:** Is agent added to `kernel.agent_registry`?
3. **Verify Task structure:** Does payload contain required fields?
4. **Check Ledger:** Is VibeLedger initialized? Are records being created?

### Common Errors

**Error:** `AttributeError: 'BaseSpecialist' object has no attribute 'agent_id'`
- **Fix:** SpecialistAgent wraps BaseSpecialist, doesn't inherit from it

**Error:** `TypeError: process() missing required positional argument`
- **Fix:** VibeAgent.process() takes Task, BaseSpecialist.execute() takes MissionContext

**Error:** `KeyError: 'mission_id'`
- **Fix:** Ensure Task payload contains all required MissionContext fields

---

## 📊 SUCCESS METRICS

### Phase 0 (ARCH-026, ARCH-027, ARCH-027B) Complete When:

- ✅ SpecialistAgent adapter implemented and tested
- ✅ SimpleLLMAgent has tool-use capability (WriteFile, ReadFile)
- ✅ Integration test passes: Kernel dispatches BOTH agent types
- ✅ Ledger audit trail complete (all executions recorded)
- ✅ All existing tests still pass (backward compatibility)
- ✅ 90+ tests passing (new integration tests added)

### Phase 1 (ARCH-028) - Next Session

- Advanced Scheduler with priority queues
- Multi-agent coordination
- Resource limits (max_concurrent)

### Phase 2 (ARCH-029, ARCH-030) - Future Session

- Invariant Checker (Soul rules enforcement)
- Conflict Resolver (Body > Soul > Mind precedence)

---

## 🚀 GETTING STARTED (NEXT AGENT)

### Recommended Workflow

```bash
# 1. Boot system and review context
./bin/system-boot.sh

# 2. Check current task
./bin/next-task.py

# 3. Read roadmap
cat docs/roadmap/phase_2_6_hybrid_integration.json | jq '.phases[0].tasks[0]'

# 4. Study reference files
vim vibe_core/agent_protocol.py
vim vibe_core/specialists/base_specialist.py
vim vibe_core/agents/llm_agent.py

# 5. Write tests FIRST
vim tests/agents/test_specialist_agent.py
uv run pytest tests/agents/test_specialist_agent.py -v  # Should fail

# 6. Implement adapter
vim vibe_core/agents/specialist_agent.py

# 7. Run tests until green
uv run pytest tests/agents/test_specialist_agent.py -v

# 8. Run full test suite (ensure no regressions)
uv run pytest tests/ -v

# 9. Commit when green
git add vibe_core/agents/specialist_agent.py tests/agents/test_specialist_agent.py
git commit -m "feat(ARCH-026): SpecialistAgent adapter (BaseSpecialist → VibeAgent)"
git push

# 10. Update roadmap JSON
# Mark ARCH-026 as complete in phase_2_6_hybrid_integration.json

# 11. Move to ARCH-027
./bin/next-task.py
```

---

## 📞 QUESTIONS TO ASK USER (If Needed)

1. **Should SpecialistAgent be in `vibe_core/agents/` or `apps/agency/agents/`?**
   - Recommendation: `vibe_core/agents/` (it's a kernel-level adapter, not app-specific)

2. **Should existing Specialist tests be updated to use Kernel dispatch?**
   - Recommendation: Add NEW integration tests, keep existing tests as-is (backward compatibility)

3. **What should happen if specialist preconditions fail?**
   - Current: Return `{"success": False, "error": "..."}`
   - Alternative: Raise `PreconditionError` exception?

---

## 🎯 FINAL CHECKLIST BEFORE STARTING

- [ ] Read this handover document completely
- [ ] Review `docs/roadmap/phase_2_6_hybrid_integration.json`
- [ ] Study `vibe_core/agent_protocol.py` (VibeAgent interface)
- [ ] Study `vibe_core/specialists/base_specialist.py` (BaseSpecialist interface)
- [ ] Read ARCH-026 acceptance criteria
- [ ] Understand Test-First workflow
- [ ] Ready to write tests for SpecialistAgent

---

**GOOD LUCK! YOU'VE GOT THIS!** 🚀

The hardest part (understanding the problem) is done. Now it's clean implementation following clear specifications.

**Remember:** ARCH-026 is the keystone. Once Specialists work with Kernel, everything else (tool-use, scheduling, governance) becomes straightforward additions.

---

**END OF HANDOVER**
