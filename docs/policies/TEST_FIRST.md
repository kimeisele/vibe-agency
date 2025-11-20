# Test-First Development Policy

**Status:** ✅ ACTIVE (Effective 2025-11-17)
**Authority:** HIL Decision (Option B)
**Trigger:** Test Debt Pattern Identified (GAD-100/GAD-500)

---

## Purpose

This policy prevents **test debt accumulation** by mandating that tests are written BEFORE or IMMEDIATELY WITH implementation code.

**Problem Pattern (Identified 2025-11-17):**
1. Agent writes code
2. Code works
3. Merge to main
4. Tests break later (imports, references, etc.)
5. New agent fixes retroactively
6. Risk of regressions increases

**Examples Found:**
- `test_phoenix_config.py`: Import path broken after GAD-100 Phase 1 vendoring
- `test_motd.py`: File reference broken (show-context.sh → .py)

---

## Core Rules

### Rule 1: Tests BEFORE or WITH Code

**MANDATORY:**
- Tests must be written BEFORE implementation (TDD preferred)
- OR: Tests written IMMEDIATELY AFTER (max 1 commit later)
- NO "fix tests later" or "tests TODO"

**Why:** Tests define behavior. Code implements behavior. Not vice versa.

---

### Rule 2: Test Migration is MANDATORY

**When code changes, tests MUST change:**

| Code Change Type | Test Requirement |
|------------------|------------------|
| New feature | Write new tests |
| Refactor | Update existing tests |
| Bug fix | Add regression test |
| Migration (vendoring, renaming) | Update import/reference paths |
| API change | Update integration tests |

**No Exceptions.** Test migration is NOT optional.

---

### Rule 3: Tests Block Merge

**Hard Stop Conditions:**
- ❌ Broken tests → NO MERGE
- ❌ Failing tests → NO MERGE
- ❌ Import errors → NO MERGE
- ❌ Test collection failures → NO MERGE

**Agents CANNOT:**
- Say "tests will be fixed in next PR"
- Merge with `# TODO: fix tests`
- Skip broken tests with `pytest.skip()`

**Tests are part of the deliverable, not optional documentation.**

---

### Rule 4: Coverage Thresholds

**Minimum Coverage:**
- New code: **80% coverage minimum**
- Bug fixes: **100% coverage** (regression test required)
- Critical paths (orchestrator, kernel): **90% coverage**

**Verification:**
```bash
# Check coverage
uv run pytest --cov=module_name --cov-report=term-missing

# Fail if below threshold
uv run pytest --cov=module_name --cov-fail-under=80
```

---

## Implementation Checklist

### For New Features

```markdown
- [ ] Write failing tests FIRST (defines expected behavior)
- [ ] Implement code until tests pass
- [ ] Add edge case tests (error handling, boundary conditions)
- [ ] Run full test suite: `uv run pytest tests/`
- [ ] Check coverage: `uv run pytest --cov=new_module`
- [ ] Verify >80% coverage on new code
- [ ] Commit code + tests TOGETHER
```

### For Migrations/Refactors

```markdown
- [ ] List all files being changed
- [ ] Identify all tests importing/referencing those files
- [ ] Update test imports BEFORE migrating code
- [ ] Run tests AFTER each migration step
- [ ] Verify zero test regressions
- [ ] Document what was migrated in commit message
```

### For Bug Fixes

```markdown
- [ ] Write failing test that reproduces bug
- [ ] Verify test fails with current code
- [ ] Fix bug
- [ ] Verify test now passes
- [ ] Run full test suite (check for regressions)
- [ ] Commit fix + test TOGETHER
```

---

## Test Debt Audit Process

**When to run:**
- Before starting new GAD implementation
- After major refactors
- Monthly (scheduled check)

**How to run:**
```bash
# Full test suite
uv run pytest tests/ -v --tb=short

# Check for import errors
uv run pytest tests/ --collect-only

# Coverage report
uv run pytest --cov=agency_os --cov-report=html
open htmlcov/index.html
```

**Document findings:**
- Create `docs/audits/test_debt_YYYY-MM-DD.md`
- List: broken tests, missing tests, low coverage areas
- Prioritize: critical (blocks work) vs nice-to-have
- Fix critical immediately, schedule rest

---

## Enforcement

### Pre-Push Checks (Automated)

Already enforced by `./bin/pre-push-check.sh`:
- ✅ Linting
- ✅ Formatting
- ⏸️ **TODO:** Add test verification

**Proposed addition to pre-push-check.sh:**
```bash
echo "3️⃣  Running tests..."
uv run pytest tests/ -x -q
if [ $? -ne 0 ]; then
    echo "   ❌ TESTS FAILED"
    echo ""
    echo "   Fix tests before pushing:"
    echo "     uv run pytest tests/ -v"
    exit 1
fi
echo "   ✅ Tests passed"
```

### CI/CD Validation (Already Active)

`.github/workflows/validate.yml` runs:
- Linting (ruff check)
- Tests (pytest)
- E2E tests (post-merge)

**If tests fail → PR blocked.**

---

## Examples: Test-First in Practice

### Example 1: GAD-500 Week 2 (Pre-Action Kernel)

**Test-First Approach:**

```python
# Step 1: Write tests FIRST
# tests/test_pre_action_kernel.py

def test_kernel_blocks_critical_file_overwrite():
    """Kernel should prevent overwriting project_manifest.json"""
    orchestrator = CoreOrchestrator()

    with pytest.raises(KernelViolationError):
        orchestrator._kernel_check_save_artifact("project_manifest.json")

def test_kernel_allows_safe_artifacts():
    """Kernel should allow safe artifact writes"""
    orchestrator = CoreOrchestrator()

    # Should not raise
    orchestrator._kernel_check_save_artifact("feature_spec.json")
```

```python
# Step 2: Implement until tests pass
# agency_os/core_system/orchestrator/core_orchestrator.py

def _kernel_check_save_artifact(self, artifact_name: str):
    CRITICAL_FILES = ["project_manifest.json", ".session_handoff.json"]

    if artifact_name in CRITICAL_FILES:
        raise KernelViolationError(f"Cannot overwrite: {artifact_name}")
```

**Result:**
- ✅ Tests define behavior
- ✅ Implementation guided by tests
- ✅ No test debt created

---

### Example 2: Import Path Migration (GAD-100)

**Wrong Way (Test Debt):**
```bash
# 1. Vendor phoenix_config to lib/
mv phoenix_config/ lib/phoenix_config/

# 2. Commit
git commit -m "vendor phoenix_config"

# 3. Push
# ❌ Tests break later (import errors)
```

**Right Way (Test-First):**
```bash
# 1. Update tests FIRST
sed -i 's/from phoenix_config/from lib.phoenix_config/g' tests/lib/test_phoenix_config.py

# 2. Verify tests still pass
uv run pytest tests/lib/test_phoenix_config.py

# 3. Vendor code
mv phoenix_config/ lib/phoenix_config/

# 4. Verify tests still pass
uv run pytest tests/lib/test_phoenix_config.py

# 5. Commit TOGETHER
git add lib/phoenix_config/ tests/lib/test_phoenix_config.py
git commit -m "feat: Vendor phoenix_config + update test imports"
```

**Result:**
- ✅ Zero test debt
- ✅ Tests never broken
- ✅ Migration verified at each step

---

## Metrics

**Track Monthly:**
1. **Test Debt Incidents:** How many times did tests break due to code changes?
2. **Test Coverage:** Overall % (target: >80%)
3. **Test-to-Code Ratio:** Lines of tests / lines of code (target: >0.5)
4. **Broken Test Duration:** How long do tests stay broken? (target: <1 hour)

**Review Quarterly:**
- Are agents following policy?
- Do we need stricter enforcement?
- Are coverage thresholds appropriate?

---

## Rationale

**Why Test-First?**

1. **Prevents regressions:** Tests catch breaking changes immediately
2. **Documents behavior:** Tests are executable specifications
3. **Enables refactoring:** Can change implementation safely
4. **Reduces debugging:** Failures isolated to specific tests
5. **Builds confidence:** Green tests = working code

**Why This Policy?**

Without this policy, we get:
- ❌ Test debt accumulation
- ❌ Broken tests lingering
- ❌ Agents bypassing tests
- ❌ Regressions in production
- ❌ Decreased code quality

With this policy, we get:
- ✅ Zero test debt
- ✅ High confidence in changes
- ✅ Fast feedback loops
- ✅ Safer refactors
- ✅ Higher code quality

---

## Related Documents

- **CLAUDE.md:** Verification commands, test status
- **GAD-100 Phase Completion:** Example of test debt identified
- **GAD-500 Rollout Plan:** Test-first approach for Week 2+
- **.github/workflows/validate.yml:** CI/CD test enforcement

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-17 | Initial policy (Option B from HIL decision) |

---

**POLICY ACTIVE: All agents must follow test-first approach effective immediately.**
