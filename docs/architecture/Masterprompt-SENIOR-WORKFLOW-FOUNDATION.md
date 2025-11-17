# Master Prompt: Senior Workflow - Foundation Closure

**GAD Reference:** Cross-cutting (GAD-1XX through GAD-4XX migration, system integrity)
**Phase:** Foundation Closure & Regression Repair
**Estimated Time:** 8-12 hours (1-2 days)
**Complexity:** Expert-Only (requires architectural understanding)
**Target Branch:** `claude/senior-foundation-closure-[SESSION_ID]`

---

## 📊 CONTEXT (What You Need to Know)

### Current State

**Architecture Migration Status:**
- ✅ **GAD-5XX through GAD-8XX:** Migrated to new structure
- ✅ **LAD-1 through LAD-3:** Complete (Layer docs)
- ✅ **VAD-001 through VAD-003:** Created (but only skeletons)
- ❌ **GAD-1XX through GAD-4XX:** NOT migrated (old files still at root)
- ❌ **Test Suite:** BROKEN (sys.exit() in module-level code)
- ⚠️ **Quality Loop:** Not fully automated (manual steps remain)

**Verify current state:**
```bash
# Architecture migration status
ls -la docs/architecture/GAD-0*.md  # Old files still exist

# Test status (will FAIL with INTERNAL ERROR)
uv run pytest --co -q 2>&1 | head -50

# Old GADs that need migration
find docs/architecture -name "GAD-00*.md" -type f

# Session context (works)
./bin/show-context.py
```

### What's Broken/Missing

**1. Test Suite Completely Broken**
- **Root Cause:** `test_prompt_composition.py` has `sys.exit(1)` at module import level (lines 23, 39)
- **Impact:** pytest cannot even collect tests → ALL test runs fail with INTERNAL ERROR
- **Evidence:** 19 collection errors, entire test suite unusable

**2. Old GAD Files Not Migrated**
```
GAD-001_Research_Integration.md → Should be GAD-1XX
GAD-002_Core_SDLC_Orchestration.md → Should be GAD-2XX
GAD-003_Research_Capability_Restoration.md → Part of GAD-1XX
GAD-004_Multi_Layered_Quality_Enforcement.md → Should be GAD-4XX
```

**3. Architectural Gaps**
- **GAD-100:** Exists but incomplete (VibeConfig just added in Phase 3)
- **GAD-3XX:** Completely undefined (no clear pillar assignment)
- **VAD tests:** Only skeletons (no real test implementation)

**4. Quality Loop Not Closed**
- Session handoff works but not fully automated
- Test results not automatically visible
- Manual steps still required for "seeing the full picture"

**Evidence:**
```bash
# Test failure
uv run pytest tests/ -v 2>&1 | grep "INTERNALERROR"

# Old GAD files
ls -la docs/architecture/GAD-00*.md

# TODOs in codebase
grep -r "TODO\|FIXME" agency_os/ --include="*.py" | wc -l  # 13 occurrences

# VAD skeleton tests
grep -A 5 "def test_" tests/architecture/test_vad*.py
```

### Dependencies

**Must exist BEFORE starting:**
- [x] GAD-5XX through GAD-8XX migrated (✅ DONE)
- [x] LAD-1 through LAD-3 complete (✅ DONE)
- [x] Session handoff system working (✅ DONE)
- [x] Test-First Development policy established (✅ DONE)

**Verify dependencies:**
```bash
# All verified - dependencies met
ls docs/architecture/GAD-5XX/
ls docs/architecture/LAD/
./bin/show-context.py
cat docs/policies/TEST_FIRST.md
```

---

## 🎯 GOAL (What Success Looks Like)

### Primary Objectives

1. **FIX TEST SUITE** → Zero collection errors, all tests can run
2. **MIGRATE OLD GADs** → GAD-001 through GAD-004 in new structure (GAD-1XX through GAD-4XX)
3. **CLOSE THE LOOP** → Full automation of context/status visibility
4. **REPAIR REGRESSIONS** → Fix all test failures caused by architecture changes
5. **DEFINE GAD-3XX** → Decide what Pillar 3 represents
6. **ZERO FRICTION** → "bin/run-vibe" or similar - one command to see everything

### Success Criteria

**Acceptance Tests:**
```bash
# 1. Test suite can collect and run
uv run pytest --co -q  # No INTERNAL ERROR, lists all tests

# 2. Core tests pass (regressions fixed)
uv run pytest tests/test_planning_workflow.py -v  # PASSES
uv run pytest tests/test_layer0_integrity.py -v  # PASSES

# 3. Architecture docs migrated
ls docs/architecture/GAD-1XX/GAD-100.md  # EXISTS (consolidated Research + Planning)
ls docs/architecture/GAD-2XX/GAD-200.md  # EXISTS (SDLC Orchestration)
ls docs/architecture/GAD-4XX/GAD-400.md  # EXISTS (Quality Enforcement)

# 4. No old GAD files at root
ls docs/architecture/GAD-00*.md 2>&1 | grep "No such file"  # OLD FILES GONE

# 5. Zero regressions
./bin/verify-all.sh  # ALL checks pass

# 6. One-command context
./bin/show-status.sh  # Shows: git, tests, linting, session handoff, TODOs (ALL in ONE view)
```

**Expected Output:**
```
✅ Test suite: 59/59 tests collected (0 errors)
✅ Core tests: 45/59 passing (14 skipped - expected)
✅ Architecture: 4 pillars migrated (GAD-1XX through GAD-4XX)
✅ Linting: 0 errors
✅ Documentation: CLAUDE.md + INDEX.md updated
✅ Session handoff: Automated
```

### Non-Goals (What NOT to Do)

- ❌ **DO NOT implement GAD-3XX content** (just define what pillar means)
- ❌ **DO NOT fix ALL skipped tests** (only fix regressions from architecture changes)
- ❌ **DO NOT implement VAD test bodies** (skeletons are fine for now)
- ❌ **DO NOT add new features** (this is repair work ONLY)
- ❌ **DO NOT touch GAD-100 Phase 4+** (phases 4-6 deferred per GAD-100_PHASE_COMPLETION.md)

---

## 🛠️ IMPLEMENTATION PLAN

### Phase 1: Emergency Repair (Test Suite)
**Goal:** Make test suite usable again
**Time:** 1-2 hours

**Tasks:**
1. **Fix test_prompt_composition.py**
   - Remove `sys.exit()` calls from module-level code (lines 23, 39)
   - Convert to proper pytest structure (setup/teardown, not import-time execution)
   - Option A: Fix the file
   - Option B: Skip/disable the file (add `@pytest.skip` at module level)

2. **Verify test collection works**
   ```bash
   uv run pytest --co -q  # Should list all tests, no INTERNAL ERROR
   ```

3. **Run smoke test**
   ```bash
   uv run pytest tests/test_layer0_integrity.py -v  # Should work
   ```

**Verification:**
```bash
# Test collection works
uv run pytest --co -q 2>&1 | grep -c "INTERNALERROR"  # Should be 0

# At least some tests can run
uv run pytest tests/test_file_based_delegation.py -v
```

**Deliverables:**
- [ ] test_prompt_composition.py fixed or disabled
- [ ] Test collection working (no INTERNAL ERROR)
- [ ] Smoke test passing

---

### Phase 2: Architecture Migration (Old GADs → New Structure)
**Goal:** Complete the GAD migration started in PR #86
**Time:** 3-4 hours

**Tasks:**

**Step 1: Define Pillar Assignments**

Review old GAD content and assign to new pillars:

| Old GAD | Content | New Pillar | Rationale |
|---------|---------|------------|-----------|
| GAD-001 | Research Integration | GAD-1XX (Planning & Research) | Research is part of Planning framework |
| GAD-003 | Research Capability Restoration | GAD-1XX (same pillar) | Continuation of GAD-001 |
| GAD-002 | Core SDLC Orchestration | GAD-2XX (Orchestration & SDLC) | Core system orchestration |
| GAD-004 | Multi-Layer Quality Enforcement | GAD-4XX (Quality & Testing) | Quality gates, testing, enforcement |
| GAD-3XX | **UNDEFINED** | GAD-3XX (TBD) | Need to decide what this pillar represents |

**Step 2: Decide on GAD-3XX Pillar**

Options for Pillar 3:
- **Option A:** Deployment & Operations (DEPLOY phase, maintenance)
- **Option B:** Agent Framework (agent composition, prompt registry)
- **Option C:** State Management (state machine, transitions, persistence)

**Recommendation:** Pick Option B or C based on what's most architecturally significant.

**Step 3: Migrate Files**

```bash
# Create GAD-1XX (Planning & Research)
mkdir -p docs/architecture/GAD-1XX
# Consolidate GAD-001 + GAD-003 → GAD-100.md (Planning & Research EPIC)
# Move GAD-001_VERIFICATION_HARNESS.md → GAD-101.md (if still relevant)

# Create GAD-2XX (Orchestration & SDLC)
mkdir -p docs/architecture/GAD-2XX
# Move GAD-002 → GAD-200.md (Core SDLC EPIC)
# Move GAD-002_VERIFICATION_HARNESS.md → GAD-201.md

# Create GAD-4XX (Quality & Testing)
mkdir -p docs/architecture/GAD-4XX
# Move GAD-004 → GAD-400.md (Quality Enforcement EPIC)

# Archive old files (don't delete yet)
mkdir -p docs/architecture/archive/pre-migration
git mv docs/architecture/GAD-00*.md docs/architecture/archive/pre-migration/
```

**Step 4: Update References**

Update all references to old GADs:
```bash
# Find references
grep -r "GAD-001\|GAD-002\|GAD-003\|GAD-004" docs/ --include="*.md"

# Update to new names
# GAD-001 → GAD-1XX or GAD-100
# GAD-002 → GAD-2XX or GAD-200
# GAD-003 → GAD-1XX (same as GAD-001)
# GAD-004 → GAD-4XX or GAD-400
```

**Step 5: Update INDEX.md and STRUCTURE.md**

```bash
# Update INDEX.md with new pillar names
# Example:
# GAD-1XX: Planning & Research
# GAD-2XX: Core Orchestration & SDLC
# GAD-3XX: [Pillar name TBD]
# GAD-4XX: Quality & Testing
```

**Verification:**
```bash
# New structure exists
ls docs/architecture/GAD-1XX/GAD-100.md
ls docs/architecture/GAD-2XX/GAD-200.md
ls docs/architecture/GAD-4XX/GAD-400.md

# Old files archived
ls docs/architecture/archive/pre-migration/GAD-00*.md

# References updated
grep -r "GAD-001" docs/architecture/*.md | wc -l  # Should be 0 (except archive)

# INDEX.md updated
grep "GAD-1XX" docs/architecture/INDEX.md
grep "GAD-2XX" docs/architecture/INDEX.md
```

**Deliverables:**
- [ ] GAD-1XX created (Planning & Research pillar)
- [ ] GAD-2XX created (Orchestration pillar)
- [ ] GAD-3XX defined (pillar name chosen)
- [ ] GAD-4XX created (Quality pillar)
- [ ] Old GAD files archived
- [ ] All references updated
- [ ] INDEX.md and STRUCTURE.md updated

---

### Phase 3: Close the Loop (Automation & Context)
**Goal:** Full automation of context visibility - one command shows everything
**Time:** 2-3 hours

**Tasks:**

**Step 1: Enhance bin/show-context.py**

Current capabilities:
- ✅ Shows session handoff
- ✅ Shows system status (if exists)
- ⚠️ Doesn't show test results
- ⚠️ Doesn't show TODOs
- ⚠️ Doesn't show recent commits

**Additions needed:**
```python
# Add to bin/show-context.py:

def show_test_status():
    """Run quick test smoke check and show status"""
    # Run: uv run pytest tests/test_layer0_integrity.py -v --tb=no
    # Parse output: X passed, Y failed, Z skipped
    # Display: ✅ Tests: 17/17 passing OR ❌ Tests: 5/17 failing

def show_todo_summary():
    """Scan for TODOs in code and docs"""
    # Run: grep -r "TODO\|FIXME" agency_os/ docs/ --include="*.py" --include="*.md"
    # Count and categorize
    # Display: ⚠️ TODOs: 13 in code, 5 in docs

def show_recent_commits():
    """Show last 3 commits for context"""
    # Run: git log --oneline -3
    # Display commits

def show_architecture_status():
    """Show GAD/VAD/LAD completion status"""
    # Check which GADs exist
    # Check VAD test status (skipped vs implemented)
    # Display: GAD-1XX: ✅, GAD-2XX: ✅, GAD-3XX: ⚠️ TBD, etc.
```

**Step 2: Create bin/show-status.sh (Master Command)**

```bash
#!/bin/bash
# bin/show-status.sh - ONE COMMAND for full system context

echo "========================================"
echo "🎯 VIBE-AGENCY SYSTEM STATUS"
echo "========================================"
echo ""

# 1. Session Handoff (already works)
./bin/show-context.py

echo ""
echo "━━━ ARCHITECTURE STATUS ━━━"
# Show GAD/VAD/LAD completion

echo ""
echo "━━━ TEST STATUS ━━━"
# Quick test smoke check

echo ""
echo "━━━ TODO SUMMARY ━━━"
# Count TODOs

echo ""
echo "━━━ RECENT ACTIVITY ━━━"
# Last 3 commits

echo ""
echo "========================================"
echo "💡 Quick Actions:"
echo "  Run all tests:     uv run pytest tests/ -v"
echo "  Fix linting:       uv run ruff check . --fix"
echo "  Pre-push check:    ./bin/pre-push-check.sh"
echo "  Verify all:        ./bin/verify-all.sh"
echo "========================================"
```

**Step 3: Auto-update system status on key events**

Options:
- **Option A:** Git hooks (already available in `.githooks/`)
- **Option B:** Add to bin/commit-and-push.sh
- **Option C:** CI/CD auto-comment on PR

Choose Option B (safest, works everywhere):
```bash
# Update bin/commit-and-push.sh to auto-run:
./bin/update-system-status.sh
./bin/show-status.sh  # Show before committing
```

**Verification:**
```bash
# One command shows everything
./bin/show-status.sh

# Should display:
# - Session handoff
# - System status (git, linting)
# - Test status (quick smoke check)
# - TODO summary
# - Recent commits
# - Architecture completion
# - Quick action commands
```

**Deliverables:**
- [ ] bin/show-context.py enhanced (test status, TODOs, architecture)
- [ ] bin/show-status.sh created (master command)
- [ ] bin/commit-and-push.sh auto-runs status update
- [ ] Documentation updated (CLAUDE.md with new commands)

---

### Phase 4: Regression Repair (Fix Broken Tests)
**Goal:** Fix test failures caused by architecture changes
**Time:** 2-3 hours

**Tasks:**

**Step 1: Identify regression sources**

Run tests and categorize failures:
```bash
# Get baseline
uv run pytest tests/ -v --tb=short 2>&1 | tee test_results.txt

# Categorize:
# - Import errors (paths changed)
# - Missing files (moved during refactor)
# - Assertion failures (behavior changed)
# - Expected skips (intentional)
```

**Step 2: Fix import path regressions**

Common issues after GAD-100 Phase 3:
```python
# OLD (might be broken):
from phoenix_config import VibeConfig  # Wrong path

# NEW (correct):
from lib.vibe_config import VibeConfig  # After Phase 1 vendoring
```

**Step 3: Fix test files with architecture assumptions**

Example issues:
- Tests expecting old directory structure
- Tests hardcoding old GAD references
- Tests importing deleted/moved modules

**Step 4: Document expected skips**

Create a "Known Skips" section in CLAUDE.md:
```markdown
### Expected Test Skips

| Test | Reason | When to Implement |
|------|--------|-------------------|
| test_vad001_* | VAD skeleton only | After GAD implementation |
| test_rogue_agent_* | 11/13 scenarios deferred (GAD-502) | Phase 2-5 of GAD-502 |
```

**Verification:**
```bash
# Core tests pass
uv run pytest tests/test_planning_workflow.py -v
uv run pytest tests/test_layer0_integrity.py -v
uv run pytest tests/test_canonical_schemas.py -v

# Acceptable failure rate
# Total: ~60 tests
# Passing: ~45 tests (75%)
# Skipped: ~14 tests (expected)
# Failing: ~1 test (acceptable if documented)

# Zero import errors
uv run pytest tests/ --tb=short 2>&1 | grep "ImportError" | wc -l  # Should be 0
```

**Deliverables:**
- [ ] All import paths fixed
- [ ] Core workflow tests passing (planning, layer0, schemas)
- [ ] Known skips documented in CLAUDE.md
- [ ] Test success rate ≥75%

---

## ✅ TEST-FIRST REQUIREMENTS

**Policy:** Test-First Development policy applies.

### Test Strategy

**Tests to Fix (not write new):**
1. `tests/test_prompt_composition.py` - Remove sys.exit(), make pytest-compatible
2. `tests/test_planning_workflow.py` - Fix import paths if broken
3. `tests/test_layer0_integrity.py` - Ensure still passing after changes
4. `tests/architecture/test_vad*.py` - Verify skeletons still work

**Test Execution:**
```bash
# Quick smoke test (Phase 1 verification)
uv run pytest tests/test_layer0_integrity.py -v

# Core workflow tests (Phase 4 verification)
uv run pytest tests/test_planning_workflow.py -v
uv run pytest tests/test_canonical_schemas.py -v

# Full suite (final verification)
uv run pytest tests/ -v --tb=short
```

**Coverage Requirements:**
- **This work:** No new code → no new coverage requirements
- **Regression fixes:** Ensure existing coverage maintained (≥80% for tested modules)

---

## 🚨 KNOWN RISKS & MITIGATIONS

### Risk 1: Breaking Working Tests During Repair
**Probability:** Medium
**Impact:** High
**Mitigation:**
- Run `./bin/verify-all.sh` BEFORE starting work (baseline)
- Fix tests incrementally (one file at a time)
- Commit after each successful fix
- Keep rollback plan ready

### Risk 2: GAD-3XX Pillar Choice May Be Wrong
**Probability:** Low
**Impact:** Medium
**Mitigation:**
- Document rationale for pillar choice in GAD-300.md
- Leave placeholder structure (can rename later)
- Consult HIL (user) if unsure

### Risk 3: Old GAD Content May Be Outdated
**Probability:** High
**Impact:** Low
**Mitigation:**
- Mark migrated GADs with "Status: LEGACY - Review Needed"
- Don't delete old files (archive them)
- Validate against actual codebase before claiming "implemented"

### Risk 4: Scope Creep (Trying to Fix Everything)
**Probability:** High
**Impact:** Medium
**Mitigation:**
- Stick to Non-Goals section (DO NOT implement VAD bodies, etc.)
- Focus on regressions ONLY (not pre-existing issues)
- Time-box each phase (if >1 hour over estimate, stop and reassess)

---

## 🔄 ROLLBACK PLAN

### If Things Go Wrong

**Scenarios:**

**Scenario 1: Test repairs break more things**
```bash
# Rollback to last good commit
git log --oneline -10  # Find last good commit
git reset --hard <commit-sha>
./bin/verify-all.sh  # Verify rollback successful
```

**Scenario 2: GAD migration creates documentation debt**
```bash
# Restore old files
git checkout docs/architecture/GAD-00*.md
# Delete new directories
rm -rf docs/architecture/GAD-1XX docs/architecture/GAD-2XX docs/architecture/GAD-4XX
# Update INDEX.md to old structure
git checkout docs/architecture/INDEX.md
```

**Scenario 3: Loop automation breaks existing workflow**
```bash
# Disable new automation
mv bin/show-status.sh bin/show-status.sh.bak
# Revert bin/commit-and-push.sh changes
git checkout bin/commit-and-push.sh
# Keep manual workflow
./bin/show-context.py  # Still works
```

**What Gets Preserved:**
- Original test files (in git history)
- Old GAD files (in archive/ directory)
- Session handoff system (don't touch)
- Existing bin/ scripts (only add, don't modify critical ones)

---

## 📚 REFERENCE MATERIALS

### Architecture Documents
- [STRUCTURE.md](../STRUCTURE.md) - 3-document-type system (GAD/VAD/LAD)
- [INDEX.md](../INDEX.md) - Current architecture index
- [MIGRATION_COMPLETE.md](../MIGRATION_COMPLETE.md) - Previous migration status
- [GAD-5XX/GAD-500.md](../GAD-5XX/GAD-500.md) - Example of migrated GAD
- [Test-First Policy](../../policies/TEST_FIRST.md) - Testing requirements

### Related Code
- [tests/test_prompt_composition.py](../../tests/test_prompt_composition.py) - BROKEN (sys.exit issue)
- [bin/show-context.py](../../bin/show-context.py) - Session context display
- [bin/verify-all.sh](../../bin/verify-all.sh) - Full verification suite
- [CLAUDE.md](../../CLAUDE.md) - Operational truth document

### External Resources
- [pytest documentation](https://docs.pytest.org/) - Test framework docs
- [Git mv documentation](https://git-scm.com/docs/git-mv) - Preserving history during migration

---

## 🎓 CONTEXT FOR AGENTS (All Intelligence Levels)

### For Simple Agents (Haiku)
**DO NOT USE HAIKU FOR THIS WORK - TOO COMPLEX**

If you must:
1. **Start with Phase 1 ONLY** (fix test_prompt_composition.py)
2. Open the file: `tests/test_prompt_composition.py`
3. Find lines with `sys.exit(1)` or `sys.exit(0)`
4. Delete those lines OR add `@pytest.mark.skip` at top of file
5. Run: `uv run pytest --co -q` - should see test list, no INTERNAL ERROR
6. **STOP. Call Sonnet/Opus for Phases 2-4**

### For Advanced Agents (Sonnet/Opus)

**Key Design Decisions:**

**GAD Migration Strategy:**
- **Consolidation over Fragmentation:** GAD-001 + GAD-003 both about Research → merge into GAD-100 (Planning & Research pillar)
- **Pillar Naming:** Pillars should be functional categories, not chronological or arbitrary
- **Backward Compatibility:** Archive old files, don't delete (git history preservation)

**Test Repair Philosophy:**
- **Regression Focus:** Only fix what broke due to architecture changes
- **Skip Documentation:** It's OK to skip tests that aren't implemented yet (VAD, Haiku hardening Phase 2-5)
- **Smoke Test Priority:** Get SOME tests passing quickly (layer0, planning workflow) before fixing everything

**Loop Automation Design:**
- **Zero Configuration:** bin/show-status.sh should work without any setup
- **Fail-Safe:** If any component fails, show partial status (don't crash)
- **Human-Friendly:** Output optimized for quick scanning (emojis, colors, short lines)

**Optimization Opportunities (NOT required):**
- Parallel test execution (pytest-xdist)
- Cached test results (pytest-cache)
- Pre-commit hooks (instead of pre-push)
- Architecture diagram auto-generation (from GAD files)

---

## 🔍 VERIFICATION CHECKLIST (Before Marking Complete)

Run these commands and ensure ALL pass or have documented explanations:

```bash
# 1. Test collection works (no INTERNAL ERROR)
uv run pytest --co -q 2>&1 | grep -c "INTERNALERROR"  # Should output: 0

# 2. Core tests pass
uv run pytest tests/test_layer0_integrity.py -v  # All pass
uv run pytest tests/test_planning_workflow.py -v  # All pass
uv run pytest tests/test_canonical_schemas.py -v  # All pass

# 3. Architecture migration complete
ls docs/architecture/GAD-1XX/GAD-100.md  # Exists
ls docs/architecture/GAD-2XX/GAD-200.md  # Exists
ls docs/architecture/GAD-4XX/GAD-400.md  # Exists
ls docs/architecture/archive/pre-migration/GAD-00*.md  # Old files archived

# 4. No broken references
grep -r "GAD-001\|GAD-002\|GAD-003\|GAD-004" docs/architecture/*.md | grep -v archive | wc -l  # Should be 0

# 5. Linting clean
uv run ruff check . --fix
uv run ruff format .

# 6. One-command context works
./bin/show-status.sh  # Displays full status

# 7. Pre-push checks pass
./bin/pre-push-check.sh  # All green

# 8. Documentation updated
grep "GAD-1XX" docs/architecture/INDEX.md  # Found
grep "show-status.sh" CLAUDE.md  # Documented
```

**Manual Checks:**
- [ ] test_prompt_composition.py doesn't have sys.exit() in module-level code
- [ ] GAD-3XX pillar name decided and documented
- [ ] All phase deliverables completed
- [ ] Session handoff updated with completion summary
- [ ] No regression in existing functionality (verified via verify-all.sh)

---

## 📝 COMPLETION REPORT (Fill this out when DONE)

**Completed By:** [Agent name/session ID]
**Date:** [YYYY-MM-DD]
**Time Taken:** [Actual hours]
**Branch:** `claude/senior-foundation-closure-[SESSION_ID]`
**PR Number:** #[XXX]

### What Was Delivered

**Phase 1: Emergency Repair**
- [ ] test_prompt_composition.py fixed/disabled
- [ ] Test collection working (verified with: `uv run pytest --co -q`)
- [ ] Smoke test passing (verified with: `uv run pytest tests/test_layer0_integrity.py -v`)

**Phase 2: Architecture Migration**
- [ ] GAD-1XX created: [List files]
- [ ] GAD-2XX created: [List files]
- [ ] GAD-3XX defined: Pillar name = [Name chosen]
- [ ] GAD-4XX created: [List files]
- [ ] Old files archived: [List archived files]
- [ ] References updated: [Number of files updated]

**Phase 3: Close the Loop**
- [ ] bin/show-context.py enhanced: [Features added]
- [ ] bin/show-status.sh created: [Verified working]
- [ ] Automation integrated: [Where auto-run happens]
- [ ] CLAUDE.md updated: [New commands documented]

**Phase 4: Regression Repair**
- [ ] Import errors fixed: [Number fixed]
- [ ] Core tests passing: [List passing tests]
- [ ] Known skips documented: [Number documented]
- [ ] Test success rate: [X%]

### Deviations from Plan

[Describe any changes to the plan and why they were necessary]

### Final Verification

```bash
# Copy-paste output of verification commands here
```

### Known Issues / Follow-Up Work

[List any issues discovered or work that needs to happen next]

---

## 🎯 NEXT STEPS (After This Work)

### Immediate Follow-Up
1. **Merge this PR** to main (after HIL review)
2. **Run bin/show-status.sh** in next session to verify automation works
3. **Update CLAUDE.md** "Last Verified" date

### Future Enhancements (NOT required now)
- Implement VAD test bodies (VAD-001, VAD-002, VAD-003)
- Complete GAD-502 Phase 2-5 (Haiku Hardening - 11/13 scenarios)
- Implement GAD-100 Phase 4-6 (Feature flags, migration tools, advanced config)
- Add architecture diagram auto-generation
- Parallel test execution (pytest-xdist)

---

**END OF MASTER PROMPT**

---

## 📌 EXECUTION NOTES

**For the agent executing this work:**

1. **Read EVERYTHING first** - This is a complex, multi-phase task
2. **Don't skip phases** - Each phase builds on the previous
3. **Verify after each phase** - Don't move forward if verification fails
4. **Ask HIL if stuck** - GAD-3XX pillar choice is judgment call
5. **Time-box work** - If any phase takes >2x estimate, stop and report
6. **Document deviations** - If you change the plan, explain why in completion report

**Emergency Contact:**
- If test suite cannot be fixed → Skip to Phase 2 (architecture migration still valuable)
- If GAD migration is ambiguous → Document options in completion report, ask HIL to decide
- If automation breaks existing workflow → Rollback Phase 3, keep Phases 1-2 work

**Success Threshold:**
- **Minimum:** Phases 1 + 2 complete (test suite usable, architecture migrated)
- **Target:** Phases 1-3 complete (+ automation)
- **Stretch:** All 4 phases + zero regressions

**Remember:** This work is FOUNDATION CLOSURE - it's OK to be thorough. Speed is secondary to correctness.
