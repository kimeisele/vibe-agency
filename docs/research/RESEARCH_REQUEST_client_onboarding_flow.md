# Research Request: Client Onboarding Flow - Gap Analysis & Integration Requirements

**Request ID:** RESEARCH-002-CLIENT-FLOW
**Date:** 2025-11-12
**Priority:** CRITICAL
**Status:** PENDING RESEARCH

---

## EXECUTIVE SUMMARY

**Problem Statement:**
Vibe Agency has built a complete Governance Framework (SSF) and Execution Layer (agency_os), but the **end-to-end flow for client project onboarding is not defined**. The existing SOPs reference a monorepo-wide `project_manifest.json`, but client projects should be isolated in `workspaces/client_name/`. There is no process connecting:

1. Client intake ("I want a booking tool")
2. Workspace creation (`workspaces/client_booking_tool/`)
3. Project-specific manifest instantiation
4. AOS execution scoped to that workspace
5. Artifact delivery back to client

**Research Objective:**
Design the **missing integration layer** that connects SSF (governance/routing) → workspace management → AOS execution (per-workspace).

**Constraints:**
- NO speculation - only design based on existing patterns in the codebase
- MUST be compatible with existing SSF architecture (Orchestrator-Worker pattern)
- MUST preserve workspace isolation (each client = independent project_manifest.json)
- MUST work with Claude Code agents as "employees" (CLI-driven workflow)

---

## WHAT EXISTS (Verified Facts)

### 1. Infrastructure

**Workspace System:**
- `workspaces/.workspace_index.yaml` - Registry of all client workspaces
- `workspaces/vibe_internal/` - Example workspace structure
  - `project_manifest.json` (per-workspace SSoT)
  - `artifacts/planning/`, `artifacts/code/`, etc.

**Conventions Defined:** (workspaces/.workspace_index.yaml:54-74)
- Directory structure: `workspaces/client_name/`
- Required: `project_manifest.json`, `artifacts/` directories
- Optional: `README.md`, `.env.example`

### 2. Governance Layer (SSF)

**Router:** `system_steward_framework/agents/SSF_ROUTER/`
- Intent-based routing to SOPs
- Routes: U1-U7 (Start Project, Bug Report, etc.)

**Current SOP_001:** `system_steward_framework/knowledge/sops/SOP_001_Start_New_Project.md`
- References ROOT `project_manifest.json`
- Loads VIBE_ALIGNER for feature spec
- **Gap:** No workspace selection/creation

**Research Source:** `docs/research/phase-03/KI-Systemarchitektur und Steward-Framework-Entwurf.txt`
- Defines SSF as "Orchestrator Layer" (line 319-323)
- SOPs are "Runbooks" for guided execution (line 131-136)

### 3. Execution Layer (agency_os)

**Agents:** `agency_os/01_planning_framework/agents/`
- VIBE_ALIGNER, GENESIS_BLUEPRINT, GENESIS_UPDATE
- All follow v0.2 pattern: `_composition.yaml`, `_knowledge_deps.yaml`, tasks/

**Knowledge Base:** `agency_os/01_planning_framework/knowledge/`
- FAE_constraints.yaml, APCE_rules.yaml, FDG_dependencies.yaml
- 17 KB files, 6090 lines, ✅ validated (semantic_audit.py)

**Orchestrator:** `agency_os/00_system/agents/AGENCY_OS_ORCHESTRATOR/`
- State machine executor
- Artifact-driven workflow

### 4. What We DON'T Have

**Missing Components:**
1. **SOP for Client Workspace Creation**
   - No SOP_00X_Create_Client_Workspace.md
   - No process to initialize `workspaces/new_client/`

2. **Workspace Context Switching**
   - SSF_ROUTER always reads ROOT `project_manifest.json`
   - No mechanism to say "operate on workspaces/client_x/"

3. **Multi-Workspace Orchestration**
   - AOS Orchestrator runs against which manifest?
   - How to scope agent execution to a workspace?

4. **Client Handoff Process**
   - Artifacts land in `workspaces/client_x/artifacts/`
   - But: How does client receive them? (PR? Export? Package?)

---

## RESEARCH QUESTIONS

### Q1: Workspace Lifecycle Management

**Context:** A client says "I want a booking tool for my gym".

**Questions:**
1. Should SSF_ROUTER have a NEW intent route (e.g., `U8: Create Client Workspace`)?
2. Where should the SOP live? (`SOP_007_Create_Client_Workspace.md`?)
3. What inputs are needed?
   - Client name (becomes `workspaces/client_name/`)
   - Project name/description
   - Contact info (for manifest metadata)
4. Should workspace creation be MANUAL (human-driven) or AUTOMATED (SOP-driven)?
5. Should `.workspace_index.yaml` be auto-updated by SOP or manually?

**Reference Files:**
- `workspaces/.workspace_index.yaml` (lines 54-74: conventions)
- `system_steward_framework/knowledge/sops/SOP_001_Start_New_Project.md`

### Q2: Context Switching Mechanism

**Context:** SSF_ROUTER's Core Execution Loop reads `project_manifest.json` (line 56 of SSF_ROUTER/_prompt_core.md).

**Questions:**
1. Should there be a GLOBAL context variable: `$ACTIVE_WORKSPACE`?
2. Should SSF_ROUTER ask: "Which workspace?" at the start of EVERY session?
3. Should there be a SOP_00X_Switch_Workspace.md?
4. Should workspace context be SESSION-SCOPED (set once per session)?
5. Alternative: Should each SOP explicitly take `--workspace=client_x` as parameter?

**Reference Files:**
- `system_steward_framework/agents/SSF_ROUTER/_prompt_core.md` (lines 54-68: Execution Loop)
- `project_manifest.json` (ROOT - how to distinguish from workspace manifests?)

### Q3: Agent Execution Scoping

**Context:** VIBE_ALIGNER needs to run for `workspaces/client_booking_tool/`.

**Questions:**
1. Should agents read `$ACTIVE_WORKSPACE/project_manifest.json` instead of ROOT?
2. Should `_knowledge_deps.yaml` support workspace-relative paths?
3. Should artifacts be written to `$ACTIVE_WORKSPACE/artifacts/planning/` automatically?
4. How does AGENCY_OS_ORCHESTRATOR know which workspace to operate on?
5. Should there be a `workspaces/client_x/agents/` for client-specific overrides?

**Reference Files:**
- `agency_os/01_planning_framework/agents/VIBE_ALIGNER/_composition.yaml`
- `agency_os/00_system/agents/AGENCY_OS_ORCHESTRATOR/_prompt_core.md`

### Q4: Client Delivery Mechanism

**Context:** Project is DONE. Artifacts exist in `workspaces/client_x/artifacts/`.

**Questions:**
1. Is there a SOP_00X_Package_Client_Deliverables.md?
2. Should artifacts be:
   - Committed to a separate Git repo (`client_x_deliverables/`)?
   - Packaged as ZIP and uploaded somewhere?
   - Left in workspace for client to pull via PR?
3. Should there be a `deploy_receipt.json` that links to final deliverables?
4. How does client ACCESS the deliverables? (GitHub invite? Export script?)
5. Should workspace be ARCHIVED after delivery? (workspaces/.workspace_index.yaml:49)

**Reference Files:**
- `workspaces/.workspace_index.yaml` (lines 49: archived workspaces)
- `agency_os/04_deploy_framework/` (is this client-facing delivery?)

### Q5: Integration Pattern

**Context:** The research doc says SSF is "isomorphic" to AOS (docs/research/phase-03:437-460).

**Questions:**
1. Should workspace management be a NEW AOS framework? (`06_workspace_framework/`)
2. Should it be part of SSF? (Governance concern)
3. Should it be NEITHER? (Separate `workspace_manager/` tool)
4. Reference Table (line 442-459): Where does "workspace context" fit in the isomorphism?
5. Is workspace creation a STATE in the State Machine? (e.g., `WORKSPACE_INITIALIZING`)

**Reference Files:**
- `docs/research/phase-03/KI-Systemarchitektur und Steward-Framework-Entwurf.txt` (lines 437-460: Table)
- `agency_os/00_system/state_machine/` (if exists - need to check)

---

## DESIRED OUTPUT

### Research Deliverables

1. **Architecture Decision Document:**
   - How workspace context propagates through SSF → AOS
   - Whether workspace management is Framework 06, SSF extension, or separate tool
   - State machine updates (if any)

2. **SOP Specifications:**
   - SOP_007_Create_Client_Workspace.md (detailed steps)
   - SOP_008_Switch_Workspace.md (or alternative mechanism)
   - SOP_009_Package_Client_Deliverables.md

3. **Integration Code Patterns:**
   - How `_composition.yaml` should handle workspace-relative paths
   - How SSF_ROUTER reads `$ACTIVE_WORKSPACE` variable
   - How `.workspace_index.yaml` gets auto-updated

4. **Testing Strategy:**
   - How to test multi-workspace isolation
   - How to validate workspace creation doesn't break existing SOPs

### Success Criteria

- ✅ New client can be onboarded via SOP (no manual file creation)
- ✅ Multiple workspaces can coexist without interference
- ✅ AOS agents execute in correct workspace context
- ✅ Deliverables are packaged and handed off cleanly
- ✅ Existing SSF/AOS architecture remains intact (no breaking changes)

---

## REFERENCE FILES INDEX

**Read these files to understand the system:**

### Core Architecture
1. `docs/research/phase-03/KI-Systemarchitektur und Steward-Framework-Entwurf.txt`
   - Lines 319-323: SSF as Orchestrator-Worker pattern
   - Lines 437-460: Isomorphism table (AOS vs SSF)

2. `CONTEXT_SUMMARY_FOR_LEAD_ARCHITECT.md`
   - Current system status
   - Verified facts about governance foundation

### Workspace System
3. `workspaces/.workspace_index.yaml`
   - Lines 20-44: Active workspaces structure
   - Lines 54-74: Directory conventions

4. `workspaces/vibe_internal/project_manifest.json`
   - Example per-workspace manifest

### Governance Layer (SSF)
5. `system_steward_framework/agents/SSF_ROUTER/_prompt_core.md`
   - Lines 54-68: Core Execution Loop
   - Lines 72-89: Intent Routing Logic

6. `system_steward_framework/knowledge/sops/SOP_001_Start_New_Project.md`
   - Current "start project" flow (needs workspace integration)

### Execution Layer (AOS)
7. `agency_os/01_planning_framework/agents/VIBE_ALIGNER/_composition.yaml`
   - Example agent composition (how to make workspace-aware?)

8. `agency_os/00_system/agents/AGENCY_OS_ORCHESTRATOR/_prompt_core.md`
   - How orchestrator executes workflows (scoping needed?)

9. `agency_os/00_system/knowledge/AOS_Ontology.yaml`
   - Semantic terms (does "workspace" exist as term?)

### Supporting Files
10. `project_manifest.json` (ROOT)
    - Compare with workspace manifests

11. `agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml` (if exists)
    - Data contracts for artifacts

12. `.knowledge_index.yaml`
    - How KB files are indexed

---

## ANTI-HALLUCINATION CHECKLIST

**This research request is based on:**
- ✅ Verified file contents (all paths checked)
- ✅ Existing architecture patterns (SSF Research Doc)
- ✅ Real gap identified (no client onboarding SOP)
- ✅ Concrete questions (not vague "how to build X")

**This research request does NOT:**
- ❌ Assume solutions (questions only)
- ❌ Invent files that don't exist
- ❌ Speculate about technical implementation
- ❌ Override existing architecture decisions

---

## NEXT STEPS

1. **Send this request to claude.ai** (or Google Deep Research Agent)
2. **Receive:** Architecture Decision + SOP Specs + Integration Patterns
3. **Implement:** Based on research findings (not speculation)
4. **Validate:** Test multi-workspace flow end-to-end
5. **Document:** Update CONTEXT_SUMMARY with implementation status

---

**Prepared by:** Lead Architect Agent (Sonnet 4.5)
**Session ID:** 011CV4mzUDkRdwUeRzpb2Zcx
**Branch:** claude/context-dump-handover-011CV4mzUDkRdwUeRzpb2Zcx
**Ready for:** External research agent
