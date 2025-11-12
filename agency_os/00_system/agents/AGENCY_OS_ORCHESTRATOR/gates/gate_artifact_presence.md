# Gate: Artifact Presence

**GATE_ID:** gate_artifact_presence
**SEVERITY:** CRITICAL
**PURPOSE:** Ensure required artifacts exist before state transitions

---

## VALIDATION RULE

**CRITICAL:** All required input artifacts must exist and be valid before transitioning to a new state.

### What This Gate Checks:

1. **File Exists:** Required artifact files are present
2. **Valid JSON:** Artifact files contain valid JSON (if applicable)
3. **Schema Compliance:** Artifacts match their data contract schemas
4. **Non-Empty:** Artifacts contain actual data, not empty stubs

---

## REQUIRED ARTIFACTS BY STATE

### PLANNING → CODING
**Required:**
- `code_gen_spec.json` (output from GENESIS_BLUEPRINT)
- `architecture.json` (output from GENESIS_BLUEPRINT)

### CODING → TESTING
**Required:**
- `test_plan.json` (output from CODE_GENERATOR)
- Code commit SHA in manifest

### TESTING → AWAITING_QA_APPROVAL
**Required:**
- `qa_report.json` (output from QA_VALIDATOR)

### AWAITING_QA_APPROVAL → DEPLOYMENT
**Required:**
- `qa_report.json` with `status: APPROVED`

### DEPLOYMENT → PRODUCTION
**Required:**
- `deploy_receipt.json` with `status: SUCCESS`

### DEPLOYMENT → MAINTENANCE
**Required:**
- `deploy_receipt.json` with `status: ROLLED_BACK`
- `bug_report.json` (auto-generated)

---

## VALIDATION LOGIC

```python
def validate_artifact_presence(state_transition, manifest):
    """
    Check if all required artifacts exist for this transition.
    """
    required_artifacts = get_required_artifacts(state_transition)

    for artifact_path in required_artifacts:
        # Check file exists
        if not os.path.exists(artifact_path):
            raise ArtifactMissingError(
                f"Required artifact missing: {artifact_path}"
            )

        # Check valid JSON (if applicable)
        if artifact_path.endswith('.json'):
            try:
                with open(artifact_path, 'r') as f:
                    data = json.load(f)
                    if not data:
                        raise ArtifactInvalidError(
                            f"Artifact is empty: {artifact_path}"
                        )
            except json.JSONDecodeError:
                raise ArtifactInvalidError(
                    f"Invalid JSON: {artifact_path}"
                )

    return True
```

---

## PASS CRITERIA

✅ All required artifacts exist
✅ All artifacts contain valid data
✅ All artifacts match schema
✅ Manifest references are correct

---

## FAIL CRITERIA

❌ Required artifact missing
❌ Artifact contains invalid JSON
❌ Artifact is empty
❌ Artifact doesn't match schema
❌ Manifest reference is broken

---

## WHY THIS MATTERS

Artifact presence ensures:
- **Data Flow:** Each state has the inputs it needs
- **No Blind Execution:** Agents don't run without context
- **Error Prevention:** Catches missing data early
- **State Machine Integrity:** Can't proceed without completing prior steps
