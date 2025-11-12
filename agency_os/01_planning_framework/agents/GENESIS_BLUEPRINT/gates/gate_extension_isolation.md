# Validation Gate: Extension Isolation

**GATE ID:** gate_extension_isolation
**TRIGGER:** After task_02_design_extensions
**SEVERITY:** CRITICAL (blocks if failed)

---

## RULE

Extensions MUST NOT import other extensions. **Zero cross-extension dependencies allowed.**

---

## VALIDATION PROCESS

```python
def validate_extension_isolation(extensions):
    """Ensure no extension imports another extension."""
    violations = []
    ext_names = {e.name for e in extensions}

    for ext in extensions:
        # Check if uses_core contains extension names
        for used in ext.uses_core:
            if used in ext_names:
                violations.append({
                    "extension": ext.name,
                    "imports": used,
                    "error": f"Extension '{ext.name}' imports extension '{used}'"
                })

    return violations
```

---

## ERROR MESSAGE TEMPLATE

If violation detected:

```
❌ VALIDATION FAILED: Extension Isolation Rule

Extension: {ext_name}
Illegal Import: {imported_extension}

Extensions MUST NOT import each other. They should only import Core modules.

**FIX:** Move shared logic from '{imported_extension}' to a Core module.

Example:
  If Extension A and Extension B both need email validation:
  - BAD: Extension A imports Extension B
  - GOOD: Create core/validation.py with email_is_valid(), both import that
```

---

## EXAMPLE VALIDATION

### ✅ PASS
```json
{
  "extensions": [
    {
      "name": "user_registration",
      "uses_core": ["validation", "storage", "error"]
    },
    {
      "name": "user_login",
      "uses_core": ["validation", "storage", "error"]
    }
  ]
}
```
Both extensions use Core modules. No cross-extension imports.

### ❌ FAIL
```json
{
  "extensions": [
    {
      "name": "user_login",
      "uses_core": ["validation", "storage", "user_registration"]
    }
  ]
}
```
**Error:** Extension 'user_login' imports extension 'user_registration'

**Fix:** Move shared user logic to core/entity.py (User entity)

---

## WHY THIS MATTERS

**Extension isolation ensures:**
- Features are independent (can enable/disable individually)
- Testing is easy (no complex dependency chains)
- Changes to Extension A don't break Extension B
- Clean architecture (unidirectional dependencies)

**If extensions import each other:**
- Creates tight coupling
- Can't disable features independently
- Hard to test
- Violates Genesis pattern
