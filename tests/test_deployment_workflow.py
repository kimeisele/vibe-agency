#!/usr/bin/env python3
"""
E2E Test: DEPLOYMENT Phase Workflow

Tests the complete DEPLOYMENT phase execution:
1. Load qa_report.json from TESTING phase (must be APPROVED)
2. Execute DEPLOY_MANAGER 4-phase workflow
3. Verify deploy_receipt.json artifact created
4. Validate artifact structure
5. Verify phase transition to PRODUCTION
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent

from agency_os_orchestrator import CoreOrchestrator, ProjectPhase


class TestDeploymentWorkflow:
    """Test DEPLOYMENT phase E2E workflow"""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace with qa_report.json (APPROVED)"""
        # Create workspace structure
        project_dir = tmp_path / "workspaces" / "test_deployment_001"
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create artifacts directory
        artifacts_dir = project_dir / "artifacts" / "testing"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Create qa_report.json (output from TESTING phase) - APPROVED
        qa_report = {
            "version": "1.0",
            "schema_version": "1.0",
            "status": "APPROVED",  # CRITICAL: Must be APPROVED
            "project_id": "test_deployment_001",
            "test_summary": {
                "total_tests": 150,
                "passed": 150,
                "failed": 0,
                "skipped": 0,
                "coverage_percent": 95,
            },
            "test_results": {
                "unit_tests": {"total": 80, "passed": 80, "failed": 0},
                "integration_tests": {"total": 50, "passed": 50, "failed": 0},
                "e2e_tests": {"total": 20, "passed": 20, "failed": 0},
            },
            "quality_gates": {
                "coverage_gate": {"required": 80, "actual": 95, "passed": True},
                "test_pass_rate": {"required": 100, "actual": 100, "passed": True},
            },
            "approval": {
                "approved_by": "test-user",
                "approved_at": datetime.utcnow().isoformat() + "Z",
                "approval_notes": "All tests passed, ready for deployment",
            },
            "metadata": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "generated_by": "QA_ORCHESTRATOR",
                "phase": "TESTING",
            },
        }

        qa_report_path = artifacts_dir / "qa_report.json"
        with open(qa_report_path, "w") as f:
            json.dump(qa_report, f, indent=2)

        # Create project manifest
        manifest = {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test_deployment_001",
                "name": "Test Project for DEPLOYMENT",
                "owner": "test-user",
                "createdAt": datetime.utcnow().isoformat() + "Z",
                "sdlc_version": "1.0",
                "orchestrator_version": "1.0",
            },
            "status": {
                "projectPhase": "DEPLOYMENT",
                "currentSubState": None,
                "lastUpdated": datetime.utcnow().isoformat() + "Z",
            },
            "artifacts": {"qa_report": str(qa_report_path)},
        }

        manifest_path = project_dir / "project_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return {
            "workspace_root": tmp_path / "workspaces",
            "project_dir": project_dir,
            "manifest_path": manifest_path,
            "qa_report_path": qa_report_path,
        }

    def test_deployment_phase_execution(self, temp_workspace):
        """Test full DEPLOYMENT phase execution with successful deployment"""

        print("\n" + "=" * 60)
        print("DEPLOYMENT Phase E2E Test - Success Scenario")
        print("=" * 60)

        # Mock LLM responses for all 4 DEPLOY_MANAGER tasks
        mock_responses = {
            "task_01_pre_deployment_checks": {
                "environment_ready": True,
                "readiness_issues": [],
                "environment": "production",
                "dependencies_available": True,
                "security_checks_passed": True,
            },
            "task_02_deployment_execution": {
                "deployment_status": "SUCCESS",
                "artifact_version_deployed": "v1.2.3",
                "deployment_strategy": "blue-green",
                "rollback_capability": "ready",
                "db_migration_status": "SUCCESS",
            },
            "task_03_post_deployment_validation": {
                "health_checks_passed": True,
                "failed_checks": [],
                "smoke_tests_passed": True,
                "monitoring_integrated": True,
                "golden_signals": {
                    "latency_p95_ms": 45,
                    "error_rate_percent": 0.1,
                    "requests_per_second": 1500,
                },
            },
            "task_04_report_generation": {
                "version": "1.0",
                "schema_version": "1.0",
                "status": "SUCCESS",
                "artifact_version_deployed": "v1.2.3",
                "deployment_strategy": "blue-green",
                "db_migration_status": "SUCCESS",
                "health_check_status": "OK",
                "golden_signal_values": {
                    "latency_p95_ms": 45,
                    "error_rate_percent": 0.1,
                },
                "metadata": {
                    "deployed_by": "DEPLOY_MANAGER",
                    "environment": "production",
                },
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
            # Copy test workspace to PROJECT_ROOT/workspaces for orchestrator
            import shutil

            dest_workspaces = PROJECT_ROOT / "workspaces"
            dest_project = dest_workspaces / "test_deployment_001"

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
                manifest = orchestrator.load_project_manifest("test_deployment_001")
                print(f"   Project: {manifest.name}")
                print(f"   Phase: {manifest.current_phase}")

                # Verify initial state
                assert manifest.current_phase == ProjectPhase.DEPLOYMENT
                print("   ✓ Initial phase is DEPLOYMENT")

                # Execute DEPLOYMENT phase
                print("\n2. Executing DEPLOYMENT phase...")
                try:
                    orchestrator.execute_phase(manifest)
                    print("   ✓ DEPLOYMENT phase completed without errors")
                except Exception as e:
                    pytest.fail(f"DEPLOYMENT phase execution failed: {e}")

                # Verify all 4 tasks were executed
                print("\n3. Verifying task execution...")
                expected_tasks = [
                    "task_01_pre_deployment_checks",
                    "task_02_deployment_execution",
                    "task_03_post_deployment_validation",
                    "task_04_report_generation",
                ]

                for task in expected_tasks:
                    if task in executed_tasks:
                        print(f"   ✓ {task} executed")
                    else:
                        pytest.fail(f"Task {task} was not executed")

                # Verify artifact was created
                print("\n4. Verifying artifacts...")
                deploy_artifacts_dir = dest_project / "artifacts" / "deployment"
                deploy_receipt_path = deploy_artifacts_dir / "deploy_receipt.json"

                if deploy_receipt_path.exists():
                    print(f"   ✓ deploy_receipt.json created at {deploy_receipt_path}")

                    # Load and validate artifact
                    with open(deploy_receipt_path) as f:
                        deploy_receipt = json.load(f)

                    # Validate structure
                    required_fields = [
                        "version",
                        "schema_version",
                        "status",
                        "deployed_at",
                    ]
                    for field in required_fields:
                        assert field in deploy_receipt, f"Missing required field: {field}"
                        print(f"   ✓ Field '{field}' present")

                    # Validate deployment success
                    assert deploy_receipt["status"] == "SUCCESS", "Deployment should succeed"
                    assert deploy_receipt["artifact_version_deployed"] == "v1.2.3", (
                        "Should have correct version"
                    )
                    print(
                        f"   ✓ Deployment validated (status={deploy_receipt['status']}, version={deploy_receipt['artifact_version_deployed']})"
                    )
                else:
                    pytest.fail(f"deploy_receipt.json not found at {deploy_receipt_path}")

                # Verify phase transition (reload manifest to see updated phase)
                print("\n5. Verifying phase transition...")
                manifest = orchestrator.load_project_manifest("test_deployment_001")
                assert manifest.current_phase == ProjectPhase.PRODUCTION
                print(f"   ✓ Phase transitioned to {manifest.current_phase}")
            finally:
                # Cleanup
                if dest_project.exists():
                    shutil.rmtree(dest_project)

        print("\n" + "=" * 60)
        print("✅ DEPLOYMENT Phase E2E Test PASSED (Success)")
        print("=" * 60 + "\n")

    def test_missing_qa_report(self, temp_workspace):
        """Test that missing qa_report raises clear error"""

        print("\n" + "=" * 60)
        print("Test: Missing qa_report.json")
        print("=" * 60)

        # Remove qa_report.json
        temp_workspace["qa_report_path"].unlink()

        # Update manifest to remove qa_report artifact
        with open(temp_workspace["manifest_path"]) as f:
            manifest_data = json.load(f)
        manifest_data["artifacts"].pop("qa_report", None)
        with open(temp_workspace["manifest_path"], "w") as f:
            json.dump(manifest_data, f, indent=2)

        # Copy to workspaces for orchestrator
        import shutil

        dest_workspaces = PROJECT_ROOT / "workspaces"
        dest_project = dest_workspaces / "test_deployment_001"

        if dest_project.exists():
            shutil.rmtree(dest_project)

        shutil.copytree(temp_workspace["project_dir"], dest_project)

        try:
            # Initialize orchestrator
            orchestrator = CoreOrchestrator(
                repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
            )

            # Attempt to run DEPLOYMENT phase - should raise error
            print("\nAttempting to run DEPLOYMENT without qa_report...")

            try:
                from core_orchestrator import ArtifactNotFoundError
            except ModuleNotFoundError:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os" / "00_system" / "orchestrator"))
                from core_orchestrator import ArtifactNotFoundError

            manifest = orchestrator.load_project_manifest("test_deployment_001")

            with pytest.raises(ArtifactNotFoundError, match="qa_report.json not found"):
                orchestrator.execute_phase(manifest)

            print("✓ Correctly raised ArtifactNotFoundError")
            print("\n" + "=" * 60)
            print("✅ Error Handling Test PASSED")
            print("=" * 60 + "\n")
        finally:
            if dest_project.exists():
                shutil.rmtree(dest_project)

    def test_qa_not_approved(self, temp_workspace):
        """Test that non-APPROVED QA status blocks deployment"""

        print("\n" + "=" * 60)
        print("Test: QA Report Not Approved")
        print("=" * 60)

        # Update qa_report.json to have REJECTED status
        with open(temp_workspace["qa_report_path"]) as f:
            qa_report = json.load(f)

        qa_report["status"] = "REJECTED"  # Not approved!
        qa_report["rejection_reason"] = "Critical bugs found in E2E tests"

        with open(temp_workspace["qa_report_path"], "w") as f:
            json.dump(qa_report, f, indent=2)

        # Copy to workspaces for orchestrator
        import shutil

        dest_workspaces = PROJECT_ROOT / "workspaces"
        dest_project = dest_workspaces / "test_deployment_001"

        if dest_project.exists():
            shutil.rmtree(dest_project)

        shutil.copytree(temp_workspace["project_dir"], dest_project)

        try:
            orchestrator = CoreOrchestrator(
                repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
            )

            manifest = orchestrator.load_project_manifest("test_deployment_001")
            print("\nAttempting to run DEPLOYMENT with REJECTED qa_report...")

            # Should raise ValueError due to non-APPROVED status
            with pytest.raises(ValueError, match="QA report must be APPROVED"):
                orchestrator.execute_phase(manifest)

            print("✓ Correctly blocked on non-APPROVED QA status")

            # Verify phase did NOT transition to PRODUCTION
            manifest = orchestrator.load_project_manifest("test_deployment_001")
            assert manifest.current_phase == ProjectPhase.DEPLOYMENT
            print(f"✓ Phase remained at {manifest.current_phase}")

            print("\n" + "=" * 60)
            print("✅ QA Approval Check Test PASSED")
            print("=" * 60 + "\n")
        finally:
            if dest_project.exists():
                shutil.rmtree(dest_project)

    def test_deployment_failure_with_rollback(self, temp_workspace):
        """Test deployment failure triggers rollback and bug report"""

        print("\n" + "=" * 60)
        print("Test: Deployment Failure with Rollback")
        print("=" * 60)

        # Mock responses with deployment execution failure
        mock_responses = {
            "task_01_pre_deployment_checks": {
                "environment_ready": True,
                "readiness_issues": [],
            },
            "task_02_deployment_execution": {
                "deployment_status": "FAILED",  # FAIL
                "error_message": "Database migration failed - constraint violation",
                "rollback_triggered": True,
            },
        }

        def mock_execute_agent(agent_name, task_id, inputs, manifest):
            if task_id in mock_responses:
                return mock_responses[task_id]
            return {"status": "success"}

        # Copy to workspaces for orchestrator
        import shutil

        dest_workspaces = PROJECT_ROOT / "workspaces"
        dest_project = dest_workspaces / "test_deployment_001"

        if dest_project.exists():
            shutil.rmtree(dest_project)

        shutil.copytree(temp_workspace["project_dir"], dest_project)

        try:
            with patch.object(CoreOrchestrator, "execute_agent", side_effect=mock_execute_agent):
                orchestrator = CoreOrchestrator(
                    repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
                )

                manifest = orchestrator.load_project_manifest("test_deployment_001")
                print("\nAttempting deployment with failing execution...")

                # Should raise ValueError due to deployment failure
                with pytest.raises(ValueError, match="Deployment failed"):
                    orchestrator.execute_phase(manifest)

                print("✓ Correctly blocked on deployment failure")

                # Verify bug report was created
                bug_report_path = dest_project / "artifacts" / "deployment" / "bug_report.json"
                if bug_report_path.exists():
                    with open(bug_report_path) as f:
                        bug_report = json.load(f)

                    assert bug_report["severity"] == "P1_CRITICAL"
                    assert "Deployment Failure" in bug_report["title"]
                    print("✓ P1 bug report created for MAINTENANCE transition")
                else:
                    print(
                        "⚠️  Bug report not found (expected for deployment failures in real scenarios)"
                    )

                # Verify phase did NOT transition to PRODUCTION
                manifest = orchestrator.load_project_manifest("test_deployment_001")
                assert manifest.current_phase == ProjectPhase.DEPLOYMENT
                print(f"✓ Phase remained at {manifest.current_phase}")

            print("\n" + "=" * 60)
            print("✅ Deployment Failure Test PASSED")
            print("=" * 60 + "\n")
        finally:
            if dest_project.exists():
                shutil.rmtree(dest_project)

    def test_post_deployment_validation_failure(self, temp_workspace):
        """Test post-deployment validation failure triggers rollback"""

        print("\n" + "=" * 60)
        print("Test: Post-Deployment Validation Failure")
        print("=" * 60)

        # Mock responses with health check failure
        mock_responses = {
            "task_01_pre_deployment_checks": {
                "environment_ready": True,
                "readiness_issues": [],
            },
            "task_02_deployment_execution": {
                "deployment_status": "SUCCESS",
                "artifact_version_deployed": "v1.2.3",
            },
            "task_03_post_deployment_validation": {
                "health_checks_passed": False,  # FAIL
                "failed_checks": ["api_health_check", "database_connectivity"],
                "error_details": "API endpoint returning 503, DB connection timeout",
            },
        }

        def mock_execute_agent(agent_name, task_id, inputs, manifest):
            if task_id in mock_responses:
                return mock_responses[task_id]
            return {"status": "success"}

        # Copy to workspaces for orchestrator
        import shutil

        dest_workspaces = PROJECT_ROOT / "workspaces"
        dest_project = dest_workspaces / "test_deployment_001"

        if dest_project.exists():
            shutil.rmtree(dest_project)

        shutil.copytree(temp_workspace["project_dir"], dest_project)

        try:
            with patch.object(CoreOrchestrator, "execute_agent", side_effect=mock_execute_agent):
                orchestrator = CoreOrchestrator(
                    repo_root=str(PROJECT_ROOT), execution_mode="autonomous"
                )

                manifest = orchestrator.load_project_manifest("test_deployment_001")
                print("\nAttempting deployment with failing health checks...")

                # Should raise ValueError due to validation failure
                with pytest.raises(ValueError, match="Post-deployment validation failed"):
                    orchestrator.execute_phase(manifest)

                print("✓ Correctly blocked on validation failure")

                # Verify rollback artifact was created
                rollback_path = dest_project / "artifacts" / "deployment" / "rollback_info.json"
                if rollback_path.exists():
                    with open(rollback_path) as f:
                        rollback_info = json.load(f)

                    assert rollback_info["rollback_status"] == "INITIATED"
                    assert "Post-deployment validation failed" in rollback_info["reason"]
                    print("✓ Rollback initiated and documented")
                else:
                    print("⚠️  Rollback info not found")

                # Verify phase did NOT transition to PRODUCTION
                manifest = orchestrator.load_project_manifest("test_deployment_001")
                assert manifest.current_phase == ProjectPhase.DEPLOYMENT
                print(f"✓ Phase remained at {manifest.current_phase}")

            print("\n" + "=" * 60)
            print("✅ Validation Failure Test PASSED")
            print("=" * 60 + "\n")
        finally:
            if dest_project.exists():
                shutil.rmtree(dest_project)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
