# ROADMAP: HYBRID AGENT INTEGRATION (Phase 2.6)

**Version:** 1.0
**Created:** 2025-11-21
**Status:** 🔴 NOT STARTED
**Goal:** Unite Kernel (ARCH-021 to ARCH-025) with Specialists (ARCH-005)

---

## 🎯 EXECUTIVE SUMMARY

**Current State:**
- ✅ Kernel exists (Scheduler, Dispatch, Ledger, LLM Integration)
- ✅ Specialists exist (Planning, Coding, Testing, Deployment, Maintenance)
- ❌ **NO CONNECTION between them!**

**Problem:**
Two parallel architectures that don't talk to each other:
- **Universe A:** `Kernel → VibeAgent → SimpleLLMAgent` (can think, cannot act)
- **Universe B:** `STEWARD → RouterBridge → BaseSpecialist` (can act, not in Kernel)

**Solution:**
Implement the **HYBRID AGENT PATTERN** - where both LLM-Agents and Specialists implement the same `VibeAgent` protocol and are dispatched by the Kernel.

**Why Brilliant:**
- **LLM-Agents:** Intelligent, non-deterministic (AI decision-making)
- **Script-Agents:** Rule-based, deterministic (Playbook workflows)
- **Both** orchestrated by same Kernel (FIFO scheduling, audit trail, resource management)
- **STEWARD** (Claude Code) submits tasks to Kernel, Kernel dispatches to appropriate agent type

---

## 📊 CURRENT STATE ANALYSIS

### What Works

| Component | Status | Details |
|-----------|--------|---------|
| **Kernel Loop** | ✅ Working | `kernel.tick()` processes tasks from queue |
| **Scheduler** | ✅ Working | FIFO queue, `submit()` and `next_task()` |
| **Ledger** | ✅ Working | SQLite audit trail for all task executions |
| **VibeAgent Protocol** | ✅ Defined | Abstract interface: `agent_id` + `process(task)` |
| **SimpleLLMAgent** | ✅ Working | Implements VibeAgent, calls LLMProvider |
| **Specialists** | ✅ Working | Planning, Coding, Testing, Deployment, Maintenance |
| **RouterBridge** | ✅ Working | Maps Playbook → Phase → Specialist |

### What's Broken

| Issue | Impact | Root Cause |
|-------|--------|------------|
| **No Integration** | Critical | `BaseSpecialist` does NOT implement `VibeAgent` protocol |
| **SimpleLLMAgent has no Tools** | High | Can only chat, cannot perform actions (no "hands") |
| **Specialists bypass Kernel** | High | Called directly by STEWARD, no Ledger audit trail |
| **No Multi-Agent Coordination** | Medium | FIFO scheduler doesn't handle resource conflicts |
| **No Invariant Checking** | Medium | Soul rules not enforced at runtime |
| **No Conflict Resolution** | Medium | Body > Soul > Mind precedence not implemented |

---

## 🏗️ THE HYBRID ARCHITECTURE (Target State)

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 7: STEWARD (Claude Code - External Operator)             │
│  - Reads mission from user                                      │
│  - Submits tasks to Kernel                                      │
│  - Monitors execution via Ledger                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 6: VibeKernel (Task Orchestration)                       │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────────┐     │
│  │  Scheduler   │→→→│   Dispatch   │→→→│    Ledger     │     │
│  │  (FIFO)      │   │ (Agent Reg.) │   │  (Audit Log)  │     │
│  └──────────────┘   └──────────────┘   └───────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
┌──────────────────────────┐   ┌──────────────────────────┐
│  TYPE 1: LLM-AGENTS      │   │  TYPE 2: SCRIPT-AGENTS   │
│  (Intelligent)           │   │  (Rule-Based)            │
├──────────────────────────┤   ├──────────────────────────┤
│ SimpleLLMAgent           │   │ SpecialistAgent Wrappers │
│  - Thinks via LLM        │   │  - PlanningAgent         │
│  - Makes decisions       │   │  - CodingAgent           │
│  - Calls Tools           │   │  - TestingAgent          │
│  (via Tool Protocol)     │   │  - DeploymentAgent       │
│                          │   │  - MaintenanceAgent      │
│  Examples:               │   │                          │
│  - Code review           │   │  Wraps BaseSpecialist    │
│  - Architecture advice   │   │  - Executes playbooks    │
│  - Refactoring suggest.  │   │  - Runs workflows        │
└──────────────────────────┘   └──────────────────────────┘
```

**Key Insight:**
- Both types implement `VibeAgent` protocol
- Both dispatched by Kernel
- Both recorded in Ledger
- LLM-Agents for intelligence, Script-Agents for execution

---

## 🗺️ INTEGRATION ROADMAP

### PHASE 1: Bridge the Gap (P0 - CRITICAL)

**Goal:** Make Specialists work with Kernel

**Tasks:**

#### ARCH-026: SpecialistAgent Adapter
**Priority:** P0
**Effort:** 2-3 hours
**Description:** Create adapter that wraps `BaseSpecialist` to implement `VibeAgent` protocol

```python
# vibe_core/agents/specialist_agent.py

class SpecialistAgent(VibeAgent):
    """
    Adapter: Makes BaseSpecialist compatible with Kernel dispatch.

    Converts:
    - Task → MissionContext (for specialist)
    - SpecialistResult → Task result (for kernel)
    """

    def __init__(self, specialist: BaseSpecialist):
        self._specialist = specialist
        self._agent_id = f"specialist-{specialist.role.lower()}"

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def process(self, task: Task) -> dict:
        # 1. Convert Task payload → MissionContext
        context = MissionContext(
            mission_id=task.payload["mission_id"],
            mission_uuid=task.payload["mission_uuid"],
            phase=task.payload["phase"],
            project_root=Path(task.payload["project_root"]),
            metadata=task.payload.get("metadata", {})
        )

        # 2. Validate preconditions
        if not self._specialist.validate_preconditions(context):
            return {
                "success": False,
                "error": "Preconditions not met"
            }

        # 3. Execute specialist
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
            return {
                "success": False,
                "error": str(e)
            }
```

**Tests:** `tests/agents/test_specialist_agent.py`
- ✅ Wrap PlanningSpecialist, register with Kernel
- ✅ Submit task → Kernel → SpecialistAgent → PlanningSpecialist
- ✅ Verify Ledger records execution
- ✅ Verify result conversion

**Definition of Done:**
- [ ] SpecialistAgent adapter implemented
- [ ] All 5 specialists wrapped (Planning, Coding, Testing, Deployment, Maintenance)
- [ ] Integration test passing (Kernel → SpecialistAgent → BaseSpecialist)
- [ ] Ledger audit trail verified

---

#### ARCH-027: Tool Protocol for SimpleLLMAgent
**Priority:** P0
**Effort:** 4-5 hours
**Description:** Give SimpleLLMAgent "hands" (ability to call tools)

**NOT the Dirty Hack!** (No `exec()` or JSON string parsing)

**Design:**

```python
# vibe_core/tools/tool_protocol.py

class ToolCall(Protocol):
    """Interface for tool invocations"""

    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        ...

class ToolRegistry:
    """Registry of available tools"""

    def __init__(self):
        self._tools: dict[str, ToolCall] = {}

    def register(self, name: str, tool: ToolCall):
        self._tools[name] = tool

    def get(self, name: str) -> ToolCall | None:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())


# vibe_core/tools/file_tools.py

class WriteFileTool(ToolCall):
    """Tool for writing files"""

    def execute(self, path: str, content: str) -> dict:
        Path(path).write_text(content)
        return {"success": True, "path": path, "bytes": len(content)}

class ReadFileTool(ToolCall):
    """Tool for reading files"""

    def execute(self, path: str) -> dict:
        content = Path(path).read_text()
        return {"success": True, "content": content}


# vibe_core/agents/llm_agent.py (UPDATED)

class SimpleLLMAgent(VibeAgent):
    """LLM-based agent with tool-use capability"""

    def __init__(
        self,
        agent_id: str,
        provider: LLMProvider,
        tool_registry: ToolRegistry | None = None,
        system_prompt: str | None = None
    ):
        self._agent_id = agent_id
        self.provider = provider
        self.tool_registry = tool_registry or ToolRegistry()
        self._system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        tools_desc = "\n".join(
            f"- {name}: {tool.__doc__}"
            for name, tool in self.tool_registry._tools.items()
        )

        return f"""You are an AI agent with access to tools.

Available tools:
{tools_desc}

To call a tool, respond with JSON:
{{"tool": "tool_name", "parameters": {{"param": "value"}}}}
"""

    def process(self, task: Task) -> dict:
        user_message = task.payload["user_message"]

        # Build messages
        messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Call LLM
        response = self.provider.chat(messages)

        # Check if response is a tool call
        if self._is_tool_call(response):
            tool_result = self._execute_tool_call(response)
            return {
                "response": response,
                "tool_result": tool_result,
                "success": True
            }

        # Regular response
        return {
            "response": response,
            "success": True
        }

    def _is_tool_call(self, response: str) -> bool:
        """Check if LLM response is a tool call"""
        try:
            data = json.loads(response.strip())
            return "tool" in data and "parameters" in data
        except:
            return False

    def _execute_tool_call(self, response: str) -> dict:
        """Execute tool call from LLM response"""
        data = json.loads(response.strip())
        tool_name = data["tool"]
        parameters = data["parameters"]

        tool = self.tool_registry.get(tool_name)
        if not tool:
            return {"error": f"Tool not found: {tool_name}"}

        return tool.execute(**parameters)
```

**Tests:** `tests/agents/test_llm_agent_tools.py`
- ✅ Register WriteFileTool, ReadFileTool
- ✅ SimpleLLMAgent calls tool via JSON response
- ✅ Tool execution recorded in Ledger
- ✅ Error handling for invalid tool calls

**Definition of Done:**
- [ ] ToolCall protocol defined
- [ ] ToolRegistry implemented
- [ ] WriteFileTool, ReadFileTool implemented
- [ ] SimpleLLMAgent updated with tool-use capability
- [ ] Integration test passing (LLM → Tool → File system)
- [ ] Ledger audit trail includes tool calls

---

### PHASE 2: Enhanced Scheduling (P1)

**Goal:** Upgrade from FIFO to intelligent scheduling

#### ARCH-028: Multi-Agent Scheduler
**Priority:** P1
**Effort:** 3-4 hours
**Description:** Add priority queues, resource limits, conflict detection

```python
# vibe_core/scheduling/advanced_scheduler.py

class TaskPriority(Enum):
    HIGH = 1
    NORMAL = 2
    LOW = 3

class AdvancedScheduler:
    """
    Scheduler with priority queues and resource management.
    """

    def __init__(self, max_concurrent: int = 3):
        self._queues = {
            TaskPriority.HIGH: [],
            TaskPriority.NORMAL: [],
            TaskPriority.LOW: []
        }
        self._running = {}  # agent_id → Task
        self._max_concurrent = max_concurrent

    def submit_task(self, task: Task, priority: TaskPriority = TaskPriority.NORMAL):
        """Submit task to priority queue"""
        self._queues[priority].append(task)

    def next_task(self) -> Task | None:
        """Get next task (highest priority first)"""
        if len(self._running) >= self._max_concurrent:
            return None  # Resource limit reached

        # Check queues in priority order
        for priority in [TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]:
            if self._queues[priority]:
                task = self._queues[priority].pop(0)
                self._running[task.agent_id] = task
                return task

        return None

    def complete_task(self, task: Task):
        """Mark task as complete, free resources"""
        if task.agent_id in self._running:
            del self._running[task.agent_id]
```

**Tests:** `tests/scheduling/test_advanced_scheduler.py`
- ✅ Submit tasks with different priorities
- ✅ High priority tasks executed first
- ✅ Resource limit enforced (max_concurrent)
- ✅ Multiple agents can run concurrently

**Definition of Done:**
- [ ] AdvancedScheduler implemented
- [ ] Priority queues working
- [ ] Resource limits enforced
- [ ] Integration with Kernel

---

### PHASE 3: Governance (P2)

**Goal:** Enforce Soul rules and conflict resolution

#### ARCH-029: Invariant Checker
**Priority:** P2
**Effort:** 2-3 hours
**Description:** Runtime enforcement of Soul rules

```python
# vibe_core/governance/invariants.py

class InvariantChecker:
    """
    Enforces Soul rules that cannot be violated.

    Soul rules define the "personality" and constraints of the system.
    """

    def __init__(self, soul_path: Path):
        self.invariants = self._load_soul(soul_path)

    def _load_soul(self, path: Path) -> dict:
        """Load soul.yaml with invariants"""
        import yaml
        return yaml.safe_load(path.read_text())

    def check(self, action: dict) -> tuple[bool, str | None]:
        """
        Check if action violates any invariants.

        Returns:
            (allowed, reason) - (True, None) if allowed, (False, reason) if blocked
        """
        # Check "never" rules
        for rule in self.invariants.get("never", []):
            if self._matches_rule(action, rule):
                return False, f"Violates Soul rule: {rule['description']}"

        # Check "always" rules
        for rule in self.invariants.get("always", []):
            if not self._matches_rule(action, rule):
                return False, f"Missing required Soul constraint: {rule['description']}"

        return True, None

    def _matches_rule(self, action: dict, rule: dict) -> bool:
        """Check if action matches rule pattern"""
        # Simple pattern matching (can be extended)
        if "tool" in rule:
            return action.get("tool") == rule["tool"]
        if "pattern" in rule:
            import re
            return bool(re.search(rule["pattern"], str(action)))
        return False
```

**Tests:** `tests/governance/test_invariant_checker.py`
- ✅ Load soul.yaml with rules
- ✅ Block actions violating "never" rules
- ✅ Enforce "always" rules
- ✅ Integration with Kernel dispatch

**Definition of Done:**
- [ ] InvariantChecker implemented
- [ ] Soul rules loaded from config/soul.yaml
- [ ] Integration with Kernel (check before dispatch)
- [ ] Tests for rule enforcement

---

#### ARCH-030: Conflict Resolver
**Priority:** P2
**Effort:** 2-3 hours
**Description:** Implement Body > Soul > Mind precedence

```python
# vibe_core/governance/resolver.py

class RuleType(Enum):
    SAFETY = 1      # Body rules (never violate)
    MISSION = 2     # Soul context (prefer to honor)
    OPTIMIZATION = 3  # Mind suggestions (if no conflict)

class ConflictResolver:
    """
    Resolves conflicts between competing rules.

    Precedence: Body > Soul > Mind
    """

    PRECEDENCE = {
        RuleType.SAFETY: 1,
        RuleType.MISSION: 2,
        RuleType.OPTIMIZATION: 3
    }

    def resolve(self, conflicts: list[dict]) -> dict:
        """
        Resolve conflicts by precedence.

        Args:
            conflicts: List of conflicting rules/decisions

        Returns:
            The winning rule (highest precedence)
        """
        if not conflicts:
            return None

        # Sort by precedence (lowest number = highest priority)
        sorted_conflicts = sorted(
            conflicts,
            key=lambda c: self.PRECEDENCE[c["type"]]
        )

        winner = sorted_conflicts[0]

        logger.info(
            f"Conflict resolved: {winner['type']} wins "
            f"(rejected: {[c['type'] for c in sorted_conflicts[1:]]})"
        )

        return winner
```

**Tests:** `tests/governance/test_conflict_resolver.py`
- ✅ Safety rules override mission rules
- ✅ Mission rules override optimization suggestions
- ✅ Logging of conflict resolution

**Definition of Done:**
- [ ] ConflictResolver implemented
- [ ] Precedence enforced (Body > Soul > Mind)
- [ ] Integration with Kernel dispatch
- [ ] Tests for conflict scenarios

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Bridge the Gap (P0)
- [ ] ARCH-026: SpecialistAgent Adapter
  - [ ] Implement adapter class
  - [ ] Wrap all 5 specialists
  - [ ] Integration tests (Kernel → Specialist)
  - [ ] Ledger audit trail verified
- [ ] ARCH-027: Tool Protocol for SimpleLLMAgent
  - [ ] Define ToolCall protocol
  - [ ] Implement ToolRegistry
  - [ ] Create WriteFileTool, ReadFileTool
  - [ ] Update SimpleLLMAgent with tool-use
  - [ ] Integration tests (LLM → Tool → File)

### Phase 2: Enhanced Scheduling (P1)
- [ ] ARCH-028: Multi-Agent Scheduler
  - [ ] Implement AdvancedScheduler
  - [ ] Add priority queues
  - [ ] Add resource limits
  - [ ] Integration with Kernel

### Phase 3: Governance (P2)
- [ ] ARCH-029: Invariant Checker
  - [ ] Implement InvariantChecker
  - [ ] Load soul.yaml rules
  - [ ] Integration with Kernel
- [ ] ARCH-030: Conflict Resolver
  - [ ] Implement ConflictResolver
  - [ ] Precedence enforcement
  - [ ] Integration with Kernel

---

## 🎯 SUCCESS CRITERIA

**Phase 1 Complete When:**
- ✅ Specialists can be dispatched by Kernel (via SpecialistAgent adapter)
- ✅ SimpleLLMAgent can call tools (WriteFile, ReadFile)
- ✅ All executions recorded in Ledger (audit trail)
- ✅ Integration tests passing (90+ tests)

**Phase 2 Complete When:**
- ✅ Multiple agents can run concurrently
- ✅ Priority queues working (high priority first)
- ✅ Resource limits enforced (max_concurrent)

**Phase 3 Complete When:**
- ✅ Soul rules enforced at runtime (InvariantChecker)
- ✅ Conflicts resolved by precedence (Body > Soul > Mind)
- ✅ All governance tests passing

---

## 🚀 VIBE CODER MINDSET

**Pragmatic Engineering:**
- ✅ Ship Phase 1 FIRST (bridge the gap)
- ✅ Phase 2 and 3 are enhancements, not blockers
- ✅ No "Dirty Hacks" (`exec()` or string parsing) - clean architecture
- ✅ Test-driven (write tests first, then implement)
- ✅ Incremental delivery (commit after each ARCH-0XX)

**NOT Architecture Astronautics:**
- ❌ No endless abstraction layers
- ❌ No "perfect" before "working"
- ❌ No bikeshedding on naming/structure
- ✅ Ship Phase 1 in 1 day
- ✅ Prove the concept works
- ✅ Iterate based on real usage

---

## 📚 REFERENCES

**Architecture Documents:**
- `docs/architecture/ARCHITECTURE_CURRENT_STATE.md` - Post-split architecture
- `docs/architecture/SPECIALIST_AGENT_CONTRACT.md` - BaseSpecialist interface
- `docs/architecture/GAD/GAD-000_operator_inversion.md` - STEWARD role
- `docs/architecture/ARCH/` - All ARCH-0XX implementation tracking

**Code Modules:**
- `vibe_core/kernel.py` - VibeKernel (ARCH-022)
- `vibe_core/scheduling/scheduler.py` - VibeScheduler (ARCH-021)
- `vibe_core/ledger.py` - VibeLedger (ARCH-024)
- `vibe_core/agent_protocol.py` - VibeAgent interface (ARCH-023)
- `vibe_core/agents/llm_agent.py` - SimpleLLMAgent (ARCH-025)
- `vibe_core/specialists/base_specialist.py` - BaseSpecialist (ARCH-005)
- `vibe_core/playbook/router_bridge.py` - RouterBridge (connects playbooks)

**Tests:**
- `tests/core/test_kernel.py` - Kernel integration tests
- `tests/test_*_workflow.py` - Specialist workflow tests (Planning, Coding, etc.)

---

## 🔄 NEXT STEPS

**Immediate Actions:**
1. **Review this roadmap** - Confirm approach with team/user
2. **Create branch:** `claude/arch-026-specialist-adapter`
3. **Start ARCH-026:** Implement SpecialistAgent adapter
4. **Write tests first:** `tests/agents/test_specialist_agent.py`
5. **Ship Phase 1:** Commit + push when integration tests pass

**Estimated Timeline:**
- Phase 1 (P0): 1 day
- Phase 2 (P1): 0.5 day
- Phase 3 (P2): 0.5 day
- **Total: ~2 days for complete integration**

---

**END OF ROADMAP**
