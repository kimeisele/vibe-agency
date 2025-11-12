# Validation Gate: Concrete Specifications

## Rule
All extracted features must have concrete input/output examples, not vague descriptions.

---

## Validation Process

For EACH feature in `extracted_features.json`:

1. Check that `input.example` is present and concrete
2. Check that `output.example` is present and concrete
3. Check that `input.format` is specific (not "TBD" or "varies")
4. Check that `output.format` is specific

---

## Pass Criteria

For each feature:
- ✅ `input.example` is not empty
- ✅ `output.example` is not empty
- ✅ `input.format` is a specific format (CSV, JSON, CLI args, etc.)
- ✅ `output.format` is a specific format

---

## Failure Conditions

- ❌ Feature has empty `input.example`
- ❌ Feature has empty `output.example`
- ❌ Feature has vague format like "TBD", "various", "depends"
- ❌ Feature description is < 10 characters (too vague)

---

## Error Message Template

```
GATE FAILED: Incomplete feature specification

Feature "{feature_name}" lacks concrete specifications.

Missing or vague:
- input.example: {current_value}
- output.example: {current_value}
- input.format: {current_value}
- output.format: {current_value}

Action: Return to Task 02 (Feature Extraction) and clarify specifics
```

---

## Purpose

Ensures features are specific enough to validate against FAE and design architecture.
