# Git Branch Strategy for Boot Sequence

**Status:** PROPOSAL - Next Phase (v1.1)  
**Date:** 2025-11-18  
**Priority:** P1 (Architectural Decision)  
**Related:** PR #111, Issue #109

---

## Problem Statement

Current boot sequence allows agents to:
1. Work on `main` branch (dangerous - no isolation)
2. Work on stale feature branches (confusing state)
3. Leave uncommitted changes (state hidden)
4. Not know which branch/PR their work belongs to

**Result:** Unclear accountability, hard to track changes, risky merges.

---

## Proposed Solution: Branch-Aware Boot

### Core Principle
**Every task execution = new isolated feature branch**

Boot should:
1. Detect if on `main` → auto-create feature branch
2. Require clean git state before proceeding
3. Track branch name in session handoff
4. Commit work to feature branch
5. Suggest PR creation at end

---

## Detailed Design

### Pre-Boot Checks (in order)

```
1. Check git availability
   ├─ If unavailable → warn, proceed (graceful)
   └─ If available → continue

2. Check current branch
   ├─ If on `main` → go to Step 3
   ├─ If on feature/* → go to Step 4
   └─ If on other → show warning, ask confirmation

3. Auto-create feature branch (if on main)
   ├─ Name: feature/{task}-{timestamp}
   │   Example: feature/implement-20251118-143022
   ├─ Checkout: git checkout -b feature/{task}-{timestamp}
   └─ Proceed to Step 4

4. Check for uncommitted changes
   ├─ If uncommitted → show soft halt warning (current behavior)
   │   Options: commit, stash, or --force
   └─ If clean → proceed to boot

5. Boot with context
   └─ Agent sees which branch they're on
```

### Branch Naming Convention

```
feature/{task}-{YYYYMMDD-HHMMSS}

Examples:
- feature/implement-20251118-143022
- feature/debug-20251118-150045
- feature/test-20251118-151530
```

**Why timestamp?**
- Unique (prevents collisions)
- Sortable (chronological ordering)
- Readable (humans can parse it)
- Lean (no complex UUID/hash needed)

---

## System Prompt Update

Add to STEWARD prompt:

```
BRANCH ISOLATION:
Your work is automatically isolated in a feature branch.

Current branch: {current_branch}

After completing this task:
1. Commit all changes: git add . && git commit -m "..."
2. Verify: git status (should be clean)
3. Push: git push origin {current_branch}
4. Create PR from GitHub UI (link auto-suggested)

DO NOT:
❌ Switch branches mid-task
❌ Merge your own PRs
❌ Push to main directly
```

---

## Session Handoff Extension

Add to `.session_handoff.json`:

```json
{
  "git": {
    "branch": "feature/implement-20251118-143022",
    "commits_in_branch": 3,
    "pr_created": false,
    "pr_url": null
  }
}
```

---

## Implementation Phases

### Phase 1: Detection (this PR)
- ✅ Detect main branch
- ✅ Show warning (soft halt, don't force)
- ✅ Document strategy

### Phase 2: Auto-Creation (v1.1)
- Auto-create feature branch on boot
- Update system prompt with branch info
- Extend session handoff

### Phase 3: PR Automation (v1.2)
- Auto-detect task completion
- Suggest PR creation
- Link PR in session handoff

### Phase 4: Cleanup (v1.3)
- Track merged branches
- Archive/delete old feature branches
- Provide branch history

---

## Edge Cases & Handling

### Case 1: Agent starts on detached HEAD
```
Behavior: Soft halt
Message: "Detached HEAD detected. Create feature branch first."
Option: git checkout -b feature/...
```

### Case 2: Branch already exists (name collision - rare)
```
Behavior: Auto-increment timestamp
Example: feature/implement-20251118-143022-1
Retry: Create with suffix until unique
```

### Case 3: Git not available
```
Behavior: Proceed with warning
Message: "Git unavailable - skipping branch isolation"
State: Continue on current branch (unsafe but graceful)
```

### Case 4: Agent on feature branch from 1 week ago
```
Current: Show status with commit count
Suggestion: "Branch 1 week old with 2 commits. Create fresh branch?"
Option 1: Continue on existing (keeps history)
Option 2: Create new fresh branch
```

### Case 5: Multiple uncommitted changes on feature branch
```
Current behavior (already handled):
- Soft halt warning
- 3 options: commit, stash, force
- No blocking
```

---

## Scalability

### Single Agent
- Boot on main → auto-creates feature branch
- Works on feature/task-timestamp
- Commits + pushes
- ✅ Clean workflow

### Multiple Agents (Sequential)
- Agent A: boots → feature/task1-t1 → commits → push
- Agent B: boots on main → pulls → feature/task2-t2 → commits → push
- ✅ No conflicts (different branches)

### Multiple Agents (Concurrent)
- Agent A & B both boot simultaneously
- A creates: feature/impl-t1
- B creates: feature/impl-t1-1 (collision handling)
- ✅ No race conditions

---

## Lean Implementation Principles

❌ **NO:**
- Complex branch management logic
- Automatic PR creation (too opinionated)
- Forced rebasing/merging
- Branch deletion automation
- Conflict resolution

✅ **YES:**
- Simple branch name generation
- Soft halts (informational, not blocking)
- Clear handoff via session state
- Graceful git failure handling
- Human-readable branch names

---

## Success Metrics

✅ Agents cannot accidentally work on `main`
✅ Each task is isolated in its own branch
✅ Branch context is visible in boot dashboard
✅ Session handoff tracks branch + PR info
✅ Graceful degradation if git unavailable
✅ < 50 LOC implementation per phase
✅ No performance impact on boot sequence

---

## Next Steps

### Immediate (this PR)
- [ ] Document this strategy (DONE)
- [ ] Add "main branch detection" warning to boot
- [ ] Include strategy in PR #111

### Phase 2 (v1.1)
- [ ] Implement auto-branch creation
- [ ] Update system prompt with branch info
- [ ] Extend session handoff schema
- [ ] Add branch info to dashboard

### Phase 3+ (Deferred)
- PR automation (v1.2)
- Branch cleanup (v1.3)
- Integration with CI/CD (v1.4)

---

## Related Documents

- **Boot Sequence:** `agency_os/core_system/runtime/boot_sequence.py`
- **System Prompt:** See `_get_system_prompt()` method
- **Session Handoff:** `.session_handoff.json` format
- **Playbook AOS Integration:** `docs/architecture/PLAYBOOK_AOS_INTEGRATION.md`

---

## Feedback & Questions

**What we know works:**
- Soft halts (warnings, not blocking)
- Graceful git error handling
- Session-based state tracking

**What needs validation:**
- Is auto-branch-on-boot too aggressive?
- Should we allow main branch work in specific scenarios?
- Branch naming - timestamp vs task vs both?
- When to suggest branch creation vs auto-create?

**Open for discussion:**
- Preferences on branch naming scheme?
- Should phase 2 auto-create or just auto-warn?
- How aggressive should "main branch protection" be?
