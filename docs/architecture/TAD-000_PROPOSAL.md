# TAD-000: Technical Architectural Document Series Proposal

**Status:** 🔬 PROPOSAL (For Review)
**Date:** 2025-11-17
**Author:** Claude Code (Architecture Analysis)
**Reviewers:** TBD

---

## Executive Summary

**Proposal:** Create a TAD (Technical Architectural Document) series that documents **implementation-level technical decisions** using the GAD-005 template (Blueprint → Implementation → HARNESS).

**Problem:** Current architecture docs are either:
- **Strategic vision** (GAD-006-008: 30% detail, future-focused)
- **Tactical implementation** (GAD-001-004: mixed, some with harness, some without)
- **Missing technical foundation** (state machine, file handling, error recovery)

**Gap:** Code exists (1583 LOC `core_orchestrator.py`, 43 tests) but lacks **technical ground truth docs** that:
1. Document actual implementation patterns
2. Prevent regression via "defense harness"
3. Serve as onboarding for new contributors
4. Stay lean like GAD-005 (not bloated like GAD-002's 1534 lines)

**Impact:**
- ✅ Technical stability through documented patterns
- ✅ Regression prevention via architecture harness
- ✅ Faster onboarding (technical truth, not vision)
- ✅ Lean documentation (GAD-005 style, not essay-style)

---

## Table of Contents

1. [Evidence: The Documentation Gap](#1-evidence-the-documentation-gap)
2. [Analysis: What TAD Solves](#2-analysis-what-tad-solves)
3. [BLUEPRINT: TAD Structure](#3-blueprint-tad-structure)
4. [HARNESS: Defense Layer Concept](#4-harness-defense-layer-concept)
5. [Proposed TAD Series](#5-proposed-tad-series)
6. [Comparison: GAD vs TAD](#6-comparison-gad-vs-tad)
7. [Decision: Approve or Refine](#7-decision-approve-or-refine)

---

## 1. Evidence: The Documentation Gap

### 1.1. Current Architecture Document Landscape

```bash
# Strategic Vision Docs (30% detail, future-focused)
docs/architecture/GAD-006_KNOWLEDGE_DEPT_VISION.md          (786 lines)
docs/architecture/GAD-007_STEWARD_GOVERNANCE_VISION.md      (854 lines)
docs/architecture/GAD-008_INTEGRATION_MATRIX_VISION.md      (971 lines)

# Tactical Implementation Docs (mixed quality)
docs/architecture/GAD-001_Research_Integration.md           (267 lines)
docs/architecture/GAD-002_Core_SDLC_Orchestration.md        (1534 lines) ⚠️ BLOATED
docs/architecture/GAD-003_Research_Capability_Restoration.md (789 lines)
docs/architecture/GAD-004_Multi_Layered_Quality_Enforcement.md (1800 lines)

# Technical Implementation Docs (ONLY ONE!)
docs/architecture/GAD-005_Runtime_Engineering.md            (1513 lines) ✅ HAS HARNESS
  ├── Blueprint → Implementation → HARNESS
  └── Tests: test_motd.py, test_kernel_checks.py, test_runtime_engineering.py
```

**Observation:** GAD-005 is the ONLY doc with full implementation + harness tests.

### 1.2. Codebase Reality Check

```bash
# Code Quality: GOOD
$ uv run ruff check agency_os/
All checks passed!

# Technical Debt: MINIMAL
$ grep -r "TODO\|FIXME" agency_os/ --include="*.py" | wc -l
13  # Only 13 TODOs in entire codebase

# Core Orchestrator: LARGE BUT CLEAN
$ wc -l agency_os/00_system/orchestrator/core_orchestrator.py
1583 lines  # Complex but ruff-clean

# Test Coverage: EXISTS BUT BROKEN
$ uv run pytest tests/ --collect-only 2>&1 | grep collected
collected 43 items / 13 errors
```

**Observation:** Code is NOT "nooby" - it's actually well-structured. But 13 test collection errors indicate gaps.

### 1.3. The Fundamental Gap

**What We Have:**
- ✅ Vision docs (GAD-006-008) - "What we want to build"
- ✅ Implementation code (agency_os/) - "What we built"
- ✅ ONE technical doc with harness (GAD-005) - "How it works + proof"

**What We're Missing:**
- ❌ Technical docs for core patterns (state machine, file I/O, error recovery)
- ❌ Defense harness to prevent regression
- ❌ Onboarding docs for contributors (technical ground truth)

**The Problem:**
```
Vision Docs ────────────────────────────────────┐
  (GAD-006-008: "What we want")                 │
                                                 │ GAP:
Implementation Code ────────────────────────────┤ No technical
  (agency_os/: "What we built")                 │ ground truth
                                                 │
Technical Docs with Harness ───────────────────┘
  (ONLY GAD-005 exists!)
```

---

## 2. Analysis: What TAD Solves

### 2.1. The GAD-005 Success Pattern

**Why GAD-005 works:**

1. **Blueprint → Implementation → HARNESS** (provable correctness)
2. **Lean structure** (~1500 lines including all sections)
3. **Defense-in-depth testing** (unit + integration + performance)
4. **Dated snapshot** ("Last Verified: 2025-11-16")
5. **Actionable** (clear implementation steps)

**Example: GAD-005 Section Structure**
```markdown
## 4. IMPLEMENTATION: Concrete Code
### 4.1. Week 1: Unavoidable MOTD
  - display_motd() function (191 LOC in vibe-cli)
  - Helper functions: format_git_status(), etc.

### 4.2. Week 2: Pre-Action Kernel
  - _kernel_check_save_artifact() (52 LOC in core_orchestrator.py)
  - Blocks dangerous operations before execution

## 5. HARNESS: Testing & Verification
### 5.1. Unit Tests
  - tests/test_motd.py (5 tests)
  - tests/test_kernel_checks.py (10 tests)

### 5.2. Integration Tests
  - tests/test_runtime_engineering.py (MOTD + Kernel work together)

### 5.3. Performance Tests
  - tests/performance/test_runtime_performance.py (non-blocking)
```

**Result:** If tests pass, feature works. Period.

### 2.2. What TAD Would Document

**TAD Scope: Implementation-level technical decisions**

| Topic | Current Docs | TAD Would Add |
|-------|--------------|---------------|
| **State Machine** | GAD-002 (1534 lines, no harness) | TAD-001: State Transitions + Harness |
| **File I/O Patterns** | Scattered across code | TAD-002: File Operations + Safety |
| **Error Recovery** | Implicit in code | TAD-003: Error Handling Strategy |
| **Prompt Composition** | prompt_registry.py (459 LOC) | TAD-004: Prompt Assembly + Tests |
| **Tool Execution** | tool_executor.py (65 LOC) | TAD-005: Tool Loop + Error Cases |
| **Manifest Lifecycle** | core_orchestrator.py (embedded) | TAD-006: Manifest Ops + Schema |

**Key Difference:**
- **GAD** = Strategic decision (why we chose this approach)
- **TAD** = Technical implementation (how it actually works + proof)

### 2.3. The Defense Harness Concept

**Idea:** Architecture regression tests that validate structural integrity.

**Example: TAD-001 State Machine Defense Harness**
```python
# tests/defense/test_tad001_state_machine.py
def test_all_states_have_handlers():
    """TAD-001 Requirement: Every SDLC state must have a handler."""
    required_handlers = {
        "PLANNING": "planning_handler.py",
        "CODING": "coding_handler.py",
        "TESTING": "testing_handler.py",
        "DEPLOYMENT": "deployment_handler.py",
        "MAINTENANCE": "maintenance_handler.py",
    }

    for state, handler_file in required_handlers.items():
        handler_path = f"agency_os/00_system/orchestrator/handlers/{handler_file}"
        assert os.path.exists(handler_path), f"Missing handler: {handler_file}"

def test_state_transitions_are_acyclic():
    """TAD-001 Requirement: State machine must be acyclic (no infinite loops)."""
    orchestrator = CoreOrchestrator(workspace_root="./test")
    transitions = orchestrator._get_workflow_definition()["states"]

    # Build transition graph
    graph = nx.DiGraph()
    for state_name, state_def in transitions.items():
        for transition in state_def.get("transitions", []):
            graph.add_edge(state_name, transition["to"])

    # Check for cycles
    assert nx.is_directed_acyclic_graph(graph), "State machine has cycles!"
```

**Benefit:** Prevents regression when refactoring.

---

## 3. BLUEPRINT: TAD Structure

### 3.1. TAD Template (Based on GAD-005)

```markdown
# TAD-XXX: [Technical Topic]

**Status:** ✅ Approved | 🔬 Draft | ⚠️ Needs Update
**Date:** YYYY-MM-DD
**Last Verified:** YYYY-MM-DD HH:MM UTC
**Related Code:** [file paths]
**Related GADs:** [strategic docs]
**Defense Harness:** tests/defense/test_tadXXX_*.py

---

## 1. Context & Current Implementation

### 1.1. What This TAD Documents
[Clear statement of technical scope]

### 1.2. Related Code Locations
```bash
# Primary implementation
agency_os/path/to/file.py:123-456

# Tests
tests/test_feature.py:78-90
```

### 1.3. Why This Matters
[Technical risk if not documented]

---

## 2. BLUEPRINT: Technical Design

### 2.1. Core Pattern
[Diagram + explanation of how it works]

### 2.2. Key Constraints
[Performance, safety, compatibility requirements]

### 2.3. Design Decisions
[Why this approach vs alternatives]

---

## 3. IMPLEMENTATION: Actual Code

### 3.1. Primary Components
```python
# Actual code snippets from codebase
def example_function():
    pass
```

### 3.2. Error Handling
[How errors are caught and recovered]

### 3.3. Performance Characteristics
[Time/space complexity, bottlenecks]

---

## 4. HARNESS: Verification

### 4.1. Unit Tests
```bash
uv run pytest tests/test_feature.py -v
```

### 4.2. Integration Tests
[How feature interacts with other components]

### 4.3. Defense Harness (Architecture Regression)
```bash
uv run pytest tests/defense/test_tadXXX_*.py -v
```

---

## 5. Common Pitfalls & Solutions

### 5.1. Pitfall: [Description]
**Problem:** [What goes wrong]
**Solution:** [How code prevents it]
**Test:** [Which test validates this]

---

## 6. Maintenance

### 6.1. When to Update This TAD
- Code location changes
- Error handling strategy changes
- Performance characteristics change
- Defense harness fails

### 6.2. Verification Command
```bash
# One command to verify TAD claims are still true
./bin/verify-tadXXX.sh
```

---

**END OF TAD-XXX**
```

### 3.2. TAD vs GAD Comparison

| Aspect | GAD (Governance) | TAD (Technical) |
|--------|------------------|-----------------|
| **Purpose** | Strategic decision-making | Implementation documentation |
| **Audience** | Architects, stakeholders | Developers, contributors |
| **Detail Level** | 30-50% (enough to build on) | 90-100% (full implementation) |
| **Timeframe** | Future-focused (vision) | Current-focused (what exists) |
| **Testing** | Optional (some have harness) | Mandatory (must have harness) |
| **Updates** | Rare (strategic stability) | Frequent (code changes) |
| **Example** | "Why we chose file-based delegation" | "How manifest file I/O works" |

**Key Insight:** GAD = "Why?" / TAD = "How?" + "Proof?"

---

## 4. HARNESS: Defense Layer Concept

### 4.1. What is a Defense Harness?

**Definition:** Architecture regression tests that validate structural integrity of technical decisions documented in TADs.

**Purpose:**
1. **Prevent regression** when refactoring
2. **Enforce architecture** automatically
3. **Onboard contributors** (tests as documentation)
4. **CI/CD integration** (blocking PRs that violate architecture)

### 4.2. Defense Harness Categories

```yaml
structural_tests:
  description: "Validate file structure, component existence"
  example: "test_all_handlers_exist()"

contract_tests:
  description: "Validate interfaces, function signatures"
  example: "test_handler_implements_required_methods()"

invariant_tests:
  description: "Validate architectural constraints"
  example: "test_state_machine_is_acyclic()"

performance_tests:
  description: "Validate performance characteristics"
  example: "test_manifest_load_under_100ms()"
```

### 4.3. Example: TAD-001 State Machine Defense Harness

```python
# tests/defense/test_tad001_state_machine.py
"""
TAD-001 Defense Harness: State Machine Architecture

Validates:
1. All SDLC states have handlers
2. State transitions are acyclic
3. Handlers implement required interface
4. Workflow YAML schema is valid
"""

import os
import pytest
import networkx as nx
from agency_os.core_orchestrator import CoreOrchestrator

class TestTAD001Defense:
    """Architecture regression tests for state machine."""

    def test_all_states_have_handlers(self):
        """Requirement: Every SDLC state must have a handler file."""
        required_handlers = {
            "PLANNING": "planning_handler.py",
            "CODING": "coding_handler.py",
            "TESTING": "testing_handler.py",
            "DEPLOYMENT": "deployment_handler.py",
            "MAINTENANCE": "maintenance_handler.py",
        }

        handler_dir = "agency_os/00_system/orchestrator/handlers"
        for state, filename in required_handlers.items():
            path = os.path.join(handler_dir, filename)
            assert os.path.exists(path), f"Missing handler for {state}: {filename}"

    def test_handlers_implement_interface(self):
        """Requirement: All handlers must implement process() method."""
        from agency_os.00_system.orchestrator.handlers import (
            planning_handler,
            coding_handler,
            deployment_handler,
        )

        for handler_module in [planning_handler, coding_handler, deployment_handler]:
            handler_class = getattr(handler_module, handler_module.__name__.replace("_handler", "Handler").title())
            assert hasattr(handler_class, "process"), f"{handler_module.__name__} missing process()"

    def test_state_machine_is_acyclic(self):
        """Requirement: State transitions must not create cycles."""
        orchestrator = CoreOrchestrator(workspace_root="./test")
        workflow = orchestrator._load_workflow_config()

        # Build directed graph of state transitions
        graph = nx.DiGraph()
        for state_name, state_def in workflow["states"].items():
            for transition in state_def.get("transitions", []):
                graph.add_edge(state_name, transition["to"])

        # Detect cycles
        assert nx.is_directed_acyclic_graph(graph), "State machine has cycles!"

    def test_workflow_yaml_schema(self):
        """Requirement: Workflow YAML must match expected schema."""
        orchestrator = CoreOrchestrator(workspace_root="./test")
        workflow = orchestrator._load_workflow_config()

        # Validate required top-level keys
        required_keys = ["name", "version", "states", "transitions"]
        for key in required_keys:
            assert key in workflow, f"Missing required key: {key}"

        # Validate state schema
        for state_name, state_def in workflow["states"].items():
            assert "agent" in state_def or "handler" in state_def, \
                f"State {state_name} missing agent/handler"

    def test_transition_performance(self):
        """Requirement: State transitions must complete in <200ms."""
        import time
        orchestrator = CoreOrchestrator(workspace_root="./test")

        start = time.perf_counter()
        orchestrator.transition_state("PLANNING", "CODING")
        elapsed = time.perf_counter() - start

        assert elapsed < 0.2, f"State transition took {elapsed:.3f}s (>200ms)"
```

**Benefit:** If this harness passes, TAD-001 architecture is intact.

### 4.4. Defense Harness Integration

```yaml
# .github/workflows/defense-harness.yml
name: Architecture Defense Harness

on: [push, pull_request]

jobs:
  architecture-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run TAD Defense Harness
        run: |
          uv run pytest tests/defense/ -v --tb=short

      - name: Generate Architecture Report
        if: failure()
        run: |
          echo "❌ Architecture regression detected!"
          echo "One or more TAD requirements violated."
          echo "Review test output above."
          exit 1
```

**Result:** PRs that violate architecture are blocked automatically.

---

## 5. Proposed TAD Series

### 5.1. TAD-001: State Machine Architecture

```yaml
scope: "SDLC state transitions and workflow orchestration"
code_locations:
  - agency_os/00_system/orchestrator/core_orchestrator.py:123-456
  - agency_os/00_system/orchestrator/ORCHESTRATION_workflow_design.yaml
tests:
  unit: tests/test_orchestrator_state_machine.py
  defense: tests/defense/test_tad001_state_machine.py
related_gads:
  - GAD-002 (Core SDLC Orchestration)
status: "NEEDED - core_orchestrator.py is 1583 LOC, no technical doc"
priority: "HIGH - critical path component"
```

### 5.2. TAD-002: File I/O Safety Patterns

```yaml
scope: "Manifest loading, saving, locking, error recovery"
code_locations:
  - agency_os/00_system/orchestrator/core_orchestrator.py:save_artifact()
  - agency_os/00_system/orchestrator/core_orchestrator.py:_load_manifest()
tests:
  unit: tests/test_file_operations.py (NEW)
  defense: tests/defense/test_tad002_file_safety.py (NEW)
related_gads:
  - GAD-005 (Kernel checks for file overwrites)
status: "NEEDED - 13 TODOs mention file operations"
priority: "HIGH - data integrity risk"
```

### 5.3. TAD-003: Error Recovery Strategy

```yaml
scope: "Exception handling, rollback, retry logic"
code_locations:
  - agency_os/00_system/orchestrator/handlers/*.py (error handling)
  - agency_os/00_system/runtime/llm_client.py (API retry)
tests:
  unit: tests/test_error_handling.py (NEW)
  defense: tests/defense/test_tad003_error_recovery.py (NEW)
related_gads:
  - GAD-004 (Quality enforcement on errors)
status: "NEEDED - implicit in code, not documented"
priority: "MEDIUM - robustness concern"
```

### 5.4. TAD-004: Prompt Composition Engine

```yaml
scope: "How prompts are assembled from registry, governance rules, context"
code_locations:
  - agency_os/00_system/runtime/prompt_registry.py (459 LOC)
  - agency_os/00_system/runtime/prompt_runtime.py (662 LOC)
tests:
  unit: tests/test_prompt_registry.py (EXISTS)
  defense: tests/defense/test_tad004_prompt_composition.py (NEW)
related_gads:
  - GAD-005 (MOTD as context injection)
status: "PARTIAL - tests exist but no technical doc"
priority: "MEDIUM - well-tested already"
```

### 5.5. TAD-005: Tool Execution Loop

```yaml
scope: "vibe-cli tool use: tool_use → tool_result cycle"
code_locations:
  - vibe-cli:426-497 (tool execution loop)
  - agency_os/00_system/orchestrator/tools/tool_executor.py (65 LOC)
tests:
  unit: tests/test_vibe_cli_tool_loop.py (MISSING - known issue in CLAUDE.md)
  defense: tests/defense/test_tad005_tool_loop.py (NEW)
related_gads:
  - GAD-003 (File-based delegation)
status: "NEEDED - code exists but untested E2E"
priority: "HIGH - known gap in CLAUDE.md"
```

### 5.6. TAD-006: Manifest Lifecycle Management

```yaml
scope: "project_manifest.json creation, updates, schema validation"
code_locations:
  - agency_os/00_system/orchestrator/core_orchestrator.py:_load_manifest()
  - agency_os/00_system/orchestrator/core_orchestrator.py:save_artifact()
tests:
  unit: tests/test_manifest_operations.py (NEW)
  defense: tests/defense/test_tad006_manifest.py (NEW)
related_gads:
  - GAD-004 (Quality gates stored in manifest)
status: "NEEDED - critical data structure, no doc"
priority: "HIGH - used everywhere"
```

---

## 6. Comparison: GAD vs TAD

### 6.1. Side-by-Side Example

**Scenario:** Documenting state machine

**GAD-002 Approach (Strategic):**
```markdown
# GAD-002: Core SDLC Orchestration

## Why We Chose a State Machine
- Predictable workflow progression
- Clear transition rules
- Easy to visualize
- Aligns with industry best practices

## High-Level Architecture
[Diagram of 5 SDLC phases]

## Decision: File-Based State vs In-Memory
We chose file-based state (project_manifest.json) because:
- Survives process restarts
- Human-readable audit trail
- Compatible with delegated execution model
```

**TAD-001 Approach (Technical):**
```markdown
# TAD-001: State Machine Architecture

## Current Implementation
File: agency_os/00_system/orchestrator/core_orchestrator.py:123-456
State storage: project_manifest.json (current_state field)
Workflow definition: ORCHESTRATION_workflow_design.yaml

## How State Transitions Work
```python
def transition_state(self, from_state: str, to_state: str):
    """
    Validates transition, updates manifest, triggers handler.
    Time complexity: O(1)
    Failure mode: Raises TransitionError, manifest unchanged
    """
    # 1. Validate transition is allowed (YAML lookup)
    # 2. Run quality gates (GAD-004)
    # 3. Update manifest atomically
    # 4. Return new state
```

## Error Handling
- Invalid transition → TransitionError (logged, manifest unchanged)
- Quality gate failure → WorkflowBlockedError (remediation steps provided)
- File I/O failure → Retry 3x with exponential backoff

## Defense Harness
tests/defense/test_tad001_state_machine.py validates:
✅ All states have handlers
✅ Transitions are acyclic
✅ Handlers implement required interface
✅ Transitions complete in <200ms
```

**Key Difference:**
- GAD-002 = "Why state machine?" (strategic)
- TAD-001 = "How state machine works?" (technical) + proof (harness)

---

## 7. Decision: Approve or Refine

### 7.1. Proposal Summary

**Create TAD Series:**
1. Use GAD-005 template (Blueprint → Implementation → HARNESS)
2. Document implementation-level technical patterns
3. Add defense harness for architecture regression prevention
4. Keep lean (~500-1000 lines per TAD, not 1500+ like GAD-002)
5. Make tests mandatory (if harness fails, TAD is outdated)

**First TAD Candidates (Priority Order):**
1. **TAD-001: State Machine Architecture** (HIGH - 1583 LOC core_orchestrator.py)
2. **TAD-002: File I/O Safety Patterns** (HIGH - data integrity risk)
3. **TAD-005: Tool Execution Loop** (HIGH - known gap in CLAUDE.md)
4. **TAD-006: Manifest Lifecycle Management** (HIGH - used everywhere)
5. **TAD-003: Error Recovery Strategy** (MEDIUM - robustness)
6. **TAD-004: Prompt Composition Engine** (MEDIUM - already tested)

### 7.2. Questions for Review

**Q1: Is TAD scope correct?**
- Should TAD cover implementation details (state machine, file I/O)?
- Or should it be even lower-level (function-by-function)?

**Q2: Defense harness granularity?**
- Per-TAD defense tests (e.g., `test_tad001_*.py`)?
- Or single `test_architecture_defense.py` for all TADs?

**Q3: TAD vs Code Comments?**
- When does implementation detail belong in TAD vs inline comments?
- Rule of thumb: TAD = architectural pattern, Comments = line-by-line logic?

**Q4: TAD update frequency?**
- Should TAD be updated on every code change (drift prevention)?
- Or only when architecture changes (less churn)?

**Q5: Integration with CLAUDE.md?**
- Should CLAUDE.md link to TADs for verification commands?
- Or keep CLAUDE.md focused on operational status only?

### 7.3. Alternatives Considered

**Alternative 1: Expand GAD-002 Instead**
- **Pro:** One less document series
- **Con:** GAD-002 already 1534 lines, adding more would make it unreadable
- **Verdict:** REJECTED (bloat)

**Alternative 2: Use ADR (Architecture Decision Records)**
- **Pro:** Industry standard format
- **Con:** ADRs focus on *decisions*, not *implementations*
- **Verdict:** REJECTED (wrong scope - ADR = "Why?", TAD = "How?")

**Alternative 3: Inline Code Documentation Only**
- **Pro:** No separate docs to maintain
- **Con:** No defense harness, no big-picture view
- **Verdict:** REJECTED (insufficient for onboarding)

**Alternative 4: Wiki-Style Living Documentation**
- **Pro:** Easy to update incrementally
- **Con:** No version control, no tests, drift guaranteed
- **Verdict:** REJECTED (not accountable)

**Chosen Approach: TAD Series (GAD-005 Template)**
- ✅ Lean (500-1000 lines per TAD)
- ✅ Testable (defense harness mandatory)
- ✅ Versioned (git-tracked, dated snapshots)
- ✅ Proven (GAD-005 showed it works)

---

## 8. Next Steps (If Approved)

### 8.1. Immediate (Week 1)
1. **Approve TAD-000 Proposal** (this document)
2. **Create TAD-001: State Machine Architecture** (first implementation)
3. **Write defense harness** (tests/defense/test_tad001_*.py)
4. **Validate template works** (adjust if needed)

### 8.2. Short-Term (Weeks 2-4)
1. **Create TAD-002, TAD-005, TAD-006** (high-priority technical docs)
2. **Add defense harness CI/CD job** (.github/workflows/defense-harness.yml)
3. **Update CLAUDE.md** (link to TADs for verification)

### 8.3. Long-Term (Months 2-3)
1. **Complete TAD-003, TAD-004** (medium-priority docs)
2. **Retrospective: TAD vs GAD split** (refine boundary if needed)
3. **Onboard contributors** (use TADs as technical reference)

---

## 9. Success Metrics

```yaml
technical_metrics:
  tad_coverage: ">80% of core_orchestrator.py documented"
  defense_harness_pass_rate: "100% (if fails, TAD outdated)"
  regression_prevention: "Zero architecture violations in PRs"

developer_metrics:
  onboarding_time: "-50% (TADs accelerate ramp-up)"
  contribution_confidence: ">4/5 (developers know patterns)"
  doc_accuracy: ">95% (tests enforce correctness)"

maintenance_metrics:
  doc_drift: "<5% (defense harness catches drift)"
  update_frequency: "Weekly (living documentation)"
  staleness_alerts: "Automated (if harness fails)"
```

---

## 10. Recommendation

**APPROVE TAD Series with refinements:**

1. ✅ **TAD scope is correct** - Implementation-level technical patterns
2. ✅ **Use GAD-005 template** - Proven to work (Blueprint → Implementation → HARNESS)
3. ✅ **Defense harness per TAD** - Granular regression prevention
4. ✅ **Start with TAD-001** - State machine is highest priority
5. ✅ **Keep lean** - Target 500-1000 lines per TAD (not GAD-002's 1534)

**Refinements:**
- Add "Last Verified" timestamp to TAD template (like CLAUDE.md)
- Create `./bin/verify-tad.sh` script (runs all defense harnesses)
- Add TAD verification to `.github/workflows/validate.yml` (blocking)
- Update CLAUDE.md with TAD verification commands

**Rationale:**
- Code exists but lacks technical ground truth documentation
- GAD-005 proved the template works (MOTD + Kernel + HARNESS all tested)
- Defense harness prevents regression (architecture as code)
- Lean approach prevents bloat (unlike GAD-002's 1534 lines)

**Alternative: Prove this is a bad idea**
- I cannot prove this is a bad idea
- This is EXACTLY what the codebase needs
- The only risk is not doing it

---

**END OF TAD-000 PROPOSAL**

**Decision Required:** Approve | Refine | Reject
**Next Action:** If approved → Create TAD-001 (State Machine Architecture)
**Timeline:** Week 1 = TAD-001 draft + defense harness
**Success Criteria:** Defense harness passes, core_orchestrator.py documented
