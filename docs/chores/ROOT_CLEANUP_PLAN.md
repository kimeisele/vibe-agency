# Root Directory Cleanup Plan

**Status:** 📋 PLANNING
**Date Created:** 2025-11-16
**Priority:** ONGOING (continuous chore, not one-time)

---

## 🎯 Purpose

Keep root directory signal-to-noise ratio high by:
- ✅ Keeping critical reference docs only
- 📁 Moving historical reports and analysis
- 🗑️ Deleting obsolete content

**Goal:** Root should have <10 files, all critical references

---

## 📋 Root Directory Audit

### Current State (29+ files)

```bash
$ ls -1 /home/user/vibe-agency/*.md /home/user/vibe-agency/*.txt /home/user/vibe-agency/*.json 2>/dev/null | wc -l
# Result: 29+ files in root (too many)
```

---

## ✅ KEEP IN ROOT (Critical References - 6 files)

These documents are essential references for ALL developers:

| File | Purpose | Type | Keep |
|------|---------|------|------|
| **README.md** | Project overview, setup guide | Reference | ✅ KEEP |
| **CLAUDE.md** | Operational truth protocol | Reference | ✅ KEEP |
| **SSOT.md** | Implementation decisions | Reference | ✅ KEEP |
| **ARCHITECTURE_V2.md** | Conceptual model | Reference | ✅ KEEP |
| **CHANGELOG.md** | Version history | Reference | ✅ KEEP |
| **CONTRIBUTING.md** | Contribution guidelines | Reference | ✅ KEEP |

---

## 📁 MOVE TO `docs/reports/` (Historical Analysis)

These are historical reports from audit/analysis sessions:

| File | Purpose | Action | Priority |
|------|---------|--------|----------|
| ARCHITECTURE_ANALYSIS_2025-11-16.md | Architecture audit | ➡️ MOVE | P1 |
| ARCHITECTURE_BREAKDOWN_REPORT.md | Component breakdown | ➡️ MOVE | P1 |
| CRITICAL_AUDIT_FINDINGS.md | Audit findings | ➡️ MOVE | P1 |
| CRITICAL_PATH_STATUS.md | Status snapshot | ➡️ MOVE | P1 |
| DEFENSE_STRATEGY_UV.md | Defense strategy analysis | ➡️ MOVE | P2 |
| DEFENSE_VALIDATION_REPORT.md | Defense validation | ➡️ MOVE | P2 |
| E2E_TEST_REPORT.md | E2E test results | ➡️ MOVE | P2 |
| FOUNDATION_ASSESSMENT.md | Foundation assessment | ➡️ MOVE | P1 |
| FOUNDATION_HARDENING_PLAN.md | Hardening plan | ➡️ MOVE | P2 |
| FOUNDATION_MIGRATION_PLAN.md | Migration plan | ➡️ MOVE | P2 |
| GOLDEN_PATH_TEST.md | Test results | ➡️ MOVE | P2 |
| MIGRATION_NOTES.md | Migration notes | ➡️ MOVE | P2 |
| PRE_FLIGHT_ASSESSMENT.md | Pre-flight checklist | ➡️ MOVE | P2 |
| REALITY_CHECK_REPORT.md | Reality check | ➡️ MOVE | P1 |
| REAL_E2E_TEST_RESULT.md | E2E results | ➡️ MOVE | P2 |

**Total to move:** 15 files

---

## 📁 MOVE TO `docs/releases/` (Release Documentation)

These are release-related documents:

| File | Purpose | Action |
|------|---------|--------|
| RELEASE_NOTES_v1.1.md | Release v1.1 notes | ➡️ MOVE |
| RELEASE_NOTES_v1.2.md | Release v1.2 notes | ➡️ MOVE |

**Total to move:** 2 files

---

## 🗑️ DELETE or ARCHIVE (Obsolete Content)

These files should be deleted or moved to archive:

| File | Type | Reason | Action |
|------|------|--------|--------|
| PR_DESCRIPTION.md | PR doc | Obsolete template | 🗑️ DELETE |
| PR_DESCRIPTION_FINAL.md | PR doc | Obsolete (superseded) | 🗑️ DELETE |
| PR_DESCRIPTION_SESSION_HANDOFF.md | PR doc | Obsolete (superseded) | 🗑️ DELETE |
| PR_TITLE.txt | PR doc | Obsolete template | 🗑️ DELETE |
| COMPOSED_PROMPT.md | Temporary | Old session artifact | 🗑️ DELETE |
| COMPOSED_PROMPT_REGISTRY_TEST.md | Temporary | Old test artifact | 🗑️ DELETE |

**Total to delete:** 6 files

---

## ❓ NEEDS USER DECISION

These files have unclear purpose - ask user before moving/deleting:

| File | Issue | Options |
|------|-------|---------|
| AGENTS_START_HERE.md | Might be useful for new developers? | Keep / Move to docs/ / Delete |
| Any other files not categorized above | Unknown | Case-by-case |

---

## 📊 Target State

After cleanup:

```
/vibe-agency/ (root)
├── README.md ✅
├── CLAUDE.md ✅
├── SSOT.md ✅
├── ARCHITECTURE_V2.md ✅
├── CHANGELOG.md ✅
├── CONTRIBUTING.md ✅
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .github/
├── agency_os/
├── system_steward_framework/
├── docs/
│   ├── reports/ ← 15 moved files + audit reports
│   ├── releases/ ← 2 moved files
│   ├── architecture/
│   └── chores/ (this file)
├── tests/
├── scripts/
├── workspaces/
└── bin/

Total files in root: ~10 (signal-to-noise ✅)
```

---

## 🚀 Execution Plan

### Phase 1: Move Reports (P1 - This Week)

```bash
# Verify docs/reports/ exists
mkdir -p docs/reports/

# Move analysis/audit files
mv ARCHITECTURE_ANALYSIS_2025-11-16.md docs/reports/
mv ARCHITECTURE_BREAKDOWN_REPORT.md docs/reports/
mv CRITICAL_AUDIT_FINDINGS.md docs/reports/
mv CRITICAL_PATH_STATUS.md docs/reports/
mv FOUNDATION_ASSESSMENT.md docs/reports/
mv REALITY_CHECK_REPORT.md docs/reports/
mv REAL_E2E_TEST_RESULT.md docs/reports/

# Note: Already moved by previous sessions:
# - CLAUDE_MD_AUDIT_2025-11-16.md → docs/reports/
# - README_AUDIT_2025-11-16.md → docs/reports/
```

### Phase 2: Move Release Notes (P2 - This Week)

```bash
# Verify docs/releases/ exists
mkdir -p docs/releases/

# Move release documentation
mv RELEASE_NOTES_v1.1.md docs/releases/
mv RELEASE_NOTES_v1.2.md docs/releases/
```

### Phase 3: Delete Obsolete Files (P3 - This Week)

```bash
# Delete PR documentation
rm -f PR_DESCRIPTION.md
rm -f PR_DESCRIPTION_FINAL.md
rm -f PR_DESCRIPTION_SESSION_HANDOFF.md
rm -f PR_TITLE.txt

# Delete temporary artifacts
rm -f COMPOSED_PROMPT.md
rm -f COMPOSED_PROMPT_REGISTRY_TEST.md
```

### Phase 4: Verify and Commit

```bash
# Verify cleanup
ls -1 *.md *.txt | wc -l  # Should be ~6
# Expected: ~6 files (README, CLAUDE, SSOT, ARCHITECTURE, CHANGELOG, CONTRIBUTING)

# Show what was moved
echo "Files in docs/reports/:"
ls -1 docs/reports/*.md | wc -l

echo "Files in docs/releases/:"
ls -1 docs/releases/*.md | wc -l

# Commit
git add -A
git commit -m "chore: Clean up root directory - move reports and release notes

- Move 15 analysis/audit reports to docs/reports/
- Move 2 release notes to docs/releases/
- Delete 6 obsolete PR files
- Reduce root files from 29+ to ~10
- Signal-to-noise ratio: ✅ improved"

git push
```

---

## 🔄 Ongoing Maintenance

**This is NOT a one-time cleanup - it's a CONTINUOUS chore.**

### Every Session

Check root directory for new files:
```bash
# List new files
git status --porcelain | grep "??" | grep -E "\.(md|txt|json)$"
```

**Rule:** Signal > Noise
- ✅ New critical reference doc? KEEP in root
- ❌ Analysis/report from this session? Move to docs/reports/
- ❌ Historical artifact? Delete or archive

### Before Every Push

```bash
# Verify root cleanliness
ls -1 *.md *.txt *.json 2>/dev/null | wc -l
# Should be <10

# If >10:
# 1. Identify new files: git status
# 2. Decide: keep/move/delete
# 3. Execute cleanup
# 4. Commit with "chore: root cleanup"
```

---

## 📝 Decision Log

### Files Already Moved (Previous Sessions)

- ✅ `docs/reports/CLAUDE_MD_AUDIT_2025-11-16.md` (created by this session)
- ✅ `docs/reports/README_AUDIT_2025-11-16.md` (created by this session)

### Files Ready to Move (This Session - Awaiting Execution)

- ⏳ ARCHITECTURE_ANALYSIS_2025-11-16.md → docs/reports/
- ⏳ CRITICAL_AUDIT_FINDINGS.md → docs/reports/
- ⏳ FOUNDATION_ASSESSMENT.md → docs/reports/
- ⏳ And 12 more (see Phase 1 above)

### Files Ready to Delete

- ⏳ PR_DESCRIPTION.md
- ⏳ PR_DESCRIPTION_FINAL.md
- ⏳ PR_DESCRIPTION_SESSION_HANDOFF.md
- ⏳ PR_TITLE.txt
- ⏳ COMPOSED_PROMPT.md
- ⏳ COMPOSED_PROMPT_REGISTRY_TEST.md

---

## ✅ Success Criteria

Cleanup is complete when:

1. ✅ Root has <10 .md/.txt/.json files
2. ✅ All critical references remain in root
3. ✅ All reports moved to docs/reports/
4. ✅ All release notes moved to docs/releases/
5. ✅ All obsolete files deleted
6. ✅ Commit message clear and descriptive
7. ✅ CI/CD passes (no broken links, etc.)

---

## 🧭 Related Documents

- **SSOT.md** - Implementation decisions (also in root, but critical)
- **CLAUDE.md** - Anti-hallucination protocol (also in root, but critical)
- **docs/chores/** - Other maintenance chores
- **docs/reports/** - Destination for historical reports
- **docs/releases/** - Destination for release notes

---

## 📊 Impact Analysis

### What Changes

- Root directory becomes cleaner (signal-to-noise ✅)
- Easier to find critical docs (no clutter)
- Historical reports organized in docs/reports/
- Release notes organized in docs/releases/

### What Stays the Same

- All content preserved (nothing lost)
- All links work (git handles moves)
- All functionality unchanged
- All tests pass (purely organizational)

### Risk Level

**🟢 LOW** - This is purely organizational. No code changes, no logic changes.

---

## 🎯 Next Steps

1. **Approve Plan** - User confirms cleanup strategy
2. **Execute Phase 1** - Move reports (15 files)
3. **Execute Phase 2** - Move release notes (2 files)
4. **Execute Phase 3** - Delete obsolete files (6 files)
5. **Verify** - Count files, check docs/reports/, confirm CI/CD
6. **Commit** - Create cleanup commit
7. **Push** - Push to branch

---

**Last Updated:** 2025-11-16
**Created By:** Claude Code (audit session)
**Status:** 📋 READY FOR EXECUTION (awaiting user approval)
