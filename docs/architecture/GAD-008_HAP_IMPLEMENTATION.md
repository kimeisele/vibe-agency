# GAD-008: Hierarchical Agent Pattern (HAP) Implementation

**Version:** 1.0
**Date:** 2025-11-21
**Status:** IMPLEMENTED (ARCH-005 through ARCH-009)
**Related Roadmap:** [Phase 2.5 Foundation Scalability](../roadmap/phase_2_5_foundation.json)

---

## Executive Summary

The **Hierarchical Agent Pattern (HAP)** refactors vibe-agency from a monolithic orchestrator into a specialist-driven architecture. Each SDLC phase is now owned by a dedicated specialist agent with:

- **Isolated Logic**: Phase-specific workflows extracted from orchestrator
- **Persistent State**: All decisions logged to SQLite (audit trail)
- **Quality Gates**: Built-in pass/fail enforcement with automatic repair loops
- **Tool Safety**: Capability-based security via playbook-driven declarations

This document explains:
1. How the HAP pattern works (conceptually)
2. Each specialist's responsibilities and workflow
3. The orchestrator's role as a pure router/coordinator
4. The critical repair loop (failure → retry) mechanism

---

## Part 1: HAP Architecture Overview

### The Core Concept

**Before (Monolithic):**
```
CoreOrchestrator
├── All PLANNING logic (500+ LOC)
├── All CODING logic (1000+ LOC)
├── All TESTING logic (500+ LOC)
├── All DEPLOYMENT logic (500+ LOC)
└── All MAINTENANCE logic (300+ LOC)
```

**After (HAP):**
```
CoreOrchestrator (< 200 LOC)
├── PlanningSpecialist (phase-specific logic)
├── CodingSpecialist (phase-specific logic)
├── TestingSpecialist (phase-specific logic)
├── DeploymentSpecialist (phase-specific logic)
└── MaintenanceSpecialist (phase-specific logic)

Shared:
├── BaseSpecialist (abstract contract)
├── SpecialistResult (return type with success/next_phase)
└── AgentRegistry (dynamic specialist lookup)
```

### The HAP Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                   SDLC Workflow                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  1. Load Phase from Manifest                            │
│     current_phase = manifest.current_phase              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  2. Get Specialist (AgentRegistry)                      │
│     specialist = get_phase_handler(current_phase)       │
│     → Looks up specialist class dynamically             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  3. Validate Preconditions                              │
│     specialist.validate_preconditions(context)          │
│     → Check required artifacts exist                    │
│     → Check phase matches expected value                │
└─────────────────────────────────────────────────────────┘
                          │
                    Yes ◄─┴─► No
                          │      │
                    Continue    Error (Stop)
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  4. Execute Phase Workflow                              │
│     result = specialist.execute(context)                │
│     → Run phase-specific logic                          │
│     → Generate artifacts                                │
│     → Return SpecialistResult(success=?, next_phase=?)  │
└─────────────────────────────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
         success=True           success=False
              │                       │
              ▼                       ▼
        ┌──────────────┐      ┌─────────────┐
        │ Transition   │      │ REPAIR LOOP │
        │ to next_phase│      │ Go back to  │
        │              │      │ CODING for  │
        │              │      │ fixes       │
        └──────────────┘      └─────────────┘
              │                       │
              └───────────┬───────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │ Save manifest with new phase    │
         │ (persists state to JSON + SQLite│
         └─────────────────────────────────┘
```

---

## Part 2: The Five Specialists

### 1. PlanningSpecialist (PLANNING phase)

**Workflow:**
1. Analyze requirements from initial prompt
2. Break down into features
3. Design architecture
4. Create feature_spec.json artifact
5. Transition to CODING

**Key Decisions:**
- Scope negotiation (what to build, what to defer)
- Architecture patterns (monolithic vs microservices, etc.)
- Technology stack selection

**Artifacts Generated:**
- `feature_spec.json` - Detailed feature specifications
- `architecture.json` - System architecture design
- `research_brief.json` - Research findings

**Returns:**
- `success=True` → Next phase: CODING
- `success=False` → (Rare) Keep in PLANNING for retry

---

### 2. CodingSpecialist (CODING phase)

**Workflow:**
1. Validate feature_spec.json from PLANNING
2. Analyze specifications
3. Generate code artifacts
4. Generate test stubs
5. Generate documentation
6. Validate output quality
7. Create code_gen_spec.json artifact
8. Transition to TESTING

**Key Decisions:**
- Code generation strategy (template-based, LLM-assisted, etc.)
- File structure and organization
- Test approach (unit, integration, E2E)

**Safety Guardrails (via ToolSafetyGuard):**
- Anti-blindness: Must read file before editing
- Blast radius: No directory deletions allowed
- Capability-based: Only allowed tools from playbook

**Artifacts Generated:**
- `generated_code/**/*.py` - Generated source code
- `code_gen_spec.json` - Code generation specification
- `test_plan.json` - Test planning document

**Returns:**
- `success=True` → Next phase: TESTING
- `success=False` → (Should not happen, but possible if generation fails catastrophically)

---

### 3. TestingSpecialist (TESTING phase) — **THE CRITICAL ONE**

**Workflow:**
1. Load code_gen_spec.json from CODING
2. Identify test target directory
3. Run pytest via subprocess
4. Parse test results
5. Generate qa_report.json
6. **Check if tests passed** ← THE CRITICAL GATE
7. If tests FAILED: **Return success=False (triggers repair loop)**
8. If tests PASSED: Return success=True, next_phase=AWAITING_QA_APPROVAL

**The Quality Gate (lines 267-282 of testing.py):**
```python
# Quality gate decision: fail if tests didn't pass
if not tests_passed:
    logger.error("❌ Quality gate FAILED: Tests did not pass")
    return SpecialistResult(
        success=False,  # ← CRITICAL: Signals REPAIR LOOP
        error=f"Tests failed: {test_results['failed']} failures, {test_results['errors']} errors",
    )

# All tests passed - move to next phase
return SpecialistResult(
    success=True,
    next_phase="AWAITING_QA_APPROVAL",
    artifacts=[str(context.project_root / "qa_report.json")],
)
```

**Artifacts Generated:**
- `qa_report.json` - Comprehensive test metrics and results

**Returns:**
- `success=False` → **REPAIR LOOP: Orchestrator must route back to CODING phase**
- `success=True` → Next phase: AWAITING_QA_APPROVAL

**This is the "Strict Gate"** that enforces quality before promotion.

---

### 4. DeploymentSpecialist (DEPLOYMENT phase)

**Workflow:**
1. Load qa_report.json from TESTING (quality gate proof)
2. Verify AWAITING_QA_APPROVAL status
3. Check deployment manifest requirements
4. Execute deployment steps (via tool calls)
5. Generate deploy_receipt.json
6. Validate deployment succeeded
7. Transition to PRODUCTION

**Key Safety Checks:**
- Requires approved QA report (proof tests passed)
- Requires explicit manifest declaration (what gets deployed)
- Validates post-deployment checks pass

**Artifacts Generated:**
- `deploy_receipt.json` - Deployment execution record
- `rollback_info.json` - Rollback instructions if needed

**Returns:**
- `success=True` → Next phase: PRODUCTION
- `success=False` → Rollback, stay in DEPLOYMENT for retry

---

### 5. MaintenanceSpecialist (MAINTENANCE phase)

**Workflow:**
1. Monitor system health
2. Log operational metrics
3. Flag issues for remediation
4. Generate maintenance reports
5. Stay in MAINTENANCE (end of SDLC cycle)

**Artifacts Generated:**
- `maintenance_report.json` - Health metrics and observations

**Returns:**
- `success=True` → Stay in PRODUCTION (mission complete)
- `success=False` → Flag issue, escalate to human

---

## Part 3: The Repair Loop (Critical Wiring)

### The Problem

**Without the repair loop** (pre-ARCH-010):
```
CODING (generates code)
   ↓
TESTING (tests fail)
   ↓
AWAITING_QA_APPROVAL (wrong! tests didn't pass)
   ↓
DEPLOYMENT (deploys broken code)
   ↓
Disaster 💥
```

### The Solution

**With the repair loop** (ARCH-010):
```
CODING (generates code)
   ↓
TESTING (tests fail)
   ├─ TestingSpecialist returns: success=False
   ├─ Orchestrator checks result.success
   └─ Detects failure → LOOP BACK TO CODING
   ↓
CODING (REPAIR MODE - context includes qa_report.json with failures)
   ├─ Fixes bugs based on test failures
   ├─ Regenerates code
   └─ Returns to TESTING
   ↓
TESTING (re-run tests)
   ├─ Tests PASS
   └─ TestingSpecialist returns: success=True
   ↓
AWAITING_QA_APPROVAL (now we can move forward)
   ↓
DEPLOYMENT (safe!)
```

### Implementation in CoreOrchestrator

**Location:** `apps/agency/orchestrator/core_orchestrator.py`, `run_full_sdlc()` and `execute_phase()` methods

**Current Code (INCOMPLETE):**
```python
# execute_phase() - lines 1731-1767
def execute_phase(self, manifest: ProjectManifest) -> None:
    handler = self.get_phase_handler(manifest.current_phase)
    handler.execute(manifest)  # ← Returns result, but we ignore it!
    # NO CHECK FOR RESULT STATUS!
```

**Required Logic (ARCH-010):**
```python
# execute_phase() should be:
def execute_phase(self, manifest: ProjectManifest) -> bool:
    """
    Execute current phase and check result.

    Returns:
        True if phase succeeded (move to next phase)
        False if phase failed (stay in current phase for retry)
    """
    handler = self.get_phase_handler(manifest.current_phase)

    # Get result (not just void)
    result = handler.execute(manifest)

    # CHECK RESULT STATUS
    if not result.success:
        logger.error(f"❌ Phase {manifest.current_phase.value} FAILED")
        logger.error(f"   Error: {result.error}")
        # THE REPAIR LOOP:
        # If TESTING failed, transition back to CODING for fixes
        if manifest.current_phase == ProjectPhase.TESTING:
            logger.warning("🔄 REPAIR LOOP: Returning to CODING phase for bug fixes")
            manifest.current_phase = ProjectPhase.CODING
            self.save_project_manifest(manifest)
            return False  # Retry same phase (which is now CODING)
        else:
            raise PhaseFailed(f"Phase {manifest.current_phase.value} failed: {result.error}")

    # Phase succeeded - move to next phase if specified
    if result.next_phase:
        logger.info(f"✅ {manifest.current_phase.value} succeeded → {result.next_phase}")
        manifest.current_phase = ProjectPhase(result.next_phase)

    self.save_project_manifest(manifest)
    return True
```

### The Loop in run_full_sdlc()

```python
def run_full_sdlc(self, project_id: str) -> None:
    manifest = self.load_project_manifest(project_id)

    # Keep looping until PRODUCTION
    while manifest.current_phase != ProjectPhase.PRODUCTION:
        try:
            success = self.execute_phase(manifest)  # Now returns bool
            # If execute_phase() returned False, loop continues
            # (manifest is in CODING, tries again)

            # Reload manifest for next iteration
            manifest = self.load_project_manifest(project_id)

        except PhaseFailed as e:
            logger.error(f"Phase failed unrecoverably: {e}")
            break
```

---

## Part 4: The SpecialistResult Contract

**Location:** `vibe_core/specialists/base_specialist.py`, lines 64-89

```python
@dataclass
class SpecialistResult:
    """Result of specialist execution."""

    success: bool                          # Whether execution completed successfully
    next_phase: str | None = None         # Recommended next SDLC phase (or None)
    artifacts: list[str] = None           # List of generated artifact paths
    decisions: list[dict[str, Any]] = None # Key decisions made
    error: str | None = None              # Error message if success=False
```

**What each field means:**

| Field | Meaning | Example |
|-------|---------|---------|
| `success=True` | Phase completed successfully | TestingSpecialist: all tests pass |
| `success=False` | Phase failed (retry/repair needed) | TestingSpecialist: tests failed |
| `next_phase="CODING"` | Recommended next phase | TestingSpecialist: "AWAITING_QA_APPROVAL" |
| `next_phase=None` | Stay in current phase | (Rare, used for error recovery) |
| `artifacts=["path/to/file.json"]` | Files generated | CodingSpecialist: ["code_gen_spec.json"] |
| `error="Tests failed: 5 failures"` | Error detail for logging/repair | TestingSpecialist failure reason |

---

## Part 5: Specialist Responsibilities Summary

| Specialist | Phase | Entry Gate | Exit Gate | Repair Logic |
|-----------|-------|-----------|-----------|--------------|
| **Planning** | PLANNING | Prompt exists | feature_spec.json created | (None - first phase) |
| **Coding** | CODING | feature_spec.json exists | code_gen_spec.json created | Takes qa_report.json, fixes bugs |
| **Testing** | TESTING | code_gen_spec.json exists | **Quality gate enforced** | Returns success=False to trigger repair |
| **Deployment** | DEPLOYMENT | qa_report.json PASSED | deploy_receipt.json created | Rollback if deployment fails |
| **Maintenance** | MAINTENANCE | System in PRODUCTION | N/A (end state) | Monitor and escalate issues |

---

## Part 6: Key Design Decisions (GAD Alignment)

### GAD-002: Hybrid Quality Gates
- **Decision 1**: Hierarchical orchestrator (✅ HAP pattern)
- **Decision 2**: Blocking gates enforced by specialists (✅ TestingSpecialist)
- **Decision 3**: Schema validation in orchestrator (✅ save_artifact())
- **Decision 4**: Continuous auditing (✅ run_horizontal_audits())

### GAD-003: File-Based Delegation
- **File Protocol**: Request/response JSON files in `.delegation/`
- **Specialist Integration**: Specialists request intelligence via orchestrator.execute_agent()

### GAD-004: Durable State
- **Phase 1**: Mission state in SQLite (ARCH-003)
- **Phase 2**: Quality gate results recorded in manifest (ARCH-010 pending)

### GAD-005: Pre-Action Kernel
- **Specialist Safety**: ToolSafetyGuard enforces tool access rules
- **Orchestrator Safety**: KernelViolationError prevents critical file overwrites

### GAD-006: Tool Safety Guard
- **Anti-blindness**: Specialist must read file before editing (CodingSpecialist)
- **Blast radius**: No rm -rf allowed (prevents accidental deletions)
- **Playbook-based**: Allowed tools declared in playbook YAML

---

## Part 7: Implementation Status

### ARCH-005: BaseSpecialist Interface ✅
- **Status**: COMPLETE
- **Location**: `vibe_core/specialists/base_specialist.py`
- **Key Exports**: `BaseSpecialist`, `MissionContext`, `SpecialistResult`

### ARCH-006 through ARCH-008: Individual Specialists ✅
- **Status**: COMPLETE (5 specialists implemented)
- **Location**: `apps/agency/specialists/*.py`
  - `planning.py` - PlanningSpecialist
  - `coding.py` - CodingSpecialist
  - `testing.py` - TestingSpecialist
  - `deployment.py` - DeploymentSpecialist
  - `maintenance.py` - MaintenanceSpecialist

### ARCH-009: Orchestrator Refactoring ✅
- **Status**: COMPLETE (pure routing logic)
- **Location**: `apps/agency/orchestrator/core_orchestrator.py`
- **Key Method**: `get_phase_handler()` uses AgentRegistry for dynamic lookup

### ARCH-010: Repair Loop Wiring (THIS TASK) ⏳
- **Status**: IN PROGRESS
- **What's Needed**:
  1. Update orchestrator to check `result.success`
  2. Implement repair loop logic for test failures
  3. Document wiring in this file ✅

---

## Part 8: Testing the Repair Loop

### Test Scenario: Code → Tests Fail → Repair → Tests Pass

```python
def test_repair_loop_integration():
    """Validate that orchestrator loops back to CODING when tests fail."""

    # 1. Start at CODING
    manifest.current_phase = ProjectPhase.CODING

    # 2. Execute CODING phase (generates code)
    result = coding_specialist.execute(context)
    assert result.success == True
    assert result.next_phase == "TESTING"
    manifest.current_phase = ProjectPhase.TESTING

    # 3. Execute TESTING phase (tests fail)
    result = testing_specialist.execute(context)
    assert result.success == False  # ← CRITICAL ASSERTION
    assert "tests failed" in result.error.lower()

    # 4. Orchestrator detects failure
    # (This is what ARCH-010 adds)
    if not result.success and manifest.current_phase == ProjectPhase.TESTING:
        manifest.current_phase = ProjectPhase.CODING  # REPAIR LOOP!

    # 5. Execute CODING again (fix mode)
    context.metadata["previous_qa_report"] = qa_report_with_failures
    result = coding_specialist.execute(context)
    assert result.success == True  # Now code is fixed

    # 6. Execute TESTING again (should pass now)
    result = testing_specialist.execute(context)
    assert result.success == True  # ← Tests pass now!
    assert result.next_phase == "AWAITING_QA_APPROVAL"
```

---

## Part 9: Troubleshooting

### Symptom: Broken code gets deployed

**Cause**: Orchestrator not checking TestingSpecialist result status

**Fix (ARCH-010)**:
```python
# In core_orchestrator.py execute_phase():
result = handler.execute(manifest)  # Get the result!
if not result.success:              # Check it!
    # Handle failure appropriately
```

### Symptom: Tests fail but orchestrator continues to AWAITING_QA_APPROVAL

**Same cause**: Missing repair loop logic

**Fix**: See Part 3 (The Repair Loop) implementation

### Symptom: Repair loop infinite loops (CODING → TESTING → CODING → ...)

**Cause**: CodingSpecialist not actually fixing bugs (needs context with qa_report)

**Fix**: Pass `qa_report.json` to CodingSpecialist in repair mode:
```python
context.metadata["previous_qa_report"] = qa_report  # Coder knows what to fix
```

---

## Conclusion

The HAP pattern with the repair loop ensures:

1. **Isolation**: Each phase is independent (can be tested, updated separately)
2. **Quality**: Quality gates are enforced before promotion (no broken code escapes)
3. **Reliability**: Failed code automatically triggers repair (no manual intervention)
4. **Visibility**: All decisions logged to SQLite (audit trail, debugging)
5. **Scalability**: Adding new phases = adding new specialists (no orchestrator changes)

This document will be updated as ARCH-010 (repair loop wiring) is completed.
