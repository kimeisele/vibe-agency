# Session Handoff Scripts

ONE COMMAND to get full session context: `./bin/show-context.py`

## Quick Start (For Next Agent)

```bash
# Get full context in one command
./bin/show-context.py
```

This shows:
- ✅ Session handoff (completed work, next TODOs, critical files)
- ✅ System status (current branch, last commit, test status)

## Scripts

### `show-context.py` ⭐ MAIN COMMAND
Displays full session context (session handoff + system status)

**Usage:**
```bash
./bin/show-context.py
```

**Output:**
- Session handoff from previous agent
- System status (auto-updated)
- Quick commands for deeper inspection

### `update-system-status.sh`
Updates `.system_status.json` with current git state

**Usage:**
```bash
./bin/update-system-status.sh
```

**Creates/Updates:**
- `.system_status.json` - Current branch, commits, test status

**Called by:**
- Git hooks (if installed)
- Manually when needed

### `create-session-handoff.sh`
Interactive helper to create `.session_handoff.json`

**Usage:**
```bash
./bin/create-session-handoff.sh
```

**Prompts for:**
- From session (branch name)
- From agent (who is handing off)
- Completed work
- Artifacts created
- Next session TODOs

**Creates:**
- `.session_handoff.json` - Manual handoff file

## Files

### `.session_handoff.json` (Manual)
Created at end of session by human/agent

**Contains:**
- Completed work
- Artifacts created
- Next session TODOs
- Context for next session
- Critical files to understand
- Anti-patterns to avoid

**Create:**
```bash
./bin/create-session-handoff.sh  # Interactive helper
# OR manually edit the file
```

### `.system_status.json` (Auto-updated)
Created/updated by `update-system-status.sh`

**Contains:**
- Current git branch
- Last commit (sha, message, date)
- Working directory status
- Test status

**Update:**
```bash
./bin/update-system-status.sh  # Manual
# OR install git hooks for automatic updates
```

## Git Hooks (Optional)

Auto-update system status after commits/pushes

**Install:**
```bash
git config core.hooksPath .githooks
```

**Uninstall:**
```bash
git config --unset core.hooksPath
```

**Hooks:**
- `.githooks/post-commit` - Updates status after commit
- `.githooks/post-push` - Updates status after push

## Workflow

### End of Session (Creating Handoff)

```bash
# 1. Create session handoff (interactive)
./bin/create-session-handoff.sh

# 2. Or manually create/edit .session_handoff.json
vim .session_handoff.json

# 3. Update system status
./bin/update-system-status.sh

# 4. Commit handoff files
git add .session_handoff.json .system_status.json
git commit -m "docs: Add session handoff for next agent"
git push
```

### Start of Session (Reading Handoff)

```bash
# 1. Get full context (ONE COMMAND)
./bin/show-context.py

# 2. Read full details if needed
cat .session_handoff.json
cat .system_status.json

# 3. Verify system claims
cat CLAUDE.md | grep 'Verify Command'
```

## Design Philosophy

✅ **Robust** - Automated system status updates (via git hooks)
✅ **Minimal** - Simple shell scripts + JSON files (no abstractions)
✅ **Holistic** - Two handoff types (manual session + auto system status)
✅ **ONE COMMAND** - `./bin/show-context.py` gives full context

**Two-File System:**
1. `.session_handoff.json` - Rich context from previous agent (manual)
2. `.system_status.json` - Current git/test state (auto-updated)

**Anti-patterns avoided:**
- ❌ No validation/schema (keep it simple)
- ❌ No HandoffManager class (no abstractions)
- ❌ No complex orchestration (just shell + JSON)

## Examples

### Example: show-context.py output

```
════════════════════════════════════════════════════════════════
📋 SESSION CONTEXT
════════════════════════════════════════════════════════════════

━━━ SESSION HANDOFF (from previous agent) ━━━

From: Claude Code (System Architect)
Session: claude/analyze-architecture-plan-01SAywRRHvVSxGmTKRf61YML
Date: 2025-11-16

Completed:
  ✅ Architecture analysis
  ✅ TODO-based handoffs implementation
  ✅ Documentation updates

Next TODOs:
  🔲 Design holistic session handoff integration
  🔲 Implement minimal integration solution
  ...

━━━ SYSTEM STATUS (auto-updated) ━━━

Last updated: 2025-11-16T11:20:18Z
Current branch: claude/continue-session-handoff-01SAywRRHvVSxGmTKRf61YML
Last commit: 3b8facf - Merge pull request #57
Working directory: ⚠️  Modified
Tests (planning): ✅ Passing
```

### Example: .session_handoff.json structure

```json
{
  "from_session": "claude/previous-branch",
  "from_agent": "Claude Code",
  "date": "2025-11-16",
  "completed": [
    "Feature X implementation",
    "Tests added"
  ],
  "next_session_todos": [
    "Implement feature Y",
    "Update documentation"
  ],
  "context_for_next_session": {
    "critical_insight": "Key insight here"
  }
}
```

### Example: .system_status.json structure

```json
{
  "timestamp": "2025-11-16T11:20:18Z",
  "git": {
    "branch": "claude/feature-branch",
    "last_commit": {
      "sha": "3b8facf",
      "message": "feat: Add feature X"
    },
    "working_directory_clean": true
  },
  "tests": {
    "planning_workflow": "passing"
  }
}
```

## See Also

- **CLAUDE.md** - Operational truth (what works, how to verify)
- **.session_handoff.json** - Previous agent's handoff
- **.system_status.json** - Current system state
