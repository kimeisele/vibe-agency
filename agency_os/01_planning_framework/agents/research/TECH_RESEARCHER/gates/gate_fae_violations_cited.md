# Validation Gate: FAE Violations Cited

**Gate ID:** gate_fae_violations_cited
**Purpose:** Ensure all flagged features reference existing FAE rule IDs
**Enforcement:** WARNING ONLY - does not block progression

---

## Validation Criteria

This gate passes ONLY if:

1. **All flagged features have fae_violation field**
   - Can be null (for constraints without FAE rules)
   - If not null, must be valid FAE rule ID format

2. **FAE rule IDs follow format**
   - Pattern: FAE-[CATEGORY]-[NUMBER]
   - Example: FAE-TECH-003, FAE-SCALE-001

3. **FAE rules are referenced, not duplicated**
   - Violations cite existing rules from FAE_constraints.yaml
   - No new rules created in research

---

## Validation Logic

```python
import re

def validate_fae_violations_cited(flagged_features):
    issues = []
    warnings = []

    # FAE rule ID pattern: FAE-CATEGORY-NUMBER
    fae_pattern = re.compile(r'^FAE-[A-Z]+-\d{3}$')

    for i, feature in enumerate(flagged_features):
        feature_name = feature.get("feature", f"Feature #{i+1}")

        # Check fae_violation field exists
        if "fae_violation" not in feature:
            issues.append(f"{feature_name}: Missing fae_violation field (should be null or FAE-XXX-YYY)")
            continue

        fae_violation = feature["fae_violation"]

        # If fae_violation is set (not null), validate format
        if fae_violation is not None:
            if not isinstance(fae_violation, str):
                issues.append(f"{feature_name}: fae_violation must be string or null, got {type(fae_violation)}")
            elif not fae_pattern.match(fae_violation):
                issues.append(f"{feature_name}: Invalid FAE rule ID format: {fae_violation} (should be FAE-XXX-YYY)")

        # Check recommendation exists
        if "recommendation" not in feature or not feature["recommendation"]:
            warnings.append(f"{feature_name}: No recommendation provided for constraint")

    # This gate is WARNING ONLY, so we pass even with issues
    # But we report them for review
    passed = True  # WARNING ONLY gate

    return {
        "passed": passed,
        "issues": issues,
        "warnings": warnings,
        "features_checked": len(flagged_features),
        "gate_type": "WARNING_ONLY"
    }
```

---

## Example: Pass vs. Fail

### ✅ PASS - Valid FAE reference
```json
{
  "flagged_features": [
    {
      "feature": "WebSocket connections",
      "fae_violation": "FAE-TECH-003",
      "recommendation": "Use managed WebSocket service"
    }
  ]
}
```

### ✅ PASS - No FAE rule (null)
```json
{
  "flagged_features": [
    {
      "feature": "Large file uploads",
      "fae_violation": null,
      "recommendation": "Use direct-to-S3 uploads"
    }
  ]
}
```

### ⚠️ WARNING - Invalid format
```json
{
  "flagged_features": [
    {
      "feature": "WebSocket connections",
      "fae_violation": "FAE-003",  // ⚠️ Missing category
      "recommendation": "Use managed service"
    }
  ]
}
```

---

## Success Message

```
✅ Gate Passed: FAE Violations Cited
- Checked: 3 flagged features
- All FAE violations properly cited or marked as null
- All have recommendations
- Ready for next task
```

---

## Warning Message

```
⚠️ Gate Warning: FAE Violations Cited
Issues found (WARNING ONLY - not blocking):
- Feature X: Invalid FAE rule ID format: FAE-003 (should be FAE-XXX-YYY)
- Feature Y: No recommendation provided

Recommendation: Fix FAE rule format and add recommendations.
Proceeding to next task (warning only).
```

---

## Notes

This gate is **WARNING ONLY** because:
- FAE rules may not exist yet for all constraints
- New constraints may need FAE team review
- Research should not be blocked by FAE rule availability
