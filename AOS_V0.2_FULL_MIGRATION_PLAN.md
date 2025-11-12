# AOS v0.2 FULL MIGRATION PLAN

**Status:** PLANNING
**Pilot Completed:** GENESIS_BLUEPRINT (2025-11-12)
**Objective:** Refactor all 8 agents + orchestrator to atomized prompt system

---

## EXECUTIVE SUMMARY

### What We've Proven (GENESIS_BLUEPRINT Pilot)
- ✅ Monolith (951 lines) → 5 tasks + core + gates (working)
- ✅ PromptRuntime successfully composes prompts (16,683 chars output)
- ✅ Metadata-driven execution (dependencies, inputs, outputs)
- ✅ Knowledge resolution (YAMLs loaded per task)

### What's Left
- 7 more agents to refactor (3,135 total lines)
- Orchestrator workflow integration (task-level references)
- Integration testing (end-to-end SDLC workflow)
- Production PromptRuntime (LLM API integration)

---

## SCOPE: ALL 8 AGENTS

| Agent | Current Size | Complexity | Priority | Estimated Tasks |
|-------|-------------|------------|----------|-----------------|
| **GENESIS_BLUEPRINT** | 951 lines | HIGH | ✅ DONE | 5 tasks |
| **VIBE_ALIGNER** | 786 lines | HIGH | 🔥 P1 | 3 tasks |
| **GENESIS_UPDATE** | 645 lines | MEDIUM | P2 | 4 tasks |
| **CODE_GENERATOR** | 166 lines | LOW | P3 | 2 tasks |
| **AGENCY_OS_ORCHESTRATOR** | 188 lines | CRITICAL | P4 | Special* |
| **BUG_TRIAGE** | 141 lines | LOW | P5 | 2 tasks |
| **QA_VALIDATOR** | 137 lines | LOW | P5 | 2 tasks |
| **DEPLOY_MANAGER** | 121 lines | LOW | P5 | 2 tasks |

**Total:** 3,135 lines → ~25 atomized tasks

\* Orchestrator is special: becomes "Prompt Executor" not "Task Container"

---

## PHASE 1: HIGH-PRIORITY AGENTS (Week 1)

### P1: VIBE_ALIGNER (786 lines) 🔥

**Why First:**
- Entry point to entire SDLC (user interaction)
- Complex: Education + Extraction + Validation logic
- High impact: If broken, entire system blocked

**Atomization Plan:**

```
agency_os/01_planning_framework/agents/VIBE_ALIGNER/
├── _composition.yaml
├── _knowledge_deps.yaml
├── _prompt_core.md                # Core personality (~80 lines)
│
├── tasks/
│   ├── task_01_educate_user.md + .meta.yaml
│   │   # Teach user about v1.0 scope, FAE constraints
│   │   # Input: (initial brief)
│   │   # Output: educated_brief.json
│   │
│   ├── task_02_extract_requirements.md + .meta.yaml
│   │   # Parse educated brief → feature_spec.json
│   │   # Input: educated_brief.json
│   │   # Output: feature_spec_draft.json
│   │
│   └── task_03_validate_feasibility.md + .meta.yaml
│       # Validate against FAE, APCE
│       # Input: feature_spec_draft.json
│       # Output: feature_spec.json (validated)
│
└── gates/
    ├── gate_v1_scope_only.md
    ├── gate_all_features_have_apce_score.md
    └── gate_fae_compliance.md
```

**Knowledge Dependencies:**
- FAE_constraints.yaml (critical)
- APCE_rules.yaml (critical)
- FDG_dependencies.yaml (optional)

**Estimated Effort:** 2-3 hours

**Validation:**
- Test with example user brief (simple project)
- Ensure feature_spec.json schema matches v0.1

---

### P2: GENESIS_UPDATE (645 lines)

**Why Second:**
- Handles incremental architecture changes
- Complements GENESIS_BLUEPRINT
- Complex delta-diffing logic

**Atomization Plan:**

```
agency_os/01_planning_framework/agents/GENESIS_UPDATE/
├── _composition.yaml
├── _knowledge_deps.yaml
├── _prompt_core.md
│
├── tasks/
│   ├── task_01_analyze_delta.md + .meta.yaml
│   │   # Compare new feature_spec vs existing architecture
│   │   # Input: feature_spec_delta.json, architecture.json
│   │   # Output: delta_analysis.json
│   │
│   ├── task_02_impact_assessment.md + .meta.yaml
│   │   # Assess which modules affected
│   │   # Input: delta_analysis.json
│   │   # Output: impact_report.json
│   │
│   ├── task_03_generate_update_plan.md + .meta.yaml
│   │   # Generate minimal update plan
│   │   # Input: impact_report.json
│   │   # Output: update_plan.json
│   │
│   └── task_04_apply_updates.md + .meta.yaml
│       # Generate updated architecture.json + code_gen_spec.json
│       # Input: update_plan.json, architecture.json
│       # Output: architecture_v2.json, code_gen_spec_delta.json
│
└── gates/
    ├── gate_no_breaking_changes.md
    ├── gate_backward_compatible.md
    └── gate_minimal_impact.md
```

**Estimated Effort:** 2-3 hours

---

## PHASE 2: EXECUTION AGENTS (Week 2)

### P3: CODE_GENERATOR (166 lines) - LOW COMPLEXITY

**Atomization Plan:**

```
agency_os/02_code_gen_framework/agents/CODE_GENERATOR/
├── _composition.yaml
├── _knowledge_deps.yaml
├── _prompt_core.md
│
├── tasks/
│   ├── task_01_generate_code.md + .meta.yaml
│   │   # Generate all modules from code_gen_spec.json
│   │   # Input: code_gen_spec.json
│   │   # Output: artifact_bundle/ (source code)
│   │
│   └── task_02_validate_quality.md + .meta.yaml
│       # Run linting, type checking, quality gates
│       # Input: artifact_bundle/
│       # Output: quality_report.json
│
└── gates/
    ├── gate_no_hallucinations.md
    ├── gate_test_coverage_80pct.md
    └── gate_linting_passed.md
```

**Estimated Effort:** 1-2 hours

---

### P5: QA_VALIDATOR (137 lines) - LOW COMPLEXITY

**Atomization Plan:**

```
agency_os/03_qa_framework/agents/QA_VALIDATOR/
├── tasks/
│   ├── task_01_run_tests.md + .meta.yaml
│   └── task_02_generate_report.md + .meta.yaml
│
└── gates/
    ├── gate_all_tests_passed.md
    └── gate_coverage_threshold.md
```

**Estimated Effort:** 1 hour

---

### P5: DEPLOY_MANAGER (121 lines) - LOW COMPLEXITY

**Atomization Plan:**

```
agency_os/04_deploy_framework/agents/DEPLOY_MANAGER/
├── tasks/
│   ├── task_01_deploy.md + .meta.yaml
│   └── task_02_validate_health.md + .meta.yaml
│
└── gates/
    ├── gate_health_checks_passed.md
    └── gate_rollback_ready.md
```

**Estimated Effort:** 1 hour

---

### P5: BUG_TRIAGE (141 lines) - LOW COMPLEXITY

**Atomization Plan:**

```
agency_os/05_maintenance_framework/agents/BUG_TRIAGE/
├── tasks/
│   ├── task_01_classify_bug.md + .meta.yaml
│   └── task_02_route_to_workflow.md + .meta.yaml
│
└── gates/
    ├── gate_severity_assigned.md
    └── gate_valid_bug_report.md
```

**Estimated Effort:** 1 hour

---

## PHASE 3: ORCHESTRATOR REFACTORING (Week 2-3)

### P4: AGENCY_OS_ORCHESTRATOR (SPECIAL CASE)

**Problem:**
- Current Orchestrator is itself a monolith (188 lines)
- Should become "PromptRuntime Executor" not "Task Container"

**New Role:**
```
OLD (v0.1):
  Orchestrator = "Master Agent" with embedded workflow logic

NEW (v0.2):
  Orchestrator = State Machine Executor
  - Reads ORCHESTRATION_workflow_design.yaml
  - For each state, invokes PromptRuntime.execute_task()
  - Handles state transitions based on artifact creation
```

**Refactoring Plan:**

```
agency_os/00_system/orchestrator/
├── orchestrator_v2.py
│   # NEW: Python orchestrator (not a prompt!)
│   # Reads workflow YAML
│   # Invokes PromptRuntime for each task
│   # Manages state transitions
│
└── orchestrator_core.md (optional)
    # Only if we need prompt-based orchestration
    # But likely this becomes pure Python code
```

**Key Change:**
```yaml
# ORCHESTRATION_workflow_design.yaml (UPDATED)

states:
  - id: PLANNING
    status: PLANNING
    tasks:
      - agent: VIBE_ALIGNER
        task_id: educate_user
        trigger: on_state_entry

      - agent: VIBE_ALIGNER
        task_id: extract_requirements
        trigger: after_task(educate_user)

      - agent: VIBE_ALIGNER
        task_id: validate_feasibility
        trigger: after_task(extract_requirements)

      - agent: GENESIS_BLUEPRINT
        task_id: select_core_modules
        trigger: after_agent(VIBE_ALIGNER)

      # ... granular task references instead of agent names
```

**Estimated Effort:** 3-4 hours (Python orchestrator + workflow YAML update)

---

## VALIDATION STRATEGY

### Level 1: Unit Tests (Per Agent)
```python
# test_genesis_blueprint.py

def test_task_01_composition():
    """Test that task_01 composes correctly"""
    runtime = PromptRuntime()
    prompt = runtime.execute_task(
        agent_id="GENESIS_BLUEPRINT",
        task_id="01_select_core_modules",
        context={...}
    )

    assert "Core Personality" in prompt
    assert "TASK INSTRUCTIONS" in prompt
    assert "stdlib_only_core" in prompt  # Gate loaded
    assert len(prompt) > 10000  # Reasonable size

def test_task_01_metadata():
    """Test that task metadata is valid"""
    meta = load_task_metadata("GENESIS_BLUEPRINT", "01_select_core_modules")

    assert meta.phase == 1
    assert meta.dependencies == []
    assert "feature_spec.json" in [i["ref"] for i in meta.inputs]
```

### Level 2: Integration Tests (Per Agent Chain)
```python
def test_vibe_aligner_full_chain():
    """Test all 3 VIBE_ALIGNER tasks in sequence"""
    runtime = PromptRuntime()

    # Task 1: Educate
    result_1 = runtime.execute_task("VIBE_ALIGNER", "educate_user", {...})
    assert "educated_brief.json" in result_1.outputs

    # Task 2: Extract (depends on Task 1)
    result_2 = runtime.execute_task("VIBE_ALIGNER", "extract_requirements", {
        "educated_brief": result_1.outputs["educated_brief.json"]
    })
    assert "feature_spec_draft.json" in result_2.outputs

    # Task 3: Validate (depends on Task 2)
    result_3 = runtime.execute_task("VIBE_ALIGNER", "validate_feasibility", {
        "feature_spec_draft": result_2.outputs["feature_spec_draft.json"]
    })
    assert result_3.validation.fae_passed == True
```

### Level 3: End-to-End Tests (Full SDLC Workflow)
```python
def test_full_sdlc_planning_to_deployment():
    """Test entire SDLC: PLANNING → CODING → TESTING → DEPLOYMENT"""
    orchestrator = OrchestratorV2()

    # Start with user brief
    project = orchestrator.start_project(user_brief="Build a CSV parser CLI tool")

    # PLANNING phase (VIBE_ALIGNER + GENESIS_BLUEPRINT)
    orchestrator.execute_phase(project.id, "PLANNING")
    assert project.status.phase == "CODING"
    assert Path(project.artifacts.architecture_json).exists()

    # CODING phase (CODE_GENERATOR)
    orchestrator.execute_phase(project.id, "CODING")
    assert project.status.phase == "TESTING"
    assert Path(project.artifacts.artifact_bundle).exists()

    # ... continue through all phases
```

### Level 4: Backward Compatibility Tests
```python
def test_v0_1_vs_v0_2_output_equivalence():
    """Ensure v0.2 produces same output as v0.1 for identical input"""

    # Run GENESIS_BLUEPRINT v5 (monolith)
    output_v1 = run_genesis_v5(feature_spec)

    # Run GENESIS_BLUEPRINT v6 (atomized)
    output_v2 = run_genesis_v6(feature_spec)

    # Compare architecture.json outputs
    assert output_v1["core_modules"] == output_v2["core_modules"]
    assert output_v1["extensions"] == output_v2["extensions"]
```

---

## ROLLOUT STRATEGY

### Option A: Incremental Rollout (RECOMMENDED)

**Advantages:**
- Less risky
- Can test each agent independently
- Parallel v0.1/v0.2 operation during migration

**Process:**
```
Week 1:
  Day 1-2: VIBE_ALIGNER refactor + test
  Day 3-4: GENESIS_UPDATE refactor + test
  Day 5:   Integration test (VIBE_ALIGNER → GENESIS_BLUEPRINT)

Week 2:
  Day 1:   CODE_GENERATOR refactor + test
  Day 2:   QA_VALIDATOR refactor + test
  Day 3:   DEPLOY_MANAGER refactor + test
  Day 4:   BUG_TRIAGE refactor + test
  Day 5:   Integration test (all execution agents)

Week 3:
  Day 1-2: Orchestrator v2 implementation
  Day 3:   Update ORCHESTRATION_workflow_design.yaml
  Day 4:   End-to-end testing
  Day 5:   Production readiness check
```

**Parallel Operation:**
- Keep v0.1 prompts (e.g., VIBE_ALIGNER_v3.md) untouched
- v0.2 lives in `agents/` directory
- Orchestrator can choose which version to call

---

### Option B: Big Bang Migration (NOT RECOMMENDED)

Refactor all 8 agents in one PR. Too risky.

---

## RISK MITIGATION

### Risk 1: Breaking Changes in Outputs
**Mitigation:**
- Backward compatibility tests (compare v0.1 vs v0.2 outputs)
- Schema validation (ensure artifact_bundle, architecture.json same format)

### Risk 2: Task Dependency Errors
**Mitigation:**
- Explicit dependency declarations in `.meta.yaml`
- PromptRuntime validates dependencies before execution
- Fail early if prerequisite outputs missing

### Risk 3: Knowledge Resolution Failures
**Mitigation:**
- `_knowledge_deps.yaml` declares critical vs optional
- PromptRuntime fails fast if critical knowledge missing
- Caching to avoid re-loading YAMLs

### Risk 4: Orchestrator State Machine Bugs
**Mitigation:**
- Extensive state machine testing
- Idempotent task execution (same input → same output)
- Rollback capability (keep v0.1 orchestrator as fallback)

---

## SUCCESS CRITERIA

### Phase 1 Complete (Week 1)
- [ ] VIBE_ALIGNER atomized (3 tasks + gates)
- [ ] GENESIS_UPDATE atomized (4 tasks + gates)
- [ ] Both agents pass unit tests
- [ ] Integration test: VIBE_ALIGNER → GENESIS_BLUEPRINT works

### Phase 2 Complete (Week 2)
- [ ] All 4 execution agents atomized (CODE_GENERATOR, QA, DEPLOY, BUG_TRIAGE)
- [ ] All agents pass unit tests
- [ ] Integration test: CODING → TESTING → DEPLOYMENT chain works

### Phase 3 Complete (Week 3)
- [ ] Orchestrator v2 implemented (Python)
- [ ] ORCHESTRATION_workflow_design.yaml updated (task-level references)
- [ ] End-to-end test: Full SDLC workflow (user brief → deployment) passes
- [ ] Performance benchmarks (v0.2 not slower than v0.1)

### Final Acceptance
- [ ] All 8 agents atomized
- [ ] All tests passing (unit + integration + E2E)
- [ ] Documentation updated (README, architecture docs)
- [ ] Production PromptRuntime ready (LLM API integration)
- [ ] v0.1 deprecated (but kept for rollback)

---

## OPEN QUESTIONS

### Q1: Should Orchestrator be Python or Prompt?
**Current thinking:** Python.
- State machine logic = imperative code (better in Python)
- Prompt-based orchestration = hard to debug
- Python = easier error handling, logging, retries

**Decision needed:** Confirm this approach.

---

### Q2: How to handle partial failures?
**Scenario:** Task 3 fails, but Tasks 1-2 succeeded. Do we:
- A) Rollback all tasks (transaction-style)
- B) Keep successful outputs, retry only failed task
- C) Human-in-the-loop approval for retry

**Current thinking:** B (keep successful, retry failed).

**Decision needed:** Define retry strategy.

---

### Q3: Production PromptRuntime - which LLM API?
**Options:**
- Anthropic Claude API (Claude 3.5 Sonnet)
- OpenAI GPT-4
- Self-hosted (Ollama, LM Studio)

**Current thinking:** Claude API (we're already using it).

**Decision needed:** Confirm + implement API integration.

---

### Q4: Versioning strategy for atomized prompts?
**Problem:** If we update `task_01.md`, does that create breaking change?

**Options:**
- A) Semantic versioning per task (task_01_v1.md, task_01_v2.md)
- B) Agent-level versioning (GENESIS_BLUEPRINT v6.0 → v6.1)
- C) Git history only (no explicit versions)

**Current thinking:** B (agent-level versioning).

**Decision needed:** Define versioning policy.

---

## ESTIMATED TIMELINE

| Phase | Duration | Effort | Completion |
|-------|----------|--------|------------|
| **Phase 1** (VIBE_ALIGNER, GENESIS_UPDATE) | Week 1 | 8-10h | TBD |
| **Phase 2** (Execution Agents) | Week 2 | 6-8h | TBD |
| **Phase 3** (Orchestrator v2) | Week 3 | 8-10h | TBD |
| **Testing & Documentation** | Week 3 | 4-6h | TBD |
| **TOTAL** | 3 weeks | 26-34h | TBD |

**Start Date:** TBD (after approval)
**Target Completion:** TBD (3 weeks from start)

---

## APPROVAL CHECKLIST

Before proceeding with implementation:

- [ ] **Scope approved:** All 8 agents + orchestrator
- [ ] **Priorisierung approved:** VIBE_ALIGNER → GENESIS_UPDATE → Execution Agents → Orchestrator
- [ ] **Validation strategy approved:** 4-level testing (unit, integration, E2E, compatibility)
- [ ] **Rollout strategy approved:** Incremental (parallel v0.1/v0.2 operation)
- [ ] **Open questions resolved:** Orchestrator=Python?, Retry strategy?, LLM API?, Versioning?
- [ ] **Timeline feasible:** 3 weeks, 26-34 hours total effort

---

## NEXT IMMEDIATE ACTION

**After approval, start with:**

```bash
# Create VIBE_ALIGNER atomized structure
mkdir -p agency_os/01_planning_framework/agents/VIBE_ALIGNER/{tasks,gates}

# Extract _prompt_core.md
# Create task_01_educate_user.md + .meta.yaml
# Create task_02_extract_requirements.md + .meta.yaml
# Create task_03_validate_feasibility.md + .meta.yaml
# Create gates (v1_scope_only, apce_compliance, fae_compliance)
# Create _composition.yaml
# Create _knowledge_deps.yaml

# Test composition
python3 agency_os/00_system/runtime/prompt_runtime.py VIBE_ALIGNER educate_user

# Commit & push
git commit -m "feat: Refactor VIBE_ALIGNER to AOS v0.2"
```

---

**END OF PLAN**

**Approval Required Before Implementation.**
