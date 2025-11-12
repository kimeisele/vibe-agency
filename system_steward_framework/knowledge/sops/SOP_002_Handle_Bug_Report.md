
# SOP-002: Handle Bug Report

**PURPOSE:** To triage a user-reported bug and create a compliant `bug_report.json` artifact, ensuring all necessary data is collected before invoking the `BUG_TRIAGE_v1` agent.

**PRE-CONDITION:** User indicates intent to report a bug.

**POST-CONDITION:**
1.  A validated `bug_report.json` artifact is created and saved.
2.  `project_manifest.json` `current_state` is set to 'MAINTENANCE_TRIAGE'.

---

## STEPS (Executed by Steward):

1.  **(Steward) [Acknowledge]** State to user: "Acknowledged. We are initiating SOP_002_Handle_Bug_Report to document this issue."
2.  **(Steward) Announce:** "Loading `knowledge/templates/bug_report_template.json`. I will now guide you step-by-step to fill this template. This is mandatory to ensure the `BUG_TRIAGE_v1` agent has sufficient information."
3.  **(Steward) Ask:** "Please provide a short, descriptive title for this bug."
4.  **(Steward) Ask:** "Please provide the exact steps to reproduce this bug, in a numbered list." (Ref: 20)
5.  **(Steward) Ask:** "What was the expected result?"
6.  **(Steward) Ask:** "What was the actual result?"
7.  **(Steward) Ask:** "Please specify the environment (e.g., OS, browser, app version)."
8.  **(Steward) Announce:** "We must now set the priority." (Ref: 20)
    *   **Ask:** "How severe is this bug? (Critical, Major, Minor, Trivial)"
    *   **Ask:** "What is the impact? (How many users are affected? High, Medium, Low)"
9.  **(Steward) [Generate Artifact]** Assemble all collected data into the `bug_report.json` format.
10. **(Steward) [Validate Artifact]** Validate the generated JSON against the `agency_os/00_system/contracts/ORCHESTRATION_data_contracts.yaml`.
11. **(Steward) Save the validated artifact.**
12. **(Steward) Guide the user to set the `project_manifest.json` `current_state` to 'MAINTENANCE_TRIAGE'.**
13. **(Steward) Announce:** "SOP_002 complete. The `bug_report.json` is filed. The AOS Orchestrator will now invoke the `BUG_TRIAGE_v1` agent for analysis."
