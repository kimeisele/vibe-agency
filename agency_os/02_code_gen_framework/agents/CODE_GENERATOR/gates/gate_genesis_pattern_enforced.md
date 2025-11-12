# Validation Gate: Genesis Pattern Enforced

## Rule
Generated code must follow the Genesis Core Pattern (Core/Extensions separation).

---

## Validation Process

1. Check that Core modules only use stdlib (except PyYAML in config)
2. Verify Extensions never import each other
3. Validate dependency direction (Extensions → Core, never Core → Extensions)
4. Check module isolation

---

## Genesis Core Pattern Rules

### Core Layer:
- ✅ stdlib-only imports (os, sys, pathlib, json, etc.)
- ✅ PyYAML allowed ONLY in config module
- ❌ NO external dependencies
- ❌ NO imports from Extensions

### Extensions Layer:
- ✅ Can import from Core
- ✅ Can use external libraries
- ❌ NEVER import other Extensions
- ❌ NEVER imported by Core

---

## Pass Criteria

- ✅ Core modules are stdlib-only
- ✅ Extensions are isolated
- ✅ Dependency direction is correct
- ✅ No circular dependencies

---

## Failure Conditions

- ❌ Core imports external library
- ❌ Core imports Extension
- ❌ Extension imports another Extension
- ❌ Circular dependency detected

---

## Error Message Template

```
GATE FAILED: Genesis Pattern violation

Module: {module_path}
Violation: {violation_type}

Issue: {description}

Example:
  src/core/auth.py imports 'requests' (external lib in core)

Action: Move external dependencies to Extensions layer
```
