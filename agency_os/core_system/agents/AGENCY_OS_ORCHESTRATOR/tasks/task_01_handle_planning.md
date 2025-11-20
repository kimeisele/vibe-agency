# Task 01: Handle Planning State

**TASK_ID:** task_01_handle_planning
**STATE:** PLANNING
**PURPOSE:** Orchestrate the planning phase of the SDLC with business validation and feature specification

---

## GOAL

Coordinate the planning workflow through two sub-states:
1. **BUSINESS_VALIDATION:** Validate business model via LEAN_CANVAS_VALIDATOR
2. **FEATURE_SPECIFICATION:** Transform validated requirements into technical specs via VIBE_ALIGNER and GENESIS_BLUEPRINT

---

## STATE HANDLER LOGIC

### Trigger
A new project is created or a bug report triggers a new planning cycle.

### Phase 1: BUSINESS_VALIDATION (Sub-State)

**When to Execute:**
- New commercial projects (default)
- User explicitly requests business validation

**Actions:**

1. **Check Project Context:**
   - Read `project_manifest.json` to determine `project_type`
   - IF `project_type == "commercial"` → Start with LEAN_CANVAS_VALIDATOR
   - IF `project_type == "portfolio" || "demo" || "personal"` → OPTIONAL, ask user
   - IF bug report/maintenance → SKIP to VIBE_ALIGNER

2. **Invoke LEAN_CANVAS_VALIDATOR:**
   - Load from `agency_os/01_planning_framework/agents/LEAN_CANVAS_VALIDATOR/`
   - Input: User's business idea or problem statement
   - Output: `lean_canvas_summary.json`
   - Location: `artifacts/planning/lean_canvas_summary.json`

3. **Transition (T0_BusinessToFeatures):**
   - **Condition:** `lean_canvas_summary.json` created AND `readiness.status == "READY"`
   - **Action:** Move to FEATURE_SPECIFICATION sub-state

### Phase 2: FEATURE_SPECIFICATION (Sub-State)

**Actions:**

1. **Invoke VIBE_ALIGNER:**
   - Load from `agency_os/01_planning_framework/agents/VIBE_ALIGNER/`
   - Input (Primary): `lean_canvas_summary.json` (if exists from Phase 1)
   - Input (Fallback): Client brief or bug report (legacy mode)
   - Output: `feature_spec.json`
   - Location: `artifacts/planning/feature_spec.json`

2. **Invoke GENESIS_BLUEPRINT:**
   - Load from `agency_os/01_planning_framework/agents/GENESIS_BLUEPRINT/`
   - Input: `feature_spec.json`
   - Output: `architecture.json` and `code_gen_spec.json`
   - Location: `artifacts/planning/architecture.json`, `artifacts/planning/code_gen_spec.json`

3. **Transition (T1_StartCoding):**
   - **Condition:** `code_gen_spec.json` is created successfully
   - **Actions:**
     - Update `project_manifest.json`:
       - Set `status.projectPhase` to `CODING`
       - Add links to all planning artifacts:
         - `lean_canvas_summary` (if exists)
         - `feature_spec`
         - `architecture`
         - `code_gen_spec`
       - Set `status.message` to "Planning complete. Ready for coding."
     - Commit and push the updated manifest

---

## REQUIRED ARTIFACTS (INPUT)

### For BUSINESS_VALIDATION:
- User's business idea or problem statement
- Client brief (initial project creation)

### For FEATURE_SPECIFICATION:
- `lean_canvas_summary.json` (from Phase 1, if exists)
- OR client brief / bug report (fallback / legacy mode)

---

## PRODUCED ARTIFACTS (OUTPUT)

### From Phase 1 (BUSINESS_VALIDATION):
- `lean_canvas_summary.json` (from LEAN_CANVAS_VALIDATOR)
  - Contains: business context, riskiest assumptions, readiness status

### From Phase 2 (FEATURE_SPECIFICATION):
- `feature_spec.json` (from VIBE_ALIGNER)
- `architecture.json` (from GENESIS_BLUEPRINT)
- `code_gen_spec.json` (from GENESIS_BLUEPRINT)

---

## SUCCESS CRITERIA

### For BUSINESS_VALIDATION Sub-State:
- ✅ LEAN_CANVAS_VALIDATOR executed successfully (if applicable)
- ✅ `lean_canvas_summary.json` created with `readiness.status == "READY"`
- ✅ Transition (T0) to FEATURE_SPECIFICATION completed

### For FEATURE_SPECIFICATION Sub-State:
- ✅ VIBE_ALIGNER executed successfully
- ✅ GENESIS_BLUEPRINT executed successfully
- ✅ All planning artifacts created
- ✅ Transition (T1) to CODING state completed
- ✅ Manifest updated and committed

---

## ROUTING DECISION TREE

```
START (New Project)
  │
  ├─→ Is project_type == "commercial"?
  │     ├─→ YES: Execute Phase 1 (LEAN_CANVAS_VALIDATOR)
  │     │         ↓
  │     │    lean_canvas_summary.json created?
  │     │         ↓
  │     │    Execute Phase 2 (VIBE_ALIGNER + GENESIS_BLUEPRINT)
  │     │         ↓
  │     │    Transition to CODING
  │     │
  │     └─→ NO: Ask user if they want business validation
  │             ├─→ YES: Execute Phase 1 → Phase 2
  │             └─→ NO: Skip to Phase 2 (legacy mode)
  │
  └─→ Is maintenance/bug fix?
        └─→ YES: Skip Phase 1, go directly to Phase 2 (VIBE_ALIGNER)
```
