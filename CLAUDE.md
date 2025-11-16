# CLAUDE.md - Operational Truth Protocol

**Version:** 2.0
**Purpose:** Prevent hallucination. Show REAL operational status, not design intent.
**Last Updated:** 2025-11-16

---

## 🎯 CORE PRINCIPLES (Never Change)

1. **Don't trust "Complete ✅" without passing tests**
2. **Test first, then claim complete**
3. **When docs contradict code, trust code**
4. **When code contradicts tests, trust tests**
5. **When in doubt: RUN THE VERIFICATION COMMAND**
6. **ALWAYS use `./bin/pre-push-check.sh` before git push** (Blocks bad commits, prevents CI/CD failures)

---

## 📖 What This Repo Is

**vibe-agency** = File-based prompt framework for AI-assisted software project planning.

**Architecture Reference:** See [ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md) for conceptual model.

**Core Flow (MVP - DELEGATION ONLY):**
```
Claude Code (operator) ← STDOUT/STDIN → vibe-cli → Core Orchestrator → SDLC Phases → Agents
```

**Note:** vibe-cli delegates intelligence requests to Claude Code operator.
See: docs/architecture/EXECUTION_MODE_STRATEGY.md

**5 SDLC Phases:**
1. PLANNING (4 sub-states: RESEARCH → BUSINESS_VALIDATION → FEATURE_SPECIFICATION → ARCHITECTURE_DESIGN)
2. CODING (5-phase code generation workflow)
3. TESTING (stub - transitions only)
4. DEPLOYMENT (4-phase deployment workflow - COMPLETE)
5. MAINTENANCE (stub - transitions only)

---

## ✅ OPERATIONAL STATUS (Dated Snapshot)

**Last Verified:** 2025-11-16 18:45 UTC (Environment corrected: venv synced with --all-extras)

### Phase Implementation Status

| Phase | Status | Evidence | Verify Command |
|-------|--------|----------|----------------|
| PLANNING | ✅ Works | test_planning_workflow.py PASSES | `uv run python -m pytest tests/test_planning_workflow.py -v` |
| CODING Handler | ✅ Works (tested E2E) | 3 tests pass (test_coding_workflow.py) | `uv run pytest tests/test_coding_workflow.py -v` |
| TESTING Handler | ⚠️ Stub only | testing_handler.py (108 lines) | `grep -n "STUB" agency_os/00_system/orchestrator/handlers/testing_handler.py` |
| DEPLOYMENT Handler | ✅ Works (tested E2E) | 5 tests pass (test_deployment_workflow.py) | `uv run pytest tests/test_deployment_workflow.py -v` |
| MAINTENANCE Handler | ⚠️ Stub only | maintenance_handler.py (106 lines) | `grep -n "STUB" agency_os/00_system/orchestrator/handlers/maintenance_handler.py` |

### Core Components

| Component | Status | Evidence | Verify Command |
|-----------|--------|----------|----------------|
| Core Orchestrator | ✅ Works | State machine tested | `python tests/test_orchestrator_state_machine.py` |
| **File-Based Delegation (GAD-003)** | **✅ Works (E2E tested)** | **manual_planning_test.py validates full PLANNING workflow** | `uv run python manual_planning_test.py` |
| **TODO-Based Handoffs** | **✅ Works** | **handoff.json created between agents** | `cat workspaces/manual-test-project/handoff.json` |
| **Session Handoff Integration** | **✅ Works** | **ONE command shows full context** | `./bin/show-context.sh` |
| **Automatic Linting Enforcement** | **✅ Works (tested live)** | **Belt + suspenders: visibility + blocking** | `./bin/show-context.sh` (see linting status) |
| **Workflow-Scoped Quality Gates (GAD-004 Phase 2)** | **✅ Works (tested)** | **Gate results recorded in manifest.status.qualityGates** | `uv run pytest tests/test_quality_gate_recording.py -v` |
| **Deployment-Scoped Validation (GAD-004 Phase 3)** | **✅ Works (tested)** | **E2E tests run on push to main/develop** | `uv run pytest tests/e2e/test_orchestrator_e2e.py -v` |
| **Multi-Layer Integration (GAD-004 Phase 4)** | **✅ Works (tested)** | **All 3 layers integrated and verified** | `uv run pytest tests/test_multi_layer_integration.py -v` |
| **Unavoidable MOTD (GAD-005 Week 1)** | **✅ Works (tested)** | **MOTD displays critical context before execution** | `uv run python tests/test_motd.py` |
| **Pre-Action Kernel (GAD-005 Week 2)** | **✅ Works (tested)** | **Kernel validates dangerous operations before execution** | `uv run python tests/test_kernel_checks.py` |
| **GAD-005 Integration (HARNESS)** | **✅ Works (tested)** | **MOTD + Kernel work together (0.827s MOTD, 0.00ms kernel)** | `uv run python tests/test_runtime_engineering.py` |
| **GAD-005-ADDITION Layer 0** | **✅ Works (tested)** | **System Integrity Verification (0.80ms check, 17/17 tests passing)** | `uv run pytest tests/test_layer0_integrity.py -v` |
| **GAD-005-ADDITION Layer 1** | **✅ Works (tested)** | **Session Shell Boot Integration (Layer 0 runs before MOTD, 24/24 tests passing)** | `uv run pytest tests/test_layer1_boot_integration.py -v` |
| Prompt Registry | ✅ Works | 9 governance rules injected | `uv run pytest tests/test_prompt_registry.py -v` |
| vibe-cli | ✅ MOTD integrated | vibe-cli (862 lines, +191 LOC for MOTD) | `wc -l vibe-cli` |
| vibe-cli Tool Loop | ⚠️ Code exists, untested E2E | vibe-cli:426-497 | `grep -A 20 "def _execute_prompt" vibe-cli \| grep tool_use` |
| Research Agents | ✅ Dependencies installed | bs4 4.14.2 (venv synced) | `uv run python -c "import bs4; print('✅ bs4:', bs4.__version__)"` |

### Planning Agents (✅ All Implemented)

| Agent | Status | Verify Command |
|-------|--------|----------------|
| VIBE_ALIGNER | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/VIBE_ALIGNER/` |
| LEAN_CANVAS_VALIDATOR | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/LEAN_CANVAS_VALIDATOR/` |
| GENESIS_BLUEPRINT | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/` |
| MARKET_RESEARCHER | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/research/MARKET_RESEARCHER/` |
| TECH_RESEARCHER | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/research/TECH_RESEARCHER/` |
| FACT_VALIDATOR | ✅ Production ready | `ls -la agency_os/01_planning_framework/agents/research/FACT_VALIDATOR/` |
| USER_RESEARCHER | ✅ No tools needed | `ls -la agency_os/01_planning_framework/agents/research/USER_RESEARCHER/` |

### Knowledge Bases (✅ All Complete)

| File | Lines | Verify Command |
|------|-------|----------------|
| FAE_constraints.yaml | 736 | `wc -l agency_os/01_planning_framework/knowledge/FAE_constraints.yaml` |
| FDG_dependencies.yaml | 2546 | `wc -l agency_os/01_planning_framework/knowledge/FDG_dependencies.yaml` |
| APCE_rules.yaml | 1304 | `wc -l agency_os/01_planning_framework/knowledge/APCE_rules.yaml` |

---

## 🔍 HOW TO VERIFY CLAIMS

### Verify File-Based Delegation Works (GAD-003)
```bash
uv run python manual_planning_test.py
# Expected: All 3 PLANNING sub-states complete successfully
# - BUSINESS_VALIDATION (3 LEAN_CANVAS_VALIDATOR tasks)
# - FEATURE_SPECIFICATION (VIBE_ALIGNER task)
# - ARCHITECTURE_DESIGN (GENESIS_BLUEPRINT task)
# Note: NOW FIXED - AUDITOR task metadata created
```

### Verify TODO-Based Handoffs Work
```bash
# Run PLANNING workflow
uv run python manual_planning_test.py

# Check handoff.json was created
cat workspaces/manual-test-project/handoff.json

# Expected: JSON with structure:
# {
#   "from_agent": "VIBE_ALIGNER",
#   "to_agent": "GENESIS_BLUEPRINT",
#   "completed": "Feature specification and scope negotiation",
#   "todos": [
#     "Select core modules from feature_spec.json",
#     "Design extension modules for complex features",
#     ...
#   ],
#   "timestamp": "2025-11-16T..."
# }
```

### Verify Session Handoff Integration Works
```bash
# ONE COMMAND to get full session context
./bin/show-context.sh

# Expected output:
# - Session handoff (from previous agent)
# - System status (current branch, commits, tests)
# - Quick commands for deeper inspection

# Update system status manually
./bin/update-system-status.sh

# Expected: Creates/updates .system_status.json

# Optional: Install git hooks for auto-updates
git config core.hooksPath .githooks
# Now .system_status.json auto-updates on commit/push
```

### Verify PLANNING Phase Works
```bash
python tests/test_planning_workflow.py
# Expected: All tests pass (state machine + transitions)
```

### Verify CODING Handler Works (E2E Tests Pass)
```bash
python3 -m pytest tests/test_coding_workflow.py -v
# Expected: 3 tests pass (test_coding_phase_execution, test_missing_feature_spec, test_quality_gates_failure)
```

### Verify DEPLOYMENT Handler Works (E2E Tests Pass)
```bash
uv run pytest tests/test_deployment_workflow.py -v
# Expected: 5 tests pass
# - test_deployment_phase_execution (success scenario)
# - test_missing_qa_report (error handling)
# - test_qa_not_approved (QA status validation)
# - test_deployment_failure_with_rollback (deployment failure handling)
# - test_post_deployment_validation_failure (health check failure handling)

# What this validates:
# ✅ DEPLOY_MANAGER agent executes 4-phase workflow
# ✅ Pre-deployment checks validate QA approval
# ✅ Deployment execution creates deploy_receipt.json
# ✅ Post-deployment validation runs health checks
# ✅ Failed deployments trigger rollback and bug report
# ✅ Phase transitions to PRODUCTION on success
```

### Verify vibe-cli Has Tool Use Loop
```bash
grep -n "tool_use\|tool_result" vibe-cli | head -10
# Expected: Multiple matches in lines 426-497
```

### Verify Research Tools Dependencies
```bash
uv run python -c "import bs4; print('✅ bs4 installed')" 2>/dev/null || echo "❌ bs4 missing (run: uv sync --all-extras)"
# Expected: ✅ bs4 installed
```

### Verify Prompt Registry Works
```bash
python tests/test_prompt_registry.py
# Expected: All tests pass (governance injection)
```

### Verify Workflow-Scoped Quality Gates Work (GAD-004 Phase 2)
```bash
python3 tests/test_quality_gate_recording.py
# Expected: All tests pass (4 tests)
# - test_quality_gate_result_recorded_in_manifest
# - test_multiple_gate_results_accumulated
# - test_get_transition_config
# - test_failed_gate_recorded_before_exception

# What this validates:
# ✅ Quality gate results are recorded in manifest.status.qualityGates
# ✅ Multiple gate results accumulate (not replaced)
# ✅ Failed gates record results before blocking transition
# ✅ Duration tracking works (duration_ms in results)
# ✅ Optional fields (message, remediation) are captured
```

### Verify Deployment-Scoped Validation Works (GAD-004 Phase 3)
```bash
# Run E2E tests
python3 tests/e2e/test_orchestrator_e2e.py
# Expected: All tests pass (3 tests)
# - test_orchestrator_initialization
# - test_workflow_yaml_loaded
# - test_prompt_registry_available

# Run performance tests (non-blocking)
python3 tests/performance/test_orchestrator_performance.py
# Expected: All tests complete (non-blocking, always exits 0)

# Verify GitHub Actions workflow exists
ls -la .github/workflows/post-merge-validation.yml
# Expected: File exists and is readable

# What this validates:
# ✅ E2E tests validate orchestrator initialization and workflow loading
# ✅ Performance tests provide non-blocking metrics
# ✅ GitHub Actions workflow will run E2E tests on push to main/develop
# ✅ Post-merge validation provides final production readiness gate
```

### Verify Multi-Layer Integration Works (GAD-004 Phase 4)
```bash
# Run integration test (tests all 3 layers together)
python3 tests/test_multi_layer_integration.py
# Expected: All tests pass
# - Layer 1: Session-scoped enforcement (pre-push checks)
# - Layer 2: Workflow-scoped quality gates (manifest recording)
# - Layer 3: Deployment-scoped validation (GitHub Actions)

# What this validates:
# ✅ All 3 GAD-004 layers work independently
# ✅ All 3 layers are properly integrated
# ✅ No conflicts between layers
# ✅ Complete defense-in-depth quality enforcement
```

### Verify Unavoidable MOTD Works (GAD-005 Week 1)
```bash
# Run MOTD tests
uv run python tests/test_motd.py
# Expected: All 5 tests pass
# - test_motd_displays (MOTD shown before execution)
# - test_motd_shows_system_status (Git, Linting, Tests)
# - test_motd_shows_session_handoff (From agent, TODOs)
# - test_motd_shows_quick_commands (show-context, pre-push-check)
# - test_motd_non_fatal (MOTD failure doesn't block execution)

# Manual test: Verify MOTD displays
uv run ./vibe-cli --help
# Expected: MOTD appears BEFORE help text
# - System Health (Git, Linting, Tests)
# - Session Handoff (if .session_handoff.json exists)
# - Quick Commands

# What this validates:
# ✅ MOTD is UNAVOIDABLE (shown in stdout before any execution)
# ✅ System status auto-updated and displayed
# ✅ Session handoff shown if exists
# ✅ MOTD failure is non-fatal (program continues)
# ✅ Critical context visible to agents without manual commands
```

### Verify Pre-Action Kernel Works (GAD-005 Week 2)
```bash
# Run Pre-Action Kernel tests
uv run python tests/test_kernel_checks.py
# Expected: All 10 tests pass
# - test_kernel_blocks_manifest_overwrite (blocks critical file overwrites)
# - test_kernel_blocks_handoff_overwrite (blocks session handoff overwrites)
# - test_kernel_allows_safe_artifacts (allows normal artifact saves)
# - test_kernel_warns_on_dirty_git (warns on uncommitted changes)
# - test_kernel_blocks_commit_with_linting_errors (blocks commits with linting errors)
# - test_kernel_allows_commit_with_passing_linting (allows commits when linting passes)
# - test_get_git_status_clean (git status detection works)
# - test_get_git_status_dirty (detects uncommitted changes)
# - test_get_system_status_exists (loads system status file)
# - test_get_system_status_missing (handles missing status file)

# What this validates:
# ✅ Kernel prevents overwriting critical files (manifest, handoff)
# ✅ Kernel warns on dirty git during state transitions
# ✅ Kernel blocks commits with linting errors
# ✅ Helper methods (_get_system_status, _get_git_status) work correctly
# ✅ Kernel provides actionable remediation steps on violations
```

### Verify GAD-005 Integration Works (HARNESS)
```bash
# Run Integration Test (MOTD + Kernel together)
uv run python tests/test_runtime_engineering.py
# Expected: Both components work together
# - MOTD displays before execution
# - Kernel blocks critical operations

# Run Performance Benchmarks (non-blocking)
uv run python tests/performance/test_runtime_performance.py
# Expected: All targets met
# - MOTD Display: <1.0s (actual: 0.827s)
# - Kernel Check: <50ms (actual: 0.00ms)
# - System Status: <200ms (actual: 0.16ms)

# What this validates:
# ✅ MOTD and Kernel work together end-to-end
# ✅ Performance targets met (MOTD fast, kernel checks instant)
# ✅ Non-blocking benchmarks (always exit 0)
# ✅ Complete GAD-005 implementation verified
```

### Verify Layer 0 Works (GAD-005-ADDITION - System Integrity)
```bash
# Run Layer 0 unit tests (14 tests)
uv run pytest tests/test_layer0_integrity.py -v
# Expected: All 14 tests pass
# - Checksum calculation
# - Manifest generation
# - Integrity verification (clean/tampered/missing files)
# - Attack simulation (modify verification script/generator)

# Run Layer 0 performance tests (3 tests)
uv run pytest tests/performance/test_layer0_performance.py -v
# Expected: All 3 tests pass
# - Integrity verification: 0.80ms (target: <100ms) ✅
# - Manifest generation: 2.16ms (target: <500ms) ✅

# Manual verification
python scripts/generate-integrity-manifest.py
# Expected: Creates .vibe/system_integrity_manifest.json with 9 critical files

python scripts/verify-system-integrity.py
# Expected: ✅ SYSTEM INTEGRITY: VERIFIED (7 critical files verified)

# What this validates:
# ✅ "Who watches the watchmen?" - regulatory framework verified
# ✅ Checksums detect tampering of critical files
# ✅ Missing files detected and reported
# ✅ Attack simulation: modifying Layer 0 scripts is detected
# ✅ Performance: <1ms integrity check (125x faster than target)
```

### Verify Layer 1 Works (GAD-005-ADDITION - Session Shell Boot Integration)
```bash
# Run Layer 1 unit tests (10 tests)
uv run pytest tests/test_layer1_boot_integration.py -v
# Expected: All 10 tests pass
# - Boot sequence runs Layer 0 verification first
# - Boot messages display correctly
# - MOTD includes system integrity status
# - Error handling (missing script, integrity failure)

# Manual verification - Test boot sequence
uv run ./vibe-cli --help
# Expected output (in order):
# 1. 🔐 VIBE AGENCY - SYSTEM BOOT
# 2. [Layer 0] Verifying system integrity...
# 3.    ✅ System integrity verified
# 4. [Layer 1] Loading session context...
# 5. MOTD displays with "System Integrity: ✅ Verified"
# 6. ✅ SYSTEM BOOT COMPLETE

# What this validates:
# ✅ Layer 0 verification integrated into vibe-cli boot sequence
# ✅ Boot-time integrity check runs BEFORE MOTD display
# ✅ Boot halts on integrity failure (with remediation steps)
# ✅ MOTD displays system integrity status in System Health section
# ✅ Non-fatal handling when verification script is missing
# ✅ Complete boot sequence works end-to-end
```

---

## 🧪 META-TEST (Self-Verification)

**Can you trust THIS document?**

Run this to verify CLAUDE.md claims match reality:

```bash
#!/bin/bash
echo "=== CLAUDE.md Self-Verification ==="

# Test 1: PLANNING really works
uv run pytest tests/test_planning_workflow.py && echo "✅ PLANNING verified" || echo "❌ PLANNING claim FALSE"

# Test 2: CODING handler E2E tests pass
uv run pytest tests/test_coding_workflow.py && echo "✅ CODING verified" || echo "❌ CODING claim FALSE"

# Test 3: vibe-cli has tool loop
grep -q "tool_use" vibe-cli && grep -q "tool_result" vibe-cli && \
  echo "✅ vibe-cli has tool support" || echo "❌ vibe-cli missing tool loop"

# Test 4: bs4 dependency
uv run python -c "import bs4" 2>/dev/null && \
  echo "✅ bs4 installed" || echo "❌ bs4 missing (run: uv sync --all-extras)"

# Test 5: Prompt Registry
uv run pytest tests/test_prompt_registry.py 2>&1 | grep -q "passed" && \
  echo "✅ Prompt Registry verified" || echo "❌ Prompt Registry not tested"

# Test 6: Session Handoff Integration
[ -f "bin/show-context.sh" ] && [ -x "bin/show-context.sh" ] && \
  echo "✅ Session handoff integration available" || echo "❌ Session handoff scripts missing"

# Test 7: Workflow-Scoped Quality Gates (GAD-004 Phase 2)
uv run pytest tests/test_quality_gate_recording.py -v 2>&1 | grep -q "passed" && \
  echo "✅ Workflow-scoped quality gates verified" || echo "❌ Quality gate recording not working"

# Test 8: Deployment-Scoped Validation (GAD-004 Phase 3)
uv run pytest tests/e2e/test_orchestrator_e2e.py -v 2>&1 | grep -q "passed" && \
  [ -f ".github/workflows/post-merge-validation.yml" ] && \
  echo "✅ Deployment-scoped validation verified" || echo "❌ E2E tests or workflow missing"

# Test 9: DEPLOYMENT handler E2E tests pass
uv run pytest tests/test_deployment_workflow.py -v 2>&1 | grep -q "5 passed" && \
  echo "✅ DEPLOYMENT handler verified" || echo "❌ DEPLOYMENT handler tests failing"

# Test 10: Multi-Layer Integration (GAD-004 Phase 4)
uv run pytest tests/test_multi_layer_integration.py -v 2>&1 | grep -q "passed" && \
  echo "✅ Multi-layer integration verified" || echo "❌ Integration test failing"

# Test 11: Unavoidable MOTD (GAD-005 Week 1)
uv run python tests/test_motd.py 2>&1 | grep -q "ALL MOTD TESTS PASSED" && \
  echo "✅ Unavoidable MOTD verified" || echo "❌ MOTD tests failing"

# Test 12: Pre-Action Kernel (GAD-005 Week 2)
uv run python tests/test_kernel_checks.py 2>&1 | grep -q "ALL KERNEL TESTS PASSED" && \
  echo "✅ Pre-Action Kernel verified" || echo "❌ Kernel tests failing"

# Test 13: GAD-005 Integration (HARNESS)
uv run python tests/test_runtime_engineering.py 2>&1 | grep -q "ALL INTEGRATION TESTS PASSED" && \
  echo "✅ GAD-005 Integration verified" || echo "❌ Integration tests failing"

# Test 14: GAD-005 Performance (HARNESS - non-blocking)
uv run python tests/performance/test_runtime_performance.py 2>&1 | grep -q "PERFORMANCE BENCHMARKS COMPLETE" && \
  echo "✅ Performance benchmarks run (non-blocking)" || echo "⚠️  Benchmarks didn't run (non-critical)"

# Test 15: GAD-005-ADDITION Layer 0 (System Integrity Verification)
uv run pytest tests/test_layer0_integrity.py tests/performance/test_layer0_performance.py -v 2>&1 | grep -q "17 passed" && \
  echo "✅ Layer 0 verified (17/17 tests)" || echo "❌ Layer 0 tests failing"

# Test 16: GAD-005-ADDITION Layer 1 (Session Shell Boot Integration)
uv run pytest tests/test_layer1_boot_integration.py -v 2>&1 | grep -q "10 passed" && \
  echo "✅ Layer 1 verified (10/10 tests)" || echo "❌ Layer 1 tests failing"
```

**If ANY test fails, CLAUDE.md is out of date or system is broken.**

---

## ⚠️ KNOWN ISSUES (As of 2025-11-15 22:39 UTC)

### 1. No vibe-cli End-to-End Test
**Issue:** Tool use loop (Lines 426-497) never tested with real API
**Impact:** Unknown if multi-turn tool execution works
**Fix:** Write `test_vibe_cli_tool_loop.py` with mock API
**Verify:** `find tests -name "*vibe_cli*"`

### 2. Complexity Near Threshold
**Issue:** `core_orchestrator.py` complexity near max (14/15 on some functions)
**Impact:** Future changes may trigger complexity violations
**Fix:** Monitor and refactor if needed
**Verify:** `python3 -m ruff check agency_os/00_system/orchestrator/core_orchestrator.py`

### 3. Documentation Drift (Non-Critical)
**Issue:** 19 files with `pip install` (should be `uv sync`)
**Impact:** Confusion for developers using old documentation
**Fix:** Update archive documentation files
**Status:** Deferred until after portfolio test

---

## 🚫 ANTI-PATTERNS (What NOT to Do)

### ❌ Don't Trust Docs Without Verification
```
BAD:  "README says complete → I assume it works"
GOOD: "README says complete → I run the test → Test missing → Status is 'untested'"
```

### ❌ Don't Confuse "Code Exists" with "Works"
```
BAD:  "coding_handler.py has 211 lines → CODING works"
GOOD: "coding_handler.py has 211 lines AND test_coding_workflow.py passes → CODING works"
```

### ❌ Don't Propose Features That Already Exist
```
BAD:  "We need a tool use loop in vibe-cli"
GOOD: "vibe-cli has tool loop (L426-497) but needs E2E test"
```

### ❌ Don't Add "Future Vision" to CLAUDE.md
```
BAD:  "Phase 4 TODO: Implement XYZ"
GOOD: "XYZ not implemented: no code in expected location"
```

### ❌ Don't Assume vibe-cli Is Autonomous
```
BAD:  "Run ./vibe-cli and it executes the project autonomously"
GOOD: "Claude Code operator uses vibe-cli to get prompts, then executes tasks manually"
```

**Critical Architecture Understanding:**
- **vibe-cli** = Prompt composition tool (returns prompts via STDOUT)
- **Claude Code** = The OPERATOR (executes prompts, does intelligent work)
- **NOT:** vibe-cli autonomous → delegates to Claude Code
- **YES:** Claude Code → uses vibe-cli → gets prompts → executes tasks

### ❌ Don't Write Tests Expecting Autonomous Behavior
```
BAD:  subprocess.run(["./vibe-cli", "run", "project"])
      # Hangs forever waiting for operator input

GOOD: orchestrator.get_next_prompt()
      # Returns prompt for operator to execute
      mock_llm_response(prompt)
      # Simulate operator providing results
      orchestrator.process_result(response)
```

### ❌ Don't Treat Claude Code as "External Service"
```
BAD:  "Ensure Claude Code operator is running and ready to respond"
      # Makes no sense - if you're reading this, YOU are Claude Code

GOOD: "As the Claude Code operator, you will:"
      1. Execute vibe-cli to get prompts
      2. Read and understand the prompt
      3. Execute the task using your capabilities
      4. Provide results back to the system
```

---

## 🎯 QUICK START (For New AI Assistants)

### Before Making Claims
```bash
# 0. Get full session context (MOST IMPORTANT - DO THIS FIRST!)
./bin/show-context.sh

# 1. Verify structure
ls -la agency_os/01_planning_framework/agents/

# 2. Check knowledge bases
wc -l agency_os/01_planning_framework/knowledge/*.yaml

# 3. Run tests to see what works
python tests/test_planning_workflow.py
python tests/test_research_agent_e2e.py  # Will fail: bs4 missing

# 4. Read honest assessment
cat ARCHITECTURE_V2.md  # Conceptual model
```

### When User Says "X is broken"
1. Run verification command from tables above
2. Read test output (don't just trust "FAILED")
3. Check actual error (e.g., "bs4 missing" vs "no integration layer")
4. Distinguish infrastructure issue from design gap

### When User Says "Implement X"
1. Search codebase first: `find . -name "*X*"`
2. Check if X already exists but is untested
3. Check ARCHITECTURE_V2.md for intended design
4. Only claim "missing" if no code exists

### **🚨 BEFORE EVERY PUSH (MANDATORY - AUTOMATED)**

**CI/CD will FAIL if you skip this!**

```bash
# ONE COMMAND - runs all checks automatically
./bin/pre-push-check.sh && git push
```

**What this does:**
1. ✅ Checks linting (ruff check)
2. ✅ Checks formatting (ruff format --check)
3. ✅ Updates system status
4. ✅ BLOCKS push if any check fails

**If checks fail:**
```bash
# Fix linting errors
uv run ruff check . --fix

# Fix formatting issues
uv run ruff format .

# Re-run checks
./bin/pre-push-check.sh
```

**Why this is MANDATORY:**
- CI/CD runs `.github/workflows/validate.yml` on every push
- It runs `uv run ruff check . --output-format=github` (line 66)
- If ruff check fails → CI/CD fails → PR cannot merge
- **./bin/pre-push-check.sh prevents CI/CD failures** by catching issues BEFORE push

**Alternative: All-in-one convenience script**
```bash
# Commits AND pushes with automatic linting enforcement
./bin/commit-and-push.sh "your commit message"
```

---

## 📚 Related Documents

- **[ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md)** - Conceptual architecture (the "should be")
- **[SSOT.md](./SSOT.md)** - Implementation decisions (the "is")
- **Test files in `tests/`** - Source of truth for "works" claims

**Document Hierarchy:**
1. **Tests** = Ultimate truth (passing = works, missing = unknown)
2. **Code** = Implementation truth (exists = implemented, missing = todo)
3. **CLAUDE.md (this file)** = Operational snapshot (dated, expect drift)
4. **ARCHITECTURE_V2.md** = Conceptual model (intended design)
5. **Other docs** = May be outdated (verify before trusting)

---

## 🔄 MAINTENANCE

### When to Update This File

**✅ Update when:**
- New component reaches "passing tests" status
- Known issue is fixed (remove from Known Issues section)
- New critical component added to codebase
- Verification command changes

**❌ Don't update for:**
- Work in progress (wait for tests to pass)
- Future plans (belongs in roadmap, not here)
- Minor refactors (unless verification changes)

### How to Update

1. Make code change
2. Write/update test
3. Run test until it passes
4. Update this file with new status + verification command
5. Update "Last Verified" date
6. Run Meta-Test to ensure claims are accurate

---

## 📊 LEGEND

| Symbol | Meaning | Definition |
|--------|---------|------------|
| ✅ Works | Has passing test | Can execute NOW, verified |
| ⚠️ Untested | Code exists, no test | Implementation present, never verified end-to-end |
| ⚠️ Stub | Minimal implementation | Allows transitions but no real functionality |
| ❌ Broken | Test fails | Known issue, see Known Issues section |
| ❌ Missing | No code found | Not implemented, no files in expected location |

---

**Last Updated:** 2025-11-16 22:30 UTC (GAD-005-ADDITION Layer 1 COMPLETE)
**Updated By:** Claude Code (Session: claude/continue-gad-0-01HG5Xtu2uCYsHjavRiZMLiz)
**Current Update:**
- ✅ **GAD-005-ADDITION Layer 1 COMPLETE** - Session Shell Boot Integration
- ✅ Added verify_system_integrity() function to vibe-cli (52 LOC)
- ✅ Added format_integrity_status() helper function for MOTD display (23 LOC)
- ✅ Integrated Layer 0 verification into main() boot sequence (runs BEFORE MOTD)
- ✅ Added boot messages: "🔐 VIBE AGENCY - SYSTEM BOOT" → Layer 0 check → MOTD
- ✅ Boot halts on integrity failure with actionable remediation steps
- ✅ MOTD now displays "System Integrity: ✅ Verified" in System Health section
- ✅ Created 10 unit tests - all passing (boot sequence, error handling, requirements validation)
- ✅ Total: 24/24 tests passing (10 Layer 1 + 14 Layer 0 from previous session)
- ✅ Zero regressions: All GAD-005 and core workflow tests still pass
- ✅ Updated CLAUDE.md with Layer 1 verification section and META-TEST entry (Test 16)
- ✅ Benefits: Complete boot-time integrity verification, unavoidable Layer 0 check, production-ready

**Previous Update:** 2025-11-16 21:36 UTC (GAD-005-ADDITION Layer 0 COMPLETE)
**Updated By:** Claude Code (Session: claude/add-show-context-script-01BJiAxBtZVGfxBtXWTjXekX)
**Update:**
- ✅ **GAD-005 COMPLETE (100%)** - Runtime Engineering with HARNESS Tests
- ✅ Week 1 (MOTD): display_motd() + 7 unit tests passing
- ✅ Week 2 (Kernel): 5 kernel methods + 10 unit tests passing
- ✅ HARNESS Integration: test_runtime_engineering.py - MOTD + Kernel work together
- ✅ HARNESS Performance: test_runtime_performance.py - all targets met (non-blocking)
- ✅ Performance Results: MOTD 0.827s (<1s), Kernel 0.00ms (<50ms), Status 0.16ms (<200ms)
- ✅ Created 2 HARNESS test files (integration + performance)
- ✅ Updated CLAUDE.md with HARNESS verification section
- ✅ Added META-TEST entries (Test 13: Integration, Test 14: Performance)
- ✅ Benefits: Complete end-to-end verification, performance validated, production-ready
- ✅ Zero regressions - all existing tests still pass (planning, MOTD, kernel)

**Previous Update:** 2025-11-16 20:50 UTC by Claude Code
- ✅ **GAD-005 Week 2 COMPLETE** - Pre-Action Kernel Implementation
- ✅ Added KernelViolationError exception to core_orchestrator.py
- ✅ Implemented 5 kernel methods: _kernel_check_save_artifact(), _kernel_check_transition_state(), _kernel_check_git_commit(), _get_system_status(), _get_git_status()
- ✅ Integrated kernel check into save_artifact() method - validates before saving
- ✅ Created tests/test_kernel_checks.py - all 10 tests passing
- ✅ Kernel prevents overwriting critical files (manifest, session handoff)
- ✅ Kernel warns on dirty git during state transitions
- ✅ Kernel blocks commits with linting errors (actionable remediation provided)
- ✅ Updated CLAUDE.md with verification commands and META-TEST entry (Test 12)
- ✅ Benefits: Runtime enforcement of safety rules, fail-fast with guidance, defense-in-depth
- ✅ Zero regressions - all existing tests still pass (planning workflow, MOTD)

**Previous Update:** 2025-11-16 19:05 UTC by Claude Code
- ✅ **GAD-005 Week 1 COMPLETE** - Unavoidable MOTD Implementation
- ✅ Implemented display_motd() + 5 helper functions in vibe-cli (+191 LOC)
- ✅ MOTD shows System Health (Git, Linting, Tests) + Session Handoff + Quick Commands
- ✅ Created tests/test_motd.py - all 5 tests passing
- ✅ MOTD integrated into main() - appears BEFORE all execution (unavoidable)
- ✅ MOTD is non-fatal - program continues even if MOTD display fails
- ✅ Updated CLAUDE.md with verification commands and META-TEST entry
- ✅ Benefits: Critical context now visible to agents automatically, no manual commands needed
- ✅ Zero regressions - all existing tests still pass

**Updates:**
- ✅ **GAD-004 COMPLETE (100%)** - Multi-Layered Quality Enforcement System
- ✅ Implemented GAD-004 Phase 4 - Integration & Documentation
- ✅ Created tests/test_multi_layer_integration.py - integration test passing
- ✅ All 3 layers verified working together (Session → Workflow → Deployment)
- ✅ Fixed all linting errors (0 errors, ruff check passes)
- ✅ Total tests: 107/108 passing (1 pre-existing failure unrelated to GAD-004)
- ✅ Zero regressions - all existing functionality intact
- ✅ Updated session handoff with GAD-004 completion evidence

**Previous Update:** 2025-11-16 15:30 UTC by Claude Code
- ✅ **DEPLOYMENT Handler COMPLETE** - Phase 4 SDLC Implementation
- ✅ Implemented full deployment_handler.py with DEPLOY_MANAGER integration (272 lines)
- ✅ 4-phase deployment workflow: Pre-Deployment Checks → Deployment Execution → Post-Deployment Validation → Report Generation
- ✅ Created tests/test_deployment_workflow.py - all 5 E2E tests passing
- ✅ Tests validate: success scenario, error handling, QA approval checks, rollback on failure, health check validation
- ✅ Added bug_report.json and rollback_info.json to artifact registry
- ✅ Updated CLAUDE.md with DEPLOYMENT verification commands and META-TEST
- ✅ Benefits: Complete SDLC workflow coverage (PLANNING → CODING → DEPLOYMENT → PRODUCTION)
- ✅ Zero regression: All existing tests still pass

**Previous Update:** 2025-11-16 15:14 UTC by Claude Code
- ✅ **GAD-004 Phase 3 COMPLETE** - Deployment-Scoped Validation
- ✅ Created `.github/workflows/post-merge-validation.yml` (E2E tests on push to main/develop)
- ✅ Created `tests/e2e/test_orchestrator_e2e.py` - all 3 E2E tests passing
- ✅ Created `tests/performance/test_orchestrator_performance.py` - non-blocking perf tests
- ✅ Added verification commands to CLAUDE.md for Phase 3
- ✅ Added Test 8 to META-TEST for deployment-scoped validation
- ✅ Benefits: Final production readiness gate, E2E validation on merge, performance monitoring
- ✅ Zero regression: All existing tests still pass (planning, session enforcement, quality gates)

**Previous Update:** 2025-11-16 13:40 UTC by Claude Code
- ✅ **Automatic Linting Enforcement COMPLETE** - Belt + Suspenders approach
- ✅ Layer 1 (Visibility): `show-context.sh` displays linting status at top
- ✅ Layer 2 (Enforcement): `./bin/commit-and-push.sh` blocks bad commits
- ✅ Layer 3 (Final Gate): CI/CD validation remains
- ✅ Works everywhere: browser, desktop, one-time environments (no git hooks needed)
- ✅ Auto-fixes what it can (F401, E501), blocks what it can't (F821)
- ✅ Tested LIVE: Created linting errors, verified detection + blocking
- ✅ Core Principle #6 updated: Use `./bin/commit-and-push.sh` instead of manual checklist
- ✅ Zero abstractions: Just shell + JSON (like session handoff system)

**Previous Update:** 2025-11-16 11:25 UTC by Claude Code
- ✅ **Session Handoff Integration COMPLETE** - Holistic two-file handoff system
- ✅ ONE command (`./bin/show-context.sh`) gives full session context
- ✅ Two-file system: `.session_handoff.json` (manual) + `.system_status.json` (auto-updated)
- ✅ Git hooks available for auto-updates (optional: `git config core.hooksPath .githooks`)
- ✅ Shell scripts: `show-context.sh`, `update-system-status.sh`, `create-session-handoff.sh`
- ✅ Zero abstractions: Just shell + JSON (no validation, no classes)
- ✅ Verified: show-context.sh displays both files correctly

**Previous Update:** 2025-11-16 10:07 UTC by Claude Code
- ✅ **TODO-Based Handoffs IMPLEMENTED** - Simple handoff.json file created between agents
- ✅ Handoffs active: LEAN_CANVAS_VALIDATOR → VIBE_ALIGNER → GENESIS_BLUEPRINT
- ✅ Benefits: Workflow transparency, resumable execution, human-readable audit trail
- ✅ Zero complexity: Just JSON file read/write (no abstractions, no validation layers)
- ✅ Verified: handoff.json created successfully in test workspace

**Previous Update:** 2025-11-16 08:12 UTC by Claude Code
- ✅ **File-Based Delegation (GAD-003) COMPLETE** - E2E test validates full PLANNING workflow
- ✅ Fixed planning_handler.py task IDs (scope_negotiation → 05_scope_negotiation, architecture_generation → 05_handoff)
- ✅ Added architecture.json to artifact registry in core_orchestrator.py
- ✅ Created manual_planning_test.py with schema-compliant mock responses for all PLANNING agents
- ✅ Verified: BUSINESS_VALIDATION, FEATURE_SPECIFICATION, ARCHITECTURE_DESIGN all complete successfully

**Previous Update:** 2025-11-15 23:30 UTC by Claude Code
- ✅ Added AI-FIRST documentation (AGENTS_START_HERE.md, README.md update)
- ✅ Added critical anti-patterns: "vibe-cli is NOT autonomous", "Claude Code is OPERATOR"
- ✅ Clarified architecture: vibe-cli returns prompts, doesn't execute autonomously

**Meta-Verification:**
```bash
# This document claims to be accurate as of 2025-11-16 15:30 UTC
# Run meta-test above to verify claims match reality
python3 tests/test_quality_gate_recording.py  # Validates GAD-004 Phase 2
python3 manual_planning_test.py  # Validates GAD-003 file-based delegation
uv run pytest tests/test_deployment_workflow.py -v  # Validates DEPLOYMENT handler Phase 4
```
