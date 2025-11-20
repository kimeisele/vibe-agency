#!/usr/bin/env python3
"""
ARCH-008: HAP Pattern Scale-Out Verification Tests

Tests that verify all 3 new specialists (Testing, Deployment, Maintenance) correctly:
    1. Inherit from BaseSpecialist
    2. Validate preconditions correctly
    3. Log lifecycle events to SQLite (start/end)
    4. Follow HAP pattern consistently

This test proves the HAP pattern scales across all SDLC phases.
"""

import json
from unittest.mock import MagicMock

import pytest

from agency_os.agents import BaseSpecialist, MissionContext
from agency_os.agents.specialists import (
    CodingSpecialist,
    DeploymentSpecialist,
    MaintenanceSpecialist,
    TestingSpecialist,
)
from agency_os.core_system.runtime.tool_safety_guard import ToolSafetyGuard
from agency_os.persistence.sqlite_store import SQLiteStore

# ============================================================================
# PARAMETRIZED TESTS - All Specialists
# ============================================================================


@pytest.mark.parametrize(
    "specialist_class,phase_name,prerequisite_artifact",
    [
        (TestingSpecialist, "TESTING", "code_gen_spec.json"),
        (DeploymentSpecialist, "DEPLOYMENT", "qa_report.json"),
        (MaintenanceSpecialist, "MAINTENANCE", "deploy_receipt.json"),
    ],
    ids=["Testing", "Deployment", "Maintenance"],
)
def test_all_specialists_inherit_base_specialist(
    specialist_class, phase_name, prerequisite_artifact
):
    """Test that all specialists properly inherit from BaseSpecialist"""
    assert issubclass(specialist_class, BaseSpecialist)

    # Verify required methods exist
    assert hasattr(specialist_class, "execute")
    assert hasattr(specialist_class, "validate_preconditions")
    assert hasattr(specialist_class, "persist_state")
    assert hasattr(specialist_class, "load_state")


@pytest.mark.parametrize(
    "specialist_class,phase_name,prerequisite_artifact",
    [
        (TestingSpecialist, "TESTING", "code_gen_spec.json"),
        (DeploymentSpecialist, "DEPLOYMENT", "qa_report.json"),
        (MaintenanceSpecialist, "MAINTENANCE", "deploy_receipt.json"),
    ],
    ids=["Testing", "Deployment", "Maintenance"],
)
def test_all_specialists_can_be_instantiated(
    specialist_class, phase_name, prerequisite_artifact, tmp_path
):
    """Test that all specialists can be instantiated with valid args"""
    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid=f"test-{phase_name.lower()}-001",
        phase=phase_name,
        status="in_progress",
    )

    specialist = specialist_class(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=None,
        playbook_root=tmp_path,
    )

    assert specialist is not None
    assert specialist.role == phase_name
    assert specialist.mission_id == mission_id


@pytest.mark.parametrize(
    "specialist_class,phase_name,prerequisite_artifact,prerequisite_data",
    [
        (TestingSpecialist, "TESTING", "code_gen_spec.json", {"version": "1.0"}),
        (
            DeploymentSpecialist,
            "DEPLOYMENT",
            "qa_report.json",
            {"version": "1.0", "status": "APPROVED"},
        ),
        (MaintenanceSpecialist, "MAINTENANCE", "deploy_receipt.json", {"version": "1.0"}),
    ],
    ids=["Testing", "Deployment", "Maintenance"],
)
def test_all_specialists_validate_preconditions(
    specialist_class, phase_name, prerequisite_artifact, prerequisite_data, tmp_path
):
    """Test that all specialists validate preconditions correctly"""
    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid=f"test-{phase_name.lower()}-002",
        phase=phase_name,
        status="in_progress",
    )

    # Create mock orchestrator that can load artifacts
    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = prerequisite_data

    specialist = specialist_class(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    # Create context
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid=f"test-{phase_name.lower()}-002",
        phase=phase_name,
        project_root=project_root,
        metadata={},
    )

    # Validate preconditions
    result = specialist.validate_preconditions(context)
    assert result is True

    # Verify artifact was loaded
    mock_orchestrator.load_artifact.assert_called_once_with(
        f"test-{phase_name.lower()}-002", prerequisite_artifact
    )


@pytest.mark.parametrize(
    "specialist_class,phase_name,prerequisite_artifact,prerequisite_data",
    [
        (TestingSpecialist, "TESTING", "code_gen_spec.json", {"version": "1.0"}),
        (
            DeploymentSpecialist,
            "DEPLOYMENT",
            "qa_report.json",
            {"version": "1.0", "status": "APPROVED"},
        ),
        (MaintenanceSpecialist, "MAINTENANCE", "deploy_receipt.json", {"version": "1.0"}),
    ],
    ids=["Testing", "Deployment", "Maintenance"],
)
def test_all_specialists_log_lifecycle_to_sqlite(
    specialist_class, phase_name, prerequisite_artifact, prerequisite_data, tmp_path
):
    """Test that all specialists log start/end events to SQLite"""
    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid=f"test-{phase_name.lower()}-003",
        phase=phase_name,
        status="in_progress",
    )

    # Create mock orchestrator
    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = prerequisite_data
    mock_orchestrator.save_artifact.return_value = None

    # Mock execute_agent if specialist needs it
    if phase_name == "DEPLOYMENT":
        mock_orchestrator.execute_agent.side_effect = [
            # Pre-deployment checks
            {"environment_ready": True, "readiness_issues": []},
            # Deployment execution
            {"deployment_status": "SUCCESS", "deployment_id": "deploy-123"},
            # Post-deployment validation
            {"health_checks_passed": True, "failed_checks": []},
            # Report generation
            {"version": "1.0", "status": "SUCCESS"},
        ]

    specialist = specialist_class(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    # Inject manifest for specialists that need it
    specialist._manifest = MagicMock()

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True, exist_ok=True)

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid=f"test-{phase_name.lower()}-003",
        phase=phase_name,
        project_root=project_root,
        metadata={},
    )

    # Execute workflow
    result = specialist.execute(context)
    assert result.success is True

    # Verify decisions were logged to SQLite
    decisions = store.get_decisions_for_mission(mission_id)
    assert len(decisions) > 0

    # Check for lifecycle decisions
    decision_types = [d.get("decision_type") for d in decisions]
    assert f"{phase_name}_STARTED" in decision_types


# ============================================================================
# INTEGRATION TEST - All Specialists Together
# ============================================================================


def test_hap_pattern_scales_to_all_phases(tmp_path):
    """
    Integration test: Verify HAP pattern works for all specialists

    This test proves that:
    1. All 4 specialists can coexist
    2. All follow the same BaseSpecialist contract
    3. All log decisions to the same SQLite database
    4. All can be instantiated and validated
    """
    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    specialists_config = [
        (CodingSpecialist, "CODING", "feature_spec.json", {"version": "1.0"}),
        (TestingSpecialist, "TESTING", "code_gen_spec.json", {"version": "1.0"}),
        (
            DeploymentSpecialist,
            "DEPLOYMENT",
            "qa_report.json",
            {"version": "1.0", "status": "APPROVED"},
        ),
        (MaintenanceSpecialist, "MAINTENANCE", "deploy_receipt.json", {"version": "1.0"}),
    ]

    created_specialists = []

    for specialist_class, phase_name, prereq_artifact, prereq_data in specialists_config:
        # Create mission
        mission_id = store.create_mission(
            mission_uuid=f"test-{phase_name.lower()}-integration",
            phase=phase_name,
            status="in_progress",
        )

        # Create mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.load_artifact.return_value = prereq_data

        # Instantiate specialist
        specialist = specialist_class(
            mission_id=mission_id,
            sqlite_store=store,
            tool_safety_guard=guard,
            orchestrator=mock_orchestrator,
            playbook_root=tmp_path,
        )

        # Verify instantiation
        assert specialist.role == phase_name
        assert isinstance(specialist, BaseSpecialist)

        # Verify preconditions
        context = MissionContext(
            mission_id=mission_id,
            mission_uuid=f"test-{phase_name.lower()}-integration",
            phase=phase_name,
            project_root=tmp_path / "project",
            metadata={},
        )

        assert specialist.validate_preconditions(context) is True

        created_specialists.append((specialist, phase_name))

    # Verify all 4 specialists created
    assert len(created_specialists) == 4

    # Verify all use the same SQLite store
    for specialist, phase_name in created_specialists:
        assert specialist.sqlite_store is store

    # Verify all use the same ToolSafetyGuard
    for specialist, phase_name in created_specialists:
        assert specialist.tool_safety_guard is guard

    print(f"✅ HAP pattern scaled successfully to {len(created_specialists)} specialists")


# ============================================================================
# SPECIALIST-SPECIFIC TESTS
# ============================================================================


def test_deployment_specialist_requires_qa_approval(tmp_path):
    """Test that DeploymentSpecialist enforces QA approval"""
    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-deployment-qa-check",
        phase="DEPLOYMENT",
        status="in_progress",
    )

    # Create mock orchestrator with UNAPPROVED QA report
    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = {
        "version": "1.0",
        "status": "PASSED",  # Not APPROVED!
    }

    specialist = DeploymentSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-deployment-qa-check",
        phase="DEPLOYMENT",
        project_root=tmp_path / "project",
        metadata={},
    )

    # Validate preconditions - should fail due to QA not approved
    result = specialist.validate_preconditions(context)
    assert result is False


def test_maintenance_specialist_stays_in_maintenance_phase(tmp_path):
    """Test that MaintenanceSpecialist returns no phase transition"""
    store = SQLiteStore(":memory:")
    guard = ToolSafetyGuard()

    mission_id = store.create_mission(
        mission_uuid="test-maintenance-phase",
        phase="MAINTENANCE",
        status="in_progress",
    )

    mock_orchestrator = MagicMock()
    mock_orchestrator.load_artifact.return_value = {"version": "1.0"}
    mock_orchestrator.save_artifact.return_value = None

    specialist = MaintenanceSpecialist(
        mission_id=mission_id,
        sqlite_store=store,
        tool_safety_guard=guard,
        orchestrator=mock_orchestrator,
        playbook_root=tmp_path,
    )

    context = MissionContext(
        mission_id=mission_id,
        mission_uuid="test-maintenance-phase",
        phase="MAINTENANCE",
        project_root=tmp_path / "project",
        metadata={},
    )

    result = specialist.execute(context)

    # Verify no phase transition (stays in MAINTENANCE)
    assert result.success is True
    assert result.next_phase is None
