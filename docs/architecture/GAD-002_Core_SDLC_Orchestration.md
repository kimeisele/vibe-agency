# 🏛️ GAD-002: Core SDLC Orchestration Architecture
**Grand Architecture Decision - Lead Architect Review**

**Date:** 2025-11-14
**Status:** 🔍 DRAFT (Awaiting Approval)
**Lead Architect:** Claude
**Reviewers:** kimeisele, Gemini
**Dependencies:** GAD-001 (Research Integration)

---

## Executive Summary

This document addresses **five critical architectural gaps** discovered during the GAD-001 implementation review. While GAD-001 successfully integrated the Research sub-framework into Planning, it revealed that the current `orchestrator.py` is **incomplete** - it only orchestrates the PLANNING phase, not the entire SDLC.

**Core Problem:** We have a "Planning-Framework-Orchestrator" instead of a "Core SDLC Orchestrator."

This GAD defines the architectural decisions needed to transform `orchestrator.py` into a complete **Core OS Orchestrator** that manages all 5 lifecycle phases (PLANNING → CODING → TESTING → DEPLOYMENT → MAINTENANCE) and integrates governance, validation, and multi-project capabilities.

---

## Problem Statement

Based on code analysis (commit `12bc9b0`), the following architectural gaps exist:

| Priority | Gap | Impact |
|----------|-----|--------|
| **P0** | SDLC-Orchestrator incomplete | Only PLANNING phase works; CODING/TESTING/DEPLOY have no execution logic |
| **P1** | system_steward_framework not integrated | AUDITOR and LEAD_ARCHITECT agents exist but are never invoked |
| **P1** | Schema validation missing | `ORCHESTRATION_data_contracts.yaml` exists but is not enforced |
| **P2** | Horizontal governance undefined | No mechanism to run cross-cutting audits (e.g., prompt security) |
| **P2** | Multi-project support unclear | Multiple workspaces exist but no concurrent execution model |

**Without solving these problems, the system cannot progress beyond PLANNING.**

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
agency_os/00_system/orchestrator/
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

## Open Questions

1. **CODING Framework API:** What does `02_code_gen_framework` expect as input? (Need to define interface)
2. **TESTING Framework API:** What does `03_qa_framework` expect as input? (Need to define interface)
3. **Agent Invocation:** How do we actually invoke agent prompts? (Current implementation is mock)
   - Option A: Anthropic API directly
   - Option B: LangChain/LlamaIndex wrapper
   - Option C: Custom LLM abstraction layer
4. **HITL Mechanism:** How do we implement "AWAITING_QA_APPROVAL" durable wait state?
   - Option A: CLI prompt (blocking)
   - Option B: Web UI approval workflow
   - Option C: Slack/Discord integration

**These questions will be addressed in subsequent GADs (GAD-003, GAD-004).**

---

## Approval

**Status:** 🔍 DRAFT
**Awaiting approval from:** kimeisele

Once approved, this document becomes the architectural blueprint for Phases 3-5 implementation.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Next Review:** After Phase 3 implementation
