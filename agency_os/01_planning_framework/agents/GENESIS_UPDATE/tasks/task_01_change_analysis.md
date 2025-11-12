# Task 01: Change Analysis

**TASK_ID:** task_01_change_analysis
**PHASE:** PHASE 1
**PURPOSE:** Understand what user wants and categorize the change

---

## GOAL

Analyze the user's change request and categorize it according to its impact on the existing architecture.

---

## CHANGE CATEGORIES

### 1. ADD_FEATURE
```
User wants: New functionality
Example: "Add comments to blog posts"
Impact: New extension, possibly new core modules, new dependencies
```

### 2. MODIFY_FEATURE
```
User wants: Change existing functionality
Example: "Change image format from PNG to JPEG"
Impact: Config changes, possibly extension logic changes
```

### 3. REMOVE_FEATURE
```
User wants: Delete functionality
Example: "Remove email notifications"
Impact: Remove extension, remove dependencies, clean up config
```

### 4. REFACTOR
```
User wants: Improve structure without changing functionality
Example: "Split the user_auth extension into separate login/register extensions"
Impact: Code reorganization, no functional changes
```

### 5. TECH_STACK_CHANGE
```
User wants: Replace technology
Example: "Switch from SQLite to PostgreSQL"
Impact: MAJOR - affects all extensions using storage
```

---

## ANALYSIS TEMPLATE

Output your analysis in this JSON format:

```json
{
  "change_type": "ADD_FEATURE|MODIFY_FEATURE|REMOVE_FEATURE|REFACTOR|TECH_STACK_CHANGE",
  "description": "User's request in their own words",
  "affected_components": [
    "extension_name",
    "core_module_name",
    "config_section"
  ],
  "ripple_effects": [
    {
      "component": "database_schema",
      "change": "Add 'comments' table"
    },
    {
      "component": "api_endpoints",
      "change": "Add POST /comments, GET /comments/:post_id"
    }
  ]
}
```

---

## SUCCESS CRITERIA

- ✅ Change type correctly identified
- ✅ All affected components listed
- ✅ Initial ripple effects identified
- ✅ User's intent clearly captured
