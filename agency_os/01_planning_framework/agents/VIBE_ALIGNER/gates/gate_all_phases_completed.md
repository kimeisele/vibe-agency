# Validation Gate: All Phases Completed

## Rule
All 6 phases of VIBE_ALIGNER must be completed before outputting feature_spec.json.

---

## Validation Process

Check that each phase has been completed:

1. **Phase 1:** Education & Calibration
   - Check: `metadata.user_educated = true`

2. **Phase 2:** Feature Extraction
   - Check: `features.length > 0`
   - Check: All features have input/output examples

3. **Phase 3:** Feasibility Validation (FAE)
   - Check: `validation.fae_passed = true`
   - Check: All must_have features have `fae_validation.passed = true`

4. **Phase 4:** Gap Detection (FDG)
   - Check: `validation.fdg_passed = true`
   - Check: All features have `dependencies` field

5. **Phase 5:** Scope Negotiation (APCE)
   - Check: `validation.apce_passed = true`
   - Check: `metadata.scope_negotiated = true`
   - Check: All features have `priority` and `complexity_score`

6. **Phase 6:** Output Generation
   - Check: Valid JSON
   - Check: `validation.ready_for_genesis = true`

---

## Pass Criteria

- ✅ All 6 phase checks pass
- ✅ `validation.all_features_complete = true`
- ✅ `validation.ready_for_genesis = true`

---

## Failure Conditions

- ❌ Any phase check fails
- ❌ Phase was skipped
- ❌ Validation flag is missing or false

---

## Error Message Template

```
GATE FAILED: Incomplete workflow

Not all phases of VIBE_ALIGNER were completed.

Missing phases:
{list_incomplete_phases}

Current state:
- user_educated: {value}
- fae_passed: {value}
- fdg_passed: {value}
- apce_passed: {value}
- scope_negotiated: {value}
- ready_for_genesis: {value}

Action: Complete missing phases before generating final output
```

---

## Purpose

Ensures the specification is complete and has gone through all necessary validation steps.
