# 🏛️ GAD-001: Research Framework Integration
**Grand Architecture Decision - Lead Architect Review**

**Date:** 2025-11-14
**Status:** ✅ APPROVED
**Approved by:** kimeisele
**Lead Architect:** Claude
**Implementation Phase:** Phase 1 (In Progress)

---

## Executive Summary

This document defines the architectural decision for integrating the vibe-research prototype into the vibe-agency main product as a sub-framework within the Planning phase.

**Key Decision:** Research is a **Capability Module** (not a Lifecycle State) and will be implemented as a **Sub-Framework** within `01_planning_framework/`.

---

## Architectural Principles

### Principle 1: Lifecycle States vs. Capability Modules

**Lifecycle States** (require own framework numbers):
- PLANNING, CODING, TESTING, DEPLOYMENT, MAINTENANCE
- These are **obligatory steps in SDLC**
- They are **sequential** (Planning → Coding → Testing...)

**Capability Modules** (belong WITHIN a framework):
- Research, Business Validation, Feature Specification
- These are **optional or alternative capabilities**
- They are **not sequential at lifecycle level**

**Decision:**
```
Research is a CAPABILITY MODULE, not a LIFECYCLE STATE
→ Research belongs IN 01_planning_framework/, NOT as separate numbered framework
```

### Principle 2: Sub-State vs. Sub-Framework

**Sub-State:**
- Defined in `ORCHESTRATION_workflow_design.yaml`
- Part of state machine
- Example: PLANNING.BUSINESS_VALIDATION → PLANNING.FEATURE_SPECIFICATION

**Sub-Framework:**
- Own directory within a framework
- Own agents, knowledge, state machine
- Example: `01_planning_framework/research/` (complete subsystem)

**Decision:**
```
Research is large enough for a SUB-FRAMEWORK
→ Own directory, own state machine, but WITHIN 01_planning_framework/
```

### Principle 3: Monorepo vs. Multi-Repo

**Decision:**
```
MONOREPO for now
→ vibe-research prototype will be integrated into vibe-agency
→ Later OPTIONAL: Extract as npm package/git submodule (when mature)
```

---

## Final Architecture

### Directory Structure

```
vibe-agency/
└── agency_os/
    └── 01_planning_framework/
        ├── agents/
        │   ├── LEAN_CANVAS_VALIDATOR/      # Existing
        │   ├── VIBE_ALIGNER/                # Existing
        │   ├── GENESIS_BLUEPRINT/           # Existing
        │   └── research/                    # NEW (Sub-Framework)
        │       ├── MARKET_RESEARCHER/
        │       ├── TECH_RESEARCHER/
        │       ├── FACT_VALIDATOR/
        │       └── USER_RESEARCHER/
        ├── knowledge/
        │   ├── PROJECT_TEMPLATES.yaml       # Existing
        │   ├── FAE_constraints.yaml         # Existing
        │   └── research/                    # NEW
        │       ├── RESEARCH_market_sizing_formulas.yaml
        │       ├── RESEARCH_competitor_analysis_templates.yaml
        │       ├── RESEARCH_constraints.yaml
        │       ├── RESEARCH_persona_templates.yaml
        │       ├── RESEARCH_interview_question_bank.yaml
        │       └── RESEARCH_red_flag_taxonomy.yaml
        └── state_machine/                   # NEW
            └── RESEARCH_workflow_design.yaml
```

---

## Orchestrator Integration

### Updated PLANNING State

```yaml
states:
  - name: "PLANNING"
    sub_states:
      - name: "RESEARCH"                 # NEW (OPTIONAL)
        responsible_agents:
          - "MARKET_RESEARCHER"
          - "TECH_RESEARCHER"
          - "FACT_VALIDATOR"
          - "USER_RESEARCHER"
        output_artifact: "research_brief.json"
        optional: true

      - name: "BUSINESS_VALIDATION"      # EXISTING (updated)
        responsible_agent: "LEAN_CANVAS_VALIDATOR"
        input_artifact: "research_brief.json"  # ← NOW OPTIONAL
        output_artifact: "lean_canvas_summary.json"

      - name: "FEATURE_SPECIFICATION"    # EXISTING
        responsible_agent: "VIBE_ALIGNER"
        input_artifact: "lean_canvas_summary.json"
        output_artifact: "feature_spec.json"
```

### Workflow Flow

```
User Request
    ↓
PLANNING.RESEARCH (optional) → research_brief.json
    ↓
PLANNING.BUSINESS_VALIDATION (uses research_brief if exists) → lean_canvas_summary.json
    ↓
PLANNING.FEATURE_SPECIFICATION → feature_spec.json
    ↓
CODING...
```

---

## Critical Decisions (APPROVED)

### 1. Research Type: (C) HYBRID ✅

**Decision:** Research agents are **ACTIVE** (do web research, API calls) **AND** use **PASSIVE** knowledge bases as templates/frameworks.

**Rationale:**
- Active agents discover new information
- Passive knowledge bases provide structure, templates, quality frameworks
- Similar to how VIBE_ALIGNER uses FAE constraints
- Best of both worlds: Structure + Discovery

### 2. vibe-research Repo Future: (B) Dev Sandbox ✅

**Decision:** Keep vibe-research as **development sandbox** for testing new Research features before integrating into vibe-agency.

**Rationale:**
- Provides isolated testing environment
- Allows experimentation without affecting main product
- Can be extracted as package later when mature
- Archiving would lose valuable testing capability

### 3. Orchestrator Implementation: (B) Hybrid Python+Prompt ✅

**Decision:** Orchestrator is **hybrid** system:
- `orchestrator.py` (Python) - State machine logic, routing, data flow
- `ORCHESTRATOR_PROMPT.md` (Markdown) - Personality, human communication, error handling

**Rationale:**
- Separation of concerns
- Python handles complex logic (testable, maintainable)
- Prompts handle AI behavior (flexible, human-friendly)
- Avoids "prompt hell" (300+ line prompts)
- Agents remain as prompts (not code)

---

## Implementation Plan

### Phase 1: Integration (Week 1) - IN PROGRESS

**Tasks:**
1. ✅ Create GAD-001 document
2. ⏳ Create `agency_os/01_planning_framework/research/` structure
3. ⏳ Copy research agents from vibe-research prototype
4. ⏳ Copy research knowledge bases
5. ⏳ Update `ORCHESTRATION_workflow_design.yaml` with RESEARCH sub-state
6. ⏳ Update `LEAN_CANVAS_VALIDATOR` to accept optional `research_brief.json`
7. ⏳ Test backward compatibility (existing workflows without Research)
8. ⏳ Commit and push Phase 1 changes

### Phase 2: Orchestrator Logic (Week 2)

**Tasks:**
1. Add RESEARCH sub-state handling in Orchestrator
2. Implement optional flag: "Do you want to run Research phase?"
3. Ensure FACT_VALIDATOR blocking logic works
4. Test full flow: RESEARCH → BUSINESS_VALIDATION → FEATURE_SPECIFICATION

### Phase 3: Documentation (Week 3)

**Tasks:**
1. Update README to explain Research capability
2. Document when to use Research (vs. skip)
3. Create example session with Research enabled
4. Update knowledge index

---

## Comparison: This Architecture vs. Gemini's Proposal

| Aspect | Gemini's Approach | Our Approach (GAD-001) |
|--------|------------------|------------------------|
| **Research Structure** | Add 2 more agents (QUERY_GEN, SYNTHESIS) = 6 total | Keep 4 agents, consolidate logic |
| **Integration** | Hardcode in Orchestrator prompt (8-step flow) | Sub-state in YAML, dynamic discovery |
| **Orchestrator** | Bloat prompt to 300+ lines | Hybrid: Python script + prompt |
| **Complexity** | More agents, more steps, more coupling | Simplify, consolidate, decouple |
| **Maintainability** | Low (prompt hell) | High (code + prompts separation) |

**Conclusion:** GAD-001 architecture is simpler, more maintainable, and more scalable.

---

## Success Criteria

### Phase 1 Success:
- ✅ Research agents integrated into vibe-agency
- ✅ No breaking changes to existing workflows
- ✅ LEAN_CANVAS_VALIDATOR accepts optional research_brief.json
- ✅ All existing tests pass

### Phase 2 Success:
- ✅ Orchestrator can optionally invoke Research phase
- ✅ FACT_VALIDATOR can block low-quality research
- ✅ Data flows correctly: research_brief → lean_canvas → feature_spec

### Phase 3 Success:
- ✅ Documentation is complete and accurate
- ✅ Example sessions demonstrate Research capability
- ✅ Users understand when to use Research

---

## Notes

- Research framework is designed to be OPTIONAL
- FACT_VALIDATOR enforces citation requirements (prevents hallucinations)
- Backward compatibility is critical (existing workflows must work)
- vibe-research repo remains as development sandbox

---

## Approval

**Approved by:** kimeisele
**Date:** 2025-11-14
**Status:** ✅ APPROVED - Proceeding with Phase 1 Implementation

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
