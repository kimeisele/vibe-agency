# Validation Gate: Spec Valid

## Rule
The `code_gen_spec.json` must be well-formed, parseable, and contain all required fields.

---

## Validation Process

1. Parse JSON (check for syntax errors)
2. Validate against schema in `ORCHESTRATION_data_contracts.yaml#code_gen_spec`
3. Check all required fields present

---

## Required Fields

```
- specId
- projectId
- architectureRef
- features[] (at least 1 feature)
- apiDefinitions (if REST API)
- contextualAwareness
```

---

## Pass Criteria

- ✅ JSON is parseable (no syntax errors)
- ✅ All required fields present
- ✅ Data types match schema
- ✅ At least 1 feature specified

---

## Failure Conditions

- ❌ JSON syntax error
- ❌ Missing required field
- ❌ Empty features array
- ❌ Invalid data types

---

## Error Message Template

```
GATE FAILED: Invalid specification

The code_gen_spec.json is malformed or incomplete.

Issues found:
{list_validation_errors}

Action: Fix code_gen_spec.json and retry
```
