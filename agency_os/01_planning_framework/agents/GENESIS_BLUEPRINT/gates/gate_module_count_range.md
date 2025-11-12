# Validation Gate: Core Module Count Range

**GATE ID:** gate_module_count_range
**TRIGGER:** After task_01_select_core_modules
**SEVERITY:** WARNING (advisory, not blocking)

---

## RULE

Total core modules should be between **6-12**.

- **Minimum:** 6 (schema, entity, config, error, tracking, + 1 domain module)
- **Maximum:** 12 (all available modules)

---

## VALIDATION PROCESS

```python
def validate_module_count(core_modules):
    count = len(core_modules)

    if count < 6:
        return {
            "status": "WARNING",
            "message": f"Only {count} core modules. Project might be too simple for Genesis pattern.",
            "recommendation": "Consider if a simpler architecture would suffice."
        }

    elif count > 12:
        return {
            "status": "WARNING",
            "message": f"{count} core modules. Risk of over-engineering.",
            "recommendation": "Consider consolidating modules or splitting into microservices."
        }

    else:
        return {
            "status": "PASS",
            "message": f"{count} core modules (within optimal range 6-12)"
        }
```

---

## WARNING MESSAGES

### If < 6 modules:
```
⚠️  ADVISORY: Low Core Module Count

Core Modules: {count}
Recommended: 6-12

Your project might be too simple for the Genesis Core pattern.

**Consider:**
- Simple script architecture (no Core/Extensions split)
- Single-file implementation
- Lightweight frameworks (Flask without Genesis)

**Continue with Genesis only if:**
- Project will grow significantly
- Need strong separation of concerns
- Building production-ready system
```

### If > 12 modules:
```
⚠️  ADVISORY: High Core Module Count

Core Modules: {count}
Recommended: 6-12

Risk of over-engineering. Too many core modules adds complexity.

**Consider:**
- Consolidating similar modules (e.g., combine transform + validation)
- Splitting into multiple services (microservices)
- Re-evaluating what belongs in Core vs Extensions

**Continue with {count} modules only if:**
- Each module has clear, distinct responsibility
- Project is large-scale (e.g., enterprise application)
- Team agrees complexity is justified
```

---

## WHY THIS MATTERS

**Sweet spot: 6-12 modules**
- Enough structure to scale
- Not so much that it's overwhelming
- Clear separation of concerns
- Manageable for 1-3 developers

**Too few (<6):**
- Might not need Genesis overhead
- Could use simpler architecture

**Too many (>12):**
- Complexity increases maintenance burden
- Might indicate unclear module boundaries
- Could benefit from service decomposition
