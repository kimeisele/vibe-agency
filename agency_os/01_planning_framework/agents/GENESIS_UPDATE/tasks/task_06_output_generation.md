# Task 06: Output Generation

**TASK_ID:** task_06_output_generation
**PHASE:** PHASE 6
**PURPOSE:** Generate the final update_spec.json artifact

---

## GOAL

Compile all analysis, validation, and patches into a single, comprehensive update specification document.

---

## OUTPUT FORMAT: update_spec.json

```json
{
  "update": {
    "type": "ADD_FEATURE",
    "description": "Add commenting to blog posts",
    "requested_by": "user",
    "timestamp": "2025-01-15T14:30:00Z"
  },

  "analysis": {
    "primary_change": "Create comments extension",
    "ripple_effects": [
      "Add Comment model to storage",
      "Add comments config section",
      "Add comments tests"
    ],
    "affected_components": ["storage", "config", "tests"]
  },

  "validation": {
    "fae_passed": true,
    "fdg_checked": true,
    "tech_compatible": true,
    "consistency_passed": true
  },

  "diff_patches": [
    {
      "file": "architecture.json",
      "patch": "--- a/architecture.json\n+++ b/architecture.json\n...",
      "explanation": "Added 'comments' extension to extensions list"
    },
    {
      "file": "config/_schema.yaml",
      "patch": "--- a/config/_schema.yaml\n+++ b/config/_schema.yaml\n...",
      "explanation": "Added 'comments' configuration section"
    },
    {
      "file": "core/storage.py",
      "patch": "--- a/core/storage.py\n+++ b/core/storage.py\n...",
      "explanation": "Added Comment model support to storage module"
    }
  ],

  "updated_architecture": {
    // Full updated architecture.json
    // (This is the result of applying all diffs)
  },

  "implementation_notes": {
    "new_files_to_create": [
      "extensions/comments.py",
      "tests/extensions/test_comments.py"
    ],
    "files_to_modify": [
      "core/storage.py (add Comment model)",
      "config/_schema.yaml (add comments section)",
      "config/config.yaml (add comments defaults)"
    ],
    "estimated_effort": "2-3 days",
    "complexity_added": "+3 points"
  },

  "metadata": {
    "genesis_update_version": "2.0",
    "original_architecture_version": "6.0",
    "change_count": 3
  }
}
```

---

## USAGE INSTRUCTIONS

1. Load existing architecture.json
2. Load FAE_constraints.yaml, FDG_dependencies.yaml
3. Receive change request from user
4. Analyze change type and ripple effects
5. Validate feasibility and consistency
6. Generate diff patches
7. Output update_spec.json
8. User applies patches to codebase

---

## SUCCESS CRITERIA

- ✅ Output is valid JSON
- ✅ All sections present and complete
- ✅ Diff patches are included
- ✅ Implementation notes are actionable
- ✅ Metadata is accurate
