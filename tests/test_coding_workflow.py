#!/usr/bin/env python3
"""
E2E Test: CODING Phase Workflow

Tests the complete CODING phase execution:
1. Load feature_spec.json from PLANNING phase
2. Execute CODE_GENERATOR 5-phase workflow
3. Verify code_gen_spec.json artifact created
4. Validate artifact structure
5. Verify phase transition to TESTING
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent

from agency_os.core_system.orchestrator.core_orchestrator import CoreOrchestrator, ProjectPhase


class TestCodingWorkflow:
    """Test CODING phase E2E workflow"""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace with feature_spec.json"""
        # Create workspace structure
        project_dir = tmp_path / "workspaces" / "test_coding_001"
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create artifacts directory
        artifacts_dir = project_dir / "artifacts" / "planning"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Create feature_spec.json (output from PLANNING phase)
        feature_spec = {
            "version": "1.0",
            "schema_version": "1.0",
            "project": {
                "id": "test_coding_001",
                "name": "Test Project for CODING",
                "description": "A test project to validate CODING phase",
            },
            "features": [
                {
                    "id": "feat_001",
                    "name": "User Authentication",
                    "description": "Implement user login and registration",
                    "priority": "high",
                    "complexity_score": 8,
                    "estimated_effort": "3 days",
                },
                {
                    "id": "feat_002",
                    "name": "Dashboard View",
                    "description": "Create user dashboard with stats",
                    "priority": "medium",
                    "complexity_score": 5,
                    "estimated_effort": "2 days",
                },
            ],
            "scope_negotiation": {
                "total_features": 2,
                "total_complexity": 13,
                "estimated_timeline": "5 days",
            },
            "code_gen_spec_ref": {
                "tech_stack": "Python/Flask",
                "architecture_pattern": "MVC",
                "target_environment": "production",
            },
            "validation": {"business_alignment": "approved", "technical_feasibility": "approved"},
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "generated_by": "GENESIS_BLUEPRINT",
                "phase": "PLANNING",
            },
        }

        feature_spec_path = artifacts_dir / "feature_spec.json"
        with open(feature_spec_path, "w") as f:
            json.dump(feature_spec, f, indent=2)

        # Create project manifest
        manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test_coding_001",
                "name": "Test Project for CODING",
                "owner": "test-user",
                "createdAt": datetime.utcnow().isoformat() + "Z",
                "sdlc_version": "1.0",
                "orchestrator_version": "1.0",
            },
            "status": {
                "projectPhase": "CODING",
                "currentSubState": None,
                "lastUpdated": datetime.utcnow().isoformat() + "Z",
            },
            "artifacts": {"feature_spec": str(feature_spec_path)},
        }

        manifest_path = project_dir / "project_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return {
            "workspace_root": tmp_path / "workspaces",
            "project_dir": project_dir,
            "manifest_path": manifest_path,
            "feature_spec_path": feature_spec_path,
        }

    def test_coding_phase_execution(self, temp_workspace):
        """Test full CODING phase execution"""

        print("\n" + "=" * 60)
        print("CODING Phase E2E Test")
        print("=" * 60)

        # Mock LLM responses for all 5 CODE_GENERATOR tasks
        mock_responses = {
            "task_01_spec_analysis_validation": {
                "spec_valid": True,
                "validation_errors": [],
                "dependencies": ["flask", "sqlalchemy", "pytest"],
                "constraints_validated": True,
            },
            "task_02_code_generation": {
                "files": [
                    {"path": "app.py", "content": "# Main Flask app", "lines": 50},
                    {"path": "models.py", "content": "# SQLAlchemy models", "lines": 30},
                    {"path": "auth.py", "content": "# Authentication logic", "lines": 40},
                ],
                "total_lines": 120,
            },
            "task_03_test_generation": {
                "tests": [
                    {"path": "test_auth.py", "content": "# Auth tests", "coverage": 95},
                    {"path": "test_models.py", "content": "# Model tests", "coverage": 90},
                ],
                "coverage_percent": 92,
            },
            "task_04_documentation_generation": {
                "docs": [
                    {"path": "README.md", "content": "# Project README"},
                    {"path": "API.md", "content": "# API Documentation"},
                ]
            },
            "task_05_quality_assurance_packaging": {
                "quality_gates_passed": True,
                "failed_gates": [],
                "artifact_bundle": {"code": "generated", "tests": "generated", "docs": "generated"},
            },
        }

        # Track which tasks were executed
        executed_tasks = []

        def mock_execute_agent(agent_name, task_id, inputs, manifest):
            """Mock agent execution"""
            print(f"  → Executing {agent_name}.{task_id}")
            executed_tasks.append(task_id)

            # Return appropriate response based on task
            if task_id in mock_responses:
                return mock_responses[task_id]

            # Fallback for unknown tasks
            return {"status": "success"}

        # Patch execute_agent method
        with patch.object(CoreOrchestrator, "execute_agent", side_effect=mock_execute_agent):
            # Initialize orchestrator (needs to use temp workspace)
            # Copy temp workspace to PROJECT_ROOT/workspaces for orchestrator to find
            import shutil

            dest_workspaces = PROJECT_ROOT / "workspaces"
            dest_project = dest_workspaces / "test_coding_001"

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

            try:
                orchestrator = CoreOrchestrator(
                    repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
                )

                print("\n1. Orchestrator initialized")

                # Load project manifest
                manifest = orchestrator.load_project_manifest("test_coding_001")
                print(f"   Project: {manifest.name}")
                print(f"   Phase: {manifest.current_phase}")

                # Verify initial state
                assert manifest.current_phase == ProjectPhase.CODING
                print("   ✓ Initial phase is CODING")

                # Execute CODING phase
                print("\n2. Executing CODING phase...")
                try:
                    orchestrator.execute_phase(manifest)
                    print("   ✓ CODING phase completed without errors")
                except Exception as e:
                    pytest.fail(f"CODING phase execution failed: {e}")

                # Verify all 5 tasks were executed
                print("\n3. Verifying task execution...")
                expected_tasks = [
                    "task_01_spec_analysis_validation",
                    "task_02_code_generation",
                    "task_03_test_generation",
                    "task_04_documentation_generation",
                    "task_05_quality_assurance_packaging",
                ]

                for task in expected_tasks:
                    if task in executed_tasks:
                        print(f"   ✓ {task} executed")
                    else:
                        pytest.fail(f"Task {task} was not executed")

                # Verify artifact was created
                print("\n4. Verifying artifacts...")
                code_artifacts_dir = dest_project / "artifacts" / "coding"
                code_gen_spec_path = code_artifacts_dir / "code_gen_spec.json"

                if code_gen_spec_path.exists():
                    print(f"   ✓ code_gen_spec.json created at {code_gen_spec_path}")

                    # Load and validate artifact
                    with open(code_gen_spec_path) as f:
                        code_gen_spec = json.load(f)

                    # Validate structure
                    required_fields = [
                        "version",
                        "schema_version",
                        "phase",
                        "statistics",
                        "metadata",
                    ]
                    for field in required_fields:
                        assert field in code_gen_spec, f"Missing required field: {field}"
                        print(f"   ✓ Field '{field}' present")

                    # Validate statistics
                    stats = code_gen_spec["statistics"]
                    assert stats["total_files"] == 3, "Should have 3 generated files"
                    assert stats["total_tests"] == 2, "Should have 2 test files"
                    assert stats["test_coverage_percent"] == 92, "Should have 92% coverage"
                    assert stats["quality_gates_passed"] is True, "Quality gates should pass"
                    print(
                        f"   ✓ Statistics validated (files={stats['total_files']}, coverage={stats['test_coverage_percent']}%)"
                    )
                else:
                    pytest.fail(f"code_gen_spec.json not found at {code_gen_spec_path}")

                # Verify phase transition (reload manifest to see updated phase)
                print("\n5. Verifying phase transition...")
                manifest = orchestrator.load_project_manifest("test_coding_001")
                assert manifest.current_phase == ProjectPhase.TESTING
                print(f"   ✓ Phase transitioned to {manifest.current_phase}")
            finally:
                # Cleanup
                if dest_project.exists():
                    shutil.rmtree(dest_project)

        print("\n" + "=" * 60)
        print("✅ CODING Phase E2E Test PASSED")
        print("=" * 60 + "\n")

    def test_missing_feature_spec(self, temp_workspace):
        """Test that missing feature_spec raises clear error"""

        print("\n" + "=" * 60)
        print("Test: Missing feature_spec.json")
        print("=" * 60)

        # Remove feature_spec.json
        temp_workspace["feature_spec_path"].unlink()

        # Update manifest to remove feature_spec artifact
        with open(temp_workspace["manifest_path"]) as f:
            manifest_data = json.load(f)
        manifest_data["artifacts"].pop("feature_spec", None)
        with open(temp_workspace["manifest_path"], "w") as f:
            json.dump(manifest_data, f, indent=2)

        # Copy to workspaces for orchestrator
        import shutil

        dest_workspaces = PROJECT_ROOT / "workspaces"
        dest_project = dest_workspaces / "test_coding_001"

        if dest_project.exists():
            shutil.rmtree(dest_project)

        shutil.copytree(temp_workspace["project_dir"], dest_project)

        try:
            # Initialize orchestrator
            orchestrator = CoreOrchestrator(
                repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
            )

            # Attempt to run CODING phase - should raise error
            print("\nAttempting to run CODING without feature_spec...")

            # Import with proper package path
            from agency_os.core_system.orchestrator.core_orchestrator import ArtifactNotFoundError

            manifest = orchestrator.load_project_manifest("test_coding_001")

            with pytest.raises(ArtifactNotFoundError, match="feature_spec.json not found"):
                orchestrator.execute_phase(manifest)

            print("✓ Correctly raised ArtifactNotFoundError")
            print("\n" + "=" * 60)
            print("✅ Error Handling Test PASSED")
            print("=" * 60 + "\n")
        finally:
            if dest_project.exists():
                shutil.rmtree(dest_project)

    def test_quality_gates_failure(self, temp_workspace):
        """Test that quality gate failures block transition"""

        print("\n" + "=" * 60)
        print("Test: Quality Gates Failure")
        print("=" * 60)

        # Mock responses with failing quality gates
        mock_responses = {
            "task_01_spec_analysis_validation": {"spec_valid": True, "validation_errors": []},
            "task_02_code_generation": {"files": [{"path": "app.py", "content": "code"}]},
            "task_03_test_generation": {"tests": [{"path": "test.py"}], "coverage_percent": 50},
            "task_04_documentation_generation": {"docs": [{"path": "README.md"}]},
            "task_05_quality_assurance_packaging": {
                "quality_gates_passed": False,  # FAIL
                "failed_gates": ["test_coverage_too_low", "linting_errors"],
                "artifact_bundle": {},
            },
        }

        def mock_execute_agent(agent_name, task_id, inputs, manifest):
            if task_id in mock_responses:
                return mock_responses[task_id]
            return {"status": "success"}

        # Copy to workspaces for orchestrator
        import shutil

        dest_workspaces = PROJECT_ROOT / "workspaces"
        dest_project = dest_workspaces / "test_coding_001"

        if dest_project.exists():
            shutil.rmtree(dest_project)

        shutil.copytree(temp_workspace["project_dir"], dest_project)

        try:
            with patch.object(CoreOrchestrator, "execute_agent", side_effect=mock_execute_agent):
                orchestrator = CoreOrchestrator(
                    repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
                )

                manifest = orchestrator.load_project_manifest("test_coding_001")
                print("\nAttempting to run CODING with failing quality gates...")

                # Should raise ValueError due to quality gates failure
                with pytest.raises(ValueError, match="quality gates failed"):
                    orchestrator.execute_phase(manifest)

                print("✓ Correctly blocked on quality gate failure")

                # Verify phase did NOT transition to TESTING
                manifest = orchestrator.load_project_manifest("test_coding_001")
                assert manifest.current_phase == ProjectPhase.CODING
                print(f"✓ Phase remained at {manifest.current_phase}")

            print("\n" + "=" * 60)
            print("✅ Quality Gates Test PASSED")
            print("=" * 60 + "\n")
        finally:
            if dest_project.exists():
                shutil.rmtree(dest_project)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
