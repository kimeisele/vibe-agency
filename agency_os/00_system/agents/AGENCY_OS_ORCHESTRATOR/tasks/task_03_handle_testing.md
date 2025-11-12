# Task 03: Handle Testing State

**TASK_ID:** task_03_handle_testing
**STATE:** TESTING
**PURPOSE:** Orchestrate automated testing and QA validation

---

## GOAL

Invoke QA_VALIDATOR to run all tests and produce a quality assessment report.

---

## STATE HANDLER LOGIC

### Trigger
`projectPhase` is `TESTING`.

### Actions

1. **Read Input Artifacts:**
   - Load `test_plan.json` from `artifacts.test`
   - Load latest code commit SHA from `artifacts.code.mainRepository.lastCommit`

2. **Invoke QA_VALIDATOR:**
   - Load from `agency_os/03_qa_framework/prompts/QA_VALIDATOR_v1.md`
   - Input: `test_plan.json` + code commit SHA
   - Output: `qa_report.json`

3. **Transition (T3_RequestQAApproval):**
   - **Condition:** `qa_report.json` is created
   - **Actions:**
     - Update `project_manifest.json`:
       - Set `status.projectPhase` to `AWAITING_QA_APPROVAL`
       - Add link to `qa_report.json` in `artifacts.test`
       - Set `status.message` to "Automated QA complete. Awaiting human approval."
     - Commit and push the updated manifest

---

## REQUIRED ARTIFACTS (INPUT)

- `test_plan.json` (from CODING state)
- Code commit SHA

---

## PRODUCED ARTIFACTS (OUTPUT)

- `qa_report.json`

---

## SUCCESS CRITERIA

- ✅ QA_VALIDATOR executed successfully
- ✅ All tests run (pass or fail recorded)
- ✅ QA report generated
- ✅ Transition to AWAITING_QA_APPROVAL state completed
- ✅ Manifest updated and committed
