# AGENT_DECISIONS.md - Common Decision Reference

**Purpose:** Stop agent thrashing by documenting HOW to make common decisions.

**Date:** 2025-11-17
**Authority:** STEWARD (Senior Orchestration Agent)

---

## 📋 Quick Decisions

### Decision: How do I run tests?

**Question:** What command should I use to run tests?

**Answer:**
```bash
# All tests
uv run pytest tests/ -v

# Single test file
uv run pytest tests/test_specific.py -v

# With coverage
uv run pytest tests/ --cov=agency_os --cov-fail-under=80

# Watch mode (run on file change)
uv run pytest-watch tests/ -- -v
```

**Note:** Always use `uv run` (not `python -m pytest`). This ensures the right venv is used.

**Verify:** Tests should pass 95%+ of the time. If <90%, investigate (might be environment issue).

---

### Decision: Should I fix tests or code first?

**Question:** Code broke some tests. Should I fix code or tests first?

**Answer:**
**Test-First Policy:** Fix code FIRST, then update tests.

1. Identify why tests break (usually imports, function signatures)
2. Fix the code
3. Update tests to match new signatures
4. Rerun: `uv run pytest tests/ -v`
5. All tests should pass before pushing

**Rationale:** Tests document expected behavior. If code changed, tests must follow.

**Exception:** If test itself is broken (bad mock, wrong assertion), fix the test. But this is rare.

**See:** [TEST_FIRST.md](./TEST_FIRST.md) for full policy.

---

### Decision: How do I handle linting errors?

**Question:** ruff check shows errors. What do I fix?

**Answer:**

**Automatic Fix (Most issues):**
```bash
# Auto-fix what can be fixed
uv run ruff check . --fix

# Format code
uv run ruff format .

# Check if fixed
uv run ruff check .
```

**Manual Fix (Some issues):**
```bash
# See unfixable errors
uv run ruff check . --output-format=long

# Examples of unfixable:
# - Undefined name (F821) - add import or define variable
# - Unused import (F401) - remove import or use it
# - Line too long (E501) - split line
```

**CRITICAL:** Don't skip linting. It blocks CI/CD.

**Verify:** `./bin/pre-push-check.sh` must show ✅ before push.

---

### Decision: Should I create a new test or add to existing?

**Question:** I wrote a new function. Should I create test_new_function.py or add to existing test file?

**Answer:**

**Create new test file IF:**
- Testing a new module/component
- Test file would exceed 500 lines
- Tests are independent (don't share setup)

**Add to existing test file IF:**
- Testing function in existing module
- Tests share setup/fixtures
- Test file is <500 lines

**Example:**
```
✅ New function in agency_os/new_component.py
   → Create: tests/test_new_component.py

✅ New function in agency_os/orchestrator/core.py (existing module)
   → Add to: tests/test_orchestrator_*.py (if exists)
   → Or create: tests/test_new_core_function.py (if related tests don't exist)

❌ Don't create: tests/test_my_random_function.py (too granular)
```

---

### Decision: When should I commit changes?

**Question:** How often should I commit? When should I push?

**Answer:**

**Commit when:**
- You've completed a logical unit of work (1-2 hours of changes)
- All tests pass
- Linting passes
- You have a clear commit message

**DON'T commit if:**
- Tests are broken
- Linting fails
- Changes are experimental (use feature branches)

**Push when:**
- Your branch has 1-3 commits
- All tests pass AND pre-push check passes
- You've updated .session_handoff.json with progress
- You're ready for the next agent to resume

**Use:**
```bash
# Check before committing
uv run pytest tests/ -v
./bin/pre-push-check.sh

# Commit with clear message
git add .
git commit -m "feat: Add new feature - clear description"

# Push when done
./bin/pre-push-check.sh && git push -u origin branch-name
```

---

### Decision: How do I handle import errors?

**Question:** Tests fail with "ModuleNotFoundError: No module named 'X'"

**Answer:**

**Step 1: Identify the missing module**
```bash
# Run failing test
uv run pytest tests/test_broken.py -v

# Output: ModuleNotFoundError: No module named 'bs4'
```

**Step 2: Install the module**
```bash
# In pyproject.toml, add to [tool.poetry.dependencies]
# Run sync
uv sync --all-extras

# Re-run test
uv run pytest tests/test_broken.py -v
```

**Step 3: Verify in fresh environment (CRITICAL)**
```bash
# The cold boot test checks this
./tests/test_cold_boot.sh
```

**CRITICAL:** Import errors that work in-session but fail in fresh environment are REGRESSIONS.

---

### Decision: What should go in a PR vs what should I push directly?

**Question:** Should I create a PR or push directly to the branch?

**Answer:**

**Create a PR if:**
- Working on feature that touches critical components (orchestrator, planning)
- Changes affect multiple files
- Want code review before merge (recommended for complex changes)
- This is the standard for vibe-agency

**Push directly (current workflow) if:**
- Bug fix in a single file
- Documentation update
- Build/config fix
- You're sure the change won't break anything

**Note:** vibe-agency uses PR-based workflow. All feature work should go through PRs.

**Example:**
```bash
# Make changes on branch
git add .
uv run pytest tests/ -v
./bin/pre-push-check.sh

# Create PR
gh pr create --title "feat: Description" --body "Why this change matters"

# Wait for review
# Then merge
```

---

### Decision: How do I update .session_handoff.json?

**Question:** Session is complete. How do I hand off to the next agent?

**Answer:**

**Use the helper script:**
```bash
# Creates .session_handoff.json with your status
./bin/create-session-handoff.sh

# It will prompt you for:
# - Current state (complete/blocked/needs-input/in-progress)
# - Summary of what was done
# - Remaining TODOs
# - Critical files to read
# - Next steps

# Verify it looks good
cat .session_handoff.json

# Commit
git add .session_handoff.json
git commit -m "chore: Update session handoff"
```

**OR manually edit .session_handoff.json:**
```json
{
  "_schema_version": "2.0_4layer",
  "_token_budget": 450,
  "layer0_bedrock": {
    "from": "AGENT_NAME - Session ID",
    "date": "2025-11-17",
    "state": "complete",
    "blocker": null
  },
  "layer1_runtime": {
    "current_status": "What I did in 1 sentence",
    "todos": [
      "Next thing for next agent to do",
      "Another thing"
    ],
    "critical_files": [
      "CLAUDE.md",
      "docs/architecture/..."
    ]
  }
}
```

**See:** .session_handoff.json (example in repo root)

---

### Decision: What's the difference between a bug fix and a refactor?

**Question:** I'm improving code quality. Is this a bug fix or refactor?

**Answer:**

**Bug Fix:**
- Fixes incorrect behavior
- Changes user-facing functionality
- Example: "Fix xyz not working"
- Tests should exist that now pass
- Commit message: `fix: Description`

**Refactor:**
- Improves code quality WITHOUT changing behavior
- No new features
- Example: "Extract method to reduce complexity"
- All tests should pass before and after
- Commit message: `refactor: Description`

**Feature:**
- Adds new functionality
- New user capability or agent behavior
- Example: "Add new API endpoint"
- Must include new tests
- Commit message: `feat: Description`

**Example commits:**
```
✅ fix: Update yaml dependency import to fix ImportError
✅ refactor: Extract planning_handler logic to separate module
✅ feat: Add cold boot test to prevent regressions
❌ fix: Refactored orchestrator (too vague)
❌ feat: Made some improvements (no value)
```

---

### Decision: What's "operational" status vs "complete"?

**Question:** My session is operational but not fully complete. How do I report this?

**Answer:**

**Use layer0_bedrock.state:**

| State | Meaning | When to use |
|-------|---------|------------|
| `operational` | System works, but work in progress | Current session actively being developed |
| `complete` | All planned work done, ready for next agent | Session finished, handing off to next agent |
| `blocked` | Can't continue without external input | Waiting for user decision or fix |
| `needs-input` | Needs info from user to proceed | Requires clarification or data |
| `in-progress` | Session is active | Don't use (deprecated, use `operational`) |

**Example:**
```json
{
  "layer0_bedrock": {
    "state": "operational",
    "blocker": null
  }
}
```

---

### Decision: How do I know when a test is "done"?

**Question:** When can I say "testing is complete"?

**Answer:**

**Use Persistence Checklist:**
```
✅ All tests pass (uv run pytest tests/ -v)
✅ 95%+ pass rate (334/343+ tests)
✅ Cold boot test passes (./tests/test_cold_boot.sh)
✅ No import errors (uv run pytest tests/test_layer0_integrity.py)
✅ Pre-push check passes (./bin/pre-push-check.sh)
✅ Committed to git (git status shows clean)
```

**Test failures are OK if:**
- They're expected/documented (known issues in CLAUDE.md)
- They're deferred (skipped tests with reason)
- They don't block CI/CD

**See:** CLAUDE.md section "Expected Test Failures"

---

## 🚫 Common Mistakes (What NOT to do)

### ❌ Claim "fixed" without testing in fresh environment

```bash
# ❌ BAD
"I fixed the yaml import issue"
(works in current .venv, never tested fresh boot)

# ✅ GOOD
"I fixed the yaml import issue"
(tested: cold boot test passes, verified in fresh venv)
```

### ❌ Commit broken tests

```bash
# ❌ BAD
git add .
git commit -m "WIP: fixing tests"  # Some tests still broken
git push

# ✅ GOOD
[Fix all tests first]
uv run pytest tests/ -v  # 95%+ passing
git add .
git commit -m "feat: Add new feature with tests"
git push
```

### ❌ Update docs without updating code

```bash
# ❌ BAD
# Updated CLAUDE.md with new verification command
# But didn't actually implement the command

# ✅ GOOD
# Implemented the feature
# Wrote/updated tests
# Updated CLAUDE.md with verification command
# Verified command works
```

### ❌ Create new files without tests

```bash
# ❌ BAD
# Created new agency_os/new_component.py (no tests)
# Claim "component ready"

# ✅ GOOD
# Created agency_os/new_component.py
# Created tests/test_new_component.py
# Tests pass (uv run pytest tests/test_new_component.py -v)
# Component ready
```

### ❌ Push without pre-push check

```bash
# ❌ BAD
git push  # Hope linting passes in CI/CD

# ✅ GOOD
./bin/pre-push-check.sh  # Verify locally first
git push
```

---

## 📞 Getting Help

**If you can't decide:**
1. Check this file for the decision
2. Run the verification command
3. Check CLAUDE.md for operational status
4. If still unsure, ask in the session handoff

**If something's missing:**
1. Add it to this file
2. Update CLAUDE.md CORE PRINCIPLES if it's critical
3. Document the decision pattern for future agents

---

## 🔄 Maintenance

**When to update this file:**
- You make the same decision twice
- Decision leads to agent thrashing
- New policy emerges from testing

**How to update:**
1. Add decision to this file
2. Reference it in commit message: "chore: Add AGENT_DECISIONS entry for X"
3. Update CLAUDE.md if it's a critical policy change
