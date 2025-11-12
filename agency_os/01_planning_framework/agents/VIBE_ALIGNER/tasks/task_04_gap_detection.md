# Task: Gap Detection (FDG)

## Objective
Proactively identify missing dependencies that the user forgot to mention but are required for their features to work.

---

## Goal
Ensure feature specifications are complete by detecting and suggesting missing dependencies using the Feature Dependency Graph (FDG).

---

## Input Artifacts
- `validated_features.json` (from Task 03)
- `FDG_dependencies.yaml` (from knowledge base)

---

## Gap Detection Process

For EACH feature in `validated_features.json`, traverse `FDG_dependencies.yaml`:

```python
# Pseudo-code for FDG gap detection
for feature in validated_features:
    # Find feature in FDG
    fdg_entry = FDG.find(feature.name)

    if fdg_entry:
        required_deps = fdg_entry.required_dependencies
        mentioned_features = set(validated_features.names)

        # Find missing dependencies
        missing = []
        for dep in required_deps:
            if dep.component not in mentioned_features:
                missing.append(dep)

        if missing:
            suggest_missing_dependencies(feature, missing)
```

---

## Gap Suggestion Dialog Template

**GOOD (Proactive & Expert):**
```
✅ COMPLETENESS CHECK: {feature_name}

I've analyzed "{feature_name}" and identified the core components needed to make it work.

To implement this feature, you'll need:
- {component_1} ({reason})
- {component_2} ({reason})
- {component_3} ({reason})

I've automatically included these in the architecture plan. Does this match your expectations?
```

**BAD (Avoid this - too many questions):**
```
❌ Do you need {component_1}?
❌ Do you need {component_2}?
❌ Do you need {component_3}?
```

---

## Example Gap Detection

**User says: "Social media scheduler"**

```
✅ COMPLETENESS CHECK: Social media scheduler

I've analyzed "social media scheduler" and identified the core components needed to make it work.

To implement this feature, you'll need:
- **Post database** (to store scheduled posts with content and metadata)
- **Scheduling service** (cron job or task queue to trigger publishing at scheduled times)
- **Social API credentials store** (secure storage for OAuth tokens)
- **Social API integration** (to actually publish to Twitter/LinkedIn/Facebook)
- **Job queue system** (to reliably process publishing jobs under load)

I've automatically included these in the architecture plan. Does this match your expectations?
```

---

## Output

Updated feature list with dependency information:

```json
{
  "features_with_dependencies": [
    {
      "id": "feature_1",
      "name": "Social media scheduler",
      "dependencies": {
        "required": [
          {
            "component": "post_database",
            "reason": "Store scheduled posts with metadata",
            "source": "FDG-042"
          },
          {
            "component": "scheduling_service",
            "reason": "Trigger publishing at scheduled times",
            "source": "FDG-042"
          },
          {
            "component": "social_api_integration",
            "reason": "Publish to social platforms",
            "source": "FDG-042"
          }
        ],
        "optional": []
      }
    }
  ]
}
```

---

## Success Criteria

- All features checked against FDG
- Missing dependencies identified and suggested
- User confirms dependency completeness
- All critical dependencies are now part of the feature list

---

## Validation Gates

- `gate_no_missing_dependencies.md` - Ensures all critical dependencies are included
