# Validation Gate: Complexity Within Threshold

## Rule
Total complexity must be within acceptable range for the user's chosen scope.

---

## Thresholds

- **Prototype:** 0-20 complexity points
- **MVP:** 20-40 complexity points
- **v1.0:** 40-60 complexity points

---

## Validation Process

1. Calculate `total_complexity` from all `must_have` and `should_have` features
2. Load user's `scope_choice` (prototype/MVP/v1.0)
3. Check if `total_complexity` exceeds threshold for chosen scope
4. If exceeded, verify user has either:
   - Agreed to extend timeline, OR
   - Moved features to `wont_have_v1`

---

## Pass Criteria

- ✅ `total_complexity` ≤ threshold for chosen scope
- ✅ If threshold exceeded, user has agreed to timeline extension
- ✅ Scope negotiation completed and documented

---

## Failure Conditions

- ❌ `total_complexity` > 60 points for v1.0 (without timeline extension)
- ❌ `total_complexity` > 40 points for MVP (without timeline extension)
- ❌ More than 10 `must_have` features (regardless of complexity)
- ❌ Any single feature > 13 complexity points in `must_have`

---

## Error Message Template

```
GATE FAILED: Complexity exceeds v1.0 threshold

Current complexity: {total_complexity} points
Maximum for {scope_choice}: {threshold} points
Overage: {overage} points

This scope is too large for the chosen timeline.

Options:
1. Move some features to v2.0 (reduce to {threshold} points)
2. Extend timeline to {extended_weeks} weeks
3. Replace complex features with simpler alternatives

Breakdown:
- must_have: {must_have_complexity} points
- should_have: {should_have_complexity} points
- wont_have_v1: {wont_have_complexity} points (excluded)

Action: Return to Task 05 (Scope Negotiation) and reduce complexity
```

---

## Purpose

Prevents project failure by ensuring scope is realistic and shippable.
