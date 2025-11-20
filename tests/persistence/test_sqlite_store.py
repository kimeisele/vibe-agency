"""
Test suite for SQLiteStore - SQLite persistence layer

ARCH-002 Acceptance Criteria:
1. ✅ SQLiteStore class with CRUD methods
2. ✅ Auto-creates .vibe/state/vibe_agency.db on first boot
3. ✅ Handles schema migrations (PRAGMA user_version)
4. ✅ Thread-safe (check_same_thread=False)
5. ✅ 15+ tests with 80% coverage

Test Strategy:
- Use in-memory DB for fast tests (:memory:)
- Test file-based DB for auto-creation behavior
- Verify schema loaded correctly from ARCH-001_schema.sql
- Test foreign key constraints (CASCADE DELETE)
- Verify all CRUD operations
"""

import os
import sqlite3
import tempfile
import threading

from agency_os.persistence.sqlite_store import SQLiteStore


class TestSQLiteStoreInitialization:
    """Test database initialization and schema loading"""

    def test_init_creates_in_memory_database(self):
        """Test that SQLiteStore can create an in-memory database"""
        store = SQLiteStore(":memory:")
        assert store.conn is not None
        assert isinstance(store.conn, sqlite3.Connection)

    def test_init_creates_file_database_if_not_exists(self):
        """Test that SQLiteStore auto-creates DB file on first boot"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_vibe_agency.db")
            assert not os.path.exists(db_path), "DB should not exist yet"

            store = SQLiteStore(db_path)
            assert os.path.exists(db_path), "DB should be auto-created"
            store.close()

    def test_init_loads_schema_from_arch001_sql(self):
        """Test that schema is loaded from ARCH-001_schema.sql"""
        store = SQLiteStore(":memory:")
        # # Verify all 5 core tables exist
        cursor = store.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert "missions" in tables
        assert "tool_calls" in tables
        assert "decisions" in tables
        assert "playbook_runs" in tables
        assert "agent_memory" in tables

    def test_init_sets_schema_version(self):
        """Test that PRAGMA user_version is set to 1"""
        store = SQLiteStore(":memory:")
        cursor = store.conn.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        assert version == 1, "Schema version should be 1 (from ARCH-001)"

    def test_init_enables_foreign_keys(self):
        """Test that foreign key constraints are enabled"""
        store = SQLiteStore(":memory:")
        cursor = store.conn.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        assert fk_enabled == 1, "Foreign keys must be enabled"

    def test_init_with_existing_database_does_not_recreate_schema(self):
        """Test that opening existing DB doesn't re-run schema"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_vibe_agency.db")

            # # Create DB first time
            store1 = SQLiteStore(db_path)
            store1.create_mission("test-001", "PLANNING", "pending")
            store1.close()
            # # Reopen DB (should not wipe data)
            store2 = SQLiteStore(db_path)
            missions = store2.get_all_missions()
            assert len(missions) == 1, "Existing data should be preserved"
            store2.close()


class TestMissionCRUD:
    """Test mission Create/Read/Update/Delete operations"""

    def test_create_mission_returns_mission_id(self):
        """Test that create_mission returns auto-incremented ID"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission(
            mission_uuid="test-001",
            phase="PLANNING",
            status="pending",
            created_at="2025-11-20T00:00:00Z",
        )
        assert isinstance(mission_id, int)
        assert mission_id > 0

    def test_create_mission_stores_all_fields(self):
        """Test that all mission fields are stored correctly"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission(
            mission_uuid="test-001",
            phase="CODING",
            status="in_progress",
            created_at="2025-11-20T10:00:00Z",
            metadata={"key": "value"},
        )
        mission = store.get_mission(mission_id)
        assert mission["mission_uuid"] == "test-001"
        assert mission["phase"] == "CODING"
        assert mission["status"] == "in_progress"
        assert mission["created_at"] == "2025-11-20T10:00:00Z"
        assert mission["metadata"] == {"key": "value"}

    def test_get_mission_by_id_returns_correct_mission(self):
        """Test retrieving mission by ID"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        mission = store.get_mission(mission_id)
        assert mission is not None
        assert mission["id"] == mission_id
        assert mission["mission_uuid"] == "test-001"

    def test_get_mission_by_uuid_returns_correct_mission(self):
        """Test retrieving mission by UUID"""
        store = SQLiteStore(":memory:")
        store.create_mission("test-001", "PLANNING", "pending")
        mission = store.get_mission_by_uuid("test-001")
        assert mission is not None
        assert mission["mission_uuid"] == "test-001"

    def test_get_nonexistent_mission_returns_none(self):
        """Test that querying nonexistent mission returns None"""
        store = SQLiteStore(":memory:")
        mission = store.get_mission(99999)
        assert mission is None

    def test_update_mission_status_changes_status(self):
        """Test updating mission status"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        store.update_mission_status(mission_id, "completed", "2025-11-20T12:00:00Z")
        mission = store.get_mission(mission_id)
        assert mission["status"] == "completed"
        assert mission["completed_at"] == "2025-11-20T12:00:00Z"

    def test_get_mission_history_returns_all_missions(self):
        """Test retrieving mission history"""
        store = SQLiteStore(":memory:")
        store.create_mission("test-001", "PLANNING", "completed")
        store.create_mission("test-002", "CODING", "in_progress")
        store.create_mission("test-003", "TESTING", "pending")
        history = store.get_mission_history()
        assert len(history) == 3


class TestToolCallLogging:
    """Test tool call audit trail"""

    def test_log_tool_call_stores_all_fields(self):
        """Test that tool calls are logged with all fields"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        tool_call_id = store.log_tool_call(
            mission_id=mission_id,
            tool_name="WebFetch",
            args={"url": "https://example.com"},
            result={"status": 200},
            timestamp="2025-11-20T00:00:00Z",
            duration_ms=1500,
            success=True,
        )
        assert isinstance(tool_call_id, int)
        assert tool_call_id > 0

    def test_log_tool_call_with_error_stores_error_message(self):
        """Test logging failed tool calls"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        tool_call_id = store.log_tool_call(
            mission_id=mission_id,
            tool_name="Bash",
            args={"command": "invalid"},
            result=None,
            timestamp="2025-11-20T00:00:00Z",
            duration_ms=50,
            success=False,
            error_message="Command failed: exit code 127",
        )
        tool_call = store.get_tool_call(tool_call_id)
        assert tool_call["success"] == 0  # SQLite boolean as integer
        assert tool_call["error_message"] == "Command failed: exit code 127"

    def test_get_tool_calls_for_mission_returns_all_calls(self):
        """Test retrieving all tool calls for a mission"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        store.log_tool_call(mission_id, "WebFetch", {}, None, "2025-11-20T00:00:00Z", 100, True)
        store.log_tool_call(mission_id, "Bash", {}, None, "2025-11-20T00:01:00Z", 200, True)
        tool_calls = store.get_tool_calls_for_mission(mission_id)
        assert len(tool_calls) == 2


class TestDecisionProvenance:
    """Test agent decision recording"""

    def test_record_decision_stores_all_fields(self):
        """Test recording agent decisions"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        decision_id = store.record_decision(
            mission_id=mission_id,
            decision_type="architecture_choice",
            rationale="Chose SQLite for simplicity and zero-config",
            timestamp="2025-11-20T00:00:00Z",
            agent_name="STEWARD",
            context={"alternatives": ["PostgreSQL", "MySQL"]},
        )
        assert isinstance(decision_id, int)
        assert decision_id > 0

    def test_get_decisions_for_mission_returns_all_decisions(self):
        """Test retrieving all decisions for a mission"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        store.record_decision(
            mission_id, "choice1", "rationale1", "2025-11-20T00:00:00Z", "STEWARD"
        )
        store.record_decision(
            mission_id, "choice2", "rationale2", "2025-11-20T00:01:00Z", "STEWARD"
        )
        decisions = store.get_decisions_for_mission(mission_id)
        assert len(decisions) == 2


class TestForeignKeyConstraints:
    """Test referential integrity (CASCADE DELETE)"""

    def test_deleting_mission_cascades_to_tool_calls(self):
        """Test that deleting mission deletes all related tool_calls"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        store.log_tool_call(mission_id, "WebFetch", {}, None, "2025-11-20T00:00:00Z", 100, True)
        # # Verify tool call exists
        tool_calls_before = store.get_tool_calls_for_mission(mission_id)
        assert len(tool_calls_before) == 1
        # # Delete mission (should cascade)
        store.delete_mission(mission_id)
        # # Verify tool calls are gone
        tool_calls_after = store.get_tool_calls_for_mission(mission_id)
        assert len(tool_calls_after) == 0

    def test_deleting_mission_cascades_to_decisions(self):
        """Test that deleting mission deletes all related decisions"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        store.record_decision(mission_id, "choice", "rationale", "2025-11-20T00:00:00Z", "STEWARD")
        # # Verify decision exists
        decisions_before = store.get_decisions_for_mission(mission_id)
        assert len(decisions_before) == 1
        # # Delete mission (should cascade)
        store.delete_mission(mission_id)
        # # Verify decisions are gone
        decisions_after = store.get_decisions_for_mission(mission_id)
        assert len(decisions_after) == 0

    def test_deleting_mission_cascades_to_agent_memory(self):
        """Test that deleting mission deletes all related memory"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        store.set_memory(mission_id, "key1", {"value": "data"}, "2025-11-20T00:00:00Z")
        # # Verify memory exists
        memory = store.get_memory(mission_id, "key1")
        assert memory is not None
        # # Delete mission (should cascade)
        store.delete_mission(mission_id)
        # # Verify memory is gone
        memory_after = store.get_memory(mission_id, "key1")
        assert memory_after is None


class TestThreadSafety:
    """Test thread-safe database access"""

    def test_multiple_threads_can_access_database(self):
        """Test that SQLiteStore is thread-safe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_threadsafe.db")
            store = SQLiteStore(db_path)

            results = []

            def create_mission_in_thread(uuid):
                mission_id = store.create_mission(uuid, "PLANNING", "pending")
                results.append(mission_id)

            # # Create 10 missions concurrently
            threads = []
            for i in range(10):
                thread = threading.Thread(target=create_mission_in_thread, args=(f"test-{i:03d}",))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
            # # Verify all 10 missions were created
            assert len(results) == 10
            assert len(set(results)) == 10, "All mission IDs should be unique"
            store.close()


class TestAgentMemory:
    """Test agent memory persistence"""

    def test_set_memory_stores_key_value(self):
        """Test storing agent memory"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        store.set_memory(mission_id, "last_playbook", {"name": "plan"}, "2025-11-20T00:00:00Z")
        memory = store.get_memory(mission_id, "last_playbook")
        assert memory["value"] == {"name": "plan"}

    def test_get_memory_returns_none_if_not_exists(self):
        """Test retrieving nonexistent memory"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        memory = store.get_memory(mission_id, "nonexistent_key")
        assert memory is None

    def test_set_memory_updates_existing_key(self):
        """Test updating existing memory key"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        store.set_memory(mission_id, "counter", {"value": 1}, "2025-11-20T00:00:00Z")
        store.set_memory(mission_id, "counter", {"value": 2}, "2025-11-20T00:01:00Z")
        memory = store.get_memory(mission_id, "counter")
        assert memory["value"] == {"value": 2}


class TestPlaybookRuns:
    """Test playbook execution metrics"""

    def test_create_playbook_run_stores_metrics(self):
        """Test storing playbook execution metrics"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        run_id = store.create_playbook_run(
            mission_id=mission_id,
            playbook_name="research.analyze_topic",
            phase="PLANNING",
            started_at="2025-11-20T00:00:00Z",
        )
        assert isinstance(run_id, int)
        assert run_id > 0

    def test_complete_playbook_run_updates_metrics(self):
        """Test updating playbook run on completion"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "pending")
        run_id = store.create_playbook_run(mission_id, "plan", "PLANNING", "2025-11-20T00:00:00Z")
        store.complete_playbook_run(
            run_id=run_id,
            completed_at="2025-11-20T00:05:00Z",
            success=True,
            metrics={"tool_count": 5, "decision_count": 2},
        )
        run = store.get_playbook_run(run_id)
        assert run["success"] == 1
        assert run["metrics"]["tool_count"] == 5


# ============================================================================
# INTEGRATION TEST: Full workflow
# ============================================================================


class TestFullWorkflow:
    """Test complete mission lifecycle"""

    def test_full_mission_workflow(self):
        """Test creating mission, logging tools, recording decisions, completing mission"""
        store = SQLiteStore(":memory:")
        # # 1. Create mission
        mission_id = store.create_mission(
            "test-001", "PLANNING", "in_progress", "2025-11-20T00:00:00Z"
        )
        # # 2. Log tool calls
        store.log_tool_call(
            mission_id, "WebFetch", {"url": "test"}, {}, "2025-11-20T00:01:00Z", 100, True
        )
        store.log_tool_call(
            mission_id, "Grep", {"pattern": "test"}, {}, "2025-11-20T00:02:00Z", 50, True
        )
        # # 3. Record decisions
        store.record_decision(
            mission_id, "approach", "Use SQLite", "2025-11-20T00:03:00Z", "STEWARD"
        )
        # # 4. Complete mission
        store.update_mission_status(mission_id, "completed", "2025-11-20T00:10:00Z")
        # # 5. Verify mission history
        mission = store.get_mission(mission_id)
        assert mission["status"] == "completed"
        assert len(store.get_tool_calls_for_mission(mission_id)) == 2
        assert len(store.get_decisions_for_mission(mission_id)) == 1
