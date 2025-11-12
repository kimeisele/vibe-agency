# Task: Validate Architecture Against FAE

**PHASE:** 4
**TASK ID:** validate_architecture
**TRIGGER:** config_system.json available

---

## OBJECTIVE

Validate the generated architecture against FAE (Feature Anti-Expansion) constraints to ensure no v1.0 infeasible features are included.

---

## INPUT ARTIFACTS

### Required:
1. **core_modules_selection.json**
2. **extensions_design.json**
3. **config_system.json**
4. **FAE_constraints.yaml** (knowledge base)

---

## VALIDATION PROCESS

### Check 1: v1.0 Scope Violations

Ensure no v2.0+ features are included in extensions:

```python
def validate_architecture(architecture, fae_constraints):
    """
    Validate the generated architecture against FAE.
    This is a FINAL safety check.
    """
    violations = []

    # Check 1: Are any v2.0 features in extensions?
    for ext in architecture.extensions:
        feature = find_feature_by_id(ext.implements_feature)

        # Check against FAE incompatibilities
        for constraint in fae_constraints.incompatibilities:
            if matches(ext.name, constraint.feature):
                if constraint.incompatible_with == "scope_v1.0":
                    violations.append({
                        "extension": ext.name,
                        "violation": f"FAE-{constraint.id}",
                        "reason": constraint.reason,
                        "recommendation": constraint.alternatives_for_v1
                    })

    return violations
```

### Check 2: Tech Stack Conflicts

Ensure no conflicting technologies:

```python
for ext in architecture.extensions:
    for dep in ext.external_deps:
        # Check against FAE tech constraints
        for tech_constraint in fae_constraints.tech_constraints:
            if dep in tech_constraint.technology:
                if has_conflict(architecture, tech_constraint):
                    violations.append({
                        "extension": ext.name,
                        "violation": f"Tech conflict: {dep}",
                        "reason": tech_constraint.reason
                    })
```

---

## IF VIOLATIONS FOUND

**DO NOT OUTPUT ARCHITECTURE.**

Instead, return error message:

```
❌ ARCHITECTURE VALIDATION FAILED

The proposed architecture violates technical feasibility constraints:

**Violation 1: {extension_name}**
Issue: {violation}
Reason: {reason}
Recommendation: {alternatives}

**Violation 2: ...**

This indicates a bug in VIBE_ALIGNER (features were not properly validated).

Please return to VIBE_ALIGNER and re-validate the feature specification.
```

**STOP EXECUTION.** Do not proceed to task_05.

---

## IF NO VIOLATIONS

Set validation status to `passed` and proceed to task_05_handoff.

---

## OUTPUT ARTIFACT

### validation_result.json

```json
{
  "validation": {
    "fae_passed": true,
    "checks": [
      "✅ Core module count: 9 (within 6-12 range)",
      "✅ Core uses only stdlib (except config → pyyaml)",
      "✅ Extensions isolated (no cross-imports)",
      "✅ All features have extensions",
      "✅ No v2.0 features in architecture"
    ],
    "violations": []
  }
}
```

Or if violations:

```json
{
  "validation": {
    "fae_passed": false,
    "checks": [
      "✅ Core module count: 9",
      "✅ Core stdlib only",
      "❌ Feature X violates v1.0 scope"
    ],
    "violations": [
      {
        "extension": "real_time_video_streaming",
        "violation": "FAE-001",
        "reason": "Requires WebRTC, STUN/TURN servers - too complex for v1.0",
        "recommendation": "Use embedded 3rd party (Zoom, Jitsi)"
      }
    ]
  }
}
```

---

## EXECUTION INSTRUCTIONS

1. Load all input artifacts
2. Load FAE_constraints.yaml
3. Run v1.0 scope validation
4. Run tech stack conflict validation
5. Generate validation_result.json
6. **IF fae_passed == false**: STOP and return error message
7. **IF fae_passed == true**: Proceed to task_05_handoff
