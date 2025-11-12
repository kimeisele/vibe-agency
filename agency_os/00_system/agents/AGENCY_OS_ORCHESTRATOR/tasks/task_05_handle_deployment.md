# Task 05: Handle Deployment State

**TASK_ID:** task_05_handle_deployment
**STATE:** DEPLOYMENT
**PURPOSE:** Orchestrate deployment to production environment

---

## GOAL

Invoke DEPLOY_MANAGER to deploy the approved code to production.

---

## STATE HANDLER LOGIC

### Trigger
`projectPhase` is `DEPLOYMENT`.

### Actions

1. **Read Input Artifacts:**
   - Load `qa_report.json` to confirm approval
   - Load code commit SHA from manifest

2. **Invoke DEPLOY_MANAGER:**
   - Load from `agency_os/04_deploy_framework/prompts/DEPLOY_MANAGER_v1.md`
   - Input: `qa_report.json` + code commit SHA
   - Output: `deploy_receipt.json`

3. **Check Deployment Result:**
   - Read `deploy_receipt.status`

---

## TRANSITIONS

### On `deploy_receipt.status == 'SUCCESS'` (T5_DeploymentSuccess)

- Update `project_manifest.json`:
  - Set `status.projectPhase` to `PRODUCTION`
  - Add link to `deploy_receipt.json` in `artifacts.deployment`
  - Set `status.message` to "Deployment successful. Project is live."
- Commit and push the updated manifest

### On `deploy_receipt.status == 'ROLLED_BACK'` (L2_DeployFailed - Loop)

- Update `project_manifest.json`:
  - Set `status.projectPhase` to `MAINTENANCE`
  - Set `status.message` to "CRITICAL: Deployment failed and was rolled back. Initiating P1 bug report."
- **Action:** Automatically generate a `bug_report.json` with `severity: P1_Critical` based on deployment failure
- Trigger maintenance workflow
- Commit and push the updated manifest

---

## REQUIRED ARTIFACTS (INPUT)

- `qa_report.json` (from TESTING state)
- Code commit SHA

---

## PRODUCED ARTIFACTS (OUTPUT)

- `deploy_receipt.json`
- `bug_report.json` (if deployment fails)

---

## SUCCESS CRITERIA

- ✅ DEPLOY_MANAGER executed successfully
- ✅ Deployment status recorded
- ✅ Appropriate transition executed
- ✅ Manifest updated and committed
- ✅ P1 bug report created if deployment failed
