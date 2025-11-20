# ARCH-001: SQLite Migration Plan

**Version:** 2.0 (Post-Reality Check)
**Created:** 2025-11-20
**Updated:** 2025-11-20 (Schema v2 revisions)
**Status:** Schema Design Complete - Awaiting Implementation
**Target Implementation:** ARCH-002, ARCH-003

---

## ⚠️ UPDATE: Schema v2 Revisions (2025-11-20)

**Context:** Phase 0 Reality Check revealed critical gaps in original schema.

**Changes Made:**
- ✅ Schema expanded from 5 → 11 tables (6 new tables added)
- ✅ Missions table: +10 columns (budget tracking, metadata extraction)
- ✅ New tables: session_narrative, domain_concepts, domain_concerns, trajectory, artifacts, quality_gates
- ✅ Adapter complexity increased: 150 → 300-500 LOC (estimated)

**See:** `docs/tasks/SCHEMA_REALITY_CHECK.md` for full analysis.

**Decision:** Option A (Dedicated Tables) approved for ProjectMemory and Artifacts - prioritize queryability over simplicity.

---

## Executive Summary

This document outlines the strategy for migrating vibe-agency from volatile JSON-based state management to persistent SQLite storage. The migration will be **incremental**, **backward-compatible**, and **reversible** to minimize disruption to active sessions.

**Key Principles:**
1. **Zero Downtime** - No session interruptions during migration
2. **Backward Compatible** - Support both JSON and SQLite during transition
3. **Data Integrity** - Never lose mission state or audit trail
4. **Reversible** - Can rollback to JSON if needed

---

## Current State Analysis

### JSON Files in Use

| File | Purpose | Volatility | Migration Priority |
|------|---------|------------|-------------------|
| `.vibe/state/active_mission.json` | Current mission state | HIGH | **P0** - Migrate first |
| `.session_handoff.json` | Inter-session handoff | MEDIUM | **P1** - Migrate second |
| `.vibe/runtime/context.json` | Runtime context | VOLATILE | **P2** - Defer (ephemeral) |
| `.vibe/config/cleanup_roadmap.json` | Roadmap tracking | LOW | **P3** - Keep as JSON (config) |
| `.vibe/system_integrity_manifest.json` | Integrity baseline | IMMUTABLE | **P3** - Keep as JSON (config) |

### Data Loss Risks (Current System)

1. **Mission History**: No persistence beyond current mission (`.vibe/state/active_mission.json` overwritten on each boot)
2. **Tool Call Audit**: No record of what tools were executed, when, or why
3. **Decision Provenance**: No record of agent decisions or rationale
4. **Performance Metrics**: No playbook execution timing data
5. **Agent Memory**: Context lost between sessions (no long-term memory)

---

## Adapter Complexity (v2 Impact)

**Original Estimate (v1):** ~150 LOC for basic mission serialization
**Revised Estimate (v2):** ~300-500 LOC due to:

1. **ProjectMemory Flattening** (High Complexity)
   - narrative array → session_narrative rows (1→N mapping)
   - domain.concepts → domain_concepts rows (array flattening)
   - domain.concerns → domain_concerns rows (array flattening)
   - trajectory object → trajectory row (1→1 mapping with JSON fields)

2. **Artifacts Flattening** (High Complexity)
   - Nested artifacts object → artifacts rows (recursive traversal)
   - Example: `artifacts.planning.architecture.ref` → `artifacts(mission_id, artifact_type='planning', artifact_name='architecture', ref=...)`

3. **Budget Extraction** (Medium Complexity)
   - budget object → missions columns (simple field mapping)

4. **Metadata Extraction** (Low Complexity)
   - metadata.owner → missions.owner (simple field mapping)

**See:** `docs/tasks/SCHEMA_REALITY_CHECK.md` Section 6.1 for detailed adapter logic examples.

---

## Migration Strategy

### Phase 1: Dual-Write Mode (Weeks 1-2)

**Objective:** Write to both JSON and SQLite, read from JSON (safe rollback)

#### Implementation Steps

1. **Create SQLiteStore Class** (ARCH-002)
   - `agency_os/persistence/sqlite_store.py`
   - Implements schema from `ARCH-001_schema.sql`
   - Auto-creates DB at `.vibe/state/missions.db` on first boot

2. **Integrate into Boot Sequence** (ARCH-003)
   - `bin/system-boot.sh` initializes SQLite DB (if not exists)
   - `boot_sequence.py` creates SQLiteStore instance
   - All state writes go to **both** JSON and SQLite

3. **Verification**
   ```bash
   # After boot, verify dual-write
   sqlite3 .vibe/state/missions.db "SELECT COUNT(*) FROM missions;"
   # Should match: jq '.mission_id' .vibe/state/active_mission.json
   ```

4. **Rollback Plan**
   - Keep writing to JSON files
   - If SQLite fails, system continues with JSON-only
   - No read dependencies on SQLite yet

#### Example: Dual-Write Mission Creation

```python
# In boot_sequence.py (Phase 1)
def create_mission(mission_data: dict):
    # Write to JSON (legacy - primary source)
    write_json(".vibe/state/active_mission.json", mission_data)

    # Write to SQLite (new - shadow storage)
    try:
        sqlite_store.insert_mission(
            mission_uuid=mission_data["mission_id"],
            phase=mission_data.get("phase", "UNKNOWN"),
            status=mission_data["status"],
            created_at=mission_data["created_at"],
            metadata=mission_data
        )
    except Exception as e:
        log.warning(f"SQLite write failed (non-critical): {e}")
        # Continue - JSON is still primary
```

---

### Phase 2: Hybrid Read Mode (Weeks 3-4)

**Objective:** Read from SQLite, fallback to JSON if missing (validation phase)

#### Implementation Steps

1. **Update Read Logic**
   - Try SQLite first
   - Fallback to JSON if SQLite query fails
   - Log discrepancies for debugging

2. **Validation Queries**
   ```python
   # Verify SQLite matches JSON
   def validate_mission_sync():
       json_mission = read_json(".vibe/state/active_mission.json")
       sql_mission = sqlite_store.get_active_mission()

       if json_mission["mission_id"] != sql_mission.mission_uuid:
           raise MismatchError("Mission ID mismatch!")
   ```

3. **Monitoring**
   - Track SQLite hit rate (should be 100% after Phase 1)
   - Alert on JSON fallbacks (indicates SQLite write failure)

---

### Phase 3: SQLite-Primary Mode (Weeks 5-6)

**Objective:** SQLite is primary, JSON is deprecated (read-only for recovery)

#### Implementation Steps

1. **Stop JSON Writes**
   - Remove JSON write calls from mission lifecycle
   - Keep reading for backward compatibility (old sessions)

2. **Migration Tool for Historical Data**
   ```bash
   # One-time migration of old JSON to SQLite
   python scripts/migrate_json_to_sqlite.py --input .vibe/state/ --db .vibe/state/missions.db
   ```

3. **Deprecation Notice**
   - Add warning to `system-boot.sh` if JSON files detected
   - Recommend running migration tool

---

### Phase 4: JSON Removal (Week 7+)

**Objective:** Fully remove JSON state management (config files remain)

#### Implementation Steps

1. **Remove JSON Read Fallbacks**
   - Delete all `read_json()` calls for state files
   - Keep for config files (`.vibe/config/*.json`)

2. **Archive Old JSON Files**
   ```bash
   # Move to archive (don't delete - keep for debugging)
   mv .vibe/state/active_mission.json .vibe/archive/active_mission_legacy.json
   ```

3. **Update Documentation**
   - Update `SSOT.md` to reflect SQLite as primary persistence
   - Remove references to JSON state files in `ARCHITECTURE_V2.md`

---

## Backward Compatibility

### Handling Old Sessions

**Scenario:** New agent session starts with old JSON state

```python
# On boot (ARCH-003 integration)
if os.path.exists(".vibe/state/active_mission.json"):
    # Detect legacy JSON state
    log.info("Legacy JSON state detected - migrating to SQLite...")

    # Import JSON into SQLite
    json_data = read_json(".vibe/state/active_mission.json")
    sqlite_store.import_legacy_mission(json_data)

    # Rename JSON (keep as backup)
    os.rename(
        ".vibe/state/active_mission.json",
        f".vibe/state/active_mission_migrated_{timestamp}.json"
    )
```

### Config Files (No Migration)

These remain as JSON indefinitely:
- `.vibe/config/cleanup_roadmap.json` (roadmap tracking)
- `.vibe/system_integrity_manifest.json` (integrity baseline)
- `.session_handoff.json` (UNTIL Phase 2 - see note below)

**Note on Session Handoff:**
- Phase 1: Keep as JSON (too critical to risk)
- Phase 2: Migrate to `agent_memory` table (key='session_handoff')
- Phase 3: JSON removed, SQLite only

---

## Schema Versioning Strategy

### PRAGMA user_version

SQLite uses `PRAGMA user_version` for schema versioning:

```sql
-- On schema creation (ARCH-001_schema.sql)
PRAGMA user_version = 1;

-- On future migration (e.g., adding 'agent_sessions' table)
PRAGMA user_version = 2;
```

### Migration Script Template

```python
# scripts/migrate_schema.py
def migrate_to_v2(conn: sqlite3.Connection):
    current_version = conn.execute("PRAGMA user_version").fetchone()[0]

    if current_version < 2:
        # Apply migration
        conn.executescript("""
            ALTER TABLE missions ADD COLUMN archived INTEGER DEFAULT 0;
            CREATE INDEX idx_missions_archived ON missions(archived);
            PRAGMA user_version = 2;
        """)
        print("✅ Migrated schema to v2")
    else:
        print("⏭️  Already at v2, skipping")
```

### Version History

| Version | Changes | Date | Migration Script |
|---------|---------|------|------------------|
| v1 | Initial schema (5 tables) | 2025-11-20 | `ARCH-001_schema.sql` (deprecated) |
| **v2** | **Reality Check revisions: +6 tables (session_narrative, domain_concepts, domain_concerns, trajectory, artifacts, quality_gates), +10 columns to missions (budget, metadata)** | **2025-11-20** | **`ARCH-001_schema.sql` (current)** |
| v3 | (Future) Add `archived` column to missions | TBD | `scripts/migrate_to_v3.py` |
| v4 | (Future) Add `agent_sessions` table | TBD | `scripts/migrate_to_v4.py` |

---

## Data Migration Tools

### 1. JSON → SQLite Importer

**Script:** `scripts/migrate_json_to_sqlite.py`

**Usage:**
```bash
# Migrate all JSON files in .vibe/state/
python scripts/migrate_json_to_sqlite.py \
    --input .vibe/state/ \
    --db .vibe/state/missions.db \
    --dry-run  # Preview changes without writing

# Apply migration
python scripts/migrate_json_to_sqlite.py \
    --input .vibe/state/ \
    --db .vibe/state/missions.db
```

**Features:**
- **Idempotent**: Can run multiple times (skips duplicates)
- **Validation**: Checks data integrity before writing
- **Dry-run**: Preview changes without modifying DB
- **Rollback**: Backs up JSON before deletion

---

### 2. SQLite → JSON Exporter (Rollback)

**Script:** `scripts/export_sqlite_to_json.py`

**Usage:**
```bash
# Export current mission to JSON (for rollback)
python scripts/export_sqlite_to_json.py \
    --db .vibe/state/missions.db \
    --mission-uuid genesis \
    --output .vibe/state/active_mission_rollback.json
```

**Use Case:** If SQLite corruption detected, export to JSON and resume

---

### 3. Schema Validator

**Script:** `scripts/validate_schema.py`

**Usage:**
```bash
# Verify schema matches ARCH-001_schema.sql (v2)
python scripts/validate_schema.py --db .vibe/state/missions.db

# Expected output (v2):
# ✅ Schema version: 2
# ✅ Table 'missions' exists (17 columns)  # v2: expanded with budget/metadata
# ✅ Table 'tool_calls' exists (9 columns)
# ✅ Table 'session_narrative' exists (6 columns)  # v2: new
# ✅ Table 'domain_concepts' exists (4 columns)    # v2: new
# ✅ Table 'domain_concerns' exists (4 columns)    # v2: new
# ✅ Table 'trajectory' exists (7 columns)         # v2: new
# ✅ Table 'artifacts' exists (10 columns)         # v2: new
# ✅ Table 'quality_gates' exists (6 columns)      # v2: new
# ✅ Foreign keys enabled
# ✅ All indexes present (28 indexes)  # v2: increased from 12
```

---

## Testing Strategy

### Unit Tests (ARCH-002)

```python
# tests/test_sqlite_store.py
def test_mission_crud():
    """Test mission create/read/update/delete"""
    store = SQLiteStore(":memory:")  # In-memory DB for tests

    # Create mission
    mission_id = store.insert_mission(
        mission_uuid="test-001",
        phase="PLANNING",
        status="in_progress",
        created_at="2025-11-20T00:00:00Z"
    )

    # Read mission
    mission = store.get_mission(mission_id)
    assert mission.mission_uuid == "test-001"

    # Update mission
    store.update_mission_status(mission_id, "completed")
    assert store.get_mission(mission_id).status == "completed"

    # Delete mission
    store.delete_mission(mission_id)
    assert store.get_mission(mission_id) is None
```

### Integration Tests (ARCH-003)

```python
# tests/test_sqlite_integration.py
def test_boot_sequence_creates_db():
    """Verify system-boot.sh creates SQLite DB"""
    if os.path.exists(".vibe/state/missions.db"):
        os.remove(".vibe/state/missions.db")

    # Run boot
    subprocess.run(["./bin/system-boot.sh"], check=True)

    # Verify DB exists
    assert os.path.exists(".vibe/state/missions.db")

    # Verify schema
    conn = sqlite3.connect(".vibe/state/missions.db")
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    assert ("missions",) in tables
```

### End-to-End Tests

```bash
# tests/test_migration_e2e.sh
#!/bin/bash
set -e

echo "🧪 Testing full migration flow..."

# 1. Start with JSON state
cp .vibe/state/active_mission.json /tmp/backup.json

# 2. Run migration
python scripts/migrate_json_to_sqlite.py --input .vibe/state/ --db .vibe/state/missions.db

# 3. Verify SQLite has data
mission_count=$(sqlite3 .vibe/state/missions.db "SELECT COUNT(*) FROM missions;")
if [ "$mission_count" -eq 0 ]; then
    echo "❌ No missions in SQLite!"
    exit 1
fi

# 4. Export back to JSON
python scripts/export_sqlite_to_json.py --db .vibe/state/missions.db --output /tmp/exported.json

# 5. Verify JSON matches original
diff <(jq -S . /tmp/backup.json) <(jq -S . /tmp/exported.json)

echo "✅ Migration E2E test passed!"
```

---

## Rollback Plan

### Rollback Triggers

Rollback to JSON if:
1. SQLite corruption detected (`PRAGMA integrity_check` fails)
2. Critical bug in SQLiteStore class (data loss risk)
3. Performance degradation (>500ms query latency)

### Rollback Procedure

```bash
# 1. Stop all agents (prevent partial writes)
pkill -f "vibe-cli"

# 2. Export SQLite to JSON (preserve latest state)
python scripts/export_sqlite_to_json.py \
    --db .vibe/state/missions.db \
    --output .vibe/state/active_mission.json

# 3. Rename SQLite DB (keep for debugging)
mv .vibe/state/missions.db .vibe/state/missions_rollback_$(date +%s).db

# 4. Restore JSON-only mode (revert ARCH-003 integration)
git revert <commit-hash-of-ARCH-003>

# 5. Restart system
./bin/system-boot.sh

# 6. Verify JSON state loaded
jq '.mission_id' .vibe/state/active_mission.json
```

---

## Performance Considerations

### Query Optimization

1. **Indexes on Hot Paths**
   - `missions.status` (querying active missions)
   - `tool_calls.mission_id, timestamp` (audit queries)
   - `agent_memory.mission_id, key` (context lookups)

2. **Batch Writes**
   ```python
   # Instead of 100 individual inserts:
   for tool_call in tool_calls:
       store.insert_tool_call(tool_call)

   # Use batch insert:
   store.insert_tool_calls_batch(tool_calls)  # Single transaction
   ```

3. **Connection Pooling**
   - Reuse single connection per session (avoid overhead)
   - Close connection on session end (free resources)

### Storage Management

1. **Archive Old Missions**
   ```sql
   -- Move completed missions older than 30 days to archive table
   INSERT INTO missions_archive SELECT * FROM missions
   WHERE status = 'completed' AND completed_at < datetime('now', '-30 days');

   DELETE FROM missions WHERE id IN (SELECT id FROM missions_archive);
   ```

2. **VACUUM Schedule**
   ```bash
   # Run monthly (reclaim deleted space)
   sqlite3 .vibe/state/missions.db "VACUUM;"
   ```

3. **Database Size Monitoring**
   ```bash
   # Alert if DB > 100MB (indicates missing archival)
   du -h .vibe/state/missions.db
   ```

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SQLite corruption | LOW | HIGH | Daily backups, `PRAGMA integrity_check` on boot |
| Migration data loss | MEDIUM | CRITICAL | Dual-write mode (Phase 1), extensive testing |
| Performance regression | LOW | MEDIUM | Benchmark before/after, rollback if >500ms latency |
| Schema migration bugs | MEDIUM | HIGH | Version all migrations, test on copy of production DB |

---

## Success Criteria

### Phase 1 Complete When:
- [ ] SQLiteStore class implemented and tested (ARCH-002)
- [ ] Boot sequence creates SQLite DB automatically (ARCH-003)
- [ ] All mission state written to both JSON and SQLite
- [ ] No errors in dual-write mode (1 week stable)

### Phase 2 Complete When:
- [ ] All reads use SQLite (JSON fallback only)
- [ ] Zero JSON fallbacks logged (SQLite 100% hit rate)
- [ ] Performance benchmarks meet targets (<100ms queries)

### Phase 3 Complete When:
- [ ] JSON writes removed from codebase
- [ ] Legacy JSON files archived (not deleted)
- [ ] Migration tool tested on production data

### Phase 4 Complete When:
- [ ] JSON read fallbacks removed
- [ ] Documentation updated (SSOT.md, ARCHITECTURE_V2.md)
- [ ] All tests passing (no JSON dependencies)

---

## Timeline

| Phase | Duration | Tasks | Completion Criteria |
|-------|----------|-------|---------------------|
| **Phase 1: Dual-Write** | 2 weeks | ARCH-002, ARCH-003 | No errors in dual-write mode |
| **Phase 2: Hybrid Read** | 2 weeks | Update read logic, validation | 100% SQLite hit rate |
| **Phase 3: SQLite-Primary** | 2 weeks | Stop JSON writes, migration tool | JSON deprecated |
| **Phase 4: JSON Removal** | 1 week | Remove JSON fallbacks, cleanup | All JSON state removed |

**Total Estimated Time:** 7 weeks

---

## Next Steps

1. **Immediate (ARCH-002):** Implement `SQLiteStore` class using `ARCH-001_schema.sql`
2. **Next (ARCH-003):** Integrate SQLiteStore into `boot_sequence.py` and `core_orchestrator.py`
3. **Testing:** Write comprehensive unit/integration tests for SQLiteStore
4. **Monitoring:** Set up logging/alerting for dual-write discrepancies

---

## References

- **Schema DDL:** `docs/tasks/ARCH-001_schema.sql`
- **Roadmap:** `docs/roadmap/phase_2_5_foundation.json`
- **Current State:** `.vibe/state/active_mission.json`
- **SQLite Docs:** https://www.sqlite.org/docs.html
- **Schema Versioning:** https://www.sqlite.org/pragma.html#pragma_user_version

---

**Document Status:** COMPLETE
**Next Review:** After ARCH-002 implementation
**Maintained By:** STEWARD (AI Agent System)
