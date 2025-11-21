# ARCH-002: Implement SQLite Store Layer

**Phase:** 0 (Persistence Foundation)
**Priority:** P0
**Estimated Time:** 180 minutes
**Dependencies:** ARCH-001

---

## Objective

Create `agency_os/persistence/sqlite_store.py` - the persistence layer that abstracts SQLite operations for the rest of the system.

---

## Acceptance Criteria

1. ✅ **Class Structure**
   - `agency_os/persistence/sqlite_store.py` created
   - Class `SQLiteStore` with initialization, CRUD operations, query methods

2. ✅ **Core Methods Implemented**
   ```python
   class SQLiteStore:
       def __init__(self, db_path: str = ".vibe/state/vibe_agency.db")
       def init_db(self) -> None  # Create schema if not exists
       def create_mission(self, phase: str, metadata: dict) -> str  # Returns mission_uuid
       def update_mission_status(self, mission_uuid: str, status: str) -> None
       def log_tool_call(self, mission_uuid: str, tool_name: str, args: dict, result: dict, success: bool) -> None
       def record_decision(self, mission_uuid: str, decision_type: str, rationale: str, agent_name: str) -> None
       def get_mission_history(self, limit: int = 10) -> list[dict]
       def get_tool_history(self, mission_uuid: str) -> list[dict]
       def get_decisions(self, mission_uuid: str) -> list[dict]
   ```

3. ✅ **Zero-Config Initialization**
   - Auto-creates `.vibe/state/vibe_agency.db` on first boot
   - Auto-creates schema using ARCH-001_schema.sql
   - Handles missing parent directory (creates `.vibe/state/`)

4. ✅ **Schema Versioning**
   - Uses `PRAGMA user_version` for schema version tracking
   - Current version: 1
   - Migration path for future versions

5. ✅ **Thread Safety**
   - Uses `sqlite3.connect(db_path, check_same_thread=False)`
   - Or implements connection pooling
   - Safe for multi-threaded environments (future-proof)

6. ✅ **Test Coverage**
   - `tests/persistence/test_sqlite_store.py` created
   - Minimum 15 tests covering:
     - Initialization (creates DB, schema)
     - Mission CRUD (create, read, update)
     - Tool call logging (success/failure cases)
     - Decision recording
     - Query operations (history, filters)
     - Edge cases (empty DB, missing mission, invalid data)
   - Coverage >= 80% for sqlite_store.py

---

## Implementation Notes

### Design Pattern: Repository Pattern

```python
from pathlib import Path
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

class SQLiteStore:
    """Repository for agent mission persistence using SQLite."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str = ".vibe/state/vibe_agency.db"):
        self.db_path = Path(db_path)
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Create database and schema if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Check schema version
            current_version = conn.execute("PRAGMA user_version").fetchone()[0]

            if current_version == 0:
                # Fresh database, apply schema
                self._apply_schema(conn)
                conn.execute(f"PRAGMA user_version = {self.SCHEMA_VERSION}")
            elif current_version < self.SCHEMA_VERSION:
                # Migration needed
                self._migrate_schema(conn, current_version)

    def _apply_schema(self, conn: sqlite3.Connection) -> None:
        """Apply ARCH-001 schema to database."""
        schema_path = Path(__file__).parent.parent.parent / "docs/tasks/ARCH-001_schema.sql"
        with open(schema_path) as f:
            conn.executescript(f.read())

    def create_mission(self, phase: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create new mission, returns mission UUID."""
        mission_uuid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO missions (mission_uuid, phase, status, created_at, metadata)
                VALUES (?, ?, 'pending', ?, ?)
                """,
                (mission_uuid, phase, now, json.dumps(metadata or {}))
            )

        return mission_uuid

    def log_tool_call(
        self,
        mission_uuid: str,
        tool_name: str,
        args: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        success: bool = True,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Log a tool execution to audit trail."""
        now = datetime.utcnow().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Get mission internal ID
            mission_id = conn.execute(
                "SELECT id FROM missions WHERE mission_uuid = ?",
                (mission_uuid,)
            ).fetchone()

            if not mission_id:
                raise ValueError(f"Mission not found: {mission_uuid}")

            conn.execute(
                """
                INSERT INTO tool_calls (
                    mission_id, tool_name, args, result, timestamp,
                    duration_ms, success, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mission_id[0],
                    tool_name,
                    json.dumps(args),
                    json.dumps(result) if result else None,
                    now,
                    duration_ms,
                    1 if success else 0,
                    error_message
                )
            )

    # Additional methods follow similar pattern...
```

### Error Handling

```python
class MissionNotFoundError(Exception):
    """Raised when mission UUID doesn't exist."""
    pass

class DatabaseError(Exception):
    """Raised for database operation failures."""
    pass
```

### JSON Serialization

- Use `json.dumps()` for storing dicts/lists
- Use `json.loads()` when retrieving
- Handle None values gracefully

---

## Testing Strategy

### Unit Tests (tests/persistence/test_sqlite_store.py)

```python
import pytest
from pathlib import Path
from agency_os.persistence.sqlite_store import SQLiteStore

@pytest.fixture
def temp_db(tmp_path):
    """Temporary database for testing."""
    db_path = tmp_path / "test_vibe.db"
    store = SQLiteStore(str(db_path))
    yield store
    # Cleanup happens automatically (tmp_path is cleaned by pytest)

def test_init_creates_database(temp_db):
    """Test that initialization creates database file."""
    assert temp_db.db_path.exists()

def test_create_mission_returns_uuid(temp_db):
    """Test mission creation returns valid UUID."""
    mission_uuid = temp_db.create_mission("PLANNING", {"user": "test"})
    assert len(mission_uuid) == 36  # UUID4 format

def test_log_tool_call_success(temp_db):
    """Test logging successful tool call."""
    mission_uuid = temp_db.create_mission("PLANNING")
    temp_db.log_tool_call(
        mission_uuid,
        "research_tool",
        {"query": "test"},
        {"results": ["a", "b"]},
        success=True,
        duration_ms=150
    )

    history = temp_db.get_tool_history(mission_uuid)
    assert len(history) == 1
    assert history[0]["tool_name"] == "research_tool"
    assert history[0]["success"] is True

def test_log_tool_call_failure(temp_db):
    """Test logging failed tool call."""
    mission_uuid = temp_db.create_mission("CODING")
    temp_db.log_tool_call(
        mission_uuid,
        "compile_tool",
        {"code": "invalid"},
        result=None,
        success=False,
        error_message="Syntax error"
    )

    history = temp_db.get_tool_history(mission_uuid)
    assert history[0]["success"] is False
    assert "Syntax error" in history[0]["error_message"]

# ... 10+ more tests covering all methods
```

---

## Deliverables

1. **agency_os/persistence/__init__.py**
   ```python
   from .sqlite_store import SQLiteStore, MissionNotFoundError, DatabaseError

   __all__ = ["SQLiteStore", "MissionNotFoundError", "DatabaseError"]
   ```

2. **agency_os/persistence/sqlite_store.py**
   - Complete implementation (300-400 LOC)
   - Docstrings for all public methods
   - Type hints

3. **tests/persistence/test_sqlite_store.py**
   - 15+ tests
   - 80%+ coverage

---

## Validation

```bash
# Run tests
uv run pytest tests/persistence/test_sqlite_store.py -v

# Check coverage
uv run pytest tests/persistence/test_sqlite_store.py --cov=agency_os.persistence --cov-report=term

# Verify in REPL
python3 -c "
from agency_os.persistence import SQLiteStore
store = SQLiteStore('.vibe/state/test.db')
mission = store.create_mission('PLANNING', {'test': True})
print(f'Created mission: {mission}')
"
```

---

## Next Steps

→ **ARCH-003:** Integrate SQLiteStore into boot_sequence.py and core_orchestrator.py
→ **ARCH-004:** Add tool call logging to tool_executor.py
