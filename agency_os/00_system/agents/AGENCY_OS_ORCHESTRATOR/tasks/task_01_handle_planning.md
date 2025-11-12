# Task 01: Handle Planning State

**TASK_ID:** task_01_handle_planning
**STATE:** PLANNING
**PURPOSE:** Orchestrate the planning phase of the SDLC

---

## GOAL

Coordinate the VIBE_ALIGNER and GENESIS_BLUEPRINT agents to produce a complete architecture specification.

---

## STATE HANDLER LOGIC

### Trigger
A new project is created or a bug report triggers a new planning cycle.

### Actions

1. **Invoke VIBE_ALIGNER:**
   - Load from `agency_os/01_planning_framework/prompts/VIBE_ALIGNER_v3.md`
   - Input: Client brief or bug report
   - Output: `feature_spec.json`

2. **Invoke GENESIS_BLUEPRINT:**
   - Load from `agency_os/01_planning_framework/prompts/GENESIS_BLUEPRINT_v5.md`
   - Input: `feature_spec.json`
   - Output: `architecture.json` and `code_gen_spec.json`

3. **Transition (T1_StartCoding):**
   - **Condition:** `code_gen_spec.json` is created successfully
   - **Actions:**
     - Update `project_manifest.json`:
       - Set `status.projectPhase` to `CODING`
       - Add links to artifacts in `artifacts.planning`
       - Set `status.message` to "Planning complete. Ready for coding."
     - Commit and push the updated manifest

---

## REQUIRED ARTIFACTS (INPUT)

- Client brief (initial project creation)
- OR bug report (maintenance cycle)

---

## PRODUCED ARTIFACTS (OUTPUT)

- `feature_spec.json` (from VIBE_ALIGNER)
- `architecture.json` (from GENESIS_BLUEPRINT)
- `code_gen_spec.json` (from GENESIS_BLUEPRINT)

---

## SUCCESS CRITERIA

- ✅ VIBE_ALIGNER executed successfully
- ✅ GENESIS_BLUEPRINT executed successfully
- ✅ All planning artifacts created
- ✅ Transition to CODING state completed
- ✅ Manifest updated and committed
