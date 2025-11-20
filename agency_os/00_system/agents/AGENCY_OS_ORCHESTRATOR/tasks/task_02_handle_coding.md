# Task 02: Handle Coding State

**TASK_ID:** task_02_handle_coding
**STATE:** CODING
**PURPOSE:** Orchestrate code generation from the architecture specification

---

## CURRENT SYSTEM STATE (Live Context - GAD-502)

**Project Phase:** {{ session.phase }}
**Git Branch:** {{ git.branch }}
**Git Status:** {{ git.uncommitted }} uncommitted change(s)
**Test Status:** {{ tests.status }} ({{ tests.failing_count }} failing)
**Last Task:** {{ session.last_task }}

---

## GOAL

Invoke CODE_GENERATOR to produce source code and test artifacts.

---

## STATE HANDLER LOGIC

### Trigger
`projectPhase` is `CODING`.

### Actions

1. **Read Input Artifacts:**
   - Load `code_gen_spec.json` from `artifacts.planning`

2. **Invoke CODE_GENERATOR:**
   - Load from `agency_os/02_code_gen_framework/prompts/CODE_GENERATOR_v1.md`
   - Input: `code_gen_spec.json`
   - Output: `artifact_bundle` (source code, tests) and `test_plan.json`

3. **Quality Gates:**
   - Run linting on generated code
   - Verify all files in spec are created

4. **Transition (T2_StartTesting):**
   - **Condition:** `artifact_bundle` is created and passes quality gates
   - **Actions:**
     - Update `project_manifest.json`:
       - Set `status.projectPhase` to `TESTING`
       - Add link to `test_plan.json` in `artifacts.test`
       - Update `artifacts.code.mainRepository.lastCommit` with new code commit SHA
       - Set `status.message` to "Coding complete. Ready for testing."
     - Commit and push the updated manifest

---

## REQUIRED ARTIFACTS (INPUT)

- `code_gen_spec.json` (from PLANNING state)

---

## PRODUCED ARTIFACTS (OUTPUT)

- `artifact_bundle` (source code files)
- `test_plan.json`
- Code commit SHA

---

## SUCCESS CRITERIA

- ✅ CODE_GENERATOR executed successfully
- ✅ All specified files created
- ✅ Linting passed
- ✅ Test plan generated
- ✅ Transition to TESTING state completed
- ✅ Manifest updated and committed
