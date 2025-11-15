# SSOT - Single Source of Truth

**Version:** 1.0
**Date:** 2025-11-15
**Purpose:** Implementation decisions, folder structure, API specifications
**Companion:** [ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md) (conceptual model)

---

## 🎯 What This Document Is

This is the **single source of truth** for implementation decisions in vibe-agency.

- **Architecture decisions** → Documented here
- **Folder structure** → Final decisions recorded
- **API specifications** → Concrete interfaces defined
- **Open questions** → None (all answered, see decisions below)
- **Deferred features** → Explicitly listed

For conceptual understanding, see [ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md).

---

## ✅ Decisions Made (2025-11-15)

### 1. Prompt Registry Location
**Decision:** `agency_os/00_system/runtime/prompt_registry.py`

**Why:**
- Part of runtime infrastructure (same level as prompt_runtime.py)
- Shared across all phases (system-wide utility)
- Not framework-specific (not in 01-05 phases)

**Status:** Not implemented (MVP priority #1)

---

### 2. System Steward Framework Position
**Decision:** Stays at repo root (`/system_steward_framework/`)

**Why:**
- SSF = Meta-governance (defines rules for AOS)
- AOS = Product execution (applies rules to user projects)
- Guardian Directives bridge the two (injected at composition-time)
- No orchestrator calls (SSF agents invoked manually)

**Integration:**
- **Design-time:** SSF defines rules (Guardian Directives, SOPs)
- **Composition-time:** Prompt Registry injects SSF rules into AOS prompts
- **Runtime:** Claude Code enforces rules (intelligence layer)
- **No orchestrator calls to SSF agents** (manual sessions only)

**Status:** Implemented, separation documented

---

### 3. RESEARCH_AGENT Scope
**Decision:** Stays in `01_planning_framework/agents/research/`

**Why:**
- Currently only PLANNING phase uses research (validated)
- Future: Other phases MAY use research (TBD)
- If cross-phase usage emerges → Refactor to `00_system/agents/` (Phase N)
- Current location OK for MVP (YAGNI principle)

**Future Intent:**
- Research capability COULD be useful for CODE_GENERATOR (tech comparisons)
- Research capability COULD be useful for QA_VALIDATOR (security advisories)
- BUT: No concrete use case yet, so keep in planning/ until proven need
- When moved: Update imports, maintain backward compatibility

**Status:** Implemented, location validated for current scope

---

### 4. Governance Injection Mechanism
**Decision:** Automatic injection via Prompt Registry

**Implementation:**
```python
# Every prompt composed via Registry automatically includes:
# 1. Guardian Directives (from SSF)
# 2. Current manifest state (workspace context)
# 3. Quality gates (if applicable)
# 4. Tool definitions (if agent uses tools)
# 5. SOPs (if HITL workflow)
```

**Not:** Manual addition to every `_prompt_core.md` (not scalable)

**Status:** Designed, implementation pending

---

### 5. Handlers 3-5 Status
**Decision:** Documented as Phase 4 TODO (stubs remain functional)

**Implementation Status:**
- ✅ Transition logic works (can move through phases)
- ✅ Create mock artifacts (qa_report.json, deploy_receipt.json, maintenance_log.json)
- ❌ No real execution (no pytest, no cloud deployment, no monitoring)

**Explicitly Marked:**
- `testing_handler.py:7-8` - "TODO (Phase 3): Full implementation"
- `deployment_handler.py:7-8` - "TODO (Phase 3): Full implementation"
- `maintenance_handler.py:7-8` - "TODO (Phase 3): Full implementation"

**When to Implement:** Phase 4 roadmap (6-12 months)

**Status:** Documented stubs, no changes needed

---

### 6. GENESIS_UPDATE Integration
**Decision:** Defer to Phase N (not MVP)

**Semantic Purpose:**
- GENESIS_BLUEPRINT creates initial architecture (fresh design)
- GENESIS_UPDATE patches existing architecture (iterative changes)
- Use case: When requirements change mid-project

**Why Deferred:**
- MVP focuses on greenfield projects (GENESIS_BLUEPRINT sufficient)
- Iterative planning is Phase N feature
- Agent exists but routing not critical path

**Status:** Orphaned, documented as future feature

---

### 7. vibe-cli.py Rename
**Decision:** Rename to `prompt-cli.py`

**Why:**
- Name collision with `vibe-cli` (integration layer)
- vibe-cli = STDIN/STDOUT bridge (primary interface)
- vibe-cli.py = Utility script (manual prompt generation)
- Rename eliminates confusion

**Implementation:** 5-minute change (rename file, update references)

**Status:** Decision made, execution deferred (low priority)

---

### 8. Tool Definitions Location
**Decision:** `agency_os/00_system/orchestrator/tools/` (current location correct)

**Why:**
- Tools are shared infrastructure (not research-specific)
- May be used by future agents (CODE_GENERATOR could use web_fetch)
- Centralized location simplifies management

**Not:** Moving to `01_planning_framework/research/tools/` (would break shared utility pattern)

**Status:** Validated, no changes needed

---

## 📁 Folder Structure (Final)

```
/vibe-agency/
│
├── system_steward_framework/          ← Meta-governance (separate)
│   ├── agents/
│   │   ├── AUDITOR/
│   │   ├── LEAD_ARCHITECT/
│   │   └── SSF_ROUTER/
│   └── knowledge/
│       ├── sops/                      ← 9 SOPs
│       ├── guardian_directives.yaml   ← 9 rules
│       ├── NFR_CATALOG.yaml
│       └── PRODUCT_QUALITY_METRICS.yaml
│
├── agency_os/                         ← Product framework
│   ├── 00_system/                     ← Core infrastructure
│   │   ├── orchestrator/
│   │   │   ├── core_orchestrator.py
│   │   │   ├── handlers/
│   │   │   │   ├── planning_handler.py       (✅ implemented)
│   │   │   │   ├── coding_handler.py         (✅ implemented)
│   │   │   │   ├── testing_handler.py        (⚠️ stub)
│   │   │   │   ├── deployment_handler.py     (⚠️ stub)
│   │   │   │   └── maintenance_handler.py    (⚠️ stub)
│   │   │   └── tools/
│   │   │       ├── tool_definitions.yaml
│   │   │       ├── tool_executor.py
│   │   │       ├── google_search_client.py
│   │   │       └── web_fetch_client.py
│   │   │
│   │   └── runtime/
│   │       ├── prompt_runtime.py      ← Low-level composition
│   │       ├── prompt_registry.py     ← High-level interface (NOT BUILT)
│   │       └── llm_client.py
│   │
│   ├── 01_planning_framework/         ← Phase 1 (✅ COMPLETE)
│   │   ├── agents/
│   │   │   ├── VIBE_ALIGNER/
│   │   │   ├── LEAN_CANVAS_VALIDATOR/
│   │   │   ├── GENESIS_BLUEPRINT/
│   │   │   ├── GENESIS_UPDATE/        ← Orphaned (future)
│   │   │   └── research/              ← Sub-framework
│   │   │       ├── MARKET_RESEARCHER/
│   │   │       ├── TECH_RESEARCHER/
│   │   │       ├── FACT_VALIDATOR/
│   │   │       └── USER_RESEARCHER/
│   │   │
│   │   └── knowledge/
│   │       ├── FAE_constraints.yaml   (736 lines)
│   │       ├── FDG_dependencies.yaml  (2546 lines)
│   │       ├── APCE_rules.yaml        (1304 lines)
│   │       ├── TECH_STACK_PATTERNS.yaml
│   │       ├── PROJECT_TEMPLATES.yaml
│   │       ├── ABSTRACTION_LEVEL_GUIDE.md
│   │       ├── planning_project_manifest.schema.json
│   │       └── research/              ← Research KBs (6 files)
│   │
│   ├── 02_code_gen_framework/         ← Phase 2 (✅ COMPLETE)
│   │   └── agents/
│   │       └── CODE_GENERATOR/
│   │
│   ├── 03_qa_framework/               ← Phase 3 (⚠️ STUB)
│   │   └── agents/
│   │       └── QA_VALIDATOR/
│   │
│   ├── 04_deploy_framework/           ← Phase 4 (⚠️ STUB)
│   │   └── agents/
│   │       └── DEPLOY_MANAGER/
│   │
│   └── 05_maintenance_framework/      ← Phase 5 (⚠️ STUB)
│       └── agents/
│           └── BUG_TRIAGE/
│
├── vibe-cli                           ← Integration layer (STDIN/STDOUT bridge)
├── prompt-cli.py                      ← Utility CLI (manual prompt generation)
│
├── scripts/
│   ├── workspace_utils.py
│   └── semantic_audit.py
│
├── workspaces/                        ← Project workspaces
│   ├── .workspace_registry.json
│   └── {project_name}/
│       ├── project_manifest.json
│       └── artifacts/
│
├── docs/
│   ├── architecture/
│   └── archive/
│       └── architecture-v1-outdated-2025-11-15/
│
├── ARCHITECTURE_V2.md                 ← Conceptual model
├── SSOT.md                            ← This file (implementation truth)
└── CLAUDE.md                          ← Anti-hallucination protocol
```

---

## 🔧 Prompt Registry API (Specification)

### Interface

```python
from agency_os.runtime import PromptRegistry

# Full composition with all injections
prompt = PromptRegistry.compose(
    agent: str,                    # Agent ID (e.g., "VIBE_ALIGNER")
    task: str,                     # Task ID (e.g., "02_feature_extraction")
    workspace: str,                # Workspace ID or name
    inject_governance: bool = True,  # Guardian Directives injection
    inject_tools: List[str] = None,  # Tool names (e.g., ["google_search"])
    inject_sops: List[str] = None,   # SOP IDs (e.g., ["SOP_001"])
    context: Dict[str, Any] = None   # Additional runtime context
) -> str
```

### Injection Layers

**Every composed prompt includes (in order):**

1. **Governance Layer** (if `inject_governance=True`)
   ```markdown
   # === GUARDIAN DIRECTIVES ===

   You operate under the following governance rules:

   1. Manifest Primacy: project_manifest.json is the single source of truth
   2. Atomicity: Tasks are atomic and independently executable
   3. Validation Gates: All outputs must pass defined quality gates
   [... 6 more directives ...]
   ```

2. **Context Layer** (automatic)
   ```markdown
   # === RUNTIME CONTEXT ===

   **Project:** project-123
   **Phase:** PLANNING
   **Workspace:** /workspaces/my-project/
   **Manifest State:**
   - current_phase: PLANNING
   - artifacts: {...}
   - budget_used: 1250 tokens
   ```

3. **Tools Layer** (if `inject_tools` specified)
   ```markdown
   # === AVAILABLE TOOLS ===

   ## Tool: google_search
   **Description:** Search the web using Google Custom Search API
   **Parameters:**
   - query (string, required): Search query
   - num_results (integer, optional): Number of results (default: 5)

   [... tool usage instructions ...]
   ```

4. **SOPs Layer** (if `inject_sops` specified)
   ```markdown
   # === STANDARD OPERATING PROCEDURES ===

   ## SOP_001: Start New Project

   **Purpose:** Initialize a new project with human input
   **Triggers:** New project creation
   **Steps:**
   1. Collect project metadata
   2. Create workspace structure
   3. Initialize manifest
   [...]
   ```

5. **Agent Core** (from PromptRuntime)
   ```markdown
   # === CORE PERSONALITY ===
   [Agent's _prompt_core.md]

   # === KNOWLEDGE BASE ===
   [Relevant YAML knowledge files]

   # === TASK INSTRUCTIONS ===
   [task_{task_id}.md]

   # === VALIDATION GATES ===
   [Quality gates for this task]
   ```

### Implementation (Thin Wrapper)

```python
# prompt_registry.py (~150 lines)

class PromptRegistry:
    """
    High-level interface for prompt composition with automatic injections.

    Wraps PromptRuntime (low-level) and adds governance/context enrichment.
    """

    @staticmethod
    def compose(agent, task, workspace, inject_governance=True,
                inject_tools=None, inject_sops=None, context=None):
        """Compose prompt with all injections"""

        # 1. Get base prompt from PromptRuntime
        runtime = PromptRuntime()
        base_prompt = runtime.execute_task(agent, task, context or {})

        # 2. Load governance directives (from SSF)
        if inject_governance:
            directives = load_guardian_directives()
            base_prompt = inject_at_top(base_prompt, directives)

        # 3. Enrich context (manifest, workspace)
        manifest = load_manifest(workspace)
        context_section = format_context(manifest, workspace)
        base_prompt = inject_after_governance(base_prompt, context_section)

        # 4. Attach tools (if specified)
        if inject_tools:
            tools_section = load_tool_definitions(inject_tools)
            base_prompt = inject_after_context(base_prompt, tools_section)

        # 5. Attach SOPs (if specified)
        if inject_sops:
            sops_section = load_sops(inject_sops)
            base_prompt = inject_after_tools(base_prompt, sops_section)

        return base_prompt
```

**Status:** Specification complete, implementation pending

---

## 🧭 CODE vs INTELLIGENCE Boundary

### CODE Layer (Deterministic, Scripted)

**What belongs in code:**
- File operations (read/write manifest, artifacts)
- State transitions (PLANNING → CODING)
- Path resolution (workspace locations)
- API calls (Anthropic, Google Search)
- Validation (schema checks, format validation)
- Composition (merge YAML, inject sections)

**Examples:**
- `core_orchestrator.py` - State machine logic
- `prompt_registry.py` - Injection rules
- `tool_executor.py` - API call execution
- `workspace_utils.py` - File operations

### INTELLIGENCE Layer (Claude Code)

**What belongs in intelligence:**
- Decisions (which tech stack? which approach?)
- Content generation (code, specs, docs)
- Reasoning (why this pattern? trade-off analysis)
- Validation (does this make sense? semantic correctness)
- Exploration (what patterns exist in codebase?)
- Gap analysis (what's missing? what conflicts?)

**Examples:**
- VIBE_ALIGNER - Feature extraction reasoning
- GENESIS_BLUEPRINT - Architecture decisions
- CODE_GENERATOR - Code synthesis
- MARKET_RESEARCHER - Market analysis

### Gray Area (Judgment Calls)

**Rule:** When in doubt, prefer INTELLIGENCE.

**Rationale:** Over-engineering code is harder to maintain than refining prompts.

---

## 🚫 NOT Doing (Explicitly Deferred)

### 1. EXPLORE Agent
**Why Deferred:**
- Requires Prompt Registry as foundation
- Adaptive behavior = complex design
- Not needed for MVP (agents work with fixed tasks)

**When:** Phase 5 (after Registry stable)

---

### 2. Runtime Governance Enforcement
**Why Deferred:**
- Governance via prompts (intelligence) works for MVP
- Runtime validation = additional code complexity
- Quality gates exist (HITL approval points)

**Current:** Guardian Directives injected into prompts (Claude Code enforces)

**Future:** Programmatic enforcement (budget limits, rollback on failures)

**When:** Phase 5

---

### 3. Full Autonomous Mode
**Why Deferred:**
- Delegated mode (vibe-cli) works well
- Autonomous mode exists but less integrated
- Production reliability needs battle-testing

**Current:** Delegated mode default, autonomous mode available

**Future:** Autonomous mode as production-grade option

**When:** Phase 6

---

### 4. prompt_registry in Separate Folder
**Why Deferred:**
- It's part of runtime/ (not a standalone module)
- Thin wrapper (~150 lines)
- No need for `00_system/prompt_registry/` structure

**Decision:** Single file `runtime/prompt_registry.py`

---

### 5. Merging SSF into agency_os
**Why Deferred:**
- Intentional separation (meta vs product)
- Different lifecycles
- Integration via Guardian Directives injection (sufficient)

**Future:** May reconsider if SSF becomes runtime component (unlikely)

---

## 📊 Implementation Status Matrix

| Component | Status | Lines | Tests | Notes |
|-----------|--------|-------|-------|-------|
| Core Orchestrator | ✅ Complete | 950 | ✅ | GAD-002, uses Registry |
| Prompt Runtime | ✅ Complete | 661 | ✅ | Composition engine |
| **Prompt Registry** | ✅ Complete | 450 | ✅ | **IMPLEMENTED 2025-11-15** |
| vibe-cli (integration) | ✅ Complete | 351 | ✅ | GAD-003 |
| prompt-cli.py (utility) | ✅ Complete | 417 | ✅ | Renamed from vibe-cli.py |
| VIBE_ALIGNER | ✅ Complete | - | ✅ | Production-ready |
| GENESIS_BLUEPRINT | ✅ Complete | - | ✅ | Production-ready |
| RESEARCH Sub-Framework | ✅ Complete | - | ✅ | GAD-003 |
| CODE_GENERATOR | ✅ Complete | - | ✅ | GAD-002 |
| Testing Handler | ⚠️ Stub | 109 | ✅ | Phase 4 TODO |
| Deployment Handler | ⚠️ Stub | 113 | ✅ | Phase 4 TODO |
| Maintenance Handler | ⚠️ Stub | 107 | ✅ | Phase 4 TODO |
| GENESIS_UPDATE | ❌ Orphaned | - | ❌ | Phase N |
| System Steward | ✅ Complete | - | ❌ | Manual invocation |

---

## 🎯 MVP Roadmap

### Phase 1: Prompt Registry (1-2 days) ✅ COMPLETE (2025-11-15)
- [x] Implement `prompt_registry.py` (~450 lines actual)
- [x] Guardian Directives loader
- [x] Context enrichment
- [x] Tool/SOP injection
- [x] Unit tests (see Test Specification below)
- [x] Integration test (VIBE_ALIGNER with governance)

**Test Specification:** ✅ ALL TESTS PASSING
- [x] **test_governance_injection**: Guardian Directives appear in composed prompt
- [x] **test_context_enrichment**: Manifest data present in output
- [x] **test_tool_injection**: Tools only appear when requested
- [x] **test_sop_injection**: SOPs only appear when requested
- [x] **test_composition_order**: Governance → Context → Tools → SOPs → Agent
- [x] **test_backward_compatibility**: PromptRuntime still works independently
- [x] **test_missing_workspace**: Graceful error when workspace doesn't exist
- [x] **test_missing_agent**: Graceful error when agent doesn't exist
- [x] **test_optional_params**: All inject_* params work when omitted

### Phase 2: Integration (1 day) ✅ COMPLETE (2025-11-15)
- [x] Update core_orchestrator to use Registry
- [x] End-to-end test (full PLANNING phase)
- [ ] Update vibe-cli to use Registry (not needed - receives composed prompts)
- [ ] Update vibe-cli.py to use Registry (deferred to Phase 4)

### Phase 3: Documentation (0.5 days) ✅ COMPLETE (2025-11-15)
- [x] Update ARCHITECTURE_V2.md (mark Registry as complete)
- [x] Update SSOT.md (implementation status)
- [x] Add Registry usage examples (in tests + docs)

### Phase 4: Cleanup (0.5 days) ✅ COMPLETE (2025-11-15)
- [x] Rename vibe-cli.py → prompt-cli.py
- [x] Archive old ARCHITECTURE.md (archived 2025-11-15)
- [x] Update all references

**Total Estimate:** 4 days for MVP Prompt Registry
**Actual Time:** ~2 hours (single session implementation!)

---

## 🚀 Rollout Strategy (Prompt Registry)

### Phase 1: Build Registry (Parallel Implementation)
- New file `prompt_registry.py`, no changes to existing code
- PromptRuntime still works (no breaking changes)
- Both paths functional

**Risk:** Low (no existing code touched)

### Phase 2: Gradual Migration
- **Step 1:** vibe-cli uses Registry (low risk, limited blast radius)
- **Step 2:** Orchestrator STILL uses PromptRuntime (high risk, deferred)
- **Step 3:** Test both paths work in isolation

**Risk:** Medium (two code paths, potential divergence)

### Phase 3: Full Cutover
- **Step 1:** Update orchestrator to use Registry
- **Step 2:** Keep PromptRuntime for 1 release (backward compatibility)
- **Step 3:** Integration tests cover all workflows

**Risk:** High (changes critical path)

**Rollback Plan:** Revert orchestrator changes, fall back to PromptRuntime

### Phase 4: Deprecation
- Remove direct PromptRuntime calls from CLI/orchestrator
- Keep PromptRuntime.py (Registry uses it internally)
- Registry is only public interface

**What Breaks During Transition:**
- Custom scripts calling PromptRuntime directly (if any exist)
- Manual prompt composition workflows

**Mitigation:**
- Search codebase for `PromptRuntime` imports before Phase 3
- Add deprecation warnings in Phase 2
- Document migration path for custom scripts

---

## 🔗 Related Documents

- **[ARCHITECTURE_V2.md](./ARCHITECTURE_V2.md)** - Conceptual model, design principles
- **[CLAUDE.md](./CLAUDE.md)** - Anti-hallucination protocol, truth verification
- **[GAD-002](./docs/architecture/GAD-002_Core_SDLC_Orchestration.md)** - Orchestrator design
- **[GAD-003](./docs/architecture/GAD-003_COMPLETION_ASSESSMENT.md)** - Research integration

---

## ✅ Verification Protocol

### Frequency
**Before every PR that touches architecture**

### Owner
**PR author + reviewer**

### Process

1. **Run Tests**
   ```bash
   pytest tests/ -v  # All must pass
   ```

2. **Check Folder Structure**
   ```bash
   ls -R agency_os/  # Must match Folder Structure section above
   ```

3. **Verify Claims**
   ```bash
   # Grep claims in docs exist in code
   grep -r "PromptRegistry" agency_os/  # Should find references after MVP
   ```

4. **Update Verification Date**
   - Update "Last Verified" date in both ARCHITECTURE_V2.md and SSOT.md

### If Verification Fails

- **Option A:** Update docs to match code (if code is correct)
- **Option B:** Update code to match docs (if docs are design intent)
- **Never merge with mismatched docs**

### Quick Verification Commands

```bash
# 1. Check file structure matches
ls -R agency_os/

# 2. Check implementation status
pytest tests/ -v

# 3. Verify decisions in code
grep -r "PromptRegistry" agency_os/  # Should find references after MVP

# 4. Check against ARCHITECTURE_V2.md
diff <(grep "^### " ARCHITECTURE_V2.md) <(grep "^### " SSOT.md)
```

**Last Verified:** 2025-11-15 (Enhanced with professional review feedback)
**Next Review:** After Prompt Registry implementation

---

**Maintainer Notes:**

When implementation changes:
1. Update this file FIRST (source of truth)
2. Update ARCHITECTURE_V2.md (conceptual alignment)
3. Run tests to verify
4. Update "Last Verified" date

**No guessing. No assumptions. Only facts from codebase.**
