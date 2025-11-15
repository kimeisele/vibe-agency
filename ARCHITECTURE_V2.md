# ARCHITECTURE V2 - vibe-agency

**Version:** 2.0
**Date:** 2025-11-15
**Status:** Current
**Supersedes:** ARCHITECTURE.md (archived 2025-11-15)

---

## 🎯 Purpose

This document describes the **conceptual architecture** of vibe-agency: a file-based prompt framework for AI-assisted software project planning and development.

For implementation details, see [SSOT.md](./SSOT.md).

---

## 🏗️ System Overview

### The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│ CLAUDE CODE (Intelligence Layer)                           │
│ - Natural language understanding                            │
│ - Decision making                                           │
│ - Content generation                                        │
│ - Validation & reasoning                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ PROMPT REGISTRY (Interface Layer) ← THE HEART              │
│ - Automatic governance injection                            │
│ - Context enrichment                                        │
│ - Tool/SOP composition                                      │
│ - Single API for all prompts                                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ AGENCY OS (Execution Layer)                                │
│ - 5 SDLC phases (PLANNING → MAINTENANCE)                   │
│ - State machine orchestrator                                │
│ - Agent framework                                           │
│ - Knowledge bases                                           │
└─────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ INTEGRATION LAYER (vibe-cli)                               │
│ - STDIN/STDOUT bridge                                       │
│ - Multi-turn tool use loop                                  │
│ - Anthropic API integration                                 │
└─────────────────────────────────────────────────────────────┘
```

### Parallel: System Steward Framework (Meta-Governance)

```
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM STEWARD FRAMEWORK (Separate)                        │
│ - Meta-level governance                                     │
│ - Architecture decisions                                    │
│ - Quality audits                                            │
│ - Guardian Directives → Injected into AOS via Registry     │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle:** SSF governs HOW we build AOS. AOS governs HOW we build user projects.

---

## 🧩 Core Components

### 1. Prompt Registry (The Heart)

**What:** Central interface for all prompt composition.

**Purpose:** Eliminate manual composition, enable automatic governance injection.

**Responsibilities:**
- Load agent prompts via PromptRuntime
- Inject Guardian Directives automatically
- Enrich with workspace context (manifest, artifacts)
- Attach tool definitions when needed
- Load SOPs for HITL workflows
- Provide single API for CLI/orchestrator

**Without Registry (Current Pain):**
```python
# Manual, error-prone, no governance
runtime = PromptRuntime()
prompt = runtime.execute_task(agent, task, context)
# Where do guardian directives go? Manual addition to every prompt!
```

**With Registry (Solution):**
```python
# Clean, automatic, governed
prompt = PromptRegistry.compose(
    agent="VIBE_ALIGNER",
    workspace="project-123",
    inject_governance=True,  # Guardian directives added automatically
    inject_tools=["google_search"],
    inject_sops=["SOP_001"]
)
```

**Status:** ✅ IMPLEMENTED (2025-11-15) - Production ready

**Implementation Details:**
- File: `agency_os/00_system/runtime/prompt_registry.py` (~450 lines)
- Automatic Guardian Directives injection (9 governance rules)
- Context enrichment (manifest, workspace paths)
- Tool/SOP injection (when requested)
- Graceful error handling and fallbacks
- Fully integrated with core orchestrator
- Comprehensive test coverage (9 unit tests + integration tests)

---

### 2. System Steward Framework (Meta-Governance)

**What:** Separate framework that governs AOS development and evolution.

**Location:** `/system_steward_framework/` (repo root, intentionally separate from agency_os)

**Agents:**
- **LEAD_ARCHITECT** - Strategic architecture decisions
- **AUDITOR** - Quality gate validation, semantic audits
- **SSF_ROUTER** - Routes governance tasks to appropriate agent

**Knowledge Bases:**
- Guardian Directives (9 rules for AOS design)
- SOPs (9 standard operating procedures)
- NFR Catalog (non-functional requirements)
- Product Quality Metrics

**Why Separate:**
- Different lifecycle (SSF evolves slower than AOS)
- Different purpose (governs design vs. executes projects)
- Different invocation (manual via sessions, not orchestrator)

**Integration Model:**
- **Design-time:** SSF defines rules (Guardian Directives, SOPs)
- **Composition-time:** Prompt Registry injects SSF rules into AOS prompts
- **Runtime:** Claude Code enforces rules (intelligence layer)
- **No orchestrator calls to SSF agents** (manual sessions only)

---

### 3. Agency OS (5 SDLC Phases)

**What:** The product framework - builds user projects through 5 phases.

**Structure:**
```
agency_os/
├── 00_system/           ← Core infrastructure
│   ├── orchestrator/    ← State machine
│   ├── runtime/         ← Prompt composition (+ Registry)
│   └── tools/           ← Shared tools (google_search, web_fetch)
│
├── 01_planning_framework/     ← FULLY IMPLEMENTED
│   ├── agents/
│   │   ├── VIBE_ALIGNER/              ← Feature extraction
│   │   ├── LEAN_CANVAS_VALIDATOR/     ← Business validation
│   │   ├── GENESIS_BLUEPRINT/         ← Architecture design
│   │   ├── GENESIS_UPDATE/            ← Architecture updates (orphaned)
│   │   └── research/                  ← Research sub-framework
│   │       ├── MARKET_RESEARCHER/
│   │       ├── TECH_RESEARCHER/
│   │       ├── FACT_VALIDATOR/
│   │       └── USER_RESEARCHER/
│   └── knowledge/       ← 7 YAML knowledge bases
│
├── 02_code_gen_framework/     ← FULLY IMPLEMENTED
│   └── agents/
│       └── CODE_GENERATOR/    ← 5-phase code generation
│
├── 03_qa_framework/           ← STUB (Phase 4 TODO)
│   └── agents/
│       └── QA_VALIDATOR/
│
├── 04_deploy_framework/       ← STUB (Phase 4 TODO)
│   └── agents/
│       └── DEPLOY_MANAGER/
│
└── 05_maintenance_framework/  ← STUB (Phase 4 TODO)
    └── agents/
        └── BUG_TRIAGE/
```

**Implementation Status:**
- **Phase 1 (PLANNING):** ✅ Fully implemented, tested, production-ready
- **Phase 2 (CODING):** ✅ Fully implemented (GAD-002)
- **Phase 3 (TESTING):** ⚠️ Stub with transition logic (Phase 4 TODO)
- **Phase 4 (DEPLOYMENT):** ⚠️ Stub with transition logic (Phase 4 TODO)
- **Phase 5 (MAINTENANCE):** ⚠️ Stub with transition logic (Phase 4 TODO)

**Note on Stubs:** Handlers exist and transitions work. They create mock artifacts and move to next phase. Full implementation deferred to Phase 4 roadmap.

---

### 4. RESEARCH Sub-Framework

**What:** Optional research capability for PLANNING phase.

**Semantic Purpose:** When planning requires unknown information (market data, tech comparisons, fact-checking), agents can actively search instead of hallucinating.

**Agents:**
- **MARKET_RESEARCHER** - Competitor analysis, market sizing, user validation
- **TECH_RESEARCHER** - Framework comparisons, library evaluation, best practices
- **FACT_VALIDATOR** - Claim verification, data validation
- **USER_RESEARCHER** - Persona development, interview guides (no tools)

**Tools:**
- `google_search` - Google Custom Search API
- `web_fetch` - Web content retrieval

**Integration:** Called by planning_handler during RESEARCH sub-state (optional step before business validation).

**Status:** ✅ Fully implemented (GAD-003)

---

### 5. Core Orchestrator

**What:** Deterministic state machine that routes execution through SDLC phases.

**Responsibilities:**
- Phase transitions (PLANNING → CODING → TESTING → DEPLOYMENT → MAINTENANCE)
- Agent routing (which agent for which task)
- Manifest management (single source of truth: project_manifest.json)
- Quality gates (enforce phase completion before transition)
- Budget tracking
- HITL coordination (human-in-the-loop approval points)

**Execution Modes:**
- **Delegated** (default) - Hands intelligence requests to Claude Code via vibe-cli
- **Autonomous** (legacy) - Calls Anthropic API directly (less integration)

**Key Design:** Orchestrator is "not alive" - it's a routing layer. Intelligence lives in Claude Code.

---

### 6. Integration Layer (vibe-cli)

**What:** STDIN/STDOUT bridge between orchestrator and Claude Code.

**Location:** `/vibe-cli` (351 lines)

**Flow:**
1. Launches orchestrator as subprocess
2. Monitors STDOUT for `INTELLIGENCE_REQUEST` (JSON)
3. Executes prompt via Anthropic API
4. Handles multi-turn tool use loop
5. Sends `INTELLIGENCE_RESPONSE` via STDIN

**Multi-turn Tool Use:**
```
Orchestrator → INTELLIGENCE_REQUEST
             ↓
         vibe-cli → Anthropic API (with tools)
             ↓
         API returns stop_reason="tool_use"
             ↓
         vibe-cli executes tools locally (tool_executor.py)
             ↓
         vibe-cli sends tool_result back to API
             ↓
         API returns final response
             ↓
         vibe-cli → INTELLIGENCE_RESPONSE → Orchestrator
```

**Status:** ✅ Fully implemented (GAD-003)

---

### 7. Knowledge Bases

**What:** Static YAML files encoding domain knowledge (constraints, dependencies, patterns).

**Purpose:** Eliminate hallucination by giving agents factual grounding.

**Core Knowledge Bases:**
1. **FAE_constraints.yaml** (736 lines) - Feasibility rules
2. **FDG_dependencies.yaml** (2546 lines) - Tech dependency mappings
3. **APCE_rules.yaml** (1304 lines) - Complexity scoring
4. **TECH_STACK_PATTERNS.yaml** - Common tech stack templates
5. **PROJECT_TEMPLATES.yaml** - Project archetypes
6. **AOS_Ontology.yaml** - Semantic terminology (enforced via semantic_audit.py)

**Research Knowledge:**
- Competitor analysis templates
- Interview question banks
- Market sizing formulas
- Persona templates
- Red flag taxonomy

**Validation:** All knowledge bases validated against ontology via `semantic_audit.py` (CI/CD).

---

## 🔄 Integration Model

### How Everything Connects

```
1. USER invokes vibe-cli
   ↓
2. vibe-cli launches orchestrator (delegated mode)
   ↓
3. Orchestrator determines next task
   ↓
4. Orchestrator requests prompt via Prompt Registry
   │  (Future: Currently uses PromptRuntime directly)
   ↓
5. Prompt Registry composes:
   │  - Agent core prompt
   │  - Guardian Directives (governance)
   │  - Knowledge dependencies
   │  - Tool definitions (if needed)
   │  - SOPs (if HITL workflow)
   │  - Runtime context (manifest, workspace)
   ↓
6. Orchestrator sends INTELLIGENCE_REQUEST (via STDOUT)
   ↓
7. vibe-cli executes prompt via Anthropic API
   │  - Multi-turn conversation if tools needed
   │  - Local tool execution via tool_executor.py
   ↓
8. vibe-cli sends INTELLIGENCE_RESPONSE (via STDIN)
   ↓
9. Orchestrator processes result, updates manifest
   ↓
10. Orchestrator transitions to next phase/task
    ↓
11. Repeat until project complete
```

---

## 🎨 Design Principles

### 1. KISS (Keep It Simple, Stupid)
- Minimal code, maximal intelligence
- File-based (no databases)
- JSON for data, YAML for knowledge, Markdown for prompts

### 2. YAGNI (You Aren't Gonna Need It)
- Build what's needed NOW
- Defer speculative features
- Stubs over incomplete implementations

### 3. CODE vs INTELLIGENCE Boundary

**CODE Layer (Deterministic):**
- Prompt Registry - Composition rules
- Orchestrator - State machine, routing
- Tool Executor - API calls, file operations
- Workspace Utils - Manifest loading, path resolution

**INTELLIGENCE Layer (Claude Code):**
- Decisions (which approach? how to implement?)
- Content generation (code, specs, docs)
- Validation (quality checks, gap analysis)
- Reasoning (trade-offs, explanations)

**Rule:** If it CAN be code, it SHOULD be code. If it NEEDS intelligence, delegate to Claude Code.

### 4. Graceful Degradation
- Research tools optional (falls back to Claude web search)
- Knowledge bases cacheable (offline mode possible)
- Stubs allow end-to-end flow even when features incomplete

### 5. Human-in-the-Loop (HITL)
- QA approval gates (can't deploy without approval)
- SOP-guided workflows (structured human input)
- Manifest as audit trail (who approved what, when)

---

## 🚧 Current Limitations

### Known Gaps (As of 2025-11-15 - Updated)

1. ~~**No Prompt Registry**~~ ✅ **RESOLVED (2025-11-15)**
   - ✅ Prompt Registry implemented and integrated
   - ✅ Automatic governance injection active
   - ✅ Central interface for all prompt composition
   - ✅ Orchestrator fully integrated

2. ~~**Guardian Directives Not Enforced**~~ ✅ **RESOLVED (2025-11-15)**
   - ✅ Guardian Directives automatically injected via Prompt Registry
   - ✅ All 9 directives enforced at runtime
   - ✅ Comprehensive test coverage

3. **Handlers 3-5 Are Stubs**
   - Testing, Deployment, Maintenance phases incomplete
   - Transition logic works, but no real execution
   - **Fix:** Phase 4 roadmap (not MVP)

4. **GENESIS_UPDATE Orphaned**
   - Architecture update agent exists but not routed
   - No iterative planning workflow
   - **Fix:** Defer to Phase N (not MVP)

5. ~~**vibe-cli.py Name Collision**~~ ✅ **RESOLVED (2025-11-15)**
   - ✅ Renamed vibe-cli.py → prompt-cli.py
   - ✅ Clear separation: vibe-cli (integration) vs prompt-cli.py (utility)
   - ✅ No more naming confusion

---

## 🔮 Future Vision

### Phase 4 (Next 3-6 months)
- **Complete Handlers 3-5**
  - Real QA execution (pytest, coverage, SAST)
  - Real deployment (cloud providers, health checks)
  - Real monitoring (golden signals, incident response)

- **Prompt Registry**
  - Central interface implemented
  - Governance auto-injection active
  - SOP loading automated

### Phase 5 (6-12 months)
- **EXPLORE Agent**
  - Adaptive codebase exploration
  - Pattern recognition
  - Intelligent routing based on discovery

- **Runtime Governance**
  - Quality gates enforced programmatically
  - Automatic rollback on failures
  - Budget enforcement (token limits)

### Phase 6 (12+ months)
- **Intelligence Matrix**
  - Multi-agent collaboration
  - Parallel execution
  - Consensus decision-making

- **Full Autonomous Mode**
  - No human intervention required (for greenfield projects)
  - HITL optional, not mandatory
  - Production-grade reliability

---

## 📚 Related Documents

- **[SSOT.md](./SSOT.md)** - Implementation decisions, folder structure, API specs
- **[CLAUDE.md](./CLAUDE.md)** - Truth protocol, anti-hallucination rules
- **[GAD-002](./docs/architecture/GAD-002_Core_SDLC_Orchestration.md)** - Orchestrator design
- **[GAD-003](./docs/architecture/GAD-003_COMPLETION_ASSESSMENT.md)** - Research integration completion

---

## 📖 Glossary

### Architecture Terms

**Meta-framework**
A framework that governs how another framework is built. SSF is a meta-framework because it defines rules for building AOS.

**Composition-time**
The phase when prompts are assembled from multiple sources (agent core + knowledge + governance + context). Happens before runtime execution.

**Runtime**
The phase when composed prompts are executed by Claude Code. Involves decision-making, content generation, and validation.

**Design-time**
The phase when rules, SOPs, and directives are created by humans or SSF agents. Precedes composition-time.

**Delegated Mode**
Execution mode where orchestrator delegates intelligence to Claude Code via STDIN/STDOUT (vibe-cli). Recommended default.

**Autonomous Mode**
Execution mode where orchestrator calls Anthropic API directly. Less integration with Claude Code ecosystem.

**Guardian Directives**
9 governance rules defined by SSF that enforce quality standards in AOS (e.g., "Manifest Primacy", "Atomicity").

**Quality Gate**
A checkpoint in the SDLC where execution pauses for validation (automated or HITL) before proceeding.

**HITL (Human-in-the-Loop)**
Approval points where human judgment is required (e.g., QA approval gate, SOP-guided workflows).

**Manifest Primacy**
Guardian Directive #1: `project_manifest.json` is the single source of truth for all project state.

**Atomic Task**
Guardian Directive #2: Every task is independently executable and produces well-defined outputs.

**Knowledge Dependency**
YAML files that agents require to make grounded decisions (e.g., FAE_constraints.yaml, FDG_dependencies.yaml).

**Prompt Registry**
High-level interface for prompt composition that automatically injects governance, context, tools, and SOPs. The "heart" of the system.

**PromptRuntime**
Low-level prompt composition engine. Used internally by Prompt Registry. Not meant for direct use.

### Framework Terms

**Agency OS (AOS)**
The product framework - builds user projects through 5 SDLC phases.

**System Steward Framework (SSF)**
Meta-governance framework - defines rules for how AOS should be built.

**Research Sub-Framework**
Optional capability in PLANNING phase for web search and fact-checking (4 agents + 2 tools).

**SDLC**
Software Development Lifecycle: PLANNING → CODING → TESTING → DEPLOYMENT → MAINTENANCE

**Stub**
Minimal implementation that allows end-to-end flow but lacks real functionality (e.g., Handlers 3-5).

**Orphaned Agent**
An agent that exists but isn't routed by the orchestrator (e.g., GENESIS_UPDATE).

---

## 🤝 For Contributors

**Before proposing changes:**
1. Read this file (conceptual model)
2. Read SSOT.md (implementation truth)
3. Run tests: `pytest tests/`
4. Check CLAUDE.md for anti-hallucination protocol

**When adding features:**
- Ask: "Can this be CODE or does it need INTELLIGENCE?"
- If CODE: Build it deterministically
- If INTELLIGENCE: Design prompts, not scripts

**When updating docs:**
- ARCHITECTURE_V2.md = Concepts (this file)
- SSOT.md = Decisions and implementation
- Keep them in sync

---

**Last Updated:** 2025-11-15 (Refined with professional review feedback)
**Maintainer:** vibe-agency core team
**Status:** Living document (update as system evolves)
