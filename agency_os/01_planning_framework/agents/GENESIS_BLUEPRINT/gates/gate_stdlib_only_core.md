# Validation Gate: stdlib-only Core

**GATE ID:** gate_stdlib_only_core
**TRIGGER:** After task_01_select_core_modules
**SEVERITY:** CRITICAL (blocks if failed)

---

## RULE

The Core layer MUST use only Python stdlib modules. **NO external libraries allowed.**

**Exception:** `config.py` module MAY use `pyyaml` (ONLY external dep allowed in Core).

---

## VALIDATION PROCESS

1. Parse `core_modules_selection.json`
2. For each module in `core_modules[]`:
   - Check if module.name == "config":
     - If YES: Allow `pyyaml` in dependencies
     - If NO: Reject ANY non-stdlib dependency
3. For each dependency:
   - Check if dependency is in Python 3.11+ stdlib
   - If NOT in stdlib → **REJECT with error**

---

## ALLOWED STDLIB MODULES

```python
STDLIB_MODULES = {
    # Data structures
    "dataclasses", "typing", "collections", "enum",

    # File I/O
    "pathlib", "os", "csv", "json", "shutil",

    # Persistence
    "sqlite3", "pickle",

    # Text processing
    "re", "string",

    # Date/Time
    "datetime", "time",

    # Logging/Error
    "logging", "traceback", "warnings",

    # Utilities
    "functools", "itertools", "operator", "copy",

    # System
    "sys", "argparse", "configparser",

    # Math
    "math", "statistics", "random",

    # Networking (if needed)
    "http", "urllib", "socket",

    # Testing
    "unittest", "doctest"
}
```

---

## FORBIDDEN IN CORE

- ❌ requests (use urllib instead)
- ❌ flask (no web frameworks in Core)
- ❌ sqlalchemy (use sqlite3)
- ❌ pandas (use csv + dataclasses)
- ❌ numpy (use stdlib math)
- ❌ pillow (image processing belongs in Extensions)
- ❌ Any external library (except pyyaml in config.py)

---

## ERROR MESSAGE TEMPLATE

If violation detected:

```
❌ VALIDATION FAILED: stdlib-only Core Rule

Module: {module_name}
Forbidden Dependency: {dependency_name}
Reason: Core modules must use only Python stdlib

**FIX:** Move '{module_name}' to Extensions layer, OR use stdlib alternative:
  - {dependency_name} → {stdlib_alternative}

Example:
  - requests → urllib.request
  - pandas → csv + dataclasses
  - sqlalchemy → sqlite3
```

---

## EXAMPLE VALIDATION

### ✅ PASS
```json
{
  "name": "io",
  "dependencies": ["pathlib", "csv", "json"]
}
```

### ✅ PASS (config exception)
```json
{
  "name": "config",
  "dependencies": ["pathlib", "pyyaml"]
}
```

### ❌ FAIL
```json
{
  "name": "io",
  "dependencies": ["pathlib", "requests"]
}
```
**Error:** Module 'io' uses external dep 'requests' (use urllib instead)

---

## WHY THIS MATTERS

**Genesis Core Pattern:**
- Core = Business logic (stdlib only) → Stable, no dependency hell
- Extensions = Features (external libs allowed) → Flexible, isolated

**If Core uses external deps:**
- Dependency conflicts
- Upgrade nightmares
- Not portable
- Violates Genesis pattern
