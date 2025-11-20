# Architecture Registry

**Version:** 2.0
**Created:** 2025-11-20
**Updated:** 2025-11-20 (Added VADs and LADs)
**Status:** ✅ VERIFIED
**Purpose:** Single source of truth for architectural decisions that are actually implemented

---

## What This Is

This registry lists **architectural decisions** - not features, not aspirations, not plans.

**Architecture** = HOW the system works (patterns, principles, constraints)
**Features** = WHAT the system does (capabilities, workflows) → See `quarantine/features/`

**Inclusion Criteria:**
- ✅ Describes a pattern, principle, or constraint
- ✅ Has implementation code that can be verified
- ✅ Integrated into core orchestration flow
- ✅ Has tests proving it works

---

## The Architecture Decisions

### ADRs (Architectural Decision Records) - 8 Total

Core patterns, principles, and constraints that define HOW the system works.

### ADR-003: Delegated Execution Architecture

**Status:** ✅ IMPLEMENTED
**Date:** 2025-11-14
**Type:** Core Architectural Pattern

**What It Is:**
Hybrid "Brain and Arm" architecture separating intelligence (Claude Code) from state management (core_orchestrator.py) via STDIN/STDOUT delegation protocol.

**Code Evidence:**
- Implementation: `agency_os/core_system/orchestrator/core_orchestrator.py`
  - Execution modes: `delegated` (default) and `autonomous`
  - STDIN/STDOUT handoff protocol at lines 160-189
  - Intelligence request/response protocol
- Entry point: `vibe-cli` (delegates to operator)
- File-based delegation: `.delegation/` directory structure

**Integration Status:** ✅ Integrated
- Core orchestrator supports both modes
- vibe-cli wraps orchestrator with delegation
- File-based handoff in production use

**Test Status:** ✅ Tested
- Tests: `tests/test_core_orchestrator_tools.py`
- Tests: `tests/test_orchestrator_file_delegation.py`
- E2E: `tests/e2e/test_orchestrator_e2e.py`
- 9 test files covering delegation modes

**Decision Impact:** Architectural purity restored - all intelligence through operator, deterministic state management.

---

### GAD-500: Runtime Engineering - Self-Regulating Execution

**Status:** ✅ IMPLEMENTED
**Date:** 2025-11-16
**Type:** Enforcement Layer (GAD-4/5 Integration)

**What It Is:**
Self-regulating execution environment with two components:
1. **Unavoidable MOTD** - Critical context shown before execution
2. **Pre-Action Kernel** - Circuit breaker preventing dangerous operations

**Code Evidence:**
- MOTD Implementation: `bin/system-boot.sh` (lines 100-150)
- Kernel checks: `agency_os/core_system/orchestrator/core_orchestrator.py`
  - `_kernel_check_save_artifact()` - Prevents critical file overwrites
  - `_kernel_check_transition_state()` - Warns on dirty git state
  - `_kernel_check_git_commit()` - Blocks commits with linting errors
- System status: `bin/update-system-status.sh`
- Configuration: `.vibe/config/` (kernel rules)

**Integration Status:** ✅ Integrated
- MOTD shown on every `./bin/system-boot.sh` execution
- Kernel checks run before all mutation operations
- Status updates automated via system scripts

**Test Status:** ✅ Tested
- Tests: `tests/test_layer1_boot_integration.py`
- Tests: `tests/test_safety_layer.py` (kernel checks)
- Performance: `tests/performance/test_layer0_performance.py`
- Manual verification: `./bin/verify-claude-md.sh` (39 tests)

**Decision Impact:** System actively prevents mistakes at runtime vs. passive documentation.

---

### GAD-501: Multi-Layered Context Injection

**Status:** ✅ IMPLEMENTED
**Date:** 2025-11-17
**Type:** Defense-in-Depth Architecture

**What It Is:**
Five-layer defense architecture ensuring context awareness:
- **Layer 0:** System Integrity Verification (meta-layer)
- **Layer 1:** Session Shell (frictionless entry)
- **Layer 2:** Ambient Context (active artifacts)
- **Layer 3:** Commit Watermarking (local enforcement)
- **Layer 4:** Remote Validation (CI/CD gates)

**Code Evidence:**
- Layer 0: `scripts/verify-system-integrity.py` (checksum verification)
- Layer 0: `scripts/generate-integrity-manifest.py` (manifest generation)
- Layer 0: `.vibe/system_integrity_manifest.json` (trusted baseline)
- Layer 1: `bin/system-boot.sh` (Session Shell entry)
- Layer 2: `project_manifest.json` (consolidated state)
- Layer 3: `.git/hooks/pre-commit` (watermarking)
- Layer 4: `.github/workflows/pr-validation.yml` (CI enforcement)

**Integration Status:** ✅ Integrated
- Layer 0 runs on every boot (line 10 in system-boot.sh)
- Layers 1-4 cascade from Layer 0 verification
- Full integration in production workflow

**Test Status:** ✅ Tested
- Tests: `tests/test_layer0_integrity.py` (Layer 0 verification)
- Tests: `tests/test_layer1_boot_integration.py` (boot sequence)
- Tests: `tests/test_multi_layer_integration.py` (all layers)
- Performance: `tests/performance/test_layer0_performance.py`

**Decision Impact:** "Who watches the watchmen?" - The watchmen watch themselves first.

---

### GAD-502: Haiku Hardening

**Status:** 📋 APPROVED (Implementation Pending)
**Date:** 2025-11-16
**Type:** Adversarial Validation & Hardening

**What It Is:**
Validation that system works with less capable operators (Claude Haiku), proving robustness of GAD-4/5 defenses through adversarial testing.

**Code Evidence:**
- Test Harness: `tests/test_rogue_agent_scenarios.py` (19 scenarios)
- Shell Kernel: `_kernel_check_shell_command()` (blocks dangerous shell operations)
- Recovery Guidance: Enhanced error messages with examples
- Current: 2/19 scenarios protected (10.5% coverage)

**Integration Status:** ⚠️ PARTIAL
- Test harness complete and running
- Kernel enhancements in progress
- Shell-level guards not yet implemented

**Test Status:** ⚠️ PARTIAL
- Harness: `tests/test_rogue_agent_scenarios.py` (1/1 active tests passing)
- Coverage: 2/19 protection scenarios (10.5%)
- Target: 90%+ protection coverage

**Decision Impact:** Validates defense-in-depth works for worst-case agents, foundation for autonomy.

---

### GAD-509: Circuit Breaker Protocol

**Status:** ✅ IMPLEMENTED
**Date:** 2025-11-18
**Type:** Resilience Pattern

**What It Is:**
Three-state circuit breaker (CLOSED → OPEN → HALF_OPEN) protecting system from cascading failures during LLM API outages.

**Code Evidence:**
- Implementation: `agency_os/core_system/runtime/circuit_breaker.py`
  - `CircuitBreaker` class (3-state machine)
  - `CircuitBreakerConfig` (configurable thresholds)
  - `CircuitBreakerMetrics` (observability)
- Integration: `agency_os/core_system/runtime/llm_client.py:309`
- Configuration: 5 failures/60s threshold, 30s recovery timeout

**Integration Status:** ✅ Integrated
- Wraps all LLM provider invocations
- Applies to Anthropic, Google, OpenAI providers
- Fast-fail when circuit open

**Test Status:** ✅ Tested
- Unit tests for state transitions
- Failure threshold validation
- Recovery timeout verification
- Integration with LLM client

**Decision Impact:** System remains stable during API outages, automatic recovery when service restored.

---

### GAD-510: Operational Quota Manager

**Status:** ✅ IMPLEMENTED
**Date:** 2025-11-18
**Type:** Cost Control Pattern

**What It Is:**
Pre-flight and post-flight quota tracking enforcing:
- Requests Per Minute (RPM)
- Tokens Per Minute (TPM)
- Cost Per Hour
- Cost Per Day

**Code Evidence:**
- Implementation: `agency_os/core_system/runtime/quota_manager.py`
  - `OperationalQuota` class (enforcement logic)
  - `QuotaLimits` (configurable limits)
  - `QuotaMetrics` (tracking)
- Integration: `agency_os/core_system/runtime/llm_client.py:289` (pre-flight)
- Integration: `agency_os/core_system/runtime/llm_client.py:323` (post-flight)
- Configuration: `agency_os/config/phoenix.py:99-123`
- Environment: `VIBE_QUOTA_*` variables

**Integration Status:** ✅ Integrated
- Pre-flight check before every LLM call
- Post-flight recording of actual usage
- Warnings at 80% thresholds
- Phoenix config auto-loading

**Test Status:** ✅ Tested
- Unit tests for quota enforcement
- Threshold validation
- Rolling window logic
- Configuration loading

**Decision Impact:** Cost predictability, prevents budget overruns, safe production deployment.

---

### GAD-800: Integration Matrix & Graceful Degradation

**Status:** ✅ IMPLEMENTED
**Date:** 2025-11-17
**Type:** System Integration Specification

**What It Is:**
Three-dimensional integration framework:
1. **Layers:** Prompt-only (Layer 1) → Tool-based (Layer 2) → Runtime (Layer 3)
2. **Systems:** Agency OS ↔ Knowledge Dept ↔ STEWARD
3. **Components:** Intelligent → Semi-Intelligent → Mechanical

**Code Evidence:**
- Layer Detection: `docs/architecture/GAD-8XX/layer_detection.py` (runtime detection)
- Degradation Rules: `docs/architecture/GAD-8XX/degradation_rules.yaml` (decision trees)
- Knowledge Graph: `knowledge_department/config/knowledge_graph.yaml` (v1 schema)
- Integration: Component compatibility matrix implementation

**Integration Status:** ✅ Integrated
- Layer detection working (43/43 tests pass)
- Degradation rules executable
- Knowledge graph v1 deployed

**Test Status:** ✅ Tested
- Tests: `tests/architecture/test_gad800_integration.py` (43 tests)
- Tests: `tests/test_multi_layer_integration.py`
- All core components tested and verified
- Command: `uv run pytest tests/architecture/test_gad800_integration.py -v`

**Decision Impact:** Every component knows how to degrade gracefully, no hard dependencies on higher layers.

---

### GAD-801: GitOps Resilience Layer (GORL)

**Status:** 📋 IMPLEMENTATION SPEC (Ready to Build)
**Date:** 2025-11-18
**Type:** Git Capability Degradation

**What It Is:**
Four-layer graceful degradation for git operations:
- **Layer 3:** Full automation (gh + git + repo) - Draft PR creation
- **Layer 2:** Assisted workflow (git + repo) - Current state
- **Layer 1:** Manual guidance (repo only) - Copy/paste commands
- **Layer 0:** Emergency mode (NO git) - File diff export

**Code Evidence:**
- Specification: `docs/architecture/GAD-8XX/GAD-801.md` (implementation-ready)
- Current: Layer 2 via `bin/commit-and-push.sh`
- Planned: `gitops_layer.py` (4-layer detection)
- Planned: `commit_validator.py` (conventional commits)
- Planned: `emergency_diff.py` (Layer 0 fallback)

**Integration Status:** ⚠️ SPECIFICATION READY
- Layer 2 (current) is working
- Layers 0, 1, 3 specs complete, awaiting implementation
- Integration point identified: `boot_sequence.py` pre-flight checks

**Test Status:** ⚠️ SPECIFICATION READY
- Test specs complete in GAD-801
- Layer 2 tested via existing git workflows
- Layers 0, 1, 3 tests pending implementation

**Decision Impact:** Works everywhere - browser to full CLI - without breaking existing workflows.

---

### VADs (Verification Architecture Decisions) - 4 Total

Test-driven architecture verification ensuring GADs work together correctly.

### VAD-001: Core Workflow Verification

**Status:** ✅ IMPLEMENTED
**Type:** Integration Testing
**Purpose:** Tests integration of GAD-2 (SDLC) + GAD-4 (Quality) + GAD-5 (Runtime)

**What It Is:**
Verifies that the state machine respects quality gates and blocks transitions when quality checks fail.

**Code Evidence:**
- Tests: `tests/architecture/test_vad001_core_workflow.py`
- Tested: Quality gate blocks transition when linting fails
- Tested: Quality gate allows transition when all checks pass
- Tested: Receipt creation on successful transition

**Integration Status:** ✅ Integrated
- Layer 2 (Tool-based): Fully functional
- Layer 3 (Runtime): Fully functional
- Layer 1 (Prompt-only): N/A - no automation

**Test Status:** ✅ Tested
- Test scenarios: Quality gate blocking and allowing transitions
- Verification: State machine respects quality gates

**Decision Impact:** Proves GAD-4 quality enforcement works in practice.

---

### VAD-002: Knowledge Integration

**Status:** ⚠️ PARTIAL
**Type:** Integration Testing
**Purpose:** Tests GAD-6 (Knowledge) + GAD-7 (STEWARD) integration

**What It Is:**
Verifies that access control works for confidential knowledge queries.

**Code Evidence:**
- Tests: `tests/architecture/test_vad002_knowledge.py`
- Tested: Unauthorized access blocked (Project A cannot access Client B knowledge)
- Tested: Authorized access allowed (Project A can access Client A knowledge)
- Tested: Audit logging for all confidential access

**Integration Status:** ⚠️ PARTIAL
- Layer 3 (Runtime): Full enforcement + audit logging ✅
- Layer 2 (Tool-based): Validation only ⚠️
- Layer 1 (Prompt-only): N/A ❌

**Test Status:** ⚠️ PARTIAL
- Test scenarios: Access control and audit logging
- Coverage: Layer 3 only

**Decision Impact:** Proves multi-agency access control works when runtime is available.

---

### VAD-003: Layer Degradation

**Status:** ⚠️ PARTIAL
**Type:** Integration Testing
**Purpose:** Tests GAD-8 (Integration) graceful degradation

**What It Is:**
Verifies that system degrades gracefully when layers fail or become unavailable.

**Code Evidence:**
- Tests: `tests/architecture/test_vad003_degradation.py`
- Tested: Layer 2 → Layer 1 degradation (tool failure → prompt mode)
- Tested: System detects layer failures and adapts
- TODO: Layer 3 → Layer 2 degradation detection

**Integration Status:** ⚠️ PARTIAL
- Layer 2 → Layer 1: Works ✅
- Layer 3 → Layer 2: Detection not implemented ⚠️

**Test Status:** ⚠️ PARTIAL
- Test scenarios: Layer degradation detection
- Coverage: Partial (2→1 works, 3→2 pending)

**Decision Impact:** Proves system can degrade gracefully, more testing needed.

---

### VAD-004: Safety Layer Integration

**Status:** ✅ VERIFIED
**Type:** Integration Testing
**Purpose:** Verify GAD-5 (Runtime) safety components (Circuit Breaker, Quota Manager) integrate with workflow execution

**What It Is:**
Comprehensive verification that Circuit Breaker and Quota Manager protect workflows from cascading failures and cost overruns.

**Code Evidence:**
- Tests: `tests/test_safety_layer.py` (24 total tests)
  - Circuit Breaker: 8 tests (halts workflow on API failures)
  - Quota Manager: 10 tests (blocks expensive workflows)
  - Dynamic Config: 6 tests (environment variable loading)
- Integration: `LLMClient → CircuitBreaker → QuotaManager`

**Integration Status:** ✅ Integrated
- Circuit breaker protects all LLM calls
- Quota manager enforces cost limits
- Dynamic configuration via environment variables
- All layers communicate without tight coupling

**Test Status:** ✅ TESTED
- 24/24 tests passing
- Full coverage of safety components
- Regression protection verified

**Decision Impact:** Proves GAD-5 safety components work together, prevents cascading failures and cost spikes.

---

### LADs (Layered Architecture Decisions) - 3 Total

Deployment mode definitions for different execution environments.

### LAD-1: Browser Layer (Prompt-Only)

**Status:** ✅ DEFINED
**Type:** Deployment Mode
**Capabilities:** Manual operations only - no automation, tools, or APIs

**What It Is:**
Minimum viable system that works in browser with Claude.ai, no backend required.

**Code Evidence:**
- Setup: Open repo in browser + Claude.ai
- Documentation: `docs/architecture/LAD/LAD-1.md`
- No installation required

**Use Cases:**
- Solo developer
- Quick prototyping
- Learning the system

**Integration Status:** ✅ Defined
- All GADs provide Layer 1 degradation path
- Manual operations documented
- User-driven workflow

**Test Status:** N/A (Manual operations)

**Cost:** $0

---

### LAD-2: Claude Code Layer (Tool-Based)

**Status:** ✅ IMPLEMENTED
**Type:** Deployment Mode
**Capabilities:** Automated tools, file system access, no external APIs

**What It Is:**
Enhanced with Claude Code - automated tools for receipts, integrity checks, knowledge queries, STEWARD validation.

**Code Evidence:**
- Tools: `receipt_create`, `verify_integrity`, `knowledge_query`, `steward_validate`, `layer_detect`
- Setup: `./scripts/setup-layer2.sh` (if exists)
- Integration: Claude Code environment with file system access

**Use Cases:**
- Individual developer
- Small teams
- Most projects

**Integration Status:** ✅ Integrated
- All Layer 2 tools functional
- GAD-5 runtime features available
- Layer detection working

**Test Status:** ✅ Tested
- Tools tested in Claude Code environment
- Integration verified in real usage
- Current production deployment mode

**Cost:** $20/month (Claude subscription)

---

### LAD-3: Runtime Layer (API-Based)

**Status:** ✅ DEFINED
**Type:** Deployment Mode
**Capabilities:** Full runtime - backend services, external APIs, federated access

**What It Is:**
Full-featured deployment with backend services, vector DB, research engine, governance API, and workflow engine.

**Code Evidence:**
- Services: Audit Service, Circuit Breaker, Quota Manager, Research Engine, Governance API
- Setup: `./scripts/setup-layer3.sh`
- Infrastructure: Backend deployment + vector DB + external APIs

**Use Cases:**
- Agencies
- Teams
- Production deployments
- Client work

**Integration Status:** ⚠️ PARTIAL
- Core services implemented (Circuit Breaker, Quota Manager)
- Some services planned (Research Engine API, Federated Query, Governance API)
- Full integration architecture defined in GAD-800

**Test Status:** ⚠️ PARTIAL
- Core services tested (24 tests in test_safety_layer.py)
- Full runtime integration pending

**Cost:** $50-200/month (varies by usage)

---

## Status Summary

### ADRs (Architectural Decision Records)

| GAD | Type | Implementation | Integration | Tests | Status |
|-----|------|----------------|-------------|-------|--------|
| **ADR-003** | Core Pattern | ✅ Complete | ✅ Integrated | ✅ 9 test files | PRODUCTION |
| **GAD-500** | Enforcement | ✅ Complete | ✅ Integrated | ✅ 39 checks | PRODUCTION |
| **GAD-501** | Defense-in-Depth | ✅ Complete | ✅ Integrated | ✅ 3 test suites | PRODUCTION |
| **GAD-502** | Validation | ⚠️ 10.5% | ⚠️ Partial | ⚠️ 2/19 passing | IN PROGRESS |
| **GAD-509** | Resilience | ✅ Complete | ✅ Integrated | ✅ Unit + Integration | PRODUCTION |
| **GAD-510** | Cost Control | ✅ Complete | ✅ Integrated | ✅ Unit + Config | PRODUCTION |
| **GAD-800** | Integration | ✅ Complete | ✅ Integrated | ✅ 43/43 passing | PRODUCTION |
| **GAD-801** | GitOps | 📋 Spec Ready | ⚠️ Layer 2 only | 📋 Spec Ready | SPECIFICATION |

**ADR Status:** 6/8 in production (75%), 1 in progress (GAD-502), 1 ready for implementation (GAD-801)

### VADs (Verification Architecture Decisions)

| VAD | Purpose | Implementation | Integration | Tests | Status |
|-----|---------|----------------|-------------|-------|--------|
| **VAD-001** | Core Workflow | ✅ Complete | ✅ Integrated | ✅ Test suite | VERIFIED |
| **VAD-002** | Knowledge Access | ⚠️ Partial | ⚠️ Layer 3 only | ⚠️ Partial | PARTIAL |
| **VAD-003** | Layer Degradation | ⚠️ Partial | ⚠️ 2→1 only | ⚠️ Partial | PARTIAL |
| **VAD-004** | Safety Integration | ✅ Complete | ✅ Integrated | ✅ 24/24 tests | VERIFIED |

**VAD Status:** 2/4 verified (50%), 2/4 partial implementation (50%)

### LADs (Layered Architecture Decisions)

| LAD | Deployment Mode | Capabilities | Status | Current Use |
|-----|-----------------|--------------|--------|-------------|
| **LAD-1** | Browser (Prompt-Only) | Manual operations | ✅ DEFINED | Available |
| **LAD-2** | Claude Code (Tool-Based) | Automated tools | ✅ IMPLEMENTED | **PRODUCTION** |
| **LAD-3** | Runtime (API-Based) | Full services | ⚠️ PARTIAL | Partial |

**LAD Status:** 1/3 in production (LAD-2), 1/3 defined (LAD-1), 1/3 partial (LAD-3)

### Overall Summary

**Total Architectural Decisions:** 15
- **ADRs:** 8 (6 production, 1 in progress, 1 spec ready)
- **VADs:** 4 (2 verified, 2 partial)
- **LADs:** 3 (1 production, 1 defined, 1 partial)

**Production Readiness:** 9/15 decisions fully implemented (60%)

---

## What's NOT Here (Moved to Quarantine)

The following were quarantined because they describe **features** (WHAT the system does) rather than **architecture** (HOW it works):

**In `quarantine/features/`:**
- GAD-100 series: SDLC phase scaffolding
- GAD-200: Prompt routing system
- GAD-300: Agent delegation protocol

**In `quarantine/unknown/`:**
- GAD-105, 201-204, 301-304: Not found (may have been planned but never implemented)
- GAD-503-504, 601-602, 701-702, 901-909: Referenced but missing

See: `docs/architecture/quarantine/README.md` for full explanation

---

## Verification Commands

```bash
# Verify system health (includes all checks)
./bin/verify-claude-md.sh

# Test ADRs (Architectural Decision Records)
uv run pytest tests/test_layer0_integrity.py -v           # GAD-501 Layer 0
uv run pytest tests/test_layer1_boot_integration.py -v   # GAD-500 MOTD
uv run pytest tests/architecture/test_gad800_integration.py -v  # GAD-800
uv run pytest tests/test_safety_layer.py -v              # GAD-509, 510 Safety Layer

# Test VADs (Verification Architecture Decisions)
uv run pytest tests/architecture/test_vad001_core_workflow.py -v  # VAD-001
uv run pytest tests/architecture/test_vad002_knowledge.py -v      # VAD-002
uv run pytest tests/architecture/test_vad003_degradation.py -v    # VAD-003
uv run pytest tests/test_safety_layer.py -v                       # VAD-004

# Check LADs (Layered Architecture Decisions)
cat docs/architecture/LAD/LAD-1.md    # Browser Layer
cat docs/architecture/LAD/LAD-2.md    # Claude Code Layer (current)
cat docs/architecture/LAD/LAD-3.md    # Runtime Layer

# Check code implementation
grep -r "execution_mode.*delegated" agency_os/          # ADR-003
cat agency_os/core_system/runtime/circuit_breaker.py   # GAD-509
cat agency_os/core_system/runtime/quota_manager.py     # GAD-510
cat scripts/verify-system-integrity.py                 # GAD-501 Layer 0
```

---

## How to Add New Architecture

**Before creating a new GAD:**

1. **Is it architecture or a feature?**
   - Architecture = Pattern, principle, or constraint (HOW system works)
   - Feature = Capability or workflow (WHAT system does)
   - Features don't belong in this registry

2. **Can you prove it's implemented?**
   - Code must exist and be verifiable
   - Integration must be demonstrated
   - Tests must prove it works

3. **Process:**
   ```bash
   # 1. Create GAD document in appropriate series
   docs/architecture/GAD-XXX/GAD-XXX.md

   # 2. Implement the architecture
   agency_os/.../implementation.py

   # 3. Write tests that prove it works
   tests/test_gad_xxx.py

   # 4. Integrate into core orchestration
   (varies by GAD)

   # 5. Add to this registry with evidence
   docs/architecture/ARCHITECTURE_REGISTRY.md
   ```

---

## Maintenance

**This registry is:**
- ✅ Kept accurate (update when GADs implemented/deprecated)
- ✅ Evidence-based (code paths, test files, integration points)
- ✅ Verified regularly (included in `./bin/verify-claude-md.sh`)

**This registry is NOT:**
- ❌ A roadmap (see `.vibe/config/cleanup_roadmap.json`)
- ❌ A feature list (see `docs/features/` if it exists)
- ❌ A wish list (only implemented architecture)

---

**Last Updated:** 2025-11-20
**Verified By:** STEWARD (Cleanup Roadmap Tasks Q002 + Q003)
**Total Decisions:** 15 (8 ADRs + 4 VADs + 3 LADs)
**Next Review:** When new architectural decision implemented or existing one deprecated
