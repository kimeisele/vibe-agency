# Validation Gate: Test Coverage Adequate

## Rule
All generated code must have adequate test coverage.

---

## Coverage Targets

- **Core modules:** 100% coverage target
- **Extension modules:** 90% coverage target
- **Integration tests:** All API endpoints covered

---

## Validation Process

For EACH code module:
1. Check that test file exists
2. Verify test coverage meets target
3. Check edge cases covered
4. Validate integration tests present (for APIs)

---

## Pass Criteria

- ✅ Every code module has test file
- ✅ Core modules: 100% coverage
- ✅ Extensions: 90% coverage
- ✅ All API endpoints have integration tests

---

## Failure Conditions

- ❌ Code module without tests
- ❌ Coverage below target
- ❌ API endpoint without integration test

---

## Error Message Template

```
GATE FAILED: Insufficient test coverage

Module: {module_path}
Coverage: {actual_coverage}%
Target: {target_coverage}%
Gap: {gap}%

Missing tests for:
- {untested_function_1}
- {untested_function_2}

Action: Generate tests for uncovered code
```
