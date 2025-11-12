# Validation Gate: Education Completed

## Rule
User must complete the education phase and choose a scope goal BEFORE feature extraction begins.

---

## Validation Process

1. Check session state for `user_educated` flag
2. Verify `user_scope_choice` is set to one of: `prototype`, `mvp`, or `v1.0`
3. Verify `core_problem_statement` is present

---

## Pass Criteria

- ✅ `user_educated = true`
- ✅ `user_scope_choice` ∈ {`prototype`, `mvp`, `v1.0`}
- ✅ `core_problem_statement` is not empty

---

## Failure Conditions

- ❌ User was not presented with scope options
- ❌ User did not explicitly choose a scope
- ❌ User did not articulate core problem

---

## Error Message Template

```
GATE FAILED: Education phase incomplete

The user must complete the education phase before feature extraction.

Required:
- User must choose scope goal (prototype/MVP/v1.0)
- User must receive education about chosen scope
- User must articulate core problem statement

Current state:
- user_educated: {current_value}
- user_scope_choice: {current_value}
- core_problem_statement: {current_value}

Action: Return to Task 01 (Education & Calibration)
```

---

## Purpose

Prevents scope creep by ensuring users understand scope boundaries before listing features.
