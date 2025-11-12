# Gate: State Integrity

**GATE_ID:** gate_state_integrity
**SEVERITY:** CRITICAL
**PURPOSE:** Ensure state transitions follow the defined state machine rules

---

## VALIDATION RULE

**CRITICAL:** All state transitions MUST follow the rules defined in `ORCHESTRATION_workflow_design.yaml`.

### What This Gate Checks:

1. **Valid Transitions:** Current state can transition to target state
2. **Required Conditions:** All conditions for transition are met
3. **No Invalid Jumps:** Can't skip states unless explicitly allowed
4. **Loop Integrity:** Error loops follow defined paths

---

## VALID STATE TRANSITIONS

```
PLANNING → CODING (T1_StartCoding)
CODING → TESTING (T2_StartTesting)
TESTING → AWAITING_QA_APPROVAL (T3_RequestQAApproval)
AWAITING_QA_APPROVAL → DEPLOYMENT (T4_StartDeployment, on approval)
AWAITING_QA_APPROVAL → CODING (L1_TestFailed, on rejection)
DEPLOYMENT → PRODUCTION (T5_DeploymentSuccess)
DEPLOYMENT → MAINTENANCE (L2_DeployFailed)
MAINTENANCE → CODING (L3_HotfixLoop)
MAINTENANCE → PLANNING (L4_RegularFixLoop)
PRODUCTION → MAINTENANCE (external trigger)
```

---

## VALIDATION LOGIC

```python
def validate_state_transition(current_state, next_state):
    """
    Check if transition from current_state to next_state is valid.
    """
    valid_transitions = {
        "PLANNING": ["CODING"],
        "CODING": ["TESTING"],
        "TESTING": ["AWAITING_QA_APPROVAL"],
        "AWAITING_QA_APPROVAL": ["DEPLOYMENT", "CODING"],
        "DEPLOYMENT": ["PRODUCTION", "MAINTENANCE"],
        "PRODUCTION": ["MAINTENANCE"],
        "MAINTENANCE": ["CODING", "PLANNING"]
    }

    if next_state not in valid_transitions.get(current_state, []):
        raise StateIntegrityError(
            f"Invalid transition: {current_state} → {next_state}"
        )

    return True
```

---

## PASS CRITERIA

✅ Transition is in the valid transitions list
✅ All required artifacts for target state exist
✅ Conditions for transition are met
✅ No state machine rules violated

---

## FAIL CRITERIA

❌ Invalid transition attempted
❌ Required artifacts missing
❌ Conditions not met
❌ State machine rules violated

---

## WHY THIS MATTERS

State integrity ensures:
- **Predictable Workflow:** No surprising state jumps
- **Artifact Chain:** Each state has required inputs
- **Error Recovery:** Loops follow defined paths
- **Auditability:** State history is traceable
