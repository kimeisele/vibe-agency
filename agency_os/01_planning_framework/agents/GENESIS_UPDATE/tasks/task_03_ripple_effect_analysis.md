# Task 03: Ripple Effect Analysis

**TASK_ID:** task_03_ripple_effect_analysis
**PHASE:** PHASE 3
**PURPOSE:** Identify ALL components that must change

---

## GOAL

Analyze the full impact of the requested change across the entire architecture, identifying all components that must be modified.

---

## RIPPLE EFFECT CATEGORIES

### 1. Database Schema Changes
```
Trigger: New feature needs persistence
Ripple:
  - Add new table(s)
  - Add foreign keys
  - Update migration scripts
```

### 2. API Changes
```
Trigger: New feature exposes endpoints
Ripple:
  - Add new routes
  - Update API documentation
  - Add authentication checks
```

### 3. Config Changes
```
Trigger: New feature needs configuration
Ripple:
  - Update config/_schema.yaml
  - Update config/config.yaml
  - Update config/config.example.yaml
```

### 4. Core Module Changes
```
Trigger: New extension needs core functionality not yet present
Ripple:
  - Add new core module OR
  - Extend existing core module API
```

### 5. Test Changes
```
Trigger: ANY code change
Ripple:
  - Add new test files
  - Update existing tests
```

---

## RIPPLE ANALYSIS TEMPLATE

```json
{
  "primary_change": {
    "component": "extensions/comments.py",
    "action": "CREATE",
    "reason": "New feature: comments on blog posts"
  },
  "ripple_effects": [
    {
      "component": "core/storage.py",
      "action": "MODIFY",
      "change": "Add Comment model support",
      "reason": "Comments need persistence"
    },
    {
      "component": "config/_schema.yaml",
      "action": "MODIFY",
      "change": "Add 'comments' section",
      "reason": "Comments need configuration (max_length, moderation, etc.)"
    },
    {
      "component": "tests/extensions/test_comments.py",
      "action": "CREATE",
      "reason": "New extension requires tests"
    }
  ]
}
```

---

## SUCCESS CRITERIA

- ✅ All affected components identified
- ✅ Database schema changes mapped
- ✅ API changes documented
- ✅ Config changes specified
- ✅ Core module impacts analyzed
- ✅ Test requirements defined
