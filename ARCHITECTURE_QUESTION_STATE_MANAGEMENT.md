# Architecture Question: System State Management Design

**Date:** 2025-11-17
**Participants:** kimeisele, Claude Code, Claude.ai (expert review)
**Priority:** P0 (blocking all work - fragmented state causing regressions)

---

## The Problem We're Solving

**Symptom:** Agent starts fresh session → sees outdated context → doesn't know about recent work.

**Example:**
```
Agent 1 (Nov 16):
  → Creates system_steward_framework/ directory
  → Commits and pushes
  → ❌ Forgets to update .session_handoff.json

Agent 2 (Nov 17):
  → Sees MOTD: "Session: Architecture Migration" (STALE!)
  → Has NO IDEA system_steward_framework exists
  → Starts working on wrong context
```

**Root Cause:** We have **4 fragmentated state sources** that are NEVER integrated:

```
.system_status.json              ← Auto-gen, NOT committed (ephemeral!)
.session_handoff.json            ← Manual, committed (forgotten!)
.vibe/system_integrity_manifest  ← Auto-gen, committed (checksums only)
git log + git status             ← Auto, committed (raw data, no aggregation)
```

---

## Current State (IST)

### File Inventory

| File | Purpose | Generated | Committed | Stale Risk |
|------|---------|-----------|-----------|------------|
| `.system_status.json` | Git/linting/tests status | Auto (git hooks) | ❌ No | ⚠️ High (lost on fresh checkout) |
| `.session_handoff.json` | Manual agent handoff | Manual | ✅ Yes | ⚠️ High (agents forget to update) |
| `.vibe/system_integrity_manifest.json` | Checksums for critical files | Auto (script) | ✅ Yes | ✅ Low (auto-gen on demand) |
| `git log` | Commit history | Auto (git) | ✅ Yes | ✅ Low (git truth) |
| `git status` | Working directory state | Auto (git) | N/A | ✅ Low (runtime query) |

### Data Flow (MOTD Display)

```
vibe-cli boot
  └─> Layer 0: verify_system_integrity()
       └─> Reads: .vibe/system_integrity_manifest.json ✅ Works
  └─> Layer 1: display_motd()
       ├─> Reads: .system_status.json
       │    └─> Shows: Git, Linting, Tests, Steward ⚠️ EPHEMERAL
       └─> Reads: .session_handoff.json
            └─> Shows: Session summary ⚠️ MANUAL (forgotten!)

  ❌ MISSING: Recent commits (git log)
  ❌ MISSING: New directories since last session
  ❌ MISSING: Uncommitted work details
```

### The Fragmentation Problem

**No single file contains:**
- System health (linting, tests) ← in .system_status.json (ephemeral!)
- Session context (who, what, when) ← in .session_handoff.json (manual!)
- Recent activity (commits, changes) ← in git (not aggregated!)
- Workflow state (SDLC phase, tasks) ← MISSING ENTIRELY!

**Result:** Agents start blind, work gets lost, regressions happen.

---

## Requirements (SOLL)

### Non-Negotiable Constraints

1. **Single Source of Truth per Domain**
   - System Health → ONE authoritative source
   - Session Context → ONE authoritative source
   - Recent Activity → ONE authoritative source

2. **Auto-Generated Where Possible**
   - Manual updates = guaranteed staleness
   - Prefer git/scripts over human memory

3. **Committed to Git**
   - No ephemeral files for critical state
   - Fresh checkout = full context available

4. **Displayed in MOTD (Unavoidable)**
   - Layer 0 integrity check (existing ✅)
   - Layer 1 MOTD (existing, but incomplete ⚠️)

5. **Lean & Robust**
   - No band-aids (fix root cause, not symptoms)
   - No "one more JSON file" without integration plan
   - Minimize file count (consolidate where possible)

---

## Architecture Question for Claude.ai

**Given:**
- 4 fragmentated state sources (see "Current State" above)
- MOTD displays only 2 of them (.system_status.json, .session_handoff.json)
- Agents start blind to recent work (git log, new directories)

**Required:**
- Single source of truth per domain (system health, session, activity)
- Auto-generated (no manual updates)
- Committed to git (no ephemeral files for critical state)
- Displayed in MOTD (unavoidable context injection)

**Question:**
**What is the correct information architecture pattern for system state management in a multi-agent AI-assisted development environment?**

Specifically:

1. **File Structure:**
   - Should we consolidate into `.vibe/system_state.json` (single file)?
   - Or keep domain separation (`.vibe/health.json`, `.vibe/session.json`, `.vibe/activity.json`)?
   - Or use append-only log (`.vibe/session_activity.jsonl`)?

2. **Data Sources:**
   - Which state should be in committed files vs. runtime queries?
   - How do we aggregate git log + git status into "recent activity"?
   - Where does STEWARD kernel prompt live (currently in ephemeral .system_status.json)?

3. **Update Mechanism:**
   - Git hooks (post-commit, post-push) for auto-updates?
   - Script-based (`bin/update-system-state.sh`)?
   - Orchestrator-based (core_orchestrator.py updates manifest)?

4. **MOTD Integration:**
   - How should display_motd() consume these sources?
   - Should it read 1 file or aggregate multiple sources?
   - Should we show raw data or computed summaries?

5. **Regression Prevention:**
   - How do we ensure agents NEVER start with stale context?
   - What happens if an agent forgets to update state?
   - Can we make state updates AUTOMATIC (not manual)?

**We need a DESIGN PATTERN, not a quick fix.**

---

## Success Criteria

✅ Agent starts fresh session → sees accurate context (last 3 commits, new dirs, current state)
✅ Zero manual updates required (all state auto-generated or derived from git)
✅ Zero ephemeral files for critical state (everything committed)
✅ MOTD shows comprehensive context (health + session + activity)
✅ Single source of truth per domain (no duplicate/conflicting data)

---

## Open Questions

1. **Bedrock Layer:** Where do kernel prompts (STEWARD principles) live?
   - Currently: `.system_status.json` (ephemeral!)
   - Should be: ??? (committed file)

2. **Workflow State:** Do we need workspace/*/manifest.json integration?
   - GAD-002 mentions ProjectManifest (per-workspace)
   - How does this relate to SYSTEM state (.vibe/*)?

3. **Session Tracking:** How do we auto-track "what agent did what"?
   - Currently: Manual .session_handoff.json updates (forgotten!)
   - Alternative: Append-only .vibe/session_activity.jsonl?

4. **Git Integration:** Should we parse git log in MOTD or pre-compute?
   - Runtime query: `git log --oneline -3` (fast, always fresh)
   - Pre-computed: `.vibe/activity.json` (faster display, stale risk)

---

## Request

**Claude.ai:** Please review this architecture question and propose a **robust, lean design pattern** for system state management that satisfies all requirements and success criteria.

**Focus on:**
- Information architecture (file structure, data ownership)
- Update mechanisms (automation, not manual)
- Integration strategy (how MOTD consumes state)
- Regression prevention (impossible to start with stale context)

**Avoid:**
- Band-aid solutions (adding more files without integration)
- Manual processes (agents forget)
- Ephemeral state for critical data (lost on fresh checkout)

We're willing to refactor existing code to get this RIGHT, not just working.
