# 🏛️ GAD-002: Core SDLC Orchestration Architecture
**Grand Architecture Decision - Lead Architect Review**

**Date:** 2025-11-14
**Status:** 🔍 DRAFT (Awaiting Approval)
**Lead Architect:** Claude
**Reviewers:** kimeisele, Gemini
**Dependencies:** GAD-001 (Research Integration)

---

## Executive Summary

This document addresses **ten critical architectural gaps** discovered during the GAD-001 implementation review. While GAD-001 successfully integrated the Research sub-framework into Planning, it revealed that the current `orchestrator.py` is **incomplete** - it only orchestrates the PLANNING phase, not the entire SDLC.

**Core Problem:** We have a "Planning-Framework-Orchestrator" instead of a "Core SDLC Orchestrator."

This GAD defines the architectural decisions needed to transform `orchestrator.py` into a complete **Core OS Orchestrator** that manages:
- **Structural Architecture** (Decisions 1-5): Orchestration, governance, validation, scaling
- **Runtime Architecture** (Decisions 6-10): Agent invocation, cost management, HITL, recovery, knowledge lifecycle

**Update History:**
- **v1.0 (Initial):** Decisions 1-5 (Structural Architecture)
- **v1.1 (Addendum):** Decisions 6-10 (Runtime & Operations Architecture) - added after critical Lead Architect review

---

## Problem Statement

Based on code analysis (commit `12bc9b0`), the following architectural gaps exist:

### Structural Architecture Gaps (Decisions 1-5)

| Priority | Gap | Impact |
|----------|-----|--------|
| **P0** | SDLC-Orchestrator incomplete | Only PLANNING phase works; CODING/TESTING/DEPLOY have no execution logic |
| **P1** | system_steward_framework not integrated | AUDITOR and LEAD_ARCHITECT agents exist but are never invoked |
| **P1** | Schema validation missing | `ORCHESTRATION_data_contracts.yaml` exists but is not enforced |
| **P2** | Horizontal governance undefined | No mechanism to run cross-cutting audits (e.g., prompt security) |
| **P2** | Multi-project support unclear | Multiple workspaces exist but no concurrent execution model |

### Runtime & Operations Gaps (Decisions 6-10)

| Priority | Gap | Impact |
|----------|-----|--------|
| **P0** | Agent invocation missing | `_execute_agent_placeholder()` returns mock data; no real LLM integration |
| **P1** | Cost management missing | No budget tracking, no rate limiting; risk of runaway costs |
| **P1** | HITL mechanism undefined | `AWAITING_QA_APPROVAL` state exists but has no implementation |
| **P2** | State recovery undefined | Orchestrator crashes lose partial progress; expensive re-execution |
| **P2** | Knowledge lifecycle undefined | Knowledge bases have no versioning, freshness tracking, or update mechanism |

**Without solving these problems, the system cannot execute even a single SDLC workflow end-to-end.**

---

## Decision 1: SDLC Orchestrator Architecture (P0)

### Problem Analysis

Current state (from `orchestrator.py:279`):
```python
def handle_planning_phase(self, project_id: str) -> None:
    """Execute PLANNING phase with all sub-states."""
    # ... complete implementation for PLANNING
    manifest.current_phase = ProjectPhase.CODING  # ← Sets state but does nothing
```

**Missing:** `handle_coding_phase()`, `handle_testing_phase()`, `handle_deployment_phase()`, `handle_maintenance_phase()`

### Solution Options

#### Option A: Monolithic Orchestrator (All-in-One)
**Description:** Extend `orchestrator.py` with all phase handlers in a single class.

```python
class Orchestrator:
    def handle_planning_phase(self, project_id: str) -> None: ...
    def handle_coding_phase(self, project_id: str) -> None: ...
    def handle_testing_phase(self, project_id: str) -> None: ...
    def handle_deployment_phase(self, project_id: str) -> None: ...
    def handle_maintenance_phase(self, project_id: str) -> None: ...

    def execute_full_sdlc(self, project_id: str) -> None:
        """Master loop through all phases"""
```

**Pros:**
- Simple to understand (one file)
- Easy to debug (linear flow)
- No inter-service communication

**Cons:**
- Will grow to 2000+ lines
- Violates single responsibility principle
- Hard to maintain long-term
- Cannot scale to parallel projects

#### Option B: Hierarchical Orchestrator (Core + Phase Handlers)
**Description:** Split into a Core Orchestrator (state machine) + specialized Phase Handlers (framework-specific logic).

```
agency_os/core_system/orchestrator/
├── core_orchestrator.py         # State machine, transitions, manifest management
├── phase_handlers/
│   ├── planning_handler.py      # Existing handle_planning_phase() logic
│   ├── coding_handler.py        # NEW: Invokes 02_code_gen_framework
│   ├── testing_handler.py       # NEW: Invokes 03_qa_framework
│   ├── deployment_handler.py    # NEW: Invokes 04_deploy_framework
│   └── maintenance_handler.py   # NEW: Invokes 05_maintenance_framework
```

**Pros:**
- Separation of concerns (state machine vs. business logic)
- Each handler is independently testable
- Easier to extend/modify individual phases
- Scales to multiple parallel projects (each handler is stateless)

**Cons:**
- More files to navigate
- Slightly more complex initialization

#### Option C: Event-Driven Orchestrator (Microservices-style)
**Description:** Each framework is a separate service with its own state machine. Orchestrator acts as event bus.

**Pros:**
- Maximum scalability
- True polyglot support (frameworks can be in different languages)

**Cons:**
- Overkill for current scope (5 frameworks)
- Requires message queue infrastructure
- Much higher complexity

### **🎯 RECOMMENDATION: Option B (Hierarchical Orchestrator)**

**Rationale:**
- **Pragmatic:** Balances simplicity (Option A) and scalability (Option C)
- **Matches current architecture:** Each framework (01-05) already has its own directory
- **Testable:** Each phase handler can be unit tested independently
- **Future-proof:** Can evolve to Option C if needed (handlers become services)

**Implementation:**
```python
# core_orchestrator.py
class CoreOrchestrator:
    def __init__(self):
        self.handlers = {
            ProjectPhase.PLANNING: PlanningHandler(self),
            ProjectPhase.CODING: CodingHandler(self),
            ProjectPhase.TESTING: TestingHandler(self),
            ProjectPhase.DEPLOYMENT: DeploymentHandler(self),
            ProjectPhase.MAINTENANCE: MaintenanceHandler(self)
        }

    def execute_phase(self, manifest: ProjectManifest) -> None:
        """Execute current phase"""
        handler = self.handlers[manifest.current_phase]
        handler.execute(manifest)

    def transition_to_next_phase(self, manifest: ProjectManifest) -> None:
        """Apply state machine transitions from workflow YAML"""
        # Load transitions from ORCHESTRATION_workflow_design.yaml
        # Update manifest.current_phase
        # Invoke next handler
```

---

## Decision 2: system_steward_framework Integration (P1)

### Problem Analysis

Current state:
```
system_steward_framework/
└── agents/
    ├── AUDITOR/           # Exists but never called
    ├── LEAD_ARCHITECT/    # Exists but never called
    └── SSF_ROUTER/        # Exists but never called
```

These agents are **governance agents** (horizontal capabilities), not SDLC agents (vertical capabilities).

### Solution Options

#### Option A: Blocking Quality Gates
**Description:** Auditor is invoked **before** each phase transition as a blocking quality gate.

```yaml
transitions:
  - name: "T1_StartCoding"
    from_state: "PLANNING"
    to_state: "CODING"
    quality_gates:
      - agent: "AUDITOR"
        check: "prompt_security_scan"
        blocking: true
```

**Pros:**
- Enforces quality before progression
- Clear "stop" point if issues found
- Fits existing state machine model

**Cons:**
- Increases transition time (blocking)
- Can become bottleneck
- Might block valid progressions (false positives)

#### Option B: Asynchronous Audit Reports
**Description:** Auditor runs in parallel, generates reports, but does not block progression.

```python
# After each phase completes
audit_report = async_invoke_auditor(manifest)
manifest.artifacts['audit_reports'].append(audit_report)
# Continue to next phase (non-blocking)
```

**Pros:**
- No blocking (fast progression)
- User can review reports later
- Good for continuous improvement

**Cons:**
- Security issues might not be caught until production
- Requires manual follow-up on reports

#### Option C: Hybrid (Critical Checks Block, Others Async)
**Description:** Define critical checks (security, data loss) as blocking, others as async.

```yaml
auditor_checks:
  - name: "prompt_security"
    severity: "critical"
    blocking: true
  - name: "performance_optimization"
    severity: "info"
    blocking: false
```

**Pros:**
- Best of both worlds
- Protects critical issues
- Allows fast progression for non-critical items

**Cons:**
- More complex configuration
- Requires clear severity taxonomy

### **🎯 RECOMMENDATION: Option C (Hybrid Blocking/Async)**

**Rationale:**
- **Security-first:** Critical issues (prompt injection, PII leaks) must block
- **Velocity-friendly:** Non-critical issues don't slow down development
- **Configurable:** Easy to adjust blocking rules as system matures

**Implementation:**
```python
# core_orchestrator.py
def apply_transition(self, manifest: ProjectManifest, transition: Transition) -> None:
    """Apply state transition with quality gates"""

    # Run blocking quality gates
    for gate in transition.quality_gates:
        if gate.blocking:
            result = self.invoke_auditor(gate.check, manifest)
            if result.status == "FAILED":
                raise QualityGateFailure(f"{gate.check} failed: {result.message}")

    # Run async quality gates (fire and forget)
    for gate in transition.quality_gates:
        if not gate.blocking:
            asyncio.create_task(self.invoke_auditor(gate.check, manifest))

    # Proceed with transition
    manifest.current_phase = transition.to_state
```

---

## Decision 3: Schema Validation (P1)

### Problem Analysis

Current state:
- `ORCHESTRATION_data_contracts.yaml` defines schemas (373 lines, 8 artifacts)
- `orchestrator.py:253` saves artifacts **without validation**:

```python
def save_artifact(self, project_id: str, artifact_name: str, data: Dict[str, Any]) -> None:
    with open(artifact_path, 'w') as f:
        json.dump(data, f, indent=2)  # ❌ No schema check
```

**Result:** Invalid artifacts can flow between phases, causing runtime errors.

### Solution Options

#### Option A: Centralized Validation in Orchestrator
**Description:** Orchestrator validates artifacts before saving/loading.

```python
def save_artifact(self, project_id: str, artifact_name: str, data: Dict[str, Any]) -> None:
    # Load schema from ORCHESTRATION_data_contracts.yaml
    schema = self.load_schema(artifact_name)
    jsonschema.validate(data, schema)  # ✅ Validate
    with open(artifact_path, 'w') as f:
        json.dump(data, f, indent=2)
```

**Pros:**
- Single point of enforcement
- Easy to debug (all validation errors happen in orchestrator)
- Agents don't need to know about schemas

**Cons:**
- Orchestrator becomes more complex
- Validation errors are late (after agent execution)

#### Option B: Agent-Level Validation
**Description:** Each agent validates its own output before returning.

```python
# Inside VIBE_ALIGNER agent logic
def generate_feature_spec(self, inputs: Dict) -> Dict:
    feature_spec = self.build_feature_spec(inputs)
    validate_against_schema(feature_spec, "feature_spec.schema.json")
    return feature_spec
```

**Pros:**
- Early validation (catch errors at source)
- Agents are responsible for their contracts
- Easier to debug (agent knows its own schema)

**Cons:**
- Every agent needs validation logic (code duplication)
- Inconsistent implementations (some agents might forget)

#### Option C: Hybrid (Agents Validate Output, Orchestrator Validates Handoff)
**Description:** Agents validate their output (optional but recommended), Orchestrator validates at phase boundaries (mandatory).

**Pros:**
- Defense in depth (two validation layers)
- Catches errors early (in agent) and late (in orchestrator)
- Enforces contracts at critical handoff points

**Cons:**
- Most complex option
- Potential for double validation overhead

### **🎯 RECOMMENDATION: Option A (Centralized in Orchestrator)**

**Rationale:**
- **Pragmatic for current architecture:** Agents are prompts (not code), can't do validation themselves yet
- **Single source of truth:** Orchestrator enforces contracts defined in `data_contracts.yaml`
- **Future-proof:** When agents become code (Phase 3+), can evolve to Option C

**Implementation:**
```python
# core_orchestrator.py
class SchemaValidator:
    def __init__(self, contracts_yaml_path: Path):
        with open(contracts_yaml_path, 'r') as f:
            self.contracts = yaml.safe_load(f)
        self.schemas = self._load_schemas()

    def validate_artifact(self, artifact_name: str, data: Dict[str, Any]) -> None:
        """Validate artifact against schema"""
        schema = self.schemas.get(artifact_name)
        if not schema:
            raise ValueError(f"No schema found for {artifact_name}")

        jsonschema.validate(data, schema)  # Raises ValidationError if invalid

# In orchestrator
def save_artifact(self, project_id: str, artifact_name: str, data: Dict[str, Any]) -> None:
    self.validator.validate_artifact(artifact_name, data)  # ✅ Validate first
    # ... then save
```

---

## Decision 4: Horizontal Governance (P2)

### Problem Analysis

Current capabilities are **vertical** (phase-specific):
- PLANNING agents (VIBE_ALIGNER, LEAN_CANVAS_VALIDATOR)
- CODING agents (future)
- TESTING agents (future)

But we need **horizontal** capabilities that span all phases:
- Security audits (prompt injection, PII leaks)
- Performance checks (complexity limits)
- Compliance (licensing, attribution)

**Question:** When/how are horizontal audits triggered?

### Solution Options

#### Option A: Pre-Deployment Batch Audit
**Description:** Run all horizontal audits as a single batch before DEPLOYMENT phase.

```python
# Before T4_StartDeployment transition
def pre_deployment_audit(self, manifest: ProjectManifest) -> None:
    auditor = AuditorAgent()

    # Audit all agent prompts
    prompt_security_report = auditor.audit_prompt_security(manifest)

    # Audit all code artifacts
    code_quality_report = auditor.audit_code_quality(manifest)

    # Audit all data flows
    privacy_report = auditor.audit_data_privacy(manifest)

    manifest.artifacts['audit_reports'] = {
        'prompt_security': prompt_security_report,
        'code_quality': code_quality_report,
        'privacy': privacy_report
    }
```

**Pros:**
- Simple to implement (single audit point)
- All audits happen together
- Clear "audit report" artifact

**Cons:**
- Late detection (issues found at end of SDLC)
- Expensive rework if issues found

#### Option B: Continuous Auditing (Per-Phase)
**Description:** Run relevant horizontal audits after each phase completes.

```yaml
states:
  - name: "PLANNING"
    horizontal_audits:
      - "prompt_security_scan"
      - "data_privacy_scan"

  - name: "CODING"
    horizontal_audits:
      - "code_security_scan"
      - "license_compliance_scan"
```

**Pros:**
- Early detection (issues found in each phase)
- Cheaper to fix (less rework)
- Spreads audit load across SDLC

**Cons:**
- More complex (multiple audit points)
- Potential for audit fatigue

#### Option C: On-Demand Auditing (User-Triggered)
**Description:** User requests audits manually (like optional RESEARCH phase).

```bash
$ vibe-cli.py audit --project=my-app --type=security
```

**Pros:**
- Maximum flexibility
- No forced delays

**Cons:**
- Users might forget to audit
- Not enforced (security risk)

### **🎯 RECOMMENDATION: Option B (Continuous Auditing Per-Phase)**

**Rationale:**
- **Shift-left security:** Catch issues early when they're cheap to fix
- **Aligned with SDLC:** Each phase has natural audit checkpoints
- **Configurable:** Can define which audits run in which phases (via YAML)

**Implementation:**
```python
# core_orchestrator.py
def complete_phase(self, manifest: ProjectManifest) -> None:
    """Called when a phase completes"""

    # Load horizontal audits for this phase
    phase_config = self.workflow['states'][manifest.current_phase]
    horizontal_audits = phase_config.get('horizontal_audits', [])

    # Run audits (async, non-blocking by default)
    audit_results = []
    for audit_type in horizontal_audits:
        result = self.run_horizontal_audit(audit_type, manifest)
        audit_results.append(result)

    # Store audit results
    manifest.artifacts.setdefault('horizontal_audits', {})[manifest.current_phase] = audit_results
```

---

## Decision 5: Multi-Project Scaling (P2)

### Problem Analysis

Current state:
```bash
/workspaces/
├── agency_toolkit/           # Workspace 1
├── prabhupad_os/             # Workspace 2
├── temple_companion/         # Workspace 3
└── vibe_research_framework/  # Workspace 4
```

Multiple workspaces exist, but `orchestrator.py` is **single-project**:
```python
def handle_planning_phase(self, project_id: str) -> None:
    """Execute PLANNING phase for ONE project"""
```

**Question:** Can orchestrator handle multiple projects concurrently?

### Solution Options

#### Option A: Single-Instance (Current Model)
**Description:** One `Orchestrator` instance per project (sequential processing).

```bash
# User runs orchestrator manually per project
$ python orchestrator.py /repo agency_toolkit
$ python orchestrator.py /repo prabhupad_os
```

**Pros:**
- Simple (current implementation)
- No concurrency issues
- Easy to debug

**Cons:**
- Slow (projects run one at a time)
- Doesn't scale

#### Option B: Multi-Instance (Parallel Workers)
**Description:** Spawn multiple `Orchestrator` instances (e.g., via multiprocessing).

```python
# orchestrator_pool.py
def run_projects_parallel(project_ids: List[str]) -> None:
    with multiprocessing.Pool(processes=4) as pool:
        pool.map(run_orchestrator_for_project, project_ids)
```

**Pros:**
- True parallelism (uses multiple CPU cores)
- Scales to many projects
- No shared state (isolated processes)

**Cons:**
- Complex inter-process communication
- Resource contention (CPU, memory, API rate limits)

#### Option C: Async Single-Instance (Cooperative Multitasking)
**Description:** One `Orchestrator` instance that uses `asyncio` to interleave project execution.

```python
# core_orchestrator.py
async def execute_phase_async(self, manifest: ProjectManifest) -> None:
    """Execute phase with async agent invocations"""
    handler = self.handlers[manifest.current_phase]
    await handler.execute_async(manifest)

# Main loop
async def run_all_projects(self, project_ids: List[str]) -> None:
    tasks = [self.execute_phase_async(pid) for pid in project_ids]
    await asyncio.gather(*tasks)
```

**Pros:**
- Good concurrency (I/O-bound workloads like API calls)
- Single process (simpler deployment)
- Shared state (easier to coordinate)

**Cons:**
- Doesn't use multiple CPU cores (Python GIL)
- Requires async/await throughout codebase

### **🎯 RECOMMENDATION: Option A for Phase 3, Plan for Option C in Phase 4**

**Rationale:**
- **Current need:** Single projects are the primary use case (e.g., one user working on one project)
- **Future need:** Multi-project will be needed for CI/CD (batch processing of multiple PRs)
- **Migration path:** Option A → Option C is straightforward (add `async` keywords), A → B is a rewrite

**Implementation (Phase 3):**
```python
# Keep current single-project model
orchestrator = Orchestrator(repo_root)
orchestrator.handle_planning_phase(project_id)
```

**Implementation (Phase 4, when needed):**
```python
# Add async support
orchestrator = AsyncOrchestrator(repo_root)
await orchestrator.run_all_projects([project1, project2, project3])
```

---

## Summary of Recommendations

| Decision | Problem | Recommendation | Priority |
|----------|---------|----------------|----------|
| 1 | SDLC Orchestrator | **Option B: Hierarchical Orchestrator** (Core + Phase Handlers) | P0 |
| 2 | Steward Integration | **Option C: Hybrid Blocking/Async** (Critical checks block, others async) | P1 |
| 3 | Schema Validation | **Option A: Centralized in Orchestrator** (Single enforcement point) | P1 |
| 4 | Horizontal Governance | **Option B: Continuous Per-Phase Auditing** (Shift-left security) | P2 |
| 5 | Multi-Project Scaling | **Option A now, Option C later** (Single-instance → Async) | P2 |

---

## Implementation Roadmap

### Phase 3: Core SDLC Orchestration (Weeks 4-6)

**Goal:** Transform orchestrator into full SDLC orchestrator.

**Tasks:**
1. ✅ Create `core_orchestrator.py` (state machine logic)
2. ✅ Extract `planning_handler.py` from current `orchestrator.py`
3. ✅ Create `coding_handler.py` (stub for now, invoke `02_code_gen_framework`)
4. ✅ Create `testing_handler.py` (stub for now, invoke `03_qa_framework`)
5. ✅ Create `deployment_handler.py` (stub for now, invoke `04_deploy_framework`)
6. ✅ Create `maintenance_handler.py` (stub for now, invoke `05_maintenance_framework`)
7. ✅ Implement schema validation in `core_orchestrator.py`
8. ✅ Update `ORCHESTRATION_workflow_design.yaml` with quality gates
9. ✅ Test full SDLC flow: PLANNING → CODING → TESTING → DEPLOYMENT → PRODUCTION

**Success Criteria:**
- ✅ Orchestrator can execute all 5 phases (even if handlers are stubs)
- ✅ State transitions work according to `ORCHESTRATION_workflow_design.yaml`
- ✅ Artifacts are validated against `ORCHESTRATION_data_contracts.yaml`
- ✅ All existing tests pass (no breaking changes)

### Phase 4: Governance Integration (Weeks 7-8)

**Goal:** Integrate `system_steward_framework` as horizontal governance.

**Tasks:**
1. ✅ Define blocking vs. async audit rules in YAML
2. ✅ Implement `invoke_auditor()` method in `core_orchestrator.py`
3. ✅ Add prompt security scan (blocking) at PLANNING → CODING transition
4. ✅ Add code security scan (blocking) at TESTING → DEPLOYMENT transition
5. ✅ Add async audits (performance, best practices) at each phase completion
6. ✅ Create audit report artifact schema
7. ✅ Test AUDITOR blocking behavior (inject failing audit to verify blocking works)

**Success Criteria:**
- ✅ AUDITOR is invoked at phase transitions
- ✅ Blocking audits can prevent progression
- ✅ Async audits generate reports without blocking
- ✅ Audit reports are stored in `manifest.artifacts['horizontal_audits']`

### Phase 5: Multi-Project Support (Weeks 9-10)

**Goal:** Enable concurrent execution of multiple projects (async model).

**Tasks:**
1. ✅ Refactor handlers to be async (`async def execute_async(...)`)
2. ✅ Add `run_all_projects()` method to orchestrator
3. ✅ Implement project queue management
4. ✅ Add rate limiting for API calls (prevent quota exhaustion)
5. ✅ Test parallel execution of 3+ projects
6. ✅ Update documentation with multi-project usage

**Success Criteria:**
- ✅ Orchestrator can run multiple projects concurrently
- ✅ Projects don't interfere with each other (proper isolation)
- ✅ API rate limits are respected

---

## Migration Strategy

### Backward Compatibility

**Critical:** This refactoring must not break existing workflows.

**Strategy:**
1. **Keep old `orchestrator.py` as fallback** (rename to `orchestrator_v1_legacy.py`)
2. **New code uses `core_orchestrator.py`** (import path changes)
3. **Deprecation warnings** in old orchestrator: "This module is deprecated, use core_orchestrator"
4. **Remove legacy code** after 2 release cycles (once confident in new system)

### Testing Strategy

**Unit Tests:**
- Test each phase handler independently (mock agent invocations)
- Test schema validation (valid/invalid artifacts)
- Test state transitions (valid/invalid transitions)

**Integration Tests:**
- Test full SDLC flow (PLANNING → PRODUCTION)
- Test error loops (TESTING failure → CODING)
- Test quality gate blocking (AUDITOR blocks bad code)

**End-to-End Tests:**
- Run real project through full SDLC
- Verify all artifacts are created
- Verify audit reports are generated

---

## Success Criteria (GAD-002 Complete)

### Phase 3 Success:
- ✅ Core SDLC Orchestrator works end-to-end (PLANNING → PRODUCTION)
- ✅ All 5 phase handlers exist and are invoked correctly
- ✅ Schema validation enforces data contracts
- ✅ No breaking changes to existing workflows

### Phase 4 Success:
- ✅ AUDITOR is integrated and invokes horizontal audits
- ✅ Blocking audits can prevent progression to next phase
- ✅ Audit reports are stored and accessible

### Phase 5 Success:
- ✅ Multiple projects can run concurrently (async model)
- ✅ API rate limits are respected
- ✅ Project isolation is maintained

---

## 🔴 ADDENDUM: Runtime & Operations Architecture

**Critical Discovery:** During final Lead Architect review, **5 additional architectural gaps** were identified in the **runtime and operations** domain. These gaps are equally critical but were initially missed because they focus on "how the system runs" rather than "how the system is structured."

Gemini's 5 questions addressed **structural architecture** (orchestration, governance, validation).
The following 5 questions address **runtime architecture** (execution, cost, recovery, monitoring).

---

## Decision 6: Agent Invocation Architecture (P0)

### Problem Analysis

Current state (from `orchestrator.py:478`):
```python
def _execute_agent_placeholder(self, agent_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    PLACEHOLDER: Execute agent by loading prompt and calling LLM.
    For Phase 2, this returns mock data.
    Phase 3 will implement actual LLM invocation via Anthropic API.
    """
    print(f"   🤖 Executing {agent_name}... (mock)")
    return {}  # ❌ MOCK DATA
```

**The Gap:**
- `prompt_runtime.py` exists (517 lines, composes prompts from fragments)
- `requirements.txt` lists `anthropic>=0.18.0`
- **BUT:** No code connects `prompt_runtime.execute_task()` → Anthropic API → parse response

**The Question:** How do we bridge `composed_prompt` → `agent_output`?

### Solution Options

#### Option A: Direct Anthropic SDK Integration
**Description:** Call Anthropic API directly from orchestrator/handlers.

```python
from anthropic import Anthropic

def _execute_agent(self, agent_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Compose prompt
    runtime = PromptRuntime()
    prompt = runtime.execute_task(agent_name, task_id="main", context=inputs)

    # 2. Call Anthropic API
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    # 3. Parse response
    return json.loads(response.content[0].text)
```

**Pros:**
- Simple, direct, no abstraction overhead
- Full control over API parameters
- Easy to debug

**Cons:**
- Tightly coupled to Anthropic (vendor lock-in)
- No retry/backoff logic
- No cost tracking
- No streaming support

#### Option B: LangChain Integration
**Description:** Use LangChain as LLM abstraction layer.

```python
from langchain.llms import Anthropic
from langchain.chains import LLMChain

def _execute_agent(self, agent_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    llm = Anthropic(model="claude-3-5-sonnet-20241022")
    chain = LLMChain(llm=llm, prompt=compose_prompt(...))
    result = chain.run(inputs)
    return parse_result(result)
```

**Pros:**
- Provider-agnostic (can swap Anthropic → OpenAI → Local)
- Built-in retry, caching, logging
- Rich ecosystem (tools, memory, agents)

**Cons:**
- Heavy dependency (100+ packages)
- Abstraction leakage (LangChain-specific concepts)
- Overhead for simple use cases
- Learning curve

#### Option C: Custom LLM Client (Thin Wrapper)
**Description:** Build a lightweight `LLMClient` class with exactly what we need.

```python
class LLMClient:
    def __init__(self, provider: str = "anthropic"):
        self.provider = provider
        self.client = self._init_client()
        self.cost_tracker = CostTracker()

    def invoke(self, prompt: str, model: str, max_tokens: int) -> str:
        # Retry logic with exponential backoff
        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )

                # Track cost
                self.cost_tracker.record(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    model=model
                )

                return response.content[0].text
            except RateLimitError:
                time.sleep(2 ** attempt)

        raise LLMInvocationError("Max retries exceeded")
```

**Pros:**
- Lightweight (no heavy dependencies)
- Full control over behavior
- Built-in retry, cost tracking, error handling
- Easy to extend (add streaming, caching later)

**Cons:**
- Must implement retry/rate-limiting ourselves
- Not provider-agnostic (but could be extended)

### **🎯 RECOMMENDATION: Option C (Custom LLM Client)**

**Rationale:**
- **Pragmatic:** We need retry, cost tracking, error handling - but not LangChain's full ecosystem
- **Control:** Full visibility into LLM invocation behavior
- **Extensible:** Can add features as needed (streaming, caching, multi-provider)
- **Testable:** Easy to mock for testing

**Implementation:**
```python
# agency_os/core_system/runtime/llm_client.py
class LLMClient:
    """Thin wrapper around LLM providers with retry, cost tracking, and error handling"""

# In core_orchestrator.py
def _execute_agent(self, agent_name: str, task_id: str, inputs: Dict) -> Dict:
    # Compose prompt
    runtime = PromptRuntime()
    prompt = runtime.execute_task(agent_name, task_id, inputs)

    # Invoke LLM
    llm = LLMClient(provider="anthropic")
    response = llm.invoke(prompt, model="claude-3-5-sonnet-20241022", max_tokens=4096)

    # Parse JSON output
    return self._parse_agent_response(response)
```

---

## Decision 7: Cost Management & Rate Limiting (P1)

### Problem Analysis

**Current state:**
- Full SDLC = ~15-20 agent invocations
- PLANNING alone = 6 agents (if RESEARCH enabled)
- At $3/MTok input, $15/MTok output:
  - Average prompt: ~50K tokens (input)
  - Average response: ~5K tokens (output)
  - **Cost per agent: ~$0.23**
  - **Cost per full SDLC: ~$3.50**

**The Gap:** No cost tracking, no budget limits, no rate limiting.

**The Question:** How do we prevent runaway costs and API quota exhaustion?

### Solution Options

#### Option A: Post-Execution Cost Reports
**Description:** Track costs after execution, report to user.

```python
# After workflow completes
cost_report = {
    'total_input_tokens': 750000,
    'total_output_tokens': 80000,
    'total_cost_usd': 3.45,
    'breakdown_by_phase': {...}
}
manifest.artifacts['cost_report'] = cost_report
```

**Pros:**
- Simple to implement
- No blocking (fast execution)

**Cons:**
- Reactive (user sees cost after spending)
- No budget enforcement

#### Option B: Pre-Execution Cost Estimation + Approval
**Description:** Estimate cost before starting workflow, ask user to approve.

```python
# Before starting SDLC
estimated_cost = orchestrator.estimate_cost(manifest)
print(f"Estimated cost: ${estimated_cost:.2f}")
if not user_approves():
    raise BudgetExceededError("User rejected estimated cost")
```

**Pros:**
- Proactive (user approves before spending)
- Prevents unexpected bills

**Cons:**
- Estimates may be inaccurate
- Adds friction to workflow

#### Option C: Hybrid (Budget Limits + Real-Time Tracking)
**Description:** Set budget limits, track in real-time, stop if exceeded.

```python
# In project_manifest.json
"budget": {
    "max_cost_usd": 10.00,
    "current_cost_usd": 0.00,
    "alert_threshold": 0.80
}

# In LLMClient
def invoke(self, prompt: str, ...) -> str:
    # Check budget before invocation
    if self.cost_tracker.current_cost >= self.budget.max_cost:
        raise BudgetExceededError(f"Budget limit reached: ${self.budget.max_cost}")

    # ... invoke LLM ...

    # Update budget
    self.cost_tracker.record(input_tokens, output_tokens, model)
```

**Pros:**
- Proactive budget enforcement
- Real-time visibility
- Prevents runaway costs

**Cons:**
- More complex implementation
- Requires cost estimation formulas

### **🎯 RECOMMENDATION: Option C (Hybrid Budget System)**

**Rationale:**
- **Safety:** Prevents accidental $100+ bills
- **Transparency:** User sees cost in real-time
- **Configurable:** Different budgets for different project types (prototype: $5, production: $50)

**Implementation:**
```python
# In project_manifest.json schema
"budget": {
    "max_cost_usd": 10.00,        # Hard limit
    "alert_threshold": 0.80,      # Warn at 80%
    "current_cost_usd": 0.00,
    "cost_breakdown": {
        "planning": 0.50,
        "coding": 0.00,
        ...
    }
}

# Rate limiting for multi-project
class RateLimiter:
    """Token bucket algorithm for API rate limiting"""
    def __init__(self, requests_per_minute: int = 50):
        self.bucket = TokenBucket(capacity=requests_per_minute)

    def acquire(self) -> None:
        """Block until token available"""
        self.bucket.consume(1)
```

---

## Decision 8: HITL (Human-in-the-Loop) Mechanism (P1)

### Problem Analysis

Current state (from `ORCHESTRATION_workflow_design.yaml:54`):
```yaml
- name: "AWAITING_QA_APPROVAL"
  description: "Ein langlebiger (durable) Wartezustand, der auf eine manuelle HITL-Genehmigung wartet."
  responsible_framework: "Orchestrator (HITL)"
```

**The Gap:** This state exists in YAML but has **no implementation**. How does the orchestrator "wait" for human approval?

**The Question:** Blocking wait (orchestrator blocks) or durable wait (orchestrator stops, resumes later)?

### Solution Options

#### Option A: Blocking Wait (CLI Prompt)
**Description:** Orchestrator blocks until user approves via CLI.

```python
def _wait_for_qa_approval(self, manifest: ProjectManifest) -> None:
    print("\n" + "="*60)
    print("QA APPROVAL REQUIRED")
    print("="*60)
    print(f"QA Report: {manifest.artifacts['qa_report']}")
    print("\nApprove deployment? (yes/no): ")

    response = input().strip().lower()
    if response != "yes":
        raise QARejectError("User rejected QA approval")
```

**Pros:**
- Simple to implement
- No infrastructure needed

**Cons:**
- Blocks orchestrator process (can't handle other projects)
- Not suitable for async workflows
- User must stay at terminal

#### Option B: Durable Wait (State Persistence + Resume)
**Description:** Orchestrator saves state and exits. User approves later, orchestrator resumes.

```python
# Orchestrator exits after saving state
manifest.current_phase = ProjectPhase.AWAITING_QA_APPROVAL
manifest.artifacts['qa_approval_pending'] = True
self.save_project_manifest(manifest)
print("Waiting for QA approval. Run 'vibe-cli resume' to continue.")
sys.exit(0)

# User approves via CLI
$ vibe-cli approve-qa --project=my-app

# Orchestrator resumes
$ vibe-cli resume --project=my-app
manifest = self.load_project_manifest(project_id)
if manifest.current_phase == ProjectPhase.AWAITING_QA_APPROVAL:
    if manifest.artifacts.get('qa_approved'):
        self.transition_to_deployment(manifest)
```

**Pros:**
- Non-blocking (orchestrator can exit)
- User approves at their convenience
- Works for async workflows

**Cons:**
- More complex (requires state persistence)
- Multiple CLI commands needed

#### Option C: Event-Driven (Webhook/Notification)
**Description:** Orchestrator registers webhook, user approves via external system (Slack, Email, Web UI).

```python
# Orchestrator registers webhook
webhook_url = self.register_approval_webhook(manifest.project_id)
send_notification(
    type="qa_approval_required",
    message=f"Approve deployment: {webhook_url}",
    channels=["slack", "email"]
)

# External system calls webhook
POST /api/approvals/{project_id}
{
  "approved": true,
  "approver": "kimeisele"
}

# Orchestrator resumes on webhook callback
def on_approval_webhook(project_id: str, approved: bool):
    manifest = self.load_project_manifest(project_id)
    if approved:
        self.transition_to_deployment(manifest)
```

**Pros:**
- Most flexible (approve from anywhere)
- Best UX (Slack/Email notification)
- Audit trail (who approved, when)

**Cons:**
- Requires infrastructure (webhook server, notification service)
- Most complex option

### **🎯 RECOMMENDATION: Option B for Phase 3, Option C for Phase 4**

**Rationale:**
- **Phase 3:** Durable wait is good enough (CLI-based approval)
- **Phase 4:** Upgrade to event-driven (Slack/Email integration)
- **Migration path:** B → C is straightforward (add webhook layer)

**Implementation (Phase 3):**
```python
# core_orchestrator.py
def handle_testing_phase(self, manifest: ProjectManifest) -> None:
    # ... run tests ...

    # Enter durable wait
    manifest.current_phase = ProjectPhase.AWAITING_QA_APPROVAL
    self.save_project_manifest(manifest)

    print("\n🔔 QA Approval Required")
    print(f"Review: workspaces/{manifest.project_id}/artifacts/qa/qa_report.json")
    print(f"Approve: vibe-cli approve-qa --project={manifest.project_id}")
    print(f"Reject:  vibe-cli reject-qa --project={manifest.project_id}")

# vibe-cli.py
@cli.command()
def approve_qa(project: str):
    """Approve QA and proceed to deployment"""
    orchestrator = Orchestrator()
    manifest = orchestrator.load_project_manifest(project)

    if manifest.current_phase != ProjectPhase.AWAITING_QA_APPROVAL:
        raise StateError("Project is not awaiting QA approval")

    manifest.artifacts['qa_approved'] = True
    manifest.artifacts['qa_approver'] = getpass.getuser()
    orchestrator.save_project_manifest(manifest)

    # Resume orchestrator
    orchestrator.handle_deployment_phase(manifest)
```

---

## Decision 9: State Recovery & Checkpointing (P2)

### Problem Analysis

**Current state:**
- `orchestrator.py` saves `project_manifest.json` (tracks `current_phase`)
- **BUT:** What if orchestrator crashes **during** agent execution?

**Scenario:**
```
PLANNING phase starts
├─ MARKET_RESEARCHER executes → ✅ completes
├─ TECH_RESEARCHER executes → ⏳ in progress
└─ ORCHESTRATOR CRASHES (power outage, OOM, etc.)
```

**On restart:** TECH_RESEARCHER must re-execute (costs $0.23, takes 30 seconds).

**The Question:** Can we checkpoint partial progress?

### Solution Options

#### Option A: No Checkpointing (Re-Execute Everything)
**Description:** On crash, restart entire phase from beginning.

**Pros:**
- Simple (no checkpointing logic)
- Idempotent (same inputs → same outputs)

**Cons:**
- Expensive (re-run all agents)
- Slow (30-60 seconds per agent)

#### Option B: Agent-Level Checkpointing
**Description:** Save each agent's output immediately after completion.

```python
def _execute_research_state(self, manifest: ProjectManifest) -> None:
    # Try to load checkpoint
    checkpoint = self.load_checkpoint(manifest, 'research')

    if 'market_analysis' not in checkpoint:
        market_analysis = self._execute_agent("MARKET_RESEARCHER", {})
        checkpoint['market_analysis'] = market_analysis
        self.save_checkpoint(manifest, 'research', checkpoint)

    if 'tech_analysis' not in checkpoint:
        tech_analysis = self._execute_agent("TECH_RESEARCHER", {})
        checkpoint['tech_analysis'] = tech_analysis
        self.save_checkpoint(manifest, 'research', checkpoint)

    # ... continue with FACT_VALIDATOR ...
```

**Pros:**
- Resumes from last successful agent
- Saves cost and time

**Cons:**
- More complex (checkpoint management)
- Disk I/O overhead

#### Option C: Hybrid (Checkpoint Only Expensive Agents)
**Description:** Only checkpoint agents that are expensive (long prompts, slow execution).

```python
CHECKPOINT_AGENTS = ["MARKET_RESEARCHER", "TECH_RESEARCHER", "CODE_GENERATOR"]

def _execute_agent(self, agent_name: str, inputs: Dict) -> Dict:
    if agent_name in CHECKPOINT_AGENTS:
        checkpoint = self.load_checkpoint(manifest, agent_name)
        if checkpoint:
            return checkpoint

    result = self._invoke_llm(agent_name, inputs)

    if agent_name in CHECKPOINT_AGENTS:
        self.save_checkpoint(manifest, agent_name, result)

    return result
```

**Pros:**
- Best cost/complexity tradeoff
- Fast agents don't pay checkpoint overhead

**Cons:**
- Must maintain CHECKPOINT_AGENTS list

### **🎯 RECOMMENDATION: Option B for Phase 4 (if needed)**

**Rationale:**
- **Not critical for Phase 3:** Orchestrator crashes are rare (stable Python process)
- **Valuable for Phase 4:** When running long multi-project workflows
- **Easy to add later:** Can implement checkpointing without breaking existing code

**Implementation (Phase 4, if needed):**
```python
# In project workspace
workspaces/my_app/
└── .checkpoints/
    └── planning_research_20251114_143022.json  # Timestamp-based checkpoints

# In core_orchestrator.py
def _execute_agent_with_checkpoint(self, agent_name: str, inputs: Dict) -> Dict:
    checkpoint_key = f"{manifest.current_phase}_{agent_name}"
    checkpoint = self.checkpoint_manager.load(manifest.project_id, checkpoint_key)

    if checkpoint:
        print(f"✓ Resuming {agent_name} from checkpoint")
        return checkpoint

    result = self._execute_agent(agent_name, inputs)

    self.checkpoint_manager.save(manifest.project_id, checkpoint_key, result)
    return result
```

---

## Decision 10: Knowledge Base Lifecycle (P2)

### Problem Analysis

**Current state:**
```
agency_os/01_planning_framework/knowledge/research/
├── RESEARCH_market_sizing_formulas.yaml       # When was this last updated?
├── RESEARCH_competitor_analysis_templates.yaml
└── RESEARCH_red_flag_taxonomy.yaml
```

**The Gap:** Knowledge bases are static files with no version tracking, no freshness indicators.

**The Question:** How do we keep knowledge bases current?

### Solution Options

#### Option A: Manual Updates (Git Commits)
**Description:** Knowledge bases are updated via git commits (like code).

**Pros:**
- Simple (no special tooling)
- Git history tracks changes

**Cons:**
- No freshness metadata
- No automated updates
- Can become stale

#### Option B: Versioned Knowledge Bases
**Description:** Add metadata to knowledge YAML files.

```yaml
# RESEARCH_market_sizing_formulas.yaml
metadata:
  version: "2.1"
  last_updated: "2025-11-14"
  maintained_by: "MARKET_RESEARCHER"
  freshness_policy: "quarterly_review"
  next_review_date: "2026-02-14"

formulas:
  tam_sam_som:
    description: "Total Addressable Market calculation"
    formula: "TAM = (Number of potential customers) × (ARPU)"
    ...
```

**Pros:**
- Clear versioning
- Freshness indicators
- Review reminders

**Cons:**
- Must maintain metadata manually
- No automated enforcement

#### Option C: Living Knowledge Base (Agent-Updated)
**Description:** Agents can update knowledge bases based on new learnings.

```python
# After MARKET_RESEARCHER completes
if new_competitor_found:
    knowledge_updater = KnowledgeBaseUpdater()
    knowledge_updater.propose_update(
        file="RESEARCH_competitor_analysis_templates.yaml",
        section="common_competitors",
        addition={"name": "NewCompetitor", "category": "SaaS"}
    )
    # Human reviews and approves update
```

**Pros:**
- Knowledge bases stay current
- Captures new learnings automatically

**Cons:**
- Complex (requires update mechanism)
- Risk of knowledge pollution (bad updates)

### **🎯 RECOMMENDATION: Option B for Phase 3, Consider Option C for Phase 5+**

**Rationale:**
- **Phase 3:** Versioned metadata is low-effort, high-value
- **Phase 5+:** Agent-updated knowledge is powerful but requires governance
- **Hybrid:** Agents propose updates, humans approve

**Implementation (Phase 3):**
```yaml
# Standard metadata header for all knowledge YAML files
metadata:
  schema_version: "1.0"
  knowledge_id: "RESEARCH_market_sizing_formulas"
  version: "2.1"
  last_updated: "2025-11-14"
  last_updated_by: "kimeisele"
  freshness_policy: "quarterly_review"
  next_review_date: "2026-02-14"
  status: "active"  # active | deprecated | draft
  changelog:
    - version: "2.1"
      date: "2025-11-14"
      changes: "Added SaaS-specific TAM formulas"
    - version: "2.0"
      date: "2025-08-01"
      changes: "Restructured for AOS v0.2"

# Add validation in PromptRuntime
def _load_knowledge_file(self, path: str) -> str:
    content = yaml.safe_load(open(path))

    # Check freshness
    next_review = content['metadata']['next_review_date']
    if datetime.now() > datetime.fromisoformat(next_review):
        logger.warning(f"Knowledge base {path} is past review date: {next_review}")

    return content
```

---

## Updated Summary of Recommendations

| Decision | Problem | Recommendation | Priority |
|----------|---------|----------------|----------|
| 1 | SDLC Orchestrator | **Hierarchical Orchestrator** (Core + Phase Handlers) | P0 |
| 2 | Steward Integration | **Hybrid Blocking/Async** (Critical checks block, others async) | P1 |
| 3 | Schema Validation | **Centralized in Orchestrator** (Single enforcement point) | P1 |
| 4 | Horizontal Governance | **Continuous Per-Phase Auditing** (Shift-left security) | P2 |
| 5 | Multi-Project Scaling | **Single-instance now, Async later** (Option A → C) | P2 |
| **6** | **Agent Invocation** | **Custom LLM Client** (Thin wrapper with retry, cost tracking) | **P0** |
| **7** | **Cost Management** | **Hybrid Budget System** (Real-time tracking + limits) | **P1** |
| **8** | **HITL Mechanism** | **Durable Wait (Phase 3) → Event-Driven (Phase 4)** | **P1** |
| **9** | **State Recovery** | **Agent-Level Checkpointing** (Phase 4, if needed) | **P2** |
| **10** | **Knowledge Lifecycle** | **Versioned Metadata** (Phase 3) | **P2** |

---

## Updated Implementation Roadmap

### Phase 3: Core SDLC Orchestration (Weeks 4-6)

**Goal:** Transform orchestrator into full SDLC orchestrator + Agent invocation.

**Tasks:**
1. ✅ Create `core_orchestrator.py` (state machine logic)
2. ✅ Extract `planning_handler.py` from current `orchestrator.py`
3. ✅ Create `coding_handler.py`, `testing_handler.py`, `deployment_handler.py`, `maintenance_handler.py`
4. ✅ Implement schema validation in `core_orchestrator.py`
5. ✅ **NEW: Create `llm_client.py`** (Decision 6)
6. ✅ **NEW: Connect `prompt_runtime.py` → `llm_client.py`** (Decision 6)
7. ✅ **NEW: Implement budget tracking in `project_manifest.json`** (Decision 7)
8. ✅ **NEW: Implement durable wait for HITL** (Decision 8)
9. ✅ **NEW: Add knowledge base metadata headers** (Decision 10)
10. ✅ Update `ORCHESTRATION_workflow_design.yaml` with quality gates
11. ✅ Test full SDLC flow: PLANNING → CODING → TESTING → DEPLOYMENT → PRODUCTION

**Success Criteria:**
- ✅ Orchestrator can execute all 5 phases (real LLM invocations, not mocks)
- ✅ Budget limits are enforced
- ✅ HITL approval workflow works (CLI-based)
- ✅ Artifacts are validated against schemas
- ✅ All existing tests pass

### Phase 4: Governance Integration (Weeks 7-8)

**Goal:** Integrate `system_steward_framework` + upgrade HITL to event-driven.

**Tasks:**
1. ✅ Define blocking vs. async audit rules in YAML
2. ✅ Implement `invoke_auditor()` method in `core_orchestrator.py`
3. ✅ Add prompt security scan (blocking) at PLANNING → CODING transition
4. ✅ Add code security scan (blocking) at TESTING → DEPLOYMENT transition
5. ✅ Add async audits (performance, best practices) at each phase completion
6. ✅ Create audit report artifact schema
7. ✅ **NEW: Upgrade HITL to event-driven (Slack/Email notifications)** (Decision 8)
8. ✅ **NEW: Implement agent-level checkpointing (if needed)** (Decision 9)
9. ✅ Test AUDITOR blocking behavior

**Success Criteria:**
- ✅ AUDITOR is invoked at phase transitions
- ✅ Blocking audits can prevent progression
- ✅ HITL approval via Slack/Email works
- ✅ Checkpoint recovery works (if implemented)

### Phase 5: Multi-Project Support (Weeks 9-10)

**Goal:** Enable concurrent execution of multiple projects (async model).

**Tasks:**
1. ✅ Refactor handlers to be async (`async def execute_async(...)`)
2. ✅ Add `run_all_projects()` method to orchestrator
3. ✅ Implement project queue management
4. ✅ Add rate limiting for API calls (prevent quota exhaustion)
5. ✅ Test parallel execution of 3+ projects
6. ✅ **NEW: Consider agent-updated knowledge bases** (Decision 10, optional)
7. ✅ Update documentation with multi-project usage

**Success Criteria:**
- ✅ Orchestrator can run multiple projects concurrently
- ✅ Projects don't interfere with each other (proper isolation)
- ✅ API rate limits are respected
- ✅ Budgets are tracked per-project

---

## Remaining Open Questions

**Framework Integration Questions (to be addressed in GAD-003):**

1. **CODING Framework API:** What does `02_code_gen_framework` expect as input? (Need to define interface)
2. **TESTING Framework API:** What does `03_qa_framework` expect as input? (Need to define interface)

**Note:** The original "Open Questions" about Agent Invocation and HITL have been promoted to formal Decisions (6 and 8) in this addendum.

---

## Approval

**Status:** ✅ APPROVED
**Approved by:** kimeisele
**Approved on:** 2025-11-14

This document is now the official architectural blueprint for Phases 3-5 implementation.

---

**Document Version:** 1.1 (Addendum: Runtime & Operations)
**Last Updated:** 2025-11-14
**Next Review:** After Phase 3 implementation

**Changelog:**
- **v1.1 (2025-11-14):** Added Decisions 6-10 (Runtime & Operations Architecture) after critical Lead Architect review
- **v1.0 (2025-11-14):** Initial version with Decisions 1-5 (Structural Architecture)
