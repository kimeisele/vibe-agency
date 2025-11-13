
# SOP-001: Start New Project

**PURPOSE:** To guide the user through the 'PLANNING' state (AOS Framework 01) and generate the initial 'feature_spec.json' artifact.

**PRE-CONDITION:** `project_manifest.json` `current_state` is 'INITIALIZING' or 'PLANNING'. (Der Steward MUSS dies vor der Ausführung prüfen).

**POST-CONDITION:**
1.  A validated `feature_spec.json` artifact is created and saved.
2.  `project_manifest.json` `code_gen_spec_uri` (oder ein Äquivalent) wird aktualisiert.
3.  `project_manifest.json` `current_state` wird auf 'AWAITING_ARCHITECTURE' gesetzt (um den `GENESIS_BLUEPRINT_v5` Agenten auszulösen).

---

## STEPS (Executed by Steward):

### STEP 0: PROJECT CONTEXT DETECTION (v1.1 NEW)

1. **(Steward) [Check]** Confirm `current_state` in `project_manifest.json` is 'INITIALIZING' or 'PLANNING'.
2. **(Steward) [Read Context]** Read `project_type` from `project_manifest.json`:
   ```python
   project_type = manifest.get("project_type", "commercial")  # Default: commercial
   ```
3. **(Steward) [Determine Workflow]** Select workflow mode:
   ```yaml
   if project_type == "commercial":
     canvas_mode: FULL_INTERVIEW
     duration_estimate: 35-45 minutes
   elif project_type in ["portfolio", "demo", "nonprofit", "personal"]:
     canvas_mode: QUICK_RESEARCH
     duration_estimate: 15-25 minutes
   ```
4. **(Steward) [Acknowledge]** State to user:
   ```
   "Acknowledged. Initiating SOP_001_Start_New_Project for a {project_type} project.

   Estimated time: {duration_estimate}
   Canvas mode: {canvas_mode}

   Ready to begin?"
   ```

---

### STEP 1-5: LEAN CANVAS VALIDATION (Adaptive)

5.  **(Steward) [Load Agent]** Announce: "Loading the 'LEAN CANVAS VALIDATOR' specialist agent in **{canvas_mode}** mode."

6.  **(Steward) Initiate LEAN_CANVAS_VALIDATOR workflow:**

    **IF canvas_mode == "FULL_INTERVIEW":**
    - Guide user through full 9-field Lean Canvas interview
    - Duration: 15-20 minutes
    - Data source: User answers

    **IF canvas_mode == "QUICK_RESEARCH":**
    - Execute WebSearch for problem domain
    - Present findings to user for confirmation (3 core fields)
    - Duration: 5-8 minutes
    - Data source: Market research + User validation

7.  **(Steward) [Receive Artifact]** Receive `lean_canvas_summary.json` from LEAN_CANVAS_VALIDATOR.
    - Note: Artifact schema is identical for both modes (backward compatible)

---

### STEP 6-12: VIBE ALIGNER & FINALIZATION (Unchanged)

8.  **(Steward) [Load Agent]** Announce: "Loading the 'VIBE ALIGNER' specialist agent (`agency_os/01_planning_framework/prompts/VIBE_ALIGNER_v3.md`)."
9.  **(Steward) [Load Knowledge]** Announce: "Loading required knowledge: `APCE_rules.yaml`, `FAE_constraints.yaml`, `FDG_dependencies.yaml`, `PRODUCT_QUALITY_METRICS.yaml`, `NFR_CATALOG.yaml`."
10. **(Steward) Initiate the VIBE_ALIGNER workflow, passing `lean_canvas_summary.json` as input.** Guide the user through the phases:
    *   Phase 1: Education (Explain constraints)
    *   Phase 2: Extraction (Interview for project goals) ← **Auto-WebSearch enabled for vague answers (v1.1)**
    *   Phase 3: Validation (Generate `feature_spec.json`)
    *   Phase 4: NFR Triage (Capture non-functional requirements) ← **(Added in v1.0 hardening)**
11. **(Steward) [Validate Artifact]** Validate `feature_spec.json` structure against `ORCHESTRATION_data_contracts.yaml`.
12. **(Steward) Save validated artifact** to `artifacts/planning/` directory.
13. **(Steward) Update `project_manifest.json`:**
    *   Set `code_gen_spec_uri` to path of new `feature_spec.json`
    *   Set `current_state` to 'AWAITING_ARCHITECTURE'
14. **(Steward) Announce:** "SOP_001 complete. System state is now 'AWAITING_ARCHITECTURE'. The `GENESIS_BLUEPRINT_v5` agent will be invoked next."

---

## v1.1 ENHANCEMENTS

### Auto-WebSearch Integration

**NEW:** VIBE_ALIGNER Phase 2 (Extraction) now auto-triggers WebSearch when:
- User says "I don't know", "not sure", "maybe"
- Response is very short (<10 words for complex question)
- Confidence level is detected as LOW

**Flow:**
```
User: "I'm not sure what the main problem is..."
Agent: "No problem! Let me research typical challenges in [your domain]."
→ Executes WebSearch
→ Presents findings: "Based on 2024 research, I found..."
→ User confirms or corrects
```

### Backward Compatibility

**If `project_type` is missing:**
- Defaults to "commercial" (full workflow)
- 100% backward compatible with existing projects

**Migration:**
- Existing projects work without changes
- Add `project_type` field to opt-in to Quick Research mode
