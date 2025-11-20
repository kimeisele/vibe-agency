#!/usr/bin/env python3
"""
ARCH-006: PlanningSpecialist Implementation Tests

Tests that verify PlanningSpecialist correctly:
    1. Implements BaseSpecialist contract
    2. Validates PLANNING phase preconditions
    3. Executes planning workflow successfully
    4. Logs decisions to SQLite
    5. Generates architecture artifacts
    6. Returns correct phase transition
"""

import json

from agency_os.agents import MissionContext, PlanningSpecialist
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.store.sqlite_store import SQLiteStore

# ============================================================================
# TEST 1: INSTANTIATION
# ============================================================================


def test_planning_specialist_can_be_instantiated(tmp_path):
    """Test that PlanningSpecialist can be instantiated with valid args"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-001",
        phase="PLANNING",
        status="in_progress",
    )

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=None,  # No orchestrator needed for basic tests
        playbook_root=tmp_path,
    )

    assert specialist is not None
    assert specialist.role == "PLANNING"
    assert specialist.mission_id == mission_id


def test_planning_specialist_warns_without_orchestrator(tmp_path, caplog):
    """Test that PlanningSpecialist logs warning when initialized without orchestrator"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-002",
        phase="PLANNING",
        status="in_progress",
    )

    PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=None,
        playbook_root=tmp_path,
    )

    # Check warning was logged
    assert any("initialized without orchestrator" in record.message for record in caplog.records)


# ============================================================================
# TEST 2: PRECONDITION VALIDATION
# ============================================================================


def test_validate_preconditions_passes_when_manifest_exists(tmp_path):
    """Test that validate_preconditions passes when manifest exists and phase is PLANNING"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-003",
        phase="PLANNING",
        status="in_progress",
    )

    # Create mock orchestrator
    class MockOrchestrator:
        pass

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=MockOrchestrator(),
        playbook_root=tmp_path,
    )

    # Create manifest
    manifest_path = tmp_path / "project_manifest.json"
    manifest_path.write_text(json.dumps({"metadata": {"name": "test-project"}}))

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-planning-003",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Should pass
    assert specialist.validate_preconditions(context) is True


def test_validate_preconditions_fails_when_manifest_missing(tmp_path):
    """Test that validate_preconditions fails when manifest does not exist"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-004",
        phase="PLANNING",
        status="in_progress",
    )

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-planning-004",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # No manifest created - should fail
    assert specialist.validate_preconditions(context) is False


def test_validate_preconditions_fails_when_wrong_phase(tmp_path):
    """Test that validate_preconditions fails when mission phase is not PLANNING"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    # Create mission in CODING phase (wrong phase)
    mission_id = store.create_mission(
        mission_uuid="test-planning-005",
        phase="CODING",
        status="in_progress",
    )

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        playbook_root=tmp_path,
    )

    # Create manifest
    manifest_path = tmp_path / "project_manifest.json"
    manifest_path.write_text(json.dumps({"metadata": {"name": "test-project"}}))

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-planning-005",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Should fail because mission phase is CODING, not PLANNING
    assert specialist.validate_preconditions(context) is False


def test_validate_preconditions_fails_without_orchestrator(tmp_path):
    """Test that validate_preconditions fails when orchestrator is not available"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-006",
        phase="PLANNING",
        status="in_progress",
    )

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=None,  # No orchestrator
        playbook_root=tmp_path,
    )

    # Create manifest
    manifest_path = tmp_path / "project_manifest.json"
    manifest_path.write_text(json.dumps({"metadata": {"name": "test-project"}}))

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-planning-006",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Should fail because orchestrator is required (temporary requirement)
    assert specialist.validate_preconditions(context) is False


# ============================================================================
# TEST 3: WORKFLOW EXECUTION
# ============================================================================


def test_execute_generates_architecture_artifact(tmp_path):
    """Test that execute() generates architecture.json artifact"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-007",
        phase="PLANNING",
        status="in_progress",
    )

    # Create mock orchestrator (minimal for testing)
    class MockOrchestrator:
        pass

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=MockOrchestrator(),
        playbook_root=tmp_path,
    )

    # Create manifest
    manifest_path = tmp_path / "project_manifest.json"
    manifest_data = {
        "metadata": {
            "name": "test-project",
            "description": "A test project for architecture generation",
        }
    }
    manifest_path.write_text(json.dumps(manifest_data))

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-planning-007",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Execute workflow
    result = specialist.execute(context)

    # Assert: Result is successful
    assert result.success is True
    assert result.next_phase == "CODING"
    assert len(result.artifacts) > 0

    # Assert: Architecture artifact was created
    artifact_path = tmp_path / "artifacts" / "planning" / "architecture.json"
    assert artifact_path.exists()

    # Assert: Architecture contains expected data
    with open(artifact_path) as f:
        architecture = json.load(f)

    assert architecture["name"] == "test-project"
    assert architecture["description"] == "A test project for architecture generation"
    assert "components" in architecture
    assert "tech_stack" in architecture
    assert architecture["generated_by"] == "PlanningSpecialist"
    assert architecture["mission_id"] == mission_id


def test_execute_logs_decisions_to_sqlite(tmp_path):
    """Test that execute() logs decisions to SQLite database"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-008",
        phase="PLANNING",
        status="in_progress",
    )

    class MockOrchestrator:
        pass

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=MockOrchestrator(),
        playbook_root=tmp_path,
    )

    # Create manifest
    manifest_path = tmp_path / "project_manifest.json"
    manifest_path.write_text(json.dumps({"metadata": {"name": "test-project"}}))

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-planning-008",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Execute workflow
    result = specialist.execute(context)

    # Assert: Result is successful
    assert result.success is True

    # Assert: Decisions were logged to SQLite
    decisions = store.get_decisions_for_mission(mission_id)
    assert len(decisions) > 0

    # Find PLANNING_STARTED decision
    planning_started = [d for d in decisions if d["decision_type"] == "PLANNING_STARTED"]
    assert len(planning_started) > 0
    assert "Beginning PLANNING phase" in planning_started[0]["rationale"]

    # Find ARCHITECTURE_GENERATED decision
    arch_generated = [d for d in decisions if d["decision_type"] == "ARCHITECTURE_GENERATED"]
    assert len(arch_generated) > 0
    assert "architecture" in arch_generated[0]["rationale"]


def test_execute_returns_correct_phase_transition(tmp_path):
    """Test that execute() returns next_phase='CODING' for successful execution"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-009",
        phase="PLANNING",
        status="in_progress",
    )

    class MockOrchestrator:
        pass

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=MockOrchestrator(),
        playbook_root=tmp_path,
    )

    # Create manifest
    manifest_path = tmp_path / "project_manifest.json"
    manifest_path.write_text(json.dumps({"metadata": {"name": "test-project"}}))

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-planning-009",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Execute workflow
    result = specialist.execute(context)

    # Assert: Phase transition is correct
    assert result.next_phase == "CODING"
    assert result.success is True


# ============================================================================
# TEST 4: ARTIFACT GENERATION
# ============================================================================


def test_generate_architecture_uses_manifest_data(tmp_path):
    """Test that _generate_architecture() uses data from project manifest"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-planning-010",
        phase="PLANNING",
        status="in_progress",
    )

    class MockOrchestrator:
        pass

    specialist = PlanningSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=MockOrchestrator(),
        playbook_root=tmp_path,
    )

    # Create manifest with specific data
    manifest_path = tmp_path / "project_manifest.json"
    manifest_data = {
        "metadata": {
            "name": "custom-project-name",
            "description": "Custom project description with specific requirements",
        }
    }
    manifest_path.write_text(json.dumps(manifest_data))

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-planning-010",
        phase="PLANNING",
        project_root=tmp_path,
        metadata={},
    )

    # Execute workflow
    specialist.execute(context)

    # Load generated architecture
    artifact_path = tmp_path / "artifacts" / "planning" / "architecture.json"
    with open(artifact_path) as f:
        architecture = json.load(f)

    # Assert: Architecture uses manifest data
    assert architecture["name"] == "custom-project-name"
    assert architecture["description"] == "Custom project description with specific requirements"


# ============================================================================
# TEST 5: INTEGRATION WITH BASE SPECIALIST
# ============================================================================


def test_planning_specialist_inherits_from_base_specialist():
    """Test that PlanningSpecialist correctly inherits from BaseSpecialist"""

    from agency_os.agents import BaseSpecialist

    assert issubclass(PlanningSpecialist, BaseSpecialist)


def test_planning_specialist_implements_required_methods():
    """Test that PlanningSpecialist implements all required abstract methods"""

    # Check that required methods exist
    assert hasattr(PlanningSpecialist, "execute")
    assert hasattr(PlanningSpecialist, "validate_preconditions")

    # Check that methods are callable
    assert callable(PlanningSpecialist.execute)
    assert callable(PlanningSpecialist.validate_preconditions)
