# TODO: Update Test Fixtures for v2.5 Specialist Validation

**Priority:** Medium
**Created:** 2025-11-20
**Context:** MAIDEN_VOYAGE verification complete, specialists have stricter validation

## Background

The v2.5 specialists (CodingSpecialist, DeploymentSpecialist) now have **improved precondition validation**. This is correct behavior - they properly validate inputs before execution.

However, 5 smoke tests fail because they don't provide required artifacts:

## Failing Tests

### 1. `tests/test_coding_workflow.py::test_coding_phase_execution`
- **Issue:** CodingSpecialist requires `feature_spec.json` from PLANNING phase
- **Error:** `Precondition failed: feature_spec.json could not be loaded`
- **Fix:** Add `feature_spec.json` to test workspace artifacts

### 2. `tests/test_coding_workflow.py::test_missing_feature_spec`
- **Issue:** Same as #1
- **Fix:** Same as #1

### 3. `tests/test_coding_workflow.py::test_quality_gates_failure`
- **Issue:** Same as #1
- **Fix:** Same as #1

### 4. `tests/test_deployment_workflow.py::test_missing_qa_report`
- **Issue:** DeploymentSpecialist requires `qa_report.json` with `status: APPROVED`
- **Error:** `Precondition failed: QA status is 'REJECTED', expected 'APPROVED'`
- **Fix:** Update test to provide proper `qa_report.json`

### 5. `tests/test_deployment_workflow.py::test_qa_not_approved`
- **Issue:** Same as #4 (this test is actually testing the rejection case, may need different approach)
- **Fix:** Use proper test setup for rejection scenario

## Required Changes

### For CODING Tests

Create `feature_spec.json` in test workspace:

```json
{
  "version": "1.0",
  "features": [
    {
      "id": "F001",
      "name": "Test Feature",
      "description": "Feature for testing CODING phase"
    }
  ],
  "acceptance_criteria": ["AC1", "AC2"],
  "technical_constraints": []
}
```

Location: `.vibe/artifacts/feature_spec.json` in test workspace

### For DEPLOYMENT Tests

1. **test_missing_qa_report**: Verify test is checking for missing artifact (should still work)
2. **test_qa_not_approved**: This test specifically checks rejection path - may need to:
   - Mark as `@pytest.mark.xfail` with reason
   - OR update specialist to allow testing rejection scenarios

## Implementation Steps

1. **Audit all workflow tests:**
   ```bash
   uv run pytest tests/test_*_workflow.py -v
   ```

2. **Create artifact fixtures:**
   - `tests/fixtures/artifacts/feature_spec.json`
   - `tests/fixtures/artifacts/qa_report_approved.json`
   - `tests/fixtures/artifacts/qa_report_rejected.json`

3. **Update test setup functions:**
   - Modify `conftest.py` or individual test setup
   - Copy fixtures to workspace `.vibe/artifacts/` during test setup

4. **Run tests again:**
   ```bash
   uv run pytest tests/test_*_workflow.py -v
   ```

5. **Update pre-push check:**
   - Verify all smoke tests pass
   - Push changes

## Why This Wasn't Done During MAIDEN_VOYAGE

- **Primary goal:** Verify v2.5 architecture works (✅ ACHIEVED)
- **Scope:** Architecture verification, not test maintenance
- **Evidence:** Specialists are working correctly - they're SUPPOSED to reject invalid inputs
- **Priority:** Documenting the architecture victory > fixing test fixtures

## References

- **MAIDEN_VOYAGE_REPORT.md** - Full verification details
- **Agency OS v2.5 Architecture** - HAP, SQLite, Registry verified
- **Specialist Preconditions:**
  - `agency_os/03_agents/specialists/coding.py:100-125`
  - `agency_os/03_agents/specialists/deployment.py:90-115`

---

**Status:** 📋 DOCUMENTED - Ready for implementation
**Estimated Time:** 30-45 minutes
**Complexity:** Low (straightforward fixture creation)
