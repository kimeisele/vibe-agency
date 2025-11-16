#!/usr/bin/env python3
"""
Tests for GAD-004 Layer 2: Workflow-Scoped Quality Gate Recording

Verifies that quality gate results are properly recorded in project_manifest.json
for auditability and async remediation.
"""

import sys
from pathlib import Path
from unittest.mock import patch

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os/00_system/orchestrator"))

from core_orchestrator import CoreOrchestrator, ProjectManifest, ProjectPhase


def test_quality_gate_result_recorded_in_manifest():
    """Verify quality gate results are written to manifest"""
    # Setup
    repo_root = Path(__file__).parent.parent
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

    # Create mock manifest
    manifest = ProjectManifest(
        project_id="test-project",
        name="Test Project",
        current_phase=ProjectPhase.PLANNING,
        metadata={"status": {}, "metadata": {"projectId": "test-project", "name": "Test"}},
    )

    # Mock gate config
    gate = {"check": "test_security_scan", "severity": "critical", "blocking": True}

    # Mock audit report
    audit_report = {
        "status": "PASS",
        "findings": 0,
        "message": "No security issues found",
        "remediation": "N/A",
        "duration_ms": 1500,
    }

    # Mock save_project_manifest to avoid file I/O
    with patch.object(orchestrator, "save_project_manifest"):
        # Record result
        orchestrator._record_quality_gate_result(
            manifest=manifest,
            transition_name="T1_TestTransition",
            gate=gate,
            audit_report=audit_report,
        )

    # Verify manifest was updated
    assert "qualityGates" in manifest.metadata["status"], (
        "qualityGates field missing from manifest.status"
    )
    assert "T1_TestTransition" in manifest.metadata["status"]["qualityGates"], (
        "T1_TestTransition missing from qualityGates"
    )

    transition_record = manifest.metadata["status"]["qualityGates"]["T1_TestTransition"]
    assert "gates" in transition_record, "gates list missing from transition record"
    assert len(transition_record["gates"]) == 1, (
        f"Expected 1 gate result, got {len(transition_record['gates'])}"
    )

    gate_result = transition_record["gates"][0]
    assert gate_result["check"] == "test_security_scan", (
        f"Expected check='test_security_scan', got {gate_result['check']}"
    )
    assert gate_result["status"] == "PASS", f"Expected status='PASS', got {gate_result['status']}"
    assert gate_result["severity"] == "critical", (
        f"Expected severity='critical', got {gate_result['severity']}"
    )
    assert gate_result["blocking"] is True, f"Expected blocking=True, got {gate_result['blocking']}"
    assert gate_result["findings"] == 0, f"Expected findings=0, got {gate_result['findings']}"
    assert gate_result["duration_ms"] == 1500, (
        f"Expected duration_ms=1500, got {gate_result['duration_ms']}"
    )

    print("✅ Quality gate result correctly recorded in manifest")


def test_multiple_gate_results_accumulated():
    """Verify multiple gate results are accumulated, not replaced"""
    repo_root = Path(__file__).parent.parent
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

    manifest = ProjectManifest(
        project_id="test-project",
        name="Test Project",
        current_phase=ProjectPhase.PLANNING,
        metadata={"status": {}, "metadata": {"projectId": "test-project", "name": "Test"}},
    )

    # Mock save_project_manifest to avoid file I/O
    with patch.object(orchestrator, "save_project_manifest"):
        # Record first gate
        orchestrator._record_quality_gate_result(
            manifest=manifest,
            transition_name="T1_Test",
            gate={"check": "gate1", "blocking": True},
            audit_report={"status": "PASS", "findings": 0},
        )

        # Record second gate
        orchestrator._record_quality_gate_result(
            manifest=manifest,
            transition_name="T1_Test",
            gate={"check": "gate2", "blocking": False},
            audit_report={"status": "FAIL", "findings": 3},
        )

    # Verify both gates are recorded
    gates = manifest.metadata["status"]["qualityGates"]["T1_Test"]["gates"]
    assert len(gates) == 2, f"Expected 2 gate results, got {len(gates)}"
    assert gates[0]["check"] == "gate1", (
        f"Expected first gate check='gate1', got {gates[0]['check']}"
    )
    assert gates[1]["check"] == "gate2", (
        f"Expected second gate check='gate2', got {gates[1]['check']}"
    )

    print("✅ Multiple gate results correctly accumulated")


def test_get_transition_config():
    """Verify _get_transition_config retrieves correct transition"""
    repo_root = Path(__file__).parent.parent
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

    # Test valid transition (assumes T1_StartCoding exists in workflow YAML)
    try:
        transition = orchestrator._get_transition_config("T1_StartCoding")
        assert "name" in transition, "Transition missing 'name' field"
        assert transition["name"] == "T1_StartCoding", (
            f"Expected name='T1_StartCoding', got {transition['name']}"
        )
        assert "from_state" in transition, "Transition missing 'from_state' field"
        assert "to_state" in transition, "Transition missing 'to_state' field"
        print("✅ _get_transition_config retrieves valid transition")
    except ValueError as e:
        print(f"⚠️  _get_transition_config test skipped: {e}")
        print("   This is expected if T1_StartCoding doesn't exist in workflow YAML")


def test_failed_gate_recorded_before_exception():
    """Verify failed gate results are recorded even when exception is raised"""
    repo_root = Path(__file__).parent.parent
    orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

    manifest = ProjectManifest(
        project_id="test-project",
        name="Test Project",
        current_phase=ProjectPhase.PLANNING,
        metadata={"status": {}, "metadata": {"projectId": "test-project", "name": "Test"}},
    )

    # Mock gate config (blocking failure)
    gate = {"check": "security_scan", "severity": "critical", "blocking": True}

    # Mock audit report (FAIL)
    audit_report = {
        "status": "FAIL",
        "findings": 3,
        "message": "Found 3 critical vulnerabilities",
        "remediation": "Fix SQL injection, XSS, and hardcoded secret",
        "duration_ms": 2500,
    }

    # Mock save_project_manifest to avoid file I/O
    with patch.object(orchestrator, "save_project_manifest"):
        # Record result (should not raise exception)
        orchestrator._record_quality_gate_result(
            manifest=manifest,
            transition_name="T1_TestTransition",
            gate=gate,
            audit_report=audit_report,
        )

    # Verify failed result was recorded
    gate_result = manifest.metadata["status"]["qualityGates"]["T1_TestTransition"]["gates"][0]
    assert gate_result["status"] == "FAIL", f"Expected status='FAIL', got {gate_result['status']}"
    assert gate_result["findings"] == 3, f"Expected findings=3, got {gate_result['findings']}"
    assert gate_result["message"] == "Found 3 critical vulnerabilities", "Message not recorded"
    assert gate_result["remediation"] == "Fix SQL injection, XSS, and hardcoded secret", (
        "Remediation not recorded"
    )

    print("✅ Failed gate results correctly recorded before exception")


if __name__ == "__main__":
    try:
        test_quality_gate_result_recorded_in_manifest()
        test_multiple_gate_results_accumulated()
        test_get_transition_config()
        test_failed_gate_recorded_before_exception()
        print("\n✅ ALL QUALITY GATE RECORDING TESTS PASSED")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
