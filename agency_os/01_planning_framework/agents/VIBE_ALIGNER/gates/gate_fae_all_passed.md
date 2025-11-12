# Validation Gate: FAE All Passed

## Rule
All "must_have" features must pass FAE (Feasibility Analysis Engine) validation.

---

## Validation Process

For EACH feature with `priority = "must_have"`:

1. Check that `fae_validation.passed = true`
2. Check that `fae_validation.issues` is empty
3. If any feature has `passed = false`, it must be either:
   - Changed to `priority = "wont_have_v1"`, OR
   - Replaced with a feasible alternative

---

## Pass Criteria

- ✅ All `must_have` features have `fae_validation.passed = true`
- ✅ All `must_have` features have `fae_validation.issues = []`
- ✅ Any infeasible features are marked `wont_have_v1` or replaced

---

## Failure Conditions

- ❌ A `must_have` feature has `fae_validation.passed = false`
- ❌ A `must_have` feature has blocking issues in `fae_validation.issues`
- ❌ User insists on keeping an infeasible feature without extending timeline

---

## Error Message Template

```
GATE FAILED: Infeasible must-have feature detected

Feature "{feature_name}" (priority: must_have) failed FAE validation.

FAE Issues:
{list_issues_from_fae_validation}

This feature is incompatible with the current scope and timeline.

Options:
1. Replace with feasible alternative (recommended)
2. Move to v2.0 (change priority to wont_have_v1)
3. Extend timeline to accommodate complexity

Action: Return to Task 03 (Feasibility Validation) and resolve
```

---

## Purpose

Prevents unrealistic expectations by blocking infeasible features from proceeding.
