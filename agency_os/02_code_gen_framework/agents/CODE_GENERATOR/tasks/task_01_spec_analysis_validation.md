# Task: Specification Analysis & Validation

## Objective
Parse, understand, and validate the `code_gen_spec.json` against constraints before code generation begins.

---

## Goal
Ensure the specification is complete, valid, and feasible before proceeding to code generation.

---

## Input Artifacts
- `code_gen_spec.json` (from GENESIS_BLUEPRINT)
- `CODE_GEN_constraints.yaml` (from knowledge base)
- `CODE_GEN_dependencies.yaml` (from knowledge base)

---

## Process

### Step 1: Parse Input
- Thoroughly read and understand the `code_gen_spec.json`
- Identify all features to be implemented
- Extract API definitions, acceptance criteria, contextual awareness

### Step 2: Validate Against Constraints
Check the specification against `CODE_GEN_constraints.yaml`:
- Technology stack compatibility
- Framework/language version requirements
- Architectural pattern compliance (Genesis Core Pattern)
- Forbidden patterns or practices
- Resource constraints

**If violations found:** Output error report and STOP (do not proceed to Phase 2)

### Step 3: Dependency Mapping
Based on `CODE_GEN_dependencies.yaml`:
- Identify all required external libraries
- Map features to required frameworks
- Detect internal module dependencies
- Validate dependency versions

---

## Output

Validation result structure:

```json
{
  "validation_passed": true,
  "spec_id": "cgs-001",
  "parsed_features": [
    {
      "feature_id": "FEAT-001",
      "description": "...",
      "required_modules": ["auth", "database"],
      "required_libraries": ["fastapi", "sqlalchemy"]
    }
  ],
  "constraints_checked": ["CONSTRAINT-001", "CONSTRAINT-005"],
  "dependency_map": {
    "external": ["fastapi==0.104.0", "sqlalchemy==2.0.0"],
    "internal": ["src/core/auth.py", "src/core/database.py"]
  },
  "issues": []
}
```

---

## Success Criteria

- ✅ `code_gen_spec.json` is valid and parseable
- ✅ All constraints validated
- ✅ All dependencies identified
- ✅ No blocking violations found
- ✅ Ready to proceed to code generation

---

## Validation Gates

- `gate_spec_valid.md` - Ensures specification is well-formed
- `gate_no_constraint_violations.md` - Ensures no constraints violated
