# Validation Gate: Valid JSON Output

## Rule
Output must be valid, parseable JSON matching the feature_spec.json schema.

---

## Validation Process

1. Parse JSON output
2. Validate against schema in `ORCHESTRATION_data_contracts.yaml#feature_spec`
3. Check all required fields are present
4. Verify data types match schema

---

## Required Top-Level Fields

```json
{
  "project": {...},        // Required
  "features": [...],       // Required, must have at least 1 feature
  "scope_negotiation": {...},  // Required
  "validation": {...},     // Required
  "metadata": {...}        // Required
}
```

---

## Pass Criteria

- ✅ Valid JSON (parseable, no syntax errors)
- ✅ All required top-level fields present
- ✅ All features have required fields per schema
- ✅ Data types match schema
- ✅ `validation.ready_for_genesis = true`

---

## Failure Conditions

- ❌ JSON syntax error (unclosed braces, missing commas, etc.)
- ❌ Missing required field
- ❌ Field has wrong data type (e.g., string instead of array)
- ❌ `validation.ready_for_genesis = false`

---

## Error Message Template

```
GATE FAILED: Invalid JSON output

The generated feature_spec.json does not match the required schema.

Issues:
{list_validation_errors}

Example issues:
- Missing field: "project.core_problem"
- Invalid type: "features" should be array, got string
- Syntax error: Unclosed brace at line 42

Action: Fix JSON structure and retry Task 06 (Output Generation)
```

---

## Purpose

Ensures output is machine-readable and can be consumed by GENESIS_BLUEPRINT.
