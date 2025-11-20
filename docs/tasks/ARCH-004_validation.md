# ARCH-004: Shadow Mode Validation Tooling

**Status:** ✅ COMPLETE
**Phase:** 2.5 (Foundation Scalability)
**Depends on:** ARCH-003 (Shadow Mode Dual Write)
**Date:** 2025-11-20

---

## 🎯 OBJECTIVE

Provide empirical validation tooling for the **Baking Period** between ARCH-003 (Shadow Mode Dual Write) and Phase 2 (Cutover to SQLite Primary).

**Question to Answer:**
> "Is the Database telling the truth?"

**Strategic Context:**
- ARCH-003 established dual-write mode (JSON → SQLite shadow copy)
- We need time-series evidence that SQLite accurately mirrors JSON state
- This tool enables confidence-building before promoting SQLite to primary source of truth

---

## 📊 DELIVERABLES

### 1. Validation Script: `bin/verify-shadow-mode.py`

**Purpose:** Deep comparison of JSON source of truth vs SQLite shadow copy

**Features:**
- ✅ Compare `project_manifest.json` → `missions` table
- ✅ Compare `project_memory.json` → v2 tables (session_narrative, domain_concepts, etc.)
- ✅ Field-level diff reporting (shows exact mismatches)
- ✅ Status badges: GREEN (match) / YELLOW (warnings) / RED (mismatches)
- ✅ Verbose mode for debugging
- ✅ JSON report output option

**Usage:**
```bash
# Basic validation
./bin/verify-shadow-mode.py

# Verbose output (shows all checks)
./bin/verify-shadow-mode.py --verbose

# Save report to file
./bin/verify-shadow-mode.py --json-output report.json

# Specify project root
./bin/verify-shadow-mode.py --project-root /path/to/project
```

**Exit Codes:**
- `0` = GREEN (100% match) or INCOMPLETE (shadow mode not initialized)
- `1` = RED (mismatches found)
- `2` = ERROR (validation failed to run)

---

### 2. vibe-shell Integration

**New Command:**
```bash
./bin/vibe-shell --verify-db
```

**Features:**
- ✅ Integrated into vibe-shell runtime
- ✅ Uses validation script with verbose output
- ✅ Proper error handling and exit codes
- ✅ User-friendly output formatting

**Health Check Integration:**
The `--health` command now includes Shadow Mode status as an observation:
```
👉 Shadow Mode: Database initialized (dual-write active)
⚪ Shadow Mode: Not initialized (database not found)
```

---

## 🔍 VALIDATION CHECKS

### Mission Table (Manifest → SQLite)

Validates that `project_manifest.json` correctly maps to `missions` table:

| Field | Source | Target Column |
|-------|--------|---------------|
| Project ID | `metadata.projectId` | `mission_uuid` |
| Phase | `status.projectPhase` | `phase` |
| Status | `status` (inferred) | `status` |
| Owner | `metadata.owner` | `owner` |
| Description | `metadata.description` | `description` |
| Created | `metadata.createdAt` | `created_at` |
| Updated | `metadata.lastUpdatedAt` | `updated_at` |
| Budget (Max) | `budget.max_cost_usd` | `max_cost_usd` |
| Budget (Current) | `budget.current_cost_usd` | `current_cost_usd` |
| API Version | `apiVersion` | `api_version` |

### Project Memory (Memory → v2 Tables)

Validates that `project_memory.json` correctly maps to v2 tables:

| Source Field | Target Table | Validation |
|--------------|--------------|------------|
| `narrative[]` | `session_narrative` | Count match, session numbers |
| `domain.concepts[]` | `domain_concepts` | Count match, concept presence |
| `domain.concerns[]` | `domain_concerns` | Count match, concern presence |
| `trajectory.phase` | `trajectory.current_phase` | Phase match |
| `trajectory.current_focus` | `trajectory.current_focus` | Focus match |
| `trajectory.completed[]` | `trajectory.completed_phases` | Array match |
| `trajectory.blockers[]` | `trajectory.blockers` | Array match |

---

## 📈 BAKING PERIOD USAGE

### Recommended Schedule

Run validation at strategic checkpoints during the baking period:

1. **After each boot** - Verify dual-write worked
2. **After state changes** - Confirm writes propagated
3. **Before cutover** - Final validation check
4. **Daily during active development** - Catch drift early

### Automated Validation (Future)

Consider integrating into CI/CD:
```bash
# In .github/workflows/validation.yml
- name: Validate Shadow Mode
  run: ./bin/verify-shadow-mode.py --json-output validation-report.json
```

---

## 🔧 IMPLEMENTATION DETAILS

### Architecture

```
┌─────────────────────┐
│ project_manifest.json│  (Source of Truth)
└──────────┬──────────┘
           │
           │ compare
           ▼
     ┌─────────────┐
     │  Validator  │
     └─────────────┘
           │
           │ query
           ▼
┌─────────────────────┐
│  vibe_agency.db     │  (Shadow Copy)
│  - missions         │
│  - session_narrative│
│  - domain_concepts  │
│  - trajectory       │
└─────────────────────┘
```

### Key Classes

**`ShadowModeValidator`** (bin/verify-shadow-mode.py)
- `validate()` - Main validation orchestrator
- `_validate_mission()` - Compare manifest → missions
- `_validate_memory()` - Compare memory → v2 tables
- `_load_json()` - JSON file loader
- `_load_db_mission()` - SQLite query helper
- `print_report()` - Human-readable output

---

## 📊 OUTPUT EXAMPLES

### GREEN Status (All Match)
```
================================================================================
ARCH-004: SHADOW MODE VALIDATION REPORT
================================================================================
Timestamp: 2025-11-20T15:30:00Z
Project:   /home/user/vibe-agency

Status:    🟢 GREEN (100% MATCH)
================================================================================

📊 VALIDATION CHECKS:

  MISSION:
    Passed: 9/9
    Failed: 0/9

  MEMORY:
    Passed: 4/4
    Failed: 0/4

================================================================================
✅ VALIDATION PASSED - SQLite shadow copy is 100% consistent with JSON
================================================================================
```

### RED Status (Mismatches)
```
================================================================================
ARCH-004: SHADOW MODE VALIDATION REPORT
================================================================================
Status:    🔴 RED (MISMATCHES)
================================================================================

📊 VALIDATION CHECKS:

  MISSION:
    Passed: 5/9
    Failed: 4/9

    Mismatches:
      • phase
        Expected: CODING
        Actual:   PLANNING
      • max_cost_usd
        Expected: 100.0
        Actual:   None

❌ ERRORS (4):
  • phase mismatch: expected=CODING, actual=PLANNING
  • max_cost_usd mismatch: expected=100.0, actual=None

================================================================================
❌ VALIDATION FAILED - Mismatches detected between JSON and SQLite
================================================================================
```

---

## ✅ ACCEPTANCE CRITERIA

- [x] **Tool exists:** `bin/verify-shadow-mode.py` executable
- [x] **Compares manifest:** Validates all mission table fields
- [x] **Compares memory:** Validates all v2 table fields
- [x] **Reports diffs:** Shows field-level mismatches
- [x] **Exit codes:** Proper return codes (0=GREEN, 1=RED)
- [x] **vibe-shell integration:** `--verify-db` flag works
- [x] **Health check observation:** Shows shadow mode status
- [x] **Documentation:** This file + inline help text

---

## 🚀 NEXT STEPS (Phase 2 Cutover)

After sufficient baking period with GREEN validation:

1. **ARCH-005:** Promote SQLite to primary source of truth
2. **ARCH-006:** Migrate JSON reads to SQLite queries
3. **ARCH-007:** Archive JSON files (keep as backup)
4. **ARCH-008:** Update documentation to reflect SQLite-first

**Criteria for cutover:**
- ✅ 7 days of continuous GREEN status
- ✅ No mismatches during active development
- ✅ All integration tests passing
- ✅ Team confidence high

---

## 📚 RELATED DOCUMENTS

- `ARCH-001_schema.sql` - SQLite schema design
- `ARCH-002_implementation.md` - v2 implementation
- `ARCH-003_dual_write.md` - Shadow mode design
- `agency_os/persistence/sqlite_store.py` - Store implementation
- `agency_os/core_system/runtime/boot_sequence.py` - Boot integration

---

## 🔐 MAINTENANCE

**Update Triggers:**
- New fields added to `project_manifest.json` → Add to `_validate_mission()`
- New tables in schema v2 → Add to `_validate_memory()`
- Schema version bump → Update validation logic

**Monitoring:**
Run weekly during baking period:
```bash
./bin/verify-shadow-mode.py --json-output /tmp/validation-$(date +%Y%m%d).json
```

Archive results for historical analysis.

---

**Completion Date:** 2025-11-20
**Verified By:** Claude Code (Sonnet 4.5)
**Status:** ✅ PRODUCTION READY
