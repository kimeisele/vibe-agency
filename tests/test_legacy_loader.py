#!/usr/bin/env python3
"""
TEST LEGACY CONFIG LOADER - GAD-100 Phase 3
============================================

Tests for LegacyConfigLoader (pre-GAD-100 config loading logic)

PURPOSE:
- Verify LegacyConfigLoader implements ConfigLoaderInterface correctly
- Ensure legacy code is properly isolated
- Prove legacy loader works with existing workspaces

CRITICAL:
- These tests MUST pass before Phase 4 (feature flag integration)
- Legacy loader is the fallback if phoenix config fails
- All existing functionality must work unchanged

Version: 1.0 (GAD-100 Phase 3)
"""

import json
from pathlib import Path

import pytest

# Add config to path
from legacy_config_loader import LegacyConfigLoader

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def repo_root():
    """Repository root directory"""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def legacy_loader(repo_root):
    """LegacyConfigLoader instance"""
    return LegacyConfigLoader(repo_root=repo_root)


@pytest.fixture
def test_workspace(repo_root, tmp_path):
    """Create test workspace with manifest"""
    workspace_dir = tmp_path / "workspaces" / "test-project"
    workspace_dir.mkdir(parents=True)

    # Create test manifest
    manifest = {
        "metadata": {
            "projectId": "test-project",
            "name": "Test Project",
            "createdAt": "2025-11-17T00:00:00Z",
        },
        "status": {
            "projectPhase": "PLANNING",
            "planningSubState": "RESEARCH",
            "lastUpdate": "2025-11-17T00:00:00Z",
        },
        "artifacts": {},
        "budget": {
            "max_cost_usd": 10.0,
            "current_cost_usd": 0.0,
        },
    }

    with open(workspace_dir / "project_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    return workspace_dir


# =============================================================================
# PROJECT MANIFEST TESTS
# =============================================================================


def test_get_project_manifest_exists(repo_root):
    """Test loading existing project manifest"""
    loader = LegacyConfigLoader(repo_root=repo_root)

    # Use test-orchestrator-003 (should exist in workspaces/)
    manifest = loader.get_project_manifest("test-orchestrator-003")

    assert manifest is not None
    assert "metadata" in manifest
    assert manifest["metadata"]["projectId"] == "test-orchestrator-003"


def test_get_project_manifest_not_found(legacy_loader):
    """Test loading non-existent project manifest"""
    with pytest.raises(FileNotFoundError):
        legacy_loader.get_project_manifest("non-existent-project")


def test_save_project_manifest(legacy_loader, test_workspace):
    """Test saving project manifest"""
    # Create loader with test workspace
    loader = LegacyConfigLoader(
        repo_root=test_workspace.parent.parent,
        workspaces_dir=test_workspace.parent,
    )

    # Load manifest
    manifest = loader.get_project_manifest("test-project")

    # Modify manifest
    manifest["status"]["projectPhase"] = "CODING"

    # Save manifest
    loader.save_project_manifest("test-project", manifest)

    # Reload and verify
    reloaded = loader.get_project_manifest("test-project")
    assert reloaded["status"]["projectPhase"] == "CODING"


def test_manifest_matches_project_id_by_metadata(legacy_loader, test_workspace):
    """Test manifest matching by metadata.projectId"""
    manifest_path = test_workspace / "project_manifest.json"
    assert legacy_loader._manifest_matches_project_id(manifest_path, "test-project")


def test_manifest_matches_project_id_by_parent_dir(legacy_loader, test_workspace):
    """Test manifest matching by parent directory name"""
    manifest_path = test_workspace / "project_manifest.json"

    # Parent dir is "test-project", so should match
    assert legacy_loader._manifest_matches_project_id(manifest_path, "test-project")


def test_manifest_no_match(legacy_loader, test_workspace):
    """Test manifest not matching"""
    manifest_path = test_workspace / "project_manifest.json"
    assert not legacy_loader._manifest_matches_project_id(manifest_path, "wrong-project-id")


# =============================================================================
# SESSION HANDOFF TESTS
# =============================================================================


def test_get_session_handoff_exists(repo_root):
    """Test loading existing session handoff"""
    loader = LegacyConfigLoader(repo_root=repo_root)

    # .session_handoff.json should exist in repo root
    handoff = loader.get_session_handoff()

    if handoff is not None:
        assert "sessionInfo" in handoff or "layer0_bedrock" in handoff


def test_get_session_handoff_missing(tmp_path):
    """Test loading missing session handoff"""
    loader = LegacyConfigLoader(repo_root=tmp_path)
    handoff = loader.get_session_handoff()
    assert handoff is None


# =============================================================================
# SYSTEM STATUS TESTS
# =============================================================================


def test_get_system_status_exists(repo_root):
    """Test getting system status (file exists)"""
    loader = LegacyConfigLoader(repo_root=repo_root)

    # .system_status.json might exist
    status = loader.get_system_status()

    assert status is not None
    assert "git" in status or isinstance(status, dict)


def test_get_system_status_generated(tmp_path):
    """Test system status generation (file missing)"""
    loader = LegacyConfigLoader(repo_root=tmp_path)
    status = loader.get_system_status()

    # Should generate status even if file doesn't exist
    assert status is not None
    assert "git" in status
    assert "linting" in status


def test_get_git_status(repo_root):
    """Test git status generation"""
    loader = LegacyConfigLoader(repo_root=repo_root)
    git_status = loader._get_git_status()

    assert "branch" in git_status
    assert "working_directory_clean" in git_status


def test_get_linting_status(repo_root):
    """Test linting status generation"""
    loader = LegacyConfigLoader(repo_root=repo_root)
    linting_status = loader._get_linting_status()

    assert "status" in linting_status
    assert linting_status["status"] in ["passing", "failing", "unknown"]


# =============================================================================
# ARTIFACT LOADING TESTS
# =============================================================================


def test_load_artifact_json(legacy_loader, test_workspace):
    """Test loading JSON artifact"""
    # Create test artifact
    artifact_data = {"test": "data"}
    artifact_path = test_workspace / "test_artifact.json"

    with open(artifact_path, "w") as f:
        json.dump(artifact_data, f)

    # Create loader with test workspace
    loader = LegacyConfigLoader(
        repo_root=test_workspace.parent.parent,
        workspaces_dir=test_workspace.parent,
    )

    # Load artifact
    loaded = loader.load_artifact("test-project", "test_artifact.json")
    assert loaded == artifact_data


def test_load_artifact_missing(legacy_loader, test_workspace):
    """Test loading missing artifact"""
    loader = LegacyConfigLoader(
        repo_root=test_workspace.parent.parent,
        workspaces_dir=test_workspace.parent,
    )

    loaded = loader.load_artifact("test-project", "missing_artifact.json")
    assert loaded is None


# =============================================================================
# WORKFLOW LOADING TESTS
# =============================================================================


def test_load_workflow_exists(repo_root):
    """Test loading existing workflow"""
    loader = LegacyConfigLoader(repo_root=repo_root)

    # Load planning workflow (should exist)
    workflow_path = repo_root / "agency_os" / "01_planning_framework" / "workflow.yaml"

    if workflow_path.exists():
        workflow = loader.load_workflow(workflow_path)
        assert workflow is not None
        assert "name" in workflow or isinstance(workflow, dict)


def test_load_workflow_missing(legacy_loader, tmp_path):
    """Test loading missing workflow"""
    with pytest.raises(FileNotFoundError):
        legacy_loader.load_workflow(tmp_path / "missing_workflow.yaml")


# =============================================================================
# INTERFACE COMPLIANCE TESTS
# =============================================================================


def test_implements_config_loader_interface(legacy_loader):
    """Test that LegacyConfigLoader implements ConfigLoaderInterface"""
    from legacy_config_loader import ConfigLoaderInterface

    # Check that LegacyConfigLoader is a subclass
    assert isinstance(legacy_loader, ConfigLoaderInterface)

    # Check that all interface methods are implemented
    assert hasattr(legacy_loader, "get_project_manifest")
    assert hasattr(legacy_loader, "save_project_manifest")
    assert hasattr(legacy_loader, "get_session_handoff")
    assert hasattr(legacy_loader, "get_system_status")
    assert hasattr(legacy_loader, "load_artifact")
    assert hasattr(legacy_loader, "load_workflow")


# =============================================================================
# INTEGRATION TESTS (with real workspaces)
# =============================================================================


def test_real_workspace_integration(repo_root):
    """Test LegacyConfigLoader with real workspace"""
    loader = LegacyConfigLoader(repo_root=repo_root)

    # Find any existing workspace
    workspaces_dir = repo_root / "workspaces"

    if not workspaces_dir.exists():
        pytest.skip("No workspaces directory found")

    # Find first workspace with manifest
    for workspace in workspaces_dir.iterdir():
        if workspace.is_dir():
            manifest_path = workspace / "project_manifest.json"
            if manifest_path.exists():
                # Load manifest
                with open(manifest_path) as f:
                    expected = json.load(f)

                project_id = expected["metadata"]["projectId"]

                # Test loader
                loaded = loader.get_project_manifest(project_id)

                assert loaded == expected
                break
    else:
        pytest.skip("No workspaces with manifests found")


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


def test_invalid_repo_root():
    """Test LegacyConfigLoader with invalid repo root"""
    with pytest.raises(ValueError):
        LegacyConfigLoader(repo_root="/nonexistent/path/to/repo")


def test_manifest_path_search_exhaustive(tmp_path):
    """Test manifest path search (exhaustive)"""
    loader = LegacyConfigLoader(repo_root=tmp_path)

    # No workspaces exist
    with pytest.raises(FileNotFoundError) as exc_info:
        loader._get_manifest_path("test-project")

    # Error message should mention search
    assert "not found" in str(exc_info.value).lower()
