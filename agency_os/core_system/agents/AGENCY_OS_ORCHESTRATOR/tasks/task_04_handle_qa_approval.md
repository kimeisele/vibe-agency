# Task 04: Handle QA Approval State

**TASK_ID:** task_04_handle_qa_approval
**STATE:** AWAITING_QA_APPROVAL
**PURPOSE:** Wait for human approval/rejection of QA results (Durable Execution)

---

## GOAL

Pause the workflow and wait for human decision on QA report. This is a long-running, paused state.

---

## STATE HANDLER LOGIC

### Trigger
`projectPhase` is `AWAITING_QA_APPROVAL`.

### Actions

1. **Pause Workflow:**
   - The underlying engine (e.g., Temporal) will pause the workflow indefinitely
   - No resources consumed during pause

2. **Send Notification:**
   - External notification sent to human approver (Slack, UI, email)

3. **Wait for Signal:**
   - Wait for one of two external signals:
     - `qa_approved_signal`
     - `qa_rejected_signal`

---

## TRANSITIONS

### On `qa_approved_signal` (T4_StartDeployment)

1. **Read QA Report:**
   - Load `qa_report.json`
   - Verify `status` is `APPROVED`

2. **Transition to DEPLOYMENT:**
   - Update `project_manifest.json`:
     - Set `status.projectPhase` to `DEPLOYMENT`
     - Set `status.message` to "QA Approved. Ready for deployment."
   - Commit and push the updated manifest

### On `qa_rejected_signal` (L1_TestFailed - Loop)

1. **Read QA Report:**
   - Load `qa_report.json`
   - Extract failure reasons

2. **Loop Back to CODING:**
   - Update `project_manifest.json`:
     - Set `status.projectPhase` to `CODING`
     - Set `status.message` to "QA Rejected. Returning to coding with feedback."
     - **CRITICAL:** Ensure `qa_report.json` is passed as feedback to the next CODING cycle
   - Commit and push the updated manifest

---

## REQUIRED ARTIFACTS (INPUT)

- `qa_report.json` (from TESTING state)

---

## PRODUCED ARTIFACTS (OUTPUT)

- None (state transition only)

---

## SUCCESS CRITERIA

- ✅ Workflow paused successfully
- ✅ Notification sent to approver
- ✅ Correct signal received
- ✅ Appropriate transition executed
- ✅ Manifest updated and committed
