#!/usr/bin/env python3
"""
E2E Test: TESTING Phase Workflow

Tests the complete TESTING phase execution:
1. Load code_gen_spec.json from CODING phase
2. Run test suite via pytest
3. Verify qa_report.json artifact created
4. Validate artifact structure
5. Verify quality gate enforcement (fail if tests fail)
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent

from apps.agency.orchestrator import CoreOrchestrator, ProjectPhase


class TestTestingWorkflow:
    """Test TESTING phase E2E workflow"""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace with code_gen_spec.json"""
        # Create workspace structure
        project_dir = tmp_path / "workspaces" / "test_testing_001"
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create artifacts directory
        artifacts_dir = project_dir / "artifacts" / "coding"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Create code_gen_spec.json (output from CODING phase)
        code_gen_spec = {
            "version": "1.0",
            "schema_version": "1.0",
            "phase": "CODING",
            "statistics": {
                "total_files": 3,
                "total_tests": 2,
                "test_coverage_percent": 92,
                "quality_gates_passed": True,
            },
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "generated_by": "CodingSpecialist",
                "phase": "CODING",
            },
        }

        code_gen_spec_path = artifacts_dir / "code_gen_spec.json"
        with open(code_gen_spec_path, "w") as f:
            json.dump(code_gen_spec, f, indent=2)

        # Create dummy tests directory (needed for test execution)
        tests_dir = project_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "__init__.py").touch()  # Create empty __init__.py
        (tests_dir / "test_example.py").write_text("def test_placeholder():\n    assert True\n")

        # Create project manifest
        manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test_testing_001",
                "name": "Test Project for TESTING",
                "owner": "test-user",
                "createdAt": datetime.utcnow().isoformat() + "Z",
                "sdlc_version": "1.0",
                "orchestrator_version": "1.0",
            },
            "status": {
                "projectPhase": "TESTING",
                "currentSubState": None,
                "lastUpdated": datetime.utcnow().isoformat() + "Z",
            },
            "artifacts": {"code_gen_spec": str(code_gen_spec_path)},
        }

        manifest_path = project_dir / "project_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return {
            "workspace_root": tmp_path / "workspaces",
            "project_dir": project_dir,
            "manifest_path": manifest_path,
            "code_gen_spec_path": code_gen_spec_path,
        }

    def test_testing_phase_with_passing_tests(self, temp_workspace):
        """Test TESTING phase with all tests passing"""

        print("\n" + "=" * 60)
        print("TESTING Phase E2E Test (Passing Tests)")
        print("=" * 60)

        # Copy temp workspace to PROJECT_ROOT/workspaces for orchestrator to find
        dest_workspaces = PROJECT_ROOT / "workspaces"
        dest_project = dest_workspaces / "test_testing_001"

        # Clean up any existing test project
        if dest_project.exists():
            shutil.rmtree(dest_project)

        # Copy test project to expected location
        print(f"Copying test project from {temp_workspace['project_dir']} to {dest_project}")
        shutil.copytree(temp_workspace["project_dir"], dest_project)
        print("✓ Test project copied")

        # Verify manifest exists and is readable
        manifest_path = dest_project / "project_manifest.json"
        assert manifest_path.exists(), f"Manifest not found at {manifest_path}"
        with open(manifest_path) as f:
            manifest_data = json.load(f)
        print(f"✓ Manifest loaded: projectId={manifest_data['metadata']['projectId']}")

        # Mock pytest to return passing tests
        def mock_subprocess_run(cmd, **kwargs):
            """Mock subprocess.run to return passing test results"""
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "tests/test_example.py::test_feature PASSED\n"
            mock_result.stdout += "tests/test_example.py::test_edge_case PASSED\n"
            mock_result.stdout += (
                "======================== 2 passed in 0.12s ========================\n"
            )
            mock_result.stderr = ""
            return mock_result

        # Also mock Path.exists to return True for test paths
        original_exists = Path.exists

        def mock_path_exists(self):
            """Mock Path.exists to return True for test paths"""
            path_str = str(self)
            if "tests" in path_str:
                return True
            return original_exists(self)

        try:
            orchestrator = CoreOrchestrator(
                repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
            )

            print("\n1. Orchestrator initialized")

            # Load project manifest
            manifest = orchestrator.load_project_manifest("test_testing_001")
            print(f"   Project: {manifest.name}")
            print(f"   Phase: {manifest.current_phase}")

            # Verify initial state
            assert manifest.current_phase == ProjectPhase.TESTING
            print("   ✓ Initial phase is TESTING")

            # Execute TESTING phase with mocked pytest and path checks
            print("\n2. Executing TESTING phase...")
            with (
                patch("subprocess.run", side_effect=mock_subprocess_run),
                patch.object(Path, "exists", mock_path_exists),
            ):
                try:
                    orchestrator.execute_phase(manifest)
                    print("   ✓ TESTING phase completed without errors")
                except Exception as e:
                    pytest.fail(f"TESTING phase execution failed: {e}")

            # Verify artifact was created
            print("\n3. Verifying artifacts...")
            qa_report_dir = dest_project / "artifacts" / "testing"
            qa_report_path = qa_report_dir / "qa_report.json"

            if qa_report_path.exists():
                print(f"   ✓ qa_report.json created at {qa_report_path}")

                # Load and validate artifact
                with open(qa_report_path) as f:
                    qa_report = json.load(f)

                # Validate structure
                required_fields = [
                    "version",
                    "status",
                    "test_execution",
                    "metadata",
                ]
                for field in required_fields:
                    assert field in qa_report, f"Missing required field: {field}"
                    print(f"   ✓ Field '{field}' present")

                # Validate test execution metrics
                test_exec = qa_report.get("test_execution", {})
                assert test_exec["passed"] == 2, "Should have 2 passed tests"
                assert test_exec["failed"] == 0, "Should have 0 failed tests"
                print(
                    f"   ✓ Test metrics correct (passed={test_exec['passed']}, failed={test_exec['failed']})"
                )

                # Verify status is PASSED
                assert qa_report["status"] == "PASSED"
                print("   ✓ QA status is PASSED")
            else:
                pytest.fail(f"qa_report.json not found at {qa_report_path}")

            # Verify phase transition
            print("\n4. Verifying phase transition...")
            manifest = orchestrator.load_project_manifest("test_testing_001")
            assert manifest.current_phase == ProjectPhase.AWAITING_QA_APPROVAL
            print(f"   ✓ Phase transitioned to {manifest.current_phase}")

        finally:
            # Cleanup
            if dest_project.exists():
                shutil.rmtree(dest_project)

        print("\n" + "=" * 60)
        print("✅ TESTING Phase E2E Test (Passing) PASSED")
        print("=" * 60 + "\n")

    def test_missing_code_gen_spec(self, temp_workspace):
        """Test that missing code_gen_spec.json raises clear error"""

        print("\n" + "=" * 60)
        print("Test: Missing code_gen_spec.json")
        print("=" * 60)

        # Remove code_gen_spec.json
        temp_workspace["code_gen_spec_path"].unlink()

        # Copy to workspaces for orchestrator
        dest_workspaces = PROJECT_ROOT / "workspaces"
        dest_project = dest_workspaces / "test_testing_001"

        if dest_project.exists():
            shutil.rmtree(dest_project)

        shutil.copytree(temp_workspace["project_dir"], dest_project)

        try:
            orchestrator = CoreOrchestrator(
                repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
            )

            print("\nAttempting to run TESTING without code_gen_spec...")

            manifest = orchestrator.load_project_manifest("test_testing_001")

            # Should raise error due to precondition failure
            with pytest.raises(RuntimeError, match="Preconditions failed"):
                orchestrator.execute_phase(manifest)

            print("✓ Correctly raised RuntimeError for missing code_gen_spec")
            print("\n" + "=" * 60)
            print("✅ Error Handling Test PASSED")
            print("=" * 60 + "\n")
        finally:
            if dest_project.exists():
                shutil.rmtree(dest_project)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
