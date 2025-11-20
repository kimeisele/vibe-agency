"""
Test suite for SQLiteStore - SQLite persistence layer (Schema v2)

ARCH-002 Acceptance Criteria:
1. ✅ SQLiteStore class with CRUD methods
2. ✅ Auto-creates .vibe/state/vibe_agency.db on first boot
3. ✅ Handles schema migrations (PRAGMA user_version = 2)
4. ✅ Thread-safe (check_same_thread=False)
5. ✅ 15+ tests with 80% coverage

Schema v2 Updates:
- Missions table: +10 columns (budget, metadata, status fields)
- New tables: session_narrative, domain_concepts, domain_concerns, trajectory, artifacts, quality_gates
- Total: 11 tables (5 original + 6 new)

Test Strategy:
- Use in-memory DB for fast tests (:memory:)
- Test file-based DB for auto-creation behavior
- Verify schema v2 loaded correctly from ARCH-001_schema.sql
- Test foreign key constraints (CASCADE DELETE)
- Verify all CRUD operations for missions (v2 fields)
- TODO: Add tests for new tables (session_narrative, artifacts, etc.) in Part 2
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
        """Test that schema v2 is loaded from ARCH-001_schema.sql"""
        store = SQLiteStore(":memory:")
        # Verify all 11 tables exist (5 original + 6 new)
        cursor = store.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

        # Original tables (v1)
        assert "missions" in tables
        assert "tool_calls" in tables
        assert "decisions" in tables
        assert "playbook_runs" in tables
        assert "agent_memory" in tables

        # v2 new tables
        assert "session_narrative" in tables
        assert "domain_concepts" in tables
        assert "domain_concerns" in tables
        assert "trajectory" in tables
        assert "artifacts" in tables
        assert "quality_gates" in tables

        # Verify total count (11 user tables + sqlite_sequence)
        assert len(tables) == 12, f"Expected 12 tables (11 + sqlite_sequence), got {len(tables)}: {tables}"

    def test_init_sets_schema_version(self):
        """Test that PRAGMA user_version is set to 2"""
        store = SQLiteStore(":memory:")
        cursor = store.conn.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        assert version == 2, "Schema version should be 2 (v2 from ARCH-001)"

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

    # ========================================================================
    # v2 TESTS: Budget tracking, metadata extraction
    # ========================================================================

    def test_create_mission_with_budget_fields(self):
        """Test creating mission with budget tracking fields (v2)"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission(
            mission_uuid="test-budget-001",
            phase="PLANNING",
            status="in_progress",
            created_at="2025-11-20T00:00:00Z",
            max_cost_usd=100.0,
            current_cost_usd=25.0,
            alert_threshold=0.80,
            cost_breakdown={"PLANNING": 25.0},
        )

        mission = store.get_mission(mission_id)
        assert mission["max_cost_usd"] == 100.0
        assert mission["current_cost_usd"] == 25.0
        assert mission["alert_threshold"] == 0.80
        assert mission["cost_breakdown"] == {"PLANNING": 25.0}

    def test_create_mission_with_metadata_fields(self):
        """Test creating mission with metadata extraction fields (v2)"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission(
            mission_uuid="test-metadata-001",
            phase="CODING",
            status="in_progress",
            created_at="2025-11-20T00:00:00Z",
            owner="agent@vibe.agency",
            description="Test project for schema v2",
            api_version="agency.os/v1alpha1",
        )

        mission = store.get_mission(mission_id)
        assert mission["owner"] == "agent@vibe.agency"
        assert mission["description"] == "Test project for schema v2"
        assert mission["api_version"] == "agency.os/v1alpha1"

    def test_create_mission_with_planning_sub_state(self):
        """Test creating mission with planning_sub_state field (v2)"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission(
            mission_uuid="test-substate-001",
            phase="PLANNING",
            status="in_progress",
            created_at="2025-11-20T00:00:00Z",
            planning_sub_state="RESEARCH",
        )

        mission = store.get_mission(mission_id)
        assert mission["planning_sub_state"] == "RESEARCH"

    def test_create_mission_with_updated_at(self):
        """Test creating mission with updated_at field (v2)"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission(
            mission_uuid="test-updated-001",
            phase="CODING",
            status="in_progress",
            created_at="2025-11-20T00:00:00Z",
            updated_at="2025-11-20T01:00:00Z",
        )

        mission = store.get_mission(mission_id)
        assert mission["updated_at"] == "2025-11-20T01:00:00Z"

    def test_update_mission_budget(self):
        """Test updating mission budget (v2)"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission(
            mission_uuid="test-budget-update-001",
            phase="PLANNING",
            status="in_progress",
            created_at="2025-11-20T00:00:00Z",
            max_cost_usd=100.0,
            current_cost_usd=25.0,
        )

        # Update budget
        store.update_mission_budget(mission_id, current_cost_usd=50.0)
        mission = store.get_mission(mission_id)
        assert mission["current_cost_usd"] == 50.0

    def test_query_missions_over_budget(self):
        """Test querying missions that exceed budget (v2)"""
        store = SQLiteStore(":memory:")

        # Mission 1: Under budget
        store.create_mission(
            "test-001",
            "PLANNING",
            "in_progress",
            created_at="2025-11-20T00:00:00Z",
            max_cost_usd=100.0,
            current_cost_usd=50.0,
        )

        # Mission 2: Over budget
        store.create_mission(
            "test-002",
            "CODING",
            "in_progress",
            created_at="2025-11-20T00:00:00Z",
            max_cost_usd=100.0,
            current_cost_usd=150.0,
        )

        # Query missions over budget
        over_budget = store.get_missions_over_budget()
        assert len(over_budget) == 1
        assert over_budget[0]["mission_uuid"] == "test-002"

    def test_query_missions_by_owner(self):
        """Test querying missions by owner (v2)"""
        store = SQLiteStore(":memory:")

        store.create_mission(
            "test-001",
            "PLANNING",
            "in_progress",
            created_at="2025-11-20T00:00:00Z",
            owner="agent1@vibe.agency",
        )
        store.create_mission(
            "test-002",
            "CODING",
            "in_progress",
            created_at="2025-11-20T00:00:00Z",
            owner="agent2@vibe.agency",
        )

        # Query missions by owner
        agent1_missions = store.get_missions_by_owner("agent1@vibe.agency")
        assert len(agent1_missions) == 1
        assert agent1_missions[0]["mission_uuid"] == "test-001"


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


class TestSessionNarrative:
    """Test session narrative (v2 - ProjectMemory)"""

    def test_add_session_narrative(self):
        """Test adding session narrative"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        session_id = store.add_session_narrative(
            mission_id=mission_id,
            session_num=1,
            summary="Completed planning phase",
            date="2025-11-20T00:00:00Z",
            phase="PLANNING",
        )
        assert isinstance(session_id, int)
        assert session_id > 0

    def test_get_session_narrative(self):
        """Test retrieving session narrative"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        store.add_session_narrative(mission_id, 1, "Session 1", "2025-11-20T00:00:00Z", "PLANNING")
        store.add_session_narrative(mission_id, 2, "Session 2", "2025-11-20T01:00:00Z", "CODING")

        narrative = store.get_session_narrative(mission_id)
        assert len(narrative) == 2
        assert narrative[0]["session_num"] == 1
        assert narrative[1]["session_num"] == 2


class TestArtifacts:
    """Test artifacts (v2 - SDLC tracking)"""

    def test_add_artifact(self):
        """Test adding artifact"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        artifact_id = store.add_artifact(
            mission_id=mission_id,
            artifact_type="planning",
            artifact_name="architecture",
            created_at="2025-11-20T00:00:00Z",
            ref="abc123",
            path="/artifacts/planning/architecture.json",
        )
        assert isinstance(artifact_id, int)
        assert artifact_id > 0

    def test_get_artifacts(self):
        """Test retrieving artifacts"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        store.add_artifact(mission_id, "planning", "arch", "2025-11-20T00:00:00Z")
        store.add_artifact(mission_id, "code", "repo", "2025-11-20T01:00:00Z")

        artifacts = store.get_artifacts(mission_id)
        assert len(artifacts) == 2

        planning_artifacts = store.get_artifacts(mission_id, "planning")
        assert len(planning_artifacts) == 1
        assert planning_artifacts[0]["artifact_type"] == "planning"


class TestQualityGates:
    """Test quality gates (v2 - GAD-004)"""

    def test_record_quality_gate(self):
        """Test recording quality gate"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        gate_id = store.record_quality_gate(
            mission_id=mission_id,
            gate_name="TEST_COVERAGE",
            status="passed",
            timestamp="2025-11-20T00:00:00Z",
            details={"coverage": 85},
        )
        assert isinstance(gate_id, int)
        assert gate_id > 0

    def test_get_quality_gates(self):
        """Test retrieving quality gates"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        store.record_quality_gate(mission_id, "GATE1", "passed", "2025-11-20T00:00:00Z")
        store.record_quality_gate(mission_id, "GATE2", "failed", "2025-11-20T01:00:00Z")

        gates = store.get_quality_gates(mission_id)
        assert len(gates) == 2
        assert gates[0]["gate_name"] == "GATE1"
        assert gates[1]["status"] == "failed"


class TestDomainTracking:
    """Test domain concepts and concerns (v2 - ProjectMemory)"""

    def test_add_domain_concept(self):
        """Test adding domain concept"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        concept_id = store.add_domain_concept(mission_id, "payment", "2025-11-20T00:00:00Z")
        assert isinstance(concept_id, int)
        assert concept_id > 0

    def test_get_domain_concepts(self):
        """Test retrieving domain concepts"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        store.add_domain_concept(mission_id, "payment", "2025-11-20T00:00:00Z")
        store.add_domain_concept(mission_id, "database", "2025-11-20T01:00:00Z")

        concepts = store.get_domain_concepts(mission_id)
        assert len(concepts) == 2
        assert "payment" in concepts
        assert "database" in concepts

    def test_add_domain_concern(self):
        """Test adding domain concern"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        concern_id = store.add_domain_concern(mission_id, "PCI compliance", "2025-11-20T00:00:00Z")
        assert isinstance(concern_id, int)
        assert concern_id > 0

    def test_get_domain_concerns(self):
        """Test retrieving domain concerns"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        store.add_domain_concern(mission_id, "PCI compliance", "2025-11-20T00:00:00Z")
        store.add_domain_concern(mission_id, "performance", "2025-11-20T01:00:00Z")

        concerns = store.get_domain_concerns(mission_id)
        assert len(concerns) == 2
        assert "PCI compliance" in concerns
        assert "performance" in concerns


class TestTrajectory:
    """Test trajectory (v2 - ProjectMemory)"""

    def test_set_trajectory(self):
        """Test setting trajectory"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        store.set_trajectory(
            mission_id=mission_id,
            current_phase="CODING",
            current_focus="payment integration",
            completed_phases=["PLANNING"],
            blockers=["5 failing tests"],
            updated_at="2025-11-20T00:00:00Z",
        )

        trajectory = store.get_trajectory(mission_id)
        assert trajectory is not None
        assert trajectory["current_phase"] == "CODING"
        assert trajectory["current_focus"] == "payment integration"
        assert trajectory["completed_phases"] == ["PLANNING"]
        assert trajectory["blockers"] == ["5 failing tests"]

    def test_update_trajectory(self):
        """Test updating trajectory (UPSERT)"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        # First set
        store.set_trajectory(mission_id, "PLANNING", "2025-11-20T00:00:00Z")

        # Update
        store.set_trajectory(
            mission_id, "CODING", "2025-11-20T01:00:00Z", current_focus="testing"
        )

        trajectory = store.get_trajectory(mission_id)
        assert trajectory["current_phase"] == "CODING"
        assert trajectory["current_focus"] == "testing"


class TestProjectMemoryAdapter:
    """Test ProjectMemory flattening adapter (v2)"""

    def test_map_project_memory_to_sql(self):
        """Test flattening project_memory.json into SQL tables"""
        store = SQLiteStore(":memory:")
        mission_id = store.create_mission("test-001", "PLANNING", "in_progress")

        memory = {
            "narrative": [
                {"session": 1, "summary": "Session 1", "date": "2025-11-20T00:00:00Z", "phase": "PLANNING"},
                {"session": 2, "summary": "Session 2", "date": "2025-11-20T01:00:00Z", "phase": "CODING"},
            ],
            "domain": {
                "concepts": ["payment", "database", "authentication"],
                "concerns": ["PCI compliance", "performance"],
            },
            "trajectory": {
                "phase": "CODING",
                "current_focus": "payment integration",
                "completed": ["PLANNING"],
                "blockers": ["5 failing tests"],
            },
        }

        store._map_project_memory_to_sql(memory, mission_id, "2025-11-20T00:00:00Z")

        # Verify session narrative
        narrative = store.get_session_narrative(mission_id)
        assert len(narrative) == 2
        assert narrative[0]["summary"] == "Session 1"

        # Verify domain concepts
        concepts = store.get_domain_concepts(mission_id)
        assert len(concepts) == 3
        assert "payment" in concepts

        # Verify domain concerns
        concerns = store.get_domain_concerns(mission_id)
        assert len(concerns) == 2
        assert "PCI compliance" in concerns

        # Verify trajectory
        trajectory = store.get_trajectory(mission_id)
        assert trajectory["current_phase"] == "CODING"
        assert trajectory["current_focus"] == "payment integration"
        assert trajectory["blockers"] == ["5 failing tests"]


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

    def test_full_v2_workflow(self):
        """Test full v2 workflow with ProjectMemory and artifacts"""
        store = SQLiteStore(":memory:")

        # 1. Create mission with budget
        mission_id = store.create_mission(
            "test-v2-001",
            "PLANNING",
            "in_progress",
            created_at="2025-11-20T00:00:00Z",
            max_cost_usd=100.0,
            owner="agent@vibe.agency",
            description="Test v2 mission",
        )

        # 2. Add session narrative
        store.add_session_narrative(mission_id, 1, "Planning complete", "2025-11-20T00:00:00Z", "PLANNING")

        # 3. Add artifacts
        store.add_artifact(mission_id, "planning", "architecture", "2025-11-20T00:00:00Z")

        # 4. Record quality gate
        store.record_quality_gate(mission_id, "PLANNING_GATE", "passed", "2025-11-20T00:00:00Z")

        # 5. Set trajectory
        store.set_trajectory(
            mission_id, "CODING", "2025-11-20T00:00:00Z", completed_phases=["PLANNING"]
        )

        # 6. Verify all data
        mission = store.get_mission(mission_id)
        assert mission["owner"] == "agent@vibe.agency"
        assert len(store.get_session_narrative(mission_id)) == 1
        assert len(store.get_artifacts(mission_id)) == 1
        assert len(store.get_quality_gates(mission_id)) == 1
        trajectory = store.get_trajectory(mission_id)
        assert trajectory["current_phase"] == "CODING"


# =============================================================================
# ARCH-003: DUAL WRITE MODE (Shadow Mode Phase 1)
# =============================================================================


class TestProjectManifestImport:
    """Test import_project_manifest method (ARCH-003)"""

    def test_import_project_manifest_creates_mission(self):
        """Test importing project_manifest.json creates mission with all fields"""
        store = SQLiteStore(":memory:")

        manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test-manifest-001",
                "name": "Test Manifest Import",
                "description": "Testing manifest import",
                "owner": "test@vibe.agency",
                "createdAt": "2025-11-20T00:00:00Z",
                "lastUpdatedAt": "2025-11-20T01:00:00Z",
            },
            "status": {
                "projectPhase": "CODING",
                "planningSubState": None,
                "lastUpdate": "2025-11-20T01:00:00Z",
                "message": "Test in progress",
            },
            "budget": {
                "max_cost_usd": 50.0,
                "current_cost_usd": 15.0,
                "alert_threshold": 0.75,
                "cost_breakdown": {"PLANNING": 5.0, "CODING": 10.0},
            },
            "artifacts": {
                "planning": {"feature_spec": "specs/feature.json"},
                "code": {"repo": "github.com/test/repo"},
            },
        }

        mission_id = store.import_project_manifest(manifest)

        # Verify mission was created
        assert mission_id > 0

        mission = store.get_mission(mission_id)
        assert mission["mission_uuid"] == "test-manifest-001"
        assert mission["phase"] == "CODING"
        assert mission["status"] == "in_progress"
        assert mission["owner"] == "test@vibe.agency"
        assert mission["description"] == "Testing manifest import"
        assert mission["max_cost_usd"] == 50.0
        assert mission["current_cost_usd"] == 15.0
        assert mission["alert_threshold"] == 0.75

    def test_import_project_manifest_with_memory(self):
        """Test importing project_manifest with project_memory"""
        store = SQLiteStore(":memory:")

        manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test-manifest-002",
                "name": "Test With Memory",
                "owner": "test@vibe.agency",
                "createdAt": "2025-11-20T00:00:00Z",
            },
            "status": {
                "projectPhase": "TESTING",
                "lastUpdate": "2025-11-20T01:00:00Z",
            },
            "budget": {"max_cost_usd": 100.0},
        }

        project_memory = {
            "narrative": [
                {
                    "session": 1,
                    "summary": "Initial setup",
                    "date": "2025-11-20T00:00:00Z",
                    "phase": "PLANNING",
                },
                {
                    "session": 2,
                    "summary": "Built core features",
                    "date": "2025-11-20T01:00:00Z",
                    "phase": "CODING",
                },
            ],
            "domain": {
                "concepts": ["authentication", "database"],
                "concerns": ["security", "performance"],
            },
            "trajectory": {
                "phase": "TESTING",
                "current_focus": "Integration tests",
                "completed": ["PLANNING", "CODING"],
                "blockers": [],
            },
        }

        mission_id = store.import_project_manifest(manifest, project_memory)

        # Verify mission created
        assert mission_id > 0

        # Verify memory imported
        narrative = store.get_session_narrative(mission_id)
        assert len(narrative) == 2
        assert narrative[0]["summary"] == "Initial setup"
        assert narrative[1]["summary"] == "Built core features"

        concepts = store.get_domain_concepts(mission_id)
        assert len(concepts) == 2

        concerns = store.get_domain_concerns(mission_id)
        assert len(concerns) == 2

        trajectory = store.get_trajectory(mission_id)
        assert trajectory["current_phase"] == "TESTING"
        assert trajectory["current_focus"] == "Integration tests"

    def test_import_project_manifest_idempotent(self):
        """Test that importing same manifest twice updates instead of duplicating"""
        store = SQLiteStore(":memory:")

        manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test-idempotent-001",
                "name": "Test Idempotent",
                "owner": "test@vibe.agency",
                "createdAt": "2025-11-20T00:00:00Z",
            },
            "status": {"projectPhase": "PLANNING", "lastUpdate": "2025-11-20T00:00:00Z"},
            "budget": {"max_cost_usd": 100.0, "current_cost_usd": 10.0},
        }

        # Import first time
        mission_id_1 = store.import_project_manifest(manifest)

        # Modify manifest
        manifest["budget"]["current_cost_usd"] = 25.0
        manifest["status"]["projectPhase"] = "CODING"

        # Import second time (should update, not create new)
        mission_id_2 = store.import_project_manifest(manifest)

        # Should be same mission ID
        assert mission_id_1 == mission_id_2

        # Verify updated values
        mission = store.get_mission(mission_id_1)
        assert mission["current_cost_usd"] == 25.0
        assert mission["phase"] == "CODING"

        # Verify no duplicates
        all_missions = store.get_mission_history()
        assert len(all_missions) == 1

    def test_import_real_project_manifest(self):
        """Test importing a real project_manifest.json from workspaces"""
        import json
        from pathlib import Path

        store = SQLiteStore(":memory:")

        # Load real manifest from workspaces
        manifest_path = Path("workspaces/test_orchestrator/project_manifest.json")
        if not manifest_path.exists():
            # Skip if workspace doesn't exist (CI environment)
            return

        with open(manifest_path) as f:
            manifest = json.load(f)

        # Import real manifest
        mission_id = store.import_project_manifest(manifest)

        # Verify it was imported correctly
        assert mission_id > 0

        mission = store.get_mission(mission_id)
        assert mission["mission_uuid"] == "test-orchestrator-003"
        assert mission["phase"] == "PLANNING"
        assert mission["owner"] == "system"
        assert mission["description"] == "Test delegated execution architecture (Claude Code integration)"
        assert mission["max_cost_usd"] == 10.0
        assert mission["current_cost_usd"] == 0.0
        assert mission["planning_sub_state"] == "BUSINESS_VALIDATION"
