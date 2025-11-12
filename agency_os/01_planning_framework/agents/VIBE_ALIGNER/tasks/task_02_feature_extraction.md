# Task: Feature Extraction

## Objective
Extract concrete, testable feature descriptions from vague user requirements using smart questioning and inference rules.

---

## Goal
Get concrete, testable feature descriptions with clear input/output specifications.

---

## Input Artifacts
- Session state from Task 01:
  - `user_scope_choice` (prototype|mvp|v1.0)
  - `core_problem_statement`
  - `target_users`

---

## Extraction Template

For EACH feature the user mentions, extract:

```json
{
  "id": "feature_X",
  "name": "Human-readable name",
  "description": "1-2 sentence description",
  "input": {
    "format": "CSV|JSON|CLI args|API request|Manual form|...",
    "example": "Concrete example of valid input",
    "constraints": "Size limits, required fields, validation rules"
  },
  "processing": {
    "description": "What happens to the input (1-2 sentences)",
    "external_dependencies": ["Library names if known"],
    "side_effects": ["Database writes", "API calls", "File system changes"]
  },
  "output": {
    "format": "Files|Database records|API responses|stdout|...",
    "example": "Concrete example of expected output",
    "success_criteria": "How do you know it worked?"
  }
}
```

---

## Smart Questioning Rules

**ASK ONLY when genuinely ambiguous:**

### Type A: Mutually Exclusive Choices
```
Example: "generate reports"
→ MUST ASK: "Output format? PDF only, Excel only, or both?"
  (Cannot infer from context)
```

### Type B: Data Direction (for sync/bidirectional flows)
```
Example: "sync data between A and B"
→ MUST ASK: "Which is source of truth? A, B, or bidirectional?"
  (Business logic needed)
```

### Type C: Multiple Valid Interpretations
```
Example: "automation tool" (no mention of batch/CLI/trigger)
→ MIGHT ASK: "Trigger mechanism? Manual CLI, cron job, or event-driven?"
  (Only if NO other keywords clarify this)
```

---

## MANDATORY INFERENCE RULES

**DO NOT ASK if keyword is present:**

| User Keyword | AUTO-INFER | NEVER ASK |
|--------------|-----------|-----------|
| "batch processing" | Input = CSV/JSON files | ❌ "What is input source?" |
| "production-ready" | Config = YAML files | ❌ "Should it be configurable?" |
| "CLI tool" | Interface = command-line | ❌ "Need web UI?" |
| "automation" | Trigger = manual/cron | ❌ "Interactive prompts?" |
| "v1.0" or "MVP" | Scope = simple only | ❌ "Complex workflows?" |
| "orchestration" + "v1.0" | Workflow = sequential | ❌ "Need dependency graphs?" |
| "generate X" | Create from scratch | ❌ "Format existing content?" |

---

## NEVER ASK:
- ❌ "Should it handle errors?" (Always YES)
- ❌ "Should it be configurable?" (If "production", YES)
- ❌ "Should it log output?" (Always YES)
- ❌ "Should it be tested?" (Always YES)

---

## Output

A list of extracted features in JSON format:

```json
{
  "extracted_features": [
    {
      "id": "feature_1",
      "name": "...",
      "description": "...",
      "input": {...},
      "processing": {...},
      "output": {...}
    }
  ]
}
```

---

## Success Criteria

- All user-mentioned features are extracted
- Each feature has concrete input/output examples
- No unnecessary questions were asked (inference rules applied)
- Features are specific enough to validate against FAE

---

## Validation Gates

- `gate_concrete_specifications.md` - Ensures all features have concrete I/O examples
