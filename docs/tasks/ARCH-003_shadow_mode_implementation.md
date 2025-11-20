# ARCH-003: Shadow Mode Implementation (Dual Write)

**Status:** ✅ COMPLETE
**Date:** 2025-11-20
**Implements:** Phase 1 of 3-Phase Shadow Mode Strategy

---

## Overview

Shadow Mode (Dual Write) is a safe migration strategy where data is written to both the old (JSON) and new (SQLite) persistence layers simultaneously, while reads continue from JSON. This allows us to validate the SQLite implementation without risk of data loss.

## Migration Strategy

```
Phase 0: Reality Check ✅ (Completed)
  └─> Schema v2 designed to prevent data loss

Phase 1: Shadow Mode ✅ (This Implementation)
  └─> Dual-write: JSON (source of truth) + SQLite (validation)

Phase 2: Cutover (Future)
  └─> Switch reads to SQLite, deprecate JSON
```

## Implementation

### 1. SQLiteStore.import_project_manifest()

**File:** `agency_os/persistence/sqlite_store.py:823-876`

```python
def import_project_manifest(
    self, manifest: dict[str, Any], project_memory: dict[str, Any] | None = None
) -> int:
    """
    Import project manifest and optional project memory to SQLite (ARCH-003)

    Features:
    - Uses _map_manifest_to_missions_row adapter (extracts budget, metadata)
    - Idempotent (UPDATE if exists, INSERT if not)
    - Optionally imports project_memory.json to v2 tables
    """
```

**What it does:**
- Converts `project_manifest.json` → missions table row
- Extracts nested fields (budget, metadata) into dedicated columns
- Updates existing mission if UUID already exists (idempotent)
- Optionally flattens `project_memory.json` into v2 tables (session_narrative, domain_concepts, etc.)

### 2. CoreOrchestrator Dual-Write

**File:** `agency_os/core_system/orchestrator/core_orchestrator.py:497-511`

**Modified:** `save_project_manifest()`

```python
# Write to disk (JSON)
with open(manifest_path, "w") as f:
    json.dump(manifest.metadata, f, indent=2)

# ARCH-003: Dual Write Mode - also write to SQLite
try:
    mission_id = self.sqlite_store.import_project_manifest(manifest.metadata)
    logger.debug(f"✅ Dual-write to SQLite: mission_id={mission_id}")
except Exception as e:
    # Non-fatal - JSON is source of truth in Shadow Mode Phase 1
    logger.warning(f"⚠️ SQLite dual-write failed (non-fatal): {e}")
```

**Safety:**
- JSON write happens first (source of truth)
- SQLite write wrapped in try/except (non-fatal if it fails)
- Logs success/failure for monitoring

### 3. ProjectMemoryManager Dual-Write

**File:** `agency_os/core_system/runtime/project_memory.py:49-73`

**Modified:** `save(memory, mission_id=None)`

```python
# Write to JSON (source of truth in Shadow Mode Phase 1)
with open(self.memory_file, "w") as f:
    json.dump(memory, f, indent=2)

# ARCH-003: Dual Write Mode - also write to SQLite if mission_id provided
if self.sqlite_store and mission_id:
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"
        self.sqlite_store._map_project_memory_to_sql(memory, mission_id, timestamp)
        logger.debug(f"✅ Dual-write project memory to SQLite: mission_id={mission_id}")
    except Exception as e:
        logger.warning(f"⚠️ SQLite dual-write for project memory failed (non-fatal): {e}")
```

**Optional mission_id:**
- If `mission_id` provided, dual-write to SQLite
- If not provided, only write to JSON (backward compatible)

### 4. BootSequence Integration

**File:** `agency_os/core_system/runtime/boot_sequence.py:25-36`

**Modified:** `__init__()`

```python
# Initialize SQLite persistence (ARCH-003: Dual Write Mode)
db_path = self.project_root / ".vibe" / "state" / "vibe_agency.db"
self.sqlite_store = SQLiteStore(str(db_path))

# Initialize memory manager with SQLite store for dual-write
self.memory_manager = ProjectMemoryManager(self.project_root, self.sqlite_store)
```

**What changed:**
- SQLiteStore initialized early (before ProjectMemoryManager)
- ProjectMemoryManager receives sqlite_store reference
- Legacy JSON migration still happens (`_migrate_legacy_json()`)

---

## Test Coverage

### Unit Tests (4 new tests)

**File:** `tests/persistence/test_sqlite_store.py:853-1041`

1. **test_import_project_manifest_creates_mission** - Basic import
2. **test_import_project_manifest_with_memory** - Import with project_memory
3. **test_import_project_manifest_idempotent** - UPDATE vs INSERT behavior
4. **test_import_real_project_manifest** - Integration with real workspace data

**Total:** 53 tests passing (49 from ARCH-002 + 4 from ARCH-003)

### Integration Test

```python
def test_import_real_project_manifest(self):
    """Test importing a real project_manifest.json from workspaces"""
    manifest_path = Path("workspaces/test_orchestrator/project_manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)

    mission_id = store.import_project_manifest(manifest)

    # Verify all fields preserved
    mission = store.get_mission(mission_id)
    assert mission["mission_uuid"] == "test-orchestrator-003"
    assert mission["planning_sub_state"] == "BUSINESS_VALIDATION"
    assert mission["max_cost_usd"] == 10.0
```

---

## Data Flow

### Before (JSON Only)

```
CoreOrchestrator.save_project_manifest()
  └─> Write project_manifest.json

ProjectMemoryManager.save()
  └─> Write project_memory.json
```

### After (Shadow Mode)

```
CoreOrchestrator.save_project_manifest()
  ├─> Write project_manifest.json (source of truth)
  └─> Write to SQLite missions table (validation)

ProjectMemoryManager.save(mission_id=123)
  ├─> Write project_memory.json (source of truth)
  └─> Write to SQLite v2 tables (validation)
      ├─> session_narrative
      ├─> domain_concepts
      ├─> domain_concerns
      └─> trajectory
```

---

## Safety Guarantees

### 1. No Data Loss
- JSON writes happen first
- SQLite writes are non-fatal (catch exceptions)
- If SQLite write fails, JSON still succeeded

### 2. Idempotency
- `import_project_manifest()` checks if mission exists by UUID
- If exists: UPDATE
- If not: INSERT
- Safe to call multiple times

### 3. Backward Compatibility
- `ProjectMemoryManager.save(memory)` still works (mission_id is optional)
- Old code continues to work without changes
- Dual-write only happens if sqlite_store provided

### 4. Monitoring
- All dual-write operations logged (debug level for success, warning for failure)
- Can track dual-write failures without breaking production

---

## Next Steps (Phase 2: Cutover)

When ready to switch to SQLite as source of truth:

1. **Validation Period** (1-2 weeks)
   - Monitor dual-write logs
   - Run data consistency checks (compare JSON vs SQLite)
   - Fix any discovered issues

2. **Read Migration**
   - Modify `load_project_manifest()` to read from SQLite
   - Keep JSON write as backup initially

3. **JSON Deprecation**
   - Remove JSON writes once SQLite reads are stable
   - Keep JSON as archival backup

4. **Tool Integration**
   - Add SQLite query tools (analytics, reporting)
   - Build dashboards on SQLite data

---

## Files Modified

1. `agency_os/persistence/sqlite_store.py`
   - Added `import_project_manifest()` method
   - Added datetime import

2. `agency_os/core_system/orchestrator/core_orchestrator.py`
   - Added SQLiteStore import
   - Added sqlite_store initialization in `__init__()`
   - Added dual-write to `save_project_manifest()`

3. `agency_os/core_system/runtime/project_memory.py`
   - Added logging import
   - Added sqlite_store parameter to `__init__()`
   - Added dual-write to `save()` with optional mission_id

4. `agency_os/core_system/runtime/boot_sequence.py`
   - Reordered initialization (sqlite_store before memory_manager)
   - Pass sqlite_store to ProjectMemoryManager

5. `tests/persistence/test_sqlite_store.py`
   - Added 4 new integration tests
   - Added real workspace data test

---

## Verification

Run complete test suite:

```bash
# SQLiteStore tests (53 tests)
uv run pytest tests/persistence/test_sqlite_store.py -v

# Verify real workspace integration
uv run pytest tests/persistence/test_sqlite_store.py::TestProjectManifestImport::test_import_real_project_manifest -v
```

All tests passing: ✅ 53/53

---

## Conclusion

Shadow Mode (Dual Write) is now active. Every time a project manifest or project memory is saved:
1. JSON is written (source of truth)
2. SQLite is written (validation)
3. Failures are logged but non-fatal

This allows us to validate the SQLite implementation in production without risk, building confidence for eventual cutover to SQLite as the primary persistence layer.
