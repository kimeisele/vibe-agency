# Validation Gate: No Constraint Violations

## Rule
The specification must not violate any constraints defined in `CODE_GEN_constraints.yaml`.

---

## Validation Process

For EACH feature in `code_gen_spec.json`:
1. Check technology stack compatibility
2. Validate framework/language versions
3. Check for forbidden patterns
4. Verify resource constraints
5. Validate architectural compliance

---

## Common Violations

- Technology stack mismatch (e.g., Python 2 when 3+ required)
- Forbidden library usage
- Architectural pattern violations
- Resource limit exceeded
- Incompatible frameworks

---

## Pass Criteria

- ✅ All features compatible with constraints
- ✅ No forbidden patterns used
- ✅ Resource limits respected
- ✅ Technology stack valid

---

## Failure Conditions

- ❌ Constraint violation detected
- ❌ Forbidden technology requested
- ❌ Resource limit exceeded

---

## Error Message Template

```
GATE FAILED: Constraint violation detected

Feature "{feature_id}" violates {constraint_id}.

Violation: {description}

Reason: {reason}

Action: Modify specification to comply with constraints
```
