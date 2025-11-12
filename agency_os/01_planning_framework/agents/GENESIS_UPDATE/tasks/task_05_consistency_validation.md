# Task 05: Consistency Validation

**TASK_ID:** task_05_consistency_validation
**PHASE:** PHASE 5
**PURPOSE:** Ensure changes don't create conflicts

---

## GOAL

Validate that the generated patches, when applied, will result in a consistent and valid architecture.

---

## VALIDATION CHECKS

### 1. No Orphaned Dependencies

```python
def check_orphaned_deps(updated_architecture):
    """
    Ensure all 'uses_core' references point to existing core modules.
    """
    core_names = {m.name for m in updated_architecture.core_modules}

    for ext in updated_architecture.extensions:
        for used in ext.uses_core:
            if used not in core_names:
                raise ValidationError(
                    f"Extension '{ext.name}' uses non-existent core module '{used}'"
                )
```

### 2. No Duplicate Extensions

```python
def check_duplicates(updated_architecture):
    """
    Ensure no two extensions have the same name.
    """
    ext_names = [e.name for e in updated_architecture.extensions]
    duplicates = [n for n in ext_names if ext_names.count(n) > 1]

    if duplicates:
        raise ValidationError(f"Duplicate extensions: {duplicates}")
```

### 3. Config Schema Matches Extensions

```python
def check_config_schema(updated_architecture):
    """
    Ensure every extension has a config section.
    """
    ext_names = {e.name for e in updated_architecture.extensions}
    config_sections = set(updated_architecture.config_system.schema.sections.keys())

    missing = ext_names - config_sections - {"global"}
    if missing:
        raise ValidationError(f"Extensions missing config sections: {missing}")
```

---

## SUCCESS CRITERIA

- ✅ No orphaned dependencies
- ✅ No duplicate extension names
- ✅ Config schema matches all extensions
- ✅ All references are valid
- ✅ Architecture remains consistent
