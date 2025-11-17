# HIDDEN DEPENDENCIES AUDIT
**Date:** 2025-11-17
**Trigger:** Recurring yaml dependency regression

## PATTERN: Session-Only "Fixes"

### Identified Cases

#### 1. **Yaml Dependency (FIXED)** ⚠️ HIGH IMPACT
- **Claim:** "Phase 4 Regression Repair - Fixed yaml dependency" (commit 19f0591)
- **Reality:** Only fixed for that session, reverted every new session
- **Why:** `uv sync --all-extras` ran manually, not persisted in boot script
- **Impact:** Every agent wasted 30s + tokens hitting ModuleNotFoundError
- **Fix Applied:** Added dependency check to system-boot.sh (commit e3c2b01)
- **Status:** ✅ RESOLVED

#### 2. **CLAUDE.md Documentation Drift** ⚠️ LOW IMPACT
- **Claim:** Line 105 - `./bin/show-context.sh` (verification command)
- **Reality:** File is actually `./bin/show-context.py`
- **Why:** File renamed from .sh to .py, docs not updated
- **Impact:** Minor - agents can auto-correct
- **Fix:** Update CLAUDE.md line 105
- **Status:** ❌ OPEN

#### 3. **Agent Thrashing - Pytest Venv** ⚠️ MEDIUM IMPACT
- **Pattern:** Fix → Revert → Fix → Revert
- **Commits:**
  - 5c23ecf: "fix: Use pytest from project venv"
  - 1ff2810: Revert of above
- **Why:** Agents disagreed on whether to use `uv run pytest` vs isolated pytest
- **Impact:** Wasted work, git history noise
- **Root Cause:** No policy document on "How to run tests"
- **Status:** ❌ SYSTEMIC ISSUE

#### 4. **Agent Thrashing - Pre-commit Hooks** ⚠️ MEDIUM IMPACT
- **Pattern:** Feature added → Reverted with reasoning
- **Commits:**
  - c049c1c: "feat: Add pre-commit hook for ruff linting"
  - 4d6c8fc: Revert (doesn't work in CI/CD)
- **Why:** Agent didn't understand environment constraints
- **Impact:** Wasted work, had to be undone
- **Root Cause:** Agents don't check "Will this work in our deployment model?"
- **Status:** ❌ SYSTEMIC ISSUE

## ROOT CAUSE ANALYSIS

### Why Do Agents Create Session-Only Fixes?

1. **Optimization Blind Spot**
   - Agent optimizes for "claim success this session"
   - No incentive to verify "will this persist next session?"
   - Example: Run `uv sync`, tests pass, claim "fixed" ✅

2. **Missing Persistence Checklist**
   - No systematic check: "Is this change in git?"
   - No verification: "Will next session inherit this state?"
   - Agents treat sessions like isolated transactions

3. **Documentation Lag**
   - Agent makes change
   - Tests pass
   - Commits code
   - Forgets to update CLAUDE.md
   - Drift accumulates

4. **No Cross-Session Verification**
   - Tests run in same session that made changes
   - No "cold boot" test that simulates fresh agent
   - Hidden dependencies never caught

5. **Thrashing From Lack of Policy**
   - No documented decisions on "pytest: uv run or isolated?"
   - Each agent makes own choice
   - Results in fix/revert cycles

## SYSTEMIC VULNERABILITIES

### High Risk Areas for Hidden Dependencies

1. **Scripts that assume venv exists**
   - ✅ system-boot.sh (NOW FIXED)
   - ❓ Other bin/*.sh scripts?

2. **Documentation claiming "Works" without persistence test**
   - CLAUDE.md has 17 "✅ Works" claims
   - Unknown how many are actually persistent

3. **Commands in Quick Start guides**
   - If command fails in fresh session → hidden dependency
   - No automated "Quick Start smoke test"

4. **Environment assumptions**
   - Git config expectations
   - Python version assumptions
   - Tool availability (jq, etc)

## RECOMMENDATIONS (BACKLOG)

### CRITICAL (P0)

1. **Create Cold Boot Test**
   ```bash
   # tests/test_cold_boot.sh
   # Deletes .venv, runs system-boot.sh, runs core tests
   # Catches session-only fixes
   ```
   **Effort:** 1 hour
   **Impact:** Prevents all future session-only regressions

2. **Add Persistence Checklist to CLAUDE.md**
   ```markdown
   ## Before Claiming "Fixed" or "Complete"
   - [ ] Change is in git (not just in-memory)
   - [ ] Would work in fresh session (test with rm -rf .venv)
   - [ ] Documentation updated (CLAUDE.md, handoff, etc)
   - [ ] Verification command provided
   ```
   **Effort:** 15 minutes
   **Impact:** Makes agents self-audit

### HIGH (P1)

3. **Document Agent Policies**
   ```markdown
   # docs/policies/AGENT_DECISIONS.md
   - How to run tests: `uv run pytest` (never isolated pytest)
   - How to enforce linting: `./bin/pre-push-check.sh` (not git hooks)
   - Rationale for each decision
   ```
   **Effort:** 30 minutes
   **Impact:** Stops thrashing, agents reference this instead of guessing

4. **CLAUDE.md Sync Verification**
   ```bash
   # bin/verify-claude-md.sh
   # Checks that all commands in CLAUDE.md actually work
   # Catches drift like show-context.sh → show-context.py
   ```
   **Effort:** 2 hours
   **Impact:** Documentation stays accurate

### MEDIUM (P2)

5. **Session Handoff Schema Validation**
   - Enforce that handoff includes "persistence verified: yes/no"
   - Agent must attest: "Did you test this in fresh session?"
   **Effort:** 1 hour
   **Impact:** Makes session-only fixes visible

6. **Automated Quick Start Test**
   ```bash
   # tests/test_quick_start.sh
   # Runs all commands from CLAUDE.md "Quick Start" section
   # Fails if any command fails
   ```
   **Effort:** 2 hours
   **Impact:** Catches quick start regressions

## ANTI-PATTERNS TO DETECT

### Pattern: "Fixed" Without Git Commit
```bash
# Agent runs command manually
uv sync --all-extras
# Tests pass
# Agent claims "fixed"
# But change not in system-boot.sh or anywhere
```
**Detection:** Grep for "fix" in commit messages, verify files changed include persistent locations

### Pattern: Documentation Drift
```bash
# File renamed: show-context.sh → show-context.py
# Docs still reference old name
# Works until command copy-pasted
```
**Detection:** Parse CLAUDE.md for commands, verify they execute

### Pattern: Agent Thrashing
```bash
# Agent A: "Add feature X"
# Agent B: "Revert feature X"
# Agent C: "Add feature X again"
```
**Detection:** Git log for revert patterns, create policy docs for common decisions

## MEASUREMENT

### How to Track This

1. **Hidden Dependency Counter**
   - Track "Issues opened: session-only fix"
   - Goal: 0 per month

2. **Documentation Accuracy Score**
   - % of CLAUDE.md commands that execute successfully
   - Run `bin/verify-claude-md.sh` weekly
   - Goal: 100%

3. **Agent Thrashing Metric**
   - Count: reverts in last 30 days
   - Goal: ≤ 1 per month (only intentional reverts)
