# Task: Output Generation

## Objective
Create the final machine-readable feature specification (feature_spec.json) for GENESIS_BLUEPRINT.

---

## Goal
Generate a complete, valid, parseable JSON specification that contains all validated, prioritized features ready for technical architecture planning.

---

## Input Artifacts
- `negotiated_features.json` (from Task 05)
- Session state: `user_scope_choice`, `core_problem_statement`, `target_users`
- `ORCHESTRATION_data_contracts.yaml` (schema reference)

---

## Pre-Output Validation Checklist

Before outputting JSON, verify:

- ✅ User completed education phase
- ✅ All features have concrete input/output examples
- ✅ All features validated against FAE
- ✅ All features checked for missing dependencies (FDG)
- ✅ Scope negotiated if complexity > threshold (APCE)
- ✅ JSON is valid (no syntax errors)
- ✅ All required fields present per data contract

---

## Output Format: feature_spec.json

```json
{
  "project": {
    "name": "Project Name",
    "category": "CLI Tool|Web App|Mobile App|API Service|...",
    "scale": "Solo User|Small Team|Production",
    "target_scope": "prototype|mvp|v1.0",
    "core_problem": "1-2 sentence description of what problem this solves",
    "target_users": "Who will use this"
  },

  "features": [
    {
      "id": "feature_1",
      "name": "Feature Name",
      "priority": "must_have|should_have|could_have|wont_have_v1",
      "complexity_score": 5,
      "estimated_effort": "1-2 weeks",
      "input": {
        "format": "CSV",
        "example": "id,name,email\n1,Alice,alice@example.com",
        "constraints": "Max 1000 rows, required columns: id, name"
      },
      "processing": {
        "description": "Validates email format, removes duplicates, enriches with domain info",
        "external_dependencies": ["email-validator"],
        "side_effects": ["Writes to logs/validation.log"]
      },
      "output": {
        "format": "JSON",
        "example": "{\"valid\": [...], \"invalid\": [...]}",
        "success_criteria": "All valid emails passed regex, no duplicates"
      },
      "dependencies": {
        "required": [
          {
            "component": "email_validation_library",
            "reason": "Must validate email format",
            "source": "FDG-XXX"
          }
        ],
        "optional": []
      },
      "fae_validation": {
        "passed": true,
        "constraints_checked": ["FAE-001", "FAE-015"],
        "issues": []
      }
    }
  ],

  "scope_negotiation": {
    "total_complexity": 45,
    "complexity_breakdown": {
      "must_have": 30,
      "should_have": 15,
      "wont_have_v1": 25
    },
    "timeline_estimate": "10-14 weeks",
    "v1_exclusions": [
      "Feature X (too complex - see FAE-005)",
      "Feature Y (nice-to-have - deprioritized)"
    ]
  },

  "validation": {
    "fae_passed": true,
    "fdg_passed": true,
    "apce_passed": true,
    "all_features_complete": true,
    "ready_for_genesis": true
  },

  "metadata": {
    "vibe_version": "3.0",
    "created_at": "2025-01-15T10:30:00Z",
    "user_educated": true,
    "scope_negotiated": true
  }
}
```

---

## Final Output Message

After generating the JSON, present to user:

```
✅ SPECIFICATION COMPLETE

I've created a comprehensive feature specification for your {project_name}.

**Summary:**
- {must_have_count} Must-Have features (v1.0 core)
- {should_have_count} Should-Have features (v1.0 goals)
- {wont_have_count} features deferred to v2.0
- Total complexity: {complexity} points
- Estimated timeline: {weeks} weeks

**Validation Status:**
✅ All features technically feasible for v1.0
✅ All critical dependencies identified
✅ Scope is realistic and shippable

**Next Step:**
This specification is ready for technical architecture planning with GENESIS_BLUEPRINT.

[Download feature_spec.json]

Would you like me to explain any aspect of the specification, or shall we proceed to architecture planning?
```

---

## Success Criteria

- Valid JSON output matching data contract schema
- All phases (1-5) completed successfully
- User acknowledges and approves the specification
- Ready for handoff to GENESIS_BLUEPRINT

---

## Validation Gates

- `gate_valid_json_output.md` - Ensures JSON is parseable and matches schema
- `gate_all_phases_completed.md` - Ensures all validation phases were executed
