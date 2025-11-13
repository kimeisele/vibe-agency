# Validation Gate: FAE Validation Passed

**GATE ID:** gate_fae_validation_passed
**TRIGGER:** After task_04_validate_architecture
**SEVERITY:** CRITICAL (blocks if failed)

---

## RULE

Architecture MUST comply with all FAE (Feasibility Analysis Engine) constraints:
- **No v2.0 features** (only implement features marked v1.0)
- **No tech stack conflicts** (e.g., can't use both Vue and React)
- **All features are feasible** within stated constraints

---

## VALIDATION PROCESS

```python
def validate_fae_compliance(architecture, fae_constraints):
    """Ensure architecture complies with FAE feasibility analysis."""
    violations = []

    # Load FAE constraints
    approved_features = {f.id for f in fae_constraints.approved_features}
    tech_stack = fae_constraints.tech_stack

    # Check 1: No v2.0 features in architecture
    for extension in architecture.extensions:
        feature_id = extension.feature_id

        # Check if feature exists in FAE approved list
        if feature_id not in approved_features:
            violations.append({
                "type": "UNAPPROVED_FEATURE",
                "extension": extension.name,
                "feature_id": feature_id,
                "error": f"Extension '{extension.name}' implements feature '{feature_id}' which was not approved by FAE"
            })

    # Check 2: No tech stack conflicts
    used_tech = set()
    for extension in architecture.extensions:
        for dep in extension.external_deps:
            used_tech.add(dep.package_name)

    conflicts = find_tech_conflicts(used_tech, tech_stack.allowed, tech_stack.forbidden)
    for conflict in conflicts:
        violations.append({
            "type": "TECH_CONFLICT",
            "package": conflict.package,
            "reason": conflict.reason,
            "error": f"Technology '{conflict.package}' conflicts with constraints: {conflict.reason}"
        })

    # Check 3: Complexity within bounds
    total_complexity = sum(ext.complexity_score for ext in architecture.extensions)
    if total_complexity > fae_constraints.max_complexity:
        violations.append({
            "type": "COMPLEXITY_EXCEEDED",
            "total": total_complexity,
            "max": fae_constraints.max_complexity,
            "error": f"Total complexity {total_complexity} exceeds FAE limit of {fae_constraints.max_complexity}"
        })

    return violations
```

---

## ERROR MESSAGE TEMPLATE

### Unapproved Feature

```
❌ VALIDATION FAILED: FAE Compliance

Type: UNAPPROVED_FEATURE
Extension: {extension_name}
Feature ID: {feature_id}

This extension implements a feature that was NOT approved in the FAE analysis.
Only v1.0 features should be implemented.

**FIX:**
1. Check feature_spec.json - is this feature marked v2.0?
2. If yes: Remove this extension (v2.0 features are out of scope)
3. If no: Update FAE constraints to include this feature

Example:
  Feature F007 (AI Recommendations) marked as v2.0
  → Remove "ai_recommender" extension
  → Defer to future release
```

### Tech Stack Conflict

```
❌ VALIDATION FAILED: FAE Compliance

Type: TECH_CONFLICT
Package: {package_name}
Reason: {conflict_reason}

This technology conflicts with the approved tech stack.

**FIX:**
1. Check FAE constraints for allowed technologies
2. Replace conflicting package with approved alternative

Example:
  Conflict: Using "moment.js" but FAE specifies "date-fns"
  → Replace moment.js with date-fns

  Conflict: Using both "React" and "Vue"
  → Choose ONE framework (as specified in FAE)
```

### Complexity Exceeded

```
❌ VALIDATION FAILED: FAE Compliance

Type: COMPLEXITY_EXCEEDED
Total Complexity: {total_complexity}
Max Allowed: {max_complexity}

The architecture exceeds the complexity budget approved by FAE.

**FIX:**
1. Remove optional features (priority = LOW or MEDIUM)
2. Simplify complex extensions
3. Defer features to v2.0

Example:
  Total: 150 complexity points
  Max: 120 points
  → Remove 30 points worth of features
  → Consider removing: "advanced_analytics" (complexity: 35)
```

---

## EXAMPLE VALIDATION

### ✅ PASS

```json
{
  "fae_constraints": {
    "approved_features": ["F001", "F002", "F003"],
    "tech_stack": {
      "framework": "React",
      "backend": "Node.js",
      "database": "PostgreSQL"
    },
    "max_complexity": 100
  },

  "architecture": {
    "extensions": [
      {
        "name": "user_registration",
        "feature_id": "F001",
        "complexity_score": 15,
        "external_deps": [
          {"package_name": "react", "version": "^18.0.0"}
        ]
      },
      {
        "name": "user_login",
        "feature_id": "F002",
        "complexity_score": 12,
        "external_deps": [
          {"package_name": "jsonwebtoken", "version": "^9.0.0"}
        ]
      }
    ]
  }
}
```
**Result:** All features approved, tech stack compatible, complexity within bounds.

### ❌ FAIL - Unapproved Feature

```json
{
  "fae_constraints": {
    "approved_features": ["F001", "F002"],  // Only v1.0 features
    "v2_features": ["F999"]
  },

  "architecture": {
    "extensions": [
      {
        "name": "ai_chatbot",
        "feature_id": "F999",  // v2.0 feature!
        "complexity_score": 50
      }
    ]
  }
}
```
**Error:** Feature F999 marked as v2.0, should not be in architecture.
**Fix:** Remove "ai_chatbot" extension, defer to v2.0.

### ❌ FAIL - Tech Stack Conflict

```json
{
  "fae_constraints": {
    "tech_stack": {
      "framework": "React",
      "forbidden": ["vue", "angular"]
    }
  },

  "architecture": {
    "extensions": [
      {
        "name": "user_dashboard",
        "external_deps": [
          {"package_name": "vue", "version": "^3.0.0"}  // Forbidden!
        ]
      }
    ]
  }
}
```
**Error:** Using Vue, but FAE specified React.
**Fix:** Rewrite dashboard using React.

### ❌ FAIL - Complexity Exceeded

```json
{
  "fae_constraints": {
    "max_complexity": 100
  },

  "architecture": {
    "extensions": [
      {"name": "ext1", "complexity_score": 40},
      {"name": "ext2", "complexity_score": 35},
      {"name": "ext3", "complexity_score": 30},
      {"name": "ext4", "complexity_score": 20}
    ]
  }
}
```
**Total:** 125 (exceeds 100)
**Fix:** Remove ext4 (20 points) or simplify ext1.

---

## WHY THIS MATTERS

**FAE validation ensures:**
- **Scope control**: Only v1.0 features are implemented
- **Tech consistency**: No conflicting dependencies
- **Feasibility**: Architecture stays within approved constraints
- **Client expectations**: Don't promise features that aren't approved

**If you skip FAE validation:**
- Risk implementing v2.0 features (scope creep)
- Tech stack conflicts (incompatible libraries)
- Complexity explosion (over budget)
- Undeliverable promises

---

## SPECIAL CASES

### Optional Features

Features marked as "optional" in FAE can be included/excluded based on complexity:

```json
{
  "fae_constraints": {
    "approved_features": ["F001", "F002"],
    "optional_features": ["F003"],
    "max_complexity": 100
  }
}
```

**Rule:** Include F003 ONLY if total complexity stays under 100.

### Tech Stack Alternatives

FAE may specify alternatives:

```json
{
  "tech_stack": {
    "orm": ["prisma", "typeorm"]  // Either is OK
  }
}
```

**Rule:** Choose ONE from the list, not both.

---

## CHECKLIST

Before passing this gate, verify:

- [ ] All features in architecture exist in FAE approved list
- [ ] No v2.0 features included
- [ ] Tech stack matches FAE specifications
- [ ] No forbidden technologies used
- [ ] Total complexity ≤ max_complexity
- [ ] All external dependencies justified
- [ ] If violations found: clear error message provided
