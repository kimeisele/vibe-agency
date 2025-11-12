
# SOP-003: Execute HITL Deployment Approval

**PURPOSE:** To manage the critical Human-in-the-Loop (HITL) checkpoint 'T4_StartDeployment' defined in `ORCHESTRATION_workflow_design.yaml`.

**PRE-CONDITION:** `project_manifest.json` `current_state` is 'AWAITING_QA_APPROVAL'. (Diese SOP wird vom Steward proaktiv geladen, wenn dieser Zustand erkannt wird).

**POST-CONDITION:**
1.  Human decision (Approve/Reject) is logged.
2.  (If Approved) User is guided to send the `qa_approved_signal` to the AOS Orchestrator.
3.  (If Rejected) User is guided to initiate the `L1_TestFailed` loop.

---

## STEPS (Executed by Steward):

1.  **(Steward) Announce proactively:** "SYSTEM PAUSED: HUMAN APPROVAL REQUIRED." (Ref: 22)
2.  **(Steward) [Context]** State: "The AOS is at state 'AWAITING_QA_APPROVAL'. I am loading SOP_003 to manage this checkpoint."
3.  **(Steward) [Load Artifact]** State: "Loading the `qa_report.json` referenced in `project_manifest.json` at `qa_report_uri`."
4.  **(Steward) Present the key findings from the report, specifically the final status (e.g., 'APPROVED') and any 'critical_errors' count.**
5.  **(Steward) State:** "This is a critical checkpoint.23 The AOS requires explicit human sign-off before proceeding to 'DEPLOYING'. Do you approve this QA report and authorize deployment? (YES/NO)"
6.  **(Steward) (Ref: 23)**
    *   **IF YES:** Record: "User [User_Name] APPROVED deployment at."
    *   **IF NO:** Record: "User [User_Name] REJECTED deployment at."
7.  **(Steward)**
    *   **State:** "Approval logged. To resume the AOS, you must now send the `qa_approved_signal` to the `AGENCY_OS_ORCHESTRATOR_v1`. Please confirm when you have triggered this signal."
    *   **(Steward waits for confirmation).**
    *   **State:** "Signal confirmed. The AOS state will now transition to 'DEPLOYING'."
8.  **(Steward) [Path - IF NO]**
    *   **State:** "Rejection logged. This triggers the 'L1_TestFailed' loop in the State Machine."
    *   **State:** "To proceed, you must manually set the `project_manifest.json` `current_state` back to 'CODING' (for code fixes) or 'AWAITING_QA' (for re-testing)."
    *   **State:** "Please provide a reason for the rejection, which I will log against the `qa_report.json`."
    *   **(Steward collects and logs the reason).**
9.  **(Steward) Announce:** "SOP_003 complete. HITL checkpoint resolved."
