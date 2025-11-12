# Validation Gate: All Code Documented

## Rule
All functions, classes, and modules must have docstrings.

---

## Validation Process

For EACH code file:
1. Check module-level docstring exists
2. Verify all public functions have docstrings
3. Check all classes have docstrings
4. Validate docstrings are complete (params, returns, raises)

---

## Docstring Requirements

### Module Docstring:
```python
"""
Module description.

This module provides...
"""
```

### Function Docstring:
```python
def function(param1: str, param2: int) -> bool:
    """
    Short description.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description

    Raises:
        ValueError: When...
    """
```

---

## Pass Criteria

- ✅ All modules have docstrings
- ✅ All public functions documented
- ✅ All classes documented
- ✅ Docstrings are complete

---

## Failure Conditions

- ❌ Missing module docstring
- ❌ Function without docstring
- ❌ Incomplete docstring (missing params/returns)

---

## Error Message Template

```
GATE FAILED: Undocumented code

File: {file_path}

Undocumented items:
- Function: {function_name} (no docstring)
- Class: {class_name} (no docstring)

Action: Add docstrings to all public APIs
```
