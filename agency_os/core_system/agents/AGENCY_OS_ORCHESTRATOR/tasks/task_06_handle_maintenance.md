# Task 06: Handle Maintenance State

**TASK_ID:** task_06_handle_maintenance
**STATE:** MAINTENANCE
**PURPOSE:** Orchestrate bug triage and resolution workflow

---

## GOAL

Invoke BUG_TRIAGE to analyze bug reports and determine the appropriate fix path.

---

## STATE HANDLER LOGIC

### Trigger
An external event (monitoring alert, user report, deployment failure) creates a `bug_report.json`.

### Actions

1. **Read Input Artifacts:**
   - Load `bug_report.json`

2. **Invoke BUG_TRIAGE:**
   - Load from `agency_os/05_maintenance_framework/prompts/BUG_TRIAGE_v1.md`
   - Input: `bug_report.json`
   - Output: `triage_result.json`

3. **Check Triage Result:**
   - Read `triage_result.decision`

---

## TRANSITIONS

### On `triage_result == 'Hotfix'` (L3_HotfixLoop - Loop)

1. **Generate Fix Spec:**
   - Triage agent produces a `code_gen_spec.json` for the fix

2. **Initiate High-Priority Workflow:**
   - A new, high-priority workflow is initiated
   - Starting directly in the `CODING` state with this new spec
   - This bypasses PLANNING for urgent fixes

### On `triage_result == 'Regular Fix'` (L4_RegularFixLoop - Loop)

1. **Add to Backlog:**
   - Triage agent flags the bug for the backlog

2. **Update Manifest:**
   - Update `project_manifest.json`:
     - Add bug to `spec.backlog` array
   - This signals PLANNING phase to consider this bug in the next development cycle

---

## REQUIRED ARTIFACTS (INPUT)

- `bug_report.json`

---

## PRODUCED ARTIFACTS (OUTPUT)

- `triage_result.json`
- `code_gen_spec.json` (if hotfix)

---

## SUCCESS CRITERIA

- ✅ BUG_TRIAGE executed successfully
- ✅ Triage decision made
- ✅ Appropriate workflow initiated
- ✅ Hotfix spec created or bug added to backlog
- ✅ Manifest updated and committed
