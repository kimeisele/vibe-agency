# Validation Gate: Artifact Bundle Valid

## Rule
The final `artifact_bundle` must be well-formed and complete.

---

## Validation Process

1. Validate JSON structure
2. Check all required sections present
3. Verify metadata is complete
4. Validate file paths are valid

---

## Required Sections

```json
{
  "bundleId": "...",
  "projectId": "...",
  "codeGenSpecRef": {...},
  "sourceCode": [...],
  "tests": [...],
  "documentation": [...],
  "metadata": {...}
}
```

---

## Pass Criteria

- ✅ JSON is valid
- ✅ All required sections present
- ✅ sourceCode has at least 1 file
- ✅ tests has at least 1 file
- ✅ metadata.qualityGatesPassed = true
- ✅ File paths are relative and valid

---

## Failure Conditions

- ❌ Malformed JSON
- ❌ Missing required section
- ❌ Empty sourceCode or tests
- ❌ Invalid file paths

---

## Error Message Template

```
GATE FAILED: Invalid artifact_bundle

Issues:
{list_validation_errors}

Example:
  - Missing section: "tests"
  - Empty array: "sourceCode"
  - Invalid path: "../../../etc/passwd"

Action: Fix bundle structure and retry
```
