# Project Health Audit - 2025-11-14

**Auditor:** Claude Code (System Architect)
**Date:** 2025-11-14 20:05 UTC
**Scope:** Full repository scan for obsolete files, inconsistencies, and maintenance needs
**Verdict:** 🟢 **HEALTHY** (with minor cleanup recommendations)

---

## Executive Summary

✅ **Good News:**
- Repository structure is clean (only 7 root .md files)
- Archive system works (1.3MB, 28 deprecated files properly moved)
- Minimal technical debt (38 TODO markers, most are planned "Phase 4" tasks)
- Recent documentation (most docs updated within last 24 hours)

⚠️ **Minor Issues:**
- Some handler stubs (testing, deployment, maintenance) have "Phase 3 TODO" markers
- No automated staleness detection
- Workspace artifacts not cleaned up regularly

---

## Detailed Findings

### 📊 Repository Stats

| Category | Count | Status |
|----------|-------|--------|
| Root .md files | 7 | ✅ Minimal |
| Python files | 26 | ✅ Reasonable |
| Agent task files | 42 | ✅ Well-structured |
| Workspace JSON artifacts | 19 | ⚠️ Should be cleaned periodically |
| Workspace .md files | 7 | ✅ Minimal |
| TODO/FIXME markers | 38 | ✅ Mostly planned (Phase 4) |
| Archive size | 1.3MB (28 files) | ✅ Archive working |

### 📁 File Age Analysis

**Recent (< 24h):**
- ✅ `CHANGELOG.md` - Created today
- ✅ `README.md` - Updated today
- ✅ `ADR-003_Delegated_Execution_Architecture.md` - Created today
- ✅ `DELEGATED_EXECUTION_GUIDE.md` - Created today

**Older but stable:**
- 🟡 `RELEASE_NOTES_v1.1.md` - Last updated 2025-11-14 06:33
- 🟡 `RELEASE_NOTES_v1.2.md` - Last updated 2025-11-14 06:33
- 🟡 Most docs/ files - Last updated 2025-11-14 06:33

**Archive:**
- ✅ 28 files properly archived in `docs/archive/`
- ✅ Includes old architecture versions, deprecated guides

### 🔍 Code Quality Findings

**Handler Stubs (To Be Implemented):**

```python
# agency_os/00_system/orchestrator/handlers/testing_handler.py
# TODO (Phase 3): Full implementation

# agency_os/00_system/orchestrator/handlers/deployment_handler.py
# TODO (Phase 3): Full implementation

# agency_os/00_system/orchestrator/handlers/maintenance_handler.py
# TODO (Phase 3): Full implementation
```

**Verdict:** These are **intentional stubs** for future phases. Not technical debt.

**Other TODOs:**

1. `core_orchestrator.py:169` - "TODO: Full JSON Schema validation with jsonschema library"
   - **Priority:** Medium
   - **Impact:** Better error messages
   - **Status:** Enhancement, not blocker

2. `orchestrator.py:323` - "TODO: This should eventually call ORCHESTRATOR_PROMPT.md for AI-driven conversation"
   - **Priority:** Low (deprecated file - use core_orchestrator.py)
   - **Impact:** N/A
   - **Status:** Can be removed (legacy)

3. `coding_handler.py:195` - "TODO: Add schema validation in Phase 4"
   - **Priority:** Low
   - **Impact:** Better artifact validation
   - **Status:** Planned enhancement

### 🗑️ Cleanup Candidates

**None found!**

The only "deprecated" files are quality gate files that are actually in use:
- `agency_os/01_planning_framework/agents/VIBE_ALIGNER/gates/gate_complexity_within_threshold.md`
- `agency_os/01_planning_framework/agents/research/FACT_VALIDATOR/gates/gate_quality_threshold.md`

These are **NOT deprecated** - filename is misleading. Should rename to `gate_*.md` pattern.

### 📦 Workspace Artifacts

**Current State:**
- 19 JSON files (artifacts from test projects)
- 7 .md files

**Recommendation:**
Create a `workspaces/.gitignore` to exclude test artifacts from repo, OR add a cleanup script.

---

## Recommendations (Prioritized)

### 🔴 High Priority (Do Now)

1. **✅ DONE** - Create `CHANGELOG.md` (completed)
2. **✅ DONE** - Update `README.md` with ADR-003 (completed)

### 🟡 Medium Priority (Next Session)

3. **Add .gitignore for workspace artifacts**
   ```bash
   echo "workspaces/*/artifacts/**/*.json" >> .gitignore
   echo "workspaces/*/artifacts/**/*.md" >> .gitignore
   ```

4. **Rename misleading gate files**
   ```bash
   # Remove "deprecated" from filenames
   mv gate_complexity_within_threshold.md gate_complexity_threshold.md
   mv gate_quality_threshold.md gate_quality_check.md
   ```

5. **Remove legacy `orchestrator.py`** (if `core_orchestrator.py` is stable)
   - Move to `docs/archive/orchestrator/orchestrator_v1.py`
   - Update any references

### 🟢 Low Priority (Future)

6. **Implement JSON Schema validation** (core_orchestrator.py:169)
7. **Add staleness detection script** (see proposal below)
8. **Create workspace cleanup command**
   ```bash
   vibe-cli cleanup --older-than=30d
   ```

---

## Staleness Detection Proposal

**Concept:** Simple Python script that checks file age and warns about outdated docs.

```python
#!/usr/bin/env python3
"""
Staleness Detector - Warns about potentially outdated documentation
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

STALENESS_THRESHOLDS = {
    "README.md": 30,  # days
    "CHANGELOG.md": 7,
    "docs/guides/*.md": 60,
    "docs/architecture/ADR-*.md": 90,
    "agency_os/**/prompts/*.md": 30,
}

def check_staleness(repo_root):
    warnings = []
    now = datetime.now()

    for pattern, max_age_days in STALENESS_THRESHOLDS.items():
        for file_path in Path(repo_root).glob(pattern):
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age_days = (now - mtime).days

            if age_days > max_age_days:
                warnings.append({
                    "file": file_path,
                    "age_days": age_days,
                    "threshold": max_age_days,
                    "severity": "warning" if age_days < max_age_days * 2 else "critical"
                })

    return warnings
```

**Usage:**
```bash
python scripts/check_staleness.py
# Output:
# ⚠️  WARNING: docs/guides/USER_GUIDE.md is 45 days old (threshold: 30 days)
# 🔴 CRITICAL: README.md is 90 days old (threshold: 30 days)
```

**Do we need this?**

**Pros:**
- ✅ Automatic detection of outdated docs
- ✅ Prevents documentation drift
- ✅ Simple to implement (30 lines of Python)

**Cons:**
- ❌ Can create false positives (stable docs that don't need updates)
- ❌ Adds maintenance overhead
- ❌ Current repo is clean - not needed yet

**Recommendation:** **Wait until we have 10+ contributors.** For now, manual audit (like this one) every 2 weeks is sufficient.

---

## Maintenance Agent Proposal

**User's idea:** A VIBE_ALIGNER LIGHT for internal maintenance tasks.

### Concept

```yaml
agent_name: JANITOR
purpose: Automated repository health checks and cleanup
mode: light  # Simplified VIBE_ALIGNER (no user interaction)

tasks:
  - staleness_check:
      threshold_days: 30
      patterns: ["README.md", "docs/**/*.md"]

  - workspace_cleanup:
      older_than_days: 30
      patterns: ["workspaces/*/artifacts/*.json"]

  - todo_analysis:
      patterns: ["**/*.py", "**/*.md"]
      categories: ["TODO", "FIXME", "HACK", "XXX"]

  - link_checker:
      check_internal_links: true
      check_external_links: false

output: maintenance_report.md
```

**Usage:**
```bash
vibe-cli maintenance --dry-run
# Output: Shows what would be cleaned/flagged

vibe-cli maintenance --run
# Output: Executes cleanup, generates report
```

### Implementation Complexity

**Estimate:** 2-4 hours

**Files to create:**
1. `agency_os/00_system/agents/JANITOR/_prompt_core.md` (~200 lines)
2. `agency_os/00_system/orchestrator/handlers/maintenance_handler.py` (extend existing)
3. `vibe-cli` - add `maintenance` subcommand

**Is it worth it?**

**Right now:** ❌ **No** - Repo is clean, manual audit works
**After 10+ contributors:** ✅ **Yes** - Automated checks become valuable

---

## Verdict

🟢 **Project health: GOOD**

**Immediate actions:**
- ✅ CHANGELOG created
- ✅ README updated
- 🟡 Add workspace .gitignore (5 minutes)

**No urgent cleanup needed.**

**Maintenance Agent:** Defer until repo has >10 contributors or >100 docs.

**Next review:** 2 weeks (2025-11-28)

---

## Audit Trail

| Date | Auditor | Findings | Action |
|------|---------|----------|--------|
| 2025-11-14 | Claude Code | Clean repo, minor TODOs | CHANGELOG + README update |
| 2025-11-28 | TBD | TBD | TBD |
