
# SOP-001: Start New Project

**PURPOSE:** To guide the user through the 'PLANNING' state (AOS Framework 01) and generate the initial 'feature_spec.json' artifact.

**PRE-CONDITION:** `project_manifest.json` `current_state` is 'INITIALIZING' or 'PLANNING'. (Der Steward MUSS dies vor der Ausführung prüfen).

**POST-CONDITION:**
1.  A validated `feature_spec.json` artifact is created and saved.
2.  `project_manifest.json` `code_gen_spec_uri` (oder ein Äquivalent) wird aktualisiert.
3.  `project_manifest.json` `current_state` wird auf 'AWAITING_ARCHITECTURE' gesetzt (um den `GENESIS_BLUEPRINT_v5` Agenten auszulösen).

---

## STEPS (Executed by Steward):

1.  **(Steward) [Check]** Confirm `current_state` in `project_manifest.json` is 'INITIALIZING' or 'PLANNING'.
2.  **(Steward) [Acknowledge]** State to user: "Acknowledged. We are initiating SOP_001_Start_New_Project to define the project scope."
3.  **(Steward) [Load Agent]** Announce: "Loading the 'VIBE ALIGNER' specialist agent (`agency_os/01_planning_framework/prompts/VIBE_ALIGNER_v3.md`)."
4.  **(Steward) [Load Knowledge]** Announce: "Loading required knowledge: `APCE_rules.yaml`, `FAE_constraints.yaml`, `FDG_dependencies.yaml`."
5.  **(Steward) Initiate the VIBE_ALIGNER workflow.** Guide the user through the three phases mandated by that agent's prompt:
    *   Phase 1: Education (Explain the constraints to the user).
    *   Phase 2: Extraction (Interview the user for project goals).
    *   Phase 3: Validation (Generate the `feature_spec.json` and ask for user confirmation).
6.  **(Steward) [Validate Artifact]** After the agent produces the `feature_spec.json`, validate its structure against the `agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml`.
7.  **(Steward) Save the validated artifact** to the `artifacts/planning/` directory (oder dem im `project_manifest.json` definierten Pfad).
8.  **(Steward) Guide the user to update the `project_manifest.json`:**
    *   Set `code_gen_spec_uri` (oder Äquivalent) auf den Pfad der neuen `feature_spec.json`.
    *   Set `current_state` to 'AWAITING_ARCHITECTURE'.
9.  **(Steward) Announce:** "SOP_001 complete. The system state is now 'AWAITING_ARCHITECTURE'. The `GENESIS_BLUEPRINT_v5` agent will now be invoked by the AOS Orchestrator."
