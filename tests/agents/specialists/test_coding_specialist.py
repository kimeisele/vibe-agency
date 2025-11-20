#!/usr/bin/env python3
"""
ARCH-007: CodingSpecialist Implementation Tests

Tests that verify CodingSpecialist correctly:
    1. Implements BaseSpecialist contract
    2. Validates CODING phase preconditions
    3. Enforces ToolSafetyGuard before file operations
    4. Logs all code modifications to SQLite
    5. Executes 5-phase coding workflow
    6. Returns correct phase transition

CRITICAL: These tests verify safety guarantees:
    - File operations must pass ToolSafetyGuard checks
    - Every code modification is logged to SQLite
    - Quality gates are enforced
"""

import json
from unittest.mock import MagicMock

import pytest
from agency_os.agents.specialists import CodingSpecialist

from agency_os.agents import MissionContext
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.store.sqlite_store import SQLiteStore

# ============================================================================
# TEST 1: INSTANTIATION
# ============================================================================


def test_coding_specialist_can_be_instantiated(tmp_path):
    """Test that CodingSpecialist can be instantiated with valid args"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-coding-001",
        phase="CODING",
        status="in_progress",
    )

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=None,  # No orchestrator needed for basic tests
        playbook_root=tmp_path,
    )

    assert specialist is not None
    assert specialist.role == "CODING"
    assert specialist.mission_id == mission_id


def test_coding_specialist_warns_without_orchestrator(tmp_path, caplog):
    """Test that CodingSpecialist logs warning when initialized without orchestrator"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-coding-002",
        phase="CODING",
        status="in_progress",
    )

    CodingSpecialist(
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


def test_validate_preconditions_passes_when_feature_spec_exists(tmp_path):
    """Test that validate_preconditions passes when feature_spec exists and phase is CODING"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-coding-003",
        phase="CODING",
        status="in_progress",
    )

    # Create mock orchestrator
    class MockOrchestrator:
        pass

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=MockOrchestrator(),
        playbook_root=tmp_path,
    )

    # Create feature_spec.json
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)
    feature_spec_path = project_root / "feature_spec.json"
    feature_spec_path.write_text(json.dumps({"version": "1.0"}))

    # Create context
    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-003",
        phase="CODING",
        project_root=project_root,
        metadata={},
    )

    # Validate preconditions
    result = specialist.validate_preconditions(context)
    assert result is True


def test_validate_preconditions_fails_when_feature_spec_missing(tmp_path):
    """Test that validate_preconditions fails when feature_spec.json is missing"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-coding-004",
        phase="CODING",
        status="in_progress",
    )

    class MockOrchestrator:
        pass

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=MockOrchestrator(),
        playbook_root=tmp_path,
    )

    # Create project root without feature_spec.json
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-004",
        phase="CODING",
        project_root=project_root,
        metadata={},
    )

    # Validate preconditions - should fail
    result = specialist.validate_preconditions(context)
    assert result is False


def test_validate_preconditions_fails_when_phase_wrong(tmp_path):
    """Test that validate_preconditions fails when current phase is not CODING"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    # Create mission with PLANNING phase (wrong phase)
    mission_id = store.create_mission(
        mission_uuid="test-coding-005",
        phase="PLANNING",  # Wrong phase!
        status="in_progress",
    )

    class MockOrchestrator:
        pass

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=MockOrchestrator(),
        playbook_root=tmp_path,
    )

    # Create feature_spec.json
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)
    feature_spec_path = project_root / "feature_spec.json"
    feature_spec_path.write_text(json.dumps({"version": "1.0"}))

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-005",
        phase="CODING",  # Context says CODING
        project_root=project_root,
        metadata={},
    )

    # Validate preconditions - should fail due to phase mismatch
    result = specialist.validate_preconditions(context)
    assert result is False


# ============================================================================
# TEST 3: SAFETY GUARD ENFORCEMENT
# ============================================================================


def test_coding_specialist_uses_tool_safety_guard_for_file_operations(tmp_path):
    """Test that CodingSpecialist enforces ToolSafetyGuard for file operations"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard(enable_strict_mode=True)  # Strict mode!

    mission_id = store.create_mission(
        mission_uuid="test-coding-006",
        phase="CODING",
        status="in_progress",
    )

    # Create mock orchestrator that returns code with file writes
    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = {"version": "1.0"}
    mock_orchestrator.active_manifest = MagicMock()

    # Simulate CODE_GENERATOR returning file operations
    mock_orchestrator.execute_agent.side_effect = [
        # Task 1: Spec validation
        {"spec_valid": True, "validation_errors": []},
        # Task 2: Code generation (file write without prior read - should fail!)
        {
            "files": [
                {"path": "hello.py", "content": "print('hello')", "language": "python"},
            ]
        },
    ]

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-006",
        phase="CODING",
        project_root=project_root,
        metadata={},
    )

    # Execute - should fail due to safety guard blocking write without read
    with pytest.raises(RuntimeError) as exc_info:
        specialist.execute(context)

    assert "safety guard" in str(exc_info.value).lower()


def test_coding_specialist_records_file_writes_to_safety_guard(tmp_path):
    """Test that CodingSpecialist records file writes to ToolSafetyGuard"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard(enable_strict_mode=False)  # Permissive mode for testing

    mission_id = store.create_mission(
        mission_uuid="test-coding-007",
        phase="CODING",
        status="in_progress",
    )

    # Create mock orchestrator that returns successful workflow
    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = {"version": "1.0"}
    mock_orchestrator.active_manifest = MagicMock()

    # Simulate full CODE_GENERATOR workflow
    mock_orchestrator.execute_agent.side_effect = [
        # Task 1: Spec validation
        {"spec_valid": True, "validation_errors": []},
        # Task 2: Code generation
        {
            "files": [
                {"path": "hello.py", "content": "print('hello')", "language": "python"},
            ]
        },
        # Task 3: Test generation
        {"tests": [{"path": "test_hello.py"}], "coverage_percent": 85},
        # Task 4: Docs generation
        {"docs": [{"path": "README.md"}]},
        # Task 5: Quality assurance
        {"quality_gates_passed": True, "failed_gates": []},
    ]

    mock_orchestrator.save_artifact.return_value = None

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-007",
        phase="CODING",
        project_root=project_root,
        metadata={},
    )

    # Execute workflow
    result = specialist.execute(context)

    # Verify file writes were recorded
    assert result.success is True
    assert len(guard.context.files_written) > 0
    assert any("hello.py" in path for path in guard.context.files_written)


# ============================================================================
# TEST 4: DECISION LOGGING
# ============================================================================


def test_coding_specialist_logs_decisions_to_sqlite(tmp_path):
    """Test that CodingSpecialist logs all decisions to SQLite"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard(enable_strict_mode=False)

    mission_id = store.create_mission(
        mission_uuid="test-coding-008",
        phase="CODING",
        status="in_progress",
    )

    # Create mock orchestrator
    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = {"version": "1.0"}
    mock_orchestrator.active_manifest = MagicMock()

    # Simulate full workflow
    mock_orchestrator.execute_agent.side_effect = [
        {"spec_valid": True, "validation_errors": []},
        {"files": [{"path": "hello.py", "content": "print('hello')", "language": "python"}]},
        {"tests": [], "coverage_percent": 0},
        {"docs": []},
        {"quality_gates_passed": True, "failed_gates": []},
    ]

    mock_orchestrator.save_artifact.return_value = None

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-008",
        phase="CODING",
        project_root=project_root,
        metadata={},
    )

    # Execute
    result = specialist.execute(context)
    assert result.success is True

    # Verify decisions were logged to SQLite
    decisions = store.get_decisions_for_mission(mission_id)
    assert len(decisions) > 0

    # Check for expected decision types
    decision_types = [d.get("decision_type") for d in decisions]
    assert "CODING_STARTED" in decision_types
    assert "SPEC_VALIDATED" in decision_types
    assert "CODE_MODIFICATION" in decision_types
    assert "QUALITY_GATES_CHECKED" in decision_types


def test_coding_specialist_logs_every_file_modification(tmp_path):
    """Test that every file modification is logged to SQLite"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard(enable_strict_mode=False)

    mission_id = store.create_mission(
        mission_uuid="test-coding-009",
        phase="CODING",
        status="in_progress",
    )

    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = {"version": "1.0"}
    mock_orchestrator.active_manifest = MagicMock()

    # Simulate generating 3 files
    mock_orchestrator.execute_agent.side_effect = [
        {"spec_valid": True, "validation_errors": []},
        {
            "files": [
                {"path": "file1.py", "content": "code1", "language": "python"},
                {"path": "file2.py", "content": "code2", "language": "python"},
                {"path": "file3.py", "content": "code3", "language": "python"},
            ]
        },
        {"tests": [], "coverage_percent": 0},
        {"docs": []},
        {"quality_gates_passed": True, "failed_gates": []},
    ]

    mock_orchestrator.save_artifact.return_value = None

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-009",
        phase="CODING",
        project_root=project_root,
        metadata={},
    )

    # Execute
    result = specialist.execute(context)
    assert result.success is True

    # Verify all 3 file modifications were logged
    decisions = store.get_decisions_for_mission(mission_id)
    code_modifications = [d for d in decisions if d.get("decision_type") == "CODE_MODIFICATION"]

    assert len(code_modifications) == 3
    file_paths = [d["context"].get("file_path") for d in code_modifications]
    assert "file1.py" in file_paths
    assert "file2.py" in file_paths
    assert "file3.py" in file_paths


# ============================================================================
# TEST 5: WORKFLOW EXECUTION
# ============================================================================


def test_coding_specialist_returns_correct_next_phase(tmp_path):
    """Test that CodingSpecialist returns TESTING as next phase"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard(enable_strict_mode=False)

    mission_id = store.create_mission(
        mission_uuid="test-coding-010",
        phase="CODING",
        status="in_progress",
    )

    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = {"version": "1.0"}
    mock_orchestrator.active_manifest = MagicMock()

    mock_orchestrator.execute_agent.side_effect = [
        {"spec_valid": True, "validation_errors": []},
        {"files": []},
        {"tests": [], "coverage_percent": 0},
        {"docs": []},
        {"quality_gates_passed": True, "failed_gates": []},
    ]

    mock_orchestrator.save_artifact.return_value = None

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-010",
        phase="CODING",
        project_root=project_root,
        metadata={},
    )

    # Execute
    result = specialist.execute(context)

    assert result.success is True
    assert result.next_phase == "TESTING"


def test_coding_specialist_fails_when_quality_gates_fail(tmp_path):
    """Test that CodingSpecialist fails when quality gates don't pass"""

    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard(enable_strict_mode=False)

    mission_id = store.create_mission(
        mission_uuid="test-coding-011",
        phase="CODING",
        status="in_progress",
    )

    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = {"version": "1.0"}
    mock_orchestrator.active_manifest = MagicMock()

    # Simulate quality gates failing
    mock_orchestrator.execute_agent.side_effect = [
        {"spec_valid": True, "validation_errors": []},
        {"files": []},
        {"tests": [], "coverage_percent": 0},
        {"docs": []},
        {"quality_gates_passed": False, "failed_gates": ["test_coverage_minimum"]},
    ]

    specialist = CodingSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-coding-011",
        phase="CODING",
        project_root=project_root,
        metadata={},
    )

    # Execute - should fail
    result = specialist.execute(context)

    assert result.success is False
    assert "quality gates" in result.error.lower()


# ============================================================================
# TEST 6: HAP PATTERN COMPLIANCE
# ============================================================================


def test_coding_specialist_implements_base_specialist_contract():
    """Test that CodingSpecialist properly implements BaseSpecialist interface"""
    from agency_os.agents import BaseSpecialist

    assert issubclass(CodingSpecialist, BaseSpecialist)

    # Verify required methods exist
    assert hasattr(CodingSpecialist, "execute")
    assert hasattr(CodingSpecialist, "validate_preconditions")
    assert hasattr(CodingSpecialist, "persist_state")
    assert hasattr(CodingSpecialist, "load_state")
