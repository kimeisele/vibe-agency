# Gate: No Orphaned Dependencies

**GATE_ID:** gate_no_orphaned_deps
**SEVERITY:** CRITICAL
**PURPOSE:** Ensure all dependencies reference existing components

---

## VALIDATION RULE

**CRITICAL:** All dependency references must point to existing components.

### What This Gate Checks:

1. **Core Module References:** Every `uses_core` reference must exist in `core_modules`
2. **Extension References:** Every `uses_extension` reference must exist in `extensions`
3. **Config References:** Every config section must have a corresponding component
4. **External Deps:** All `external_deps` must be in `requirements.txt`

---

## VALIDATION LOGIC

```python
def validate_no_orphaned_deps(updated_architecture):
    """
    Check for orphaned dependencies after applying patches.
    """
    errors = []

    # Get all valid core module names
    core_names = {m.name for m in updated_architecture.core_modules}

    # Check each extension's dependencies
    for ext in updated_architecture.extensions:
        for used_core in ext.uses_core:
            if used_core not in core_names:
                errors.append(
                    f"Extension '{ext.name}' references non-existent core module '{used_core}'"
                )

    return errors
```

---

## PASS CRITERIA

✅ All `uses_core` references exist
✅ All `uses_extension` references exist
✅ All config sections map to components
✅ All external deps are declared

---

## FAIL CRITERIA

❌ References to non-existent modules
❌ Broken dependency chains
❌ Missing config sections
❌ Undeclared external dependencies

---

## WHY THIS MATTERS

Orphaned dependencies cause:
- **Runtime Errors:** Code tries to import non-existent modules
- **Build Failures:** Missing dependencies break compilation
- **Inconsistent State:** Architecture document doesn't match reality
- **Technical Debt:** Cleanup becomes harder over time
