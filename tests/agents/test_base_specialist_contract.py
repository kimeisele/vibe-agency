#!/usr/bin/env python3
"""
ARCH-005: BaseSpecialist Contract Verification Tests

Tests that verify the BaseSpecialist abstract base class contract is enforced.

Test Coverage:
    1. ABC mechanism prevents direct instantiation
    2. ABC mechanism prevents incomplete subclass instantiation
    3. Complete subclass can be instantiated
    4. Lifecycle methods work correctly
    5. Persistence methods work correctly
    6. Helper methods work correctly
"""

from pathlib import Path

import pytest

from agency_os.agents import BaseSpecialist, MissionContext, SpecialistResult
from agency_os.core_system.runtime.tool_safety_guard import ToolSafetyGuard
from agency_os.persistence.sqlite_store import SQLiteStore

# ============================================================================
# TEST 1: ABC ENFORCEMENT
# ============================================================================


def test_cannot_instantiate_base_specialist_directly():
    """Test that BaseSpecialist cannot be instantiated directly (ABC)"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    # Attempt to instantiate BaseSpecialist directly should fail
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseSpecialist(
            role="TEST",
            mission_id=1,
            sqlite_store=store,
            tool_safety_guard=guard,
        )


def test_incomplete_specialist_cannot_be_instantiated():
    """Test that incomplete specialist (missing abstract methods) cannot be instantiated"""

    # Define incomplete specialist (missing validate_preconditions)
    class IncompleteSpecialist(BaseSpecialist):
        def execute(self, context: MissionContext) -> SpecialistResult:
            return SpecialistResult(success=True)

        # Missing: validate_preconditions()

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    # Attempt to instantiate incomplete specialist should fail
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompleteSpecialist(
            role="INCOMPLETE",
            mission_id=1,
            sqlite_store=store,
            tool_safety_guard=guard,
        )


# ============================================================================
# TEST 2: COMPLETE IMPLEMENTATION
# ============================================================================


class MinimalSpecialist(BaseSpecialist):
    """Minimal complete specialist for testing"""

    def execute(self, context: MissionContext) -> SpecialistResult:
        """Minimal execute implementation"""
        return SpecialistResult(success=True, next_phase="NEXT")

    def validate_preconditions(self, context: MissionContext) -> bool:
        """Minimal precondition validation"""
        return True


def test_complete_specialist_can_be_instantiated(tmp_path):
    """Test that complete specialist (all abstract methods implemented) can be instantiated"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    # Create mission
    mission_id = store.create_mission(
        mission_uuid="test-001", phase="TESTING", status="in_progress"
    )

    # Should succeed
    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,  # Use tmp_path for testing
    )

    assert specialist is not None
    assert specialist.role == "TESTING"
    assert specialist.mission_id == mission_id


def test_specialist_requires_valid_constructor_args(tmp_path):
    """Test that specialist validates constructor arguments"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    # Test: empty role should fail
    with pytest.raises(ValueError, match="role is REQUIRED"):
        MinimalSpecialist(
            role="",
            mission_id=1,
            sqlite_store=store,
            tool_safety_guard=guard,
            playbook_root=tmp_path,
        )

    # Test: invalid mission_id should fail
    with pytest.raises(ValueError, match="mission_id must be positive"):
        MinimalSpecialist(
            role="TEST",
            mission_id=0,
            sqlite_store=store,
            tool_safety_guard=guard,
            playbook_root=tmp_path,
        )


# ============================================================================
# TEST 3: LIFECYCLE METHODS
# ============================================================================


def test_lifecycle_hooks_are_called(tmp_path):
    """Test that lifecycle hooks (on_start, on_complete, on_error) work"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001", phase="TESTING", status="in_progress"
    )

    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-001",
        phase="TESTING",
        project_root=Path("/tmp"),
        metadata={},
    )

    # Test on_start hook
    specialist.on_start(context)
    assert specialist.started_at is not None

    # Test on_complete hook
    result = SpecialistResult(success=True)
    specialist.on_complete(context, result)
    assert specialist.completed_at is not None


def test_on_error_hook_persists_state(tmp_path):
    """Test that on_error hook persists partial state"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001", phase="TESTING", status="in_progress"
    )

    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-001",
        phase="TESTING",
        project_root=Path("/tmp"),
        metadata={},
    )

    # Simulate error
    error = ValueError("Test error")
    result = specialist.on_error(context, error)

    # Assert error result returned
    assert result.success is False
    assert "Test error" in result.error

    # Assert state was persisted
    assert "error" in specialist.state
    assert "failed_at" in specialist.state


# ============================================================================
# TEST 4: PERSISTENCE METHODS
# ============================================================================


def test_persist_state_saves_to_database(tmp_path):
    """Test that persist_state() saves state to SQLite"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001", phase="TESTING", status="in_progress"
    )

    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    # Set some state
    specialist.state = {"test_key": "test_value", "count": 42}

    # Persist state
    specialist.persist_state()

    # Verify state was saved as decision
    decisions = store.get_decisions_for_mission(mission_id)
    assert len(decisions) > 0

    # Find STATE_CHECKPOINT decision
    checkpoints = [d for d in decisions if d.get("decision_type") == "STATE_CHECKPOINT"]
    assert len(checkpoints) > 0

    # Verify state data
    checkpoint = checkpoints[0]
    assert checkpoint["context"]["test_key"] == "test_value"
    assert checkpoint["context"]["count"] == 42


def test_load_state_restores_from_database(tmp_path):
    """Test that load_state() restores state from SQLite"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001", phase="TESTING", status="in_progress"
    )

    # Create first specialist and save state
    specialist1 = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    specialist1.state = {"checkpoint": "data", "progress": 75}
    specialist1.persist_state()

    # Create second specialist and load state (simulates crash recovery)
    specialist2 = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    loaded_state = specialist2.load_state()

    # Verify state was restored
    assert loaded_state["checkpoint"] == "data"
    assert loaded_state["progress"] == 75
    assert specialist2.state["checkpoint"] == "data"


# ============================================================================
# TEST 5: HELPER METHODS
# ============================================================================


def test_log_decision_creates_audit_trail(tmp_path):
    """Test that _log_decision() creates audit trail in SQLite"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001", phase="TESTING", status="in_progress"
    )

    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    # Log a decision
    specialist._log_decision(
        decision_type="ARCHITECTURE_CHOICE",
        rationale="Chose microservices for scalability",
        data={"pattern": "microservices", "services": 5},
    )

    # Verify decision was logged
    decisions = store.get_decisions_for_mission(mission_id)
    assert len(decisions) > 0

    decision = decisions[0]
    assert decision["decision_type"] == "ARCHITECTURE_CHOICE"
    assert "microservices" in decision["rationale"]
    assert decision["context"]["pattern"] == "microservices"


def test_get_mission_data_returns_mission(tmp_path):
    """Test that get_mission_data() returns full mission record"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001",
        phase="TESTING",
        status="in_progress",
        owner="test@vibe.agency",
        description="Test mission",
    )

    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    # Get mission data
    mission = specialist.get_mission_data()

    assert mission["id"] == mission_id
    assert mission["mission_uuid"] == "test-001"
    assert mission["phase"] == "TESTING"
    assert mission["owner"] == "test@vibe.agency"


def test_get_mission_data_raises_if_mission_not_found(tmp_path):
    """Test that get_mission_data() raises ValueError if mission not found"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    # Create specialist with non-existent mission_id
    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=999,  # Non-existent
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    # Should raise ValueError
    with pytest.raises(ValueError, match="Mission not found"):
        specialist.get_mission_data()


# ============================================================================
# TEST 6: PLAYBOOK INTEGRATION
# ============================================================================


def test_load_playbook_raises_if_not_found(tmp_path):
    """Test that _load_playbook() raises FileNotFoundError if playbook missing"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001", phase="TESTING", status="in_progress"
    )

    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    # Attempt to load non-existent playbook
    with pytest.raises(FileNotFoundError, match="Playbook not found"):
        specialist._load_playbook("non_existent_playbook.yaml")


# ============================================================================
# TEST 7: STRING REPRESENTATION
# ============================================================================


def test_specialist_repr(tmp_path):
    """Test that __repr__ returns useful string representation"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-001", phase="TESTING", status="in_progress"
    )

    specialist = MinimalSpecialist(
        role="TESTING",
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    repr_str = repr(specialist)

    assert "MinimalSpecialist" in repr_str
    assert "TESTING" in repr_str
    assert str(mission_id) in repr_str
