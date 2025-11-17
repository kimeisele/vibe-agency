#!/usr/bin/env python3
"""
TEST VIBE CONFIG - GAD-100 Phase 3
===================================

Tests for VibeConfig (phoenix_config wrapper)

PURPOSE:
- Verify VibeConfig implements ConfigLoaderInterface correctly
- Ensure phoenix_config integration works
- Test environment overlays (base/dev/prod)
- Test schema validation integration

CRITICAL:
- These tests MUST pass before Phase 4 (feature flag integration)
- VibeConfig is the NEW config system (GAD-100)
- Must prove equivalent behavior to LegacyConfigLoader

Version: 1.0 (GAD-100 Phase 3)
"""

import json
import sys
from pathlib import Path

import pytest

# Add config to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "config"))

# Check if phoenix_config is available
try:
    from vibe_config import VibeConfig, PHOENIX_AVAILABLE
except ImportError:
    PHOENIX_AVAILABLE = False


# Skip all tests if phoenix_config not available
pytestmark = pytest.mark.skipif(
    not PHOENIX_AVAILABLE,
    reason="phoenix_config not available (run GAD-100 Phase 1 first)",
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def repo_root():
    """Repository root directory"""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def vibe_config(repo_root):
    """VibeConfig instance (development environment)"""
    return VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)


@pytest.fixture
def test_workspace(repo_root, tmp_path):
    """Create test workspace with manifest"""
    workspace_dir = tmp_path / "workspaces" / "test-project-vibe"
    workspace_dir.mkdir(parents=True)

    # Copy config files to tmp_path (needed for VibeConfig)
    import shutil

    config_src = repo_root / "config"
    config_dst = tmp_path / "config"
    if config_src.exists():
        shutil.copytree(config_src, config_dst, dirs_exist_ok=True)

    # Create test manifest
    manifest = {
        "metadata": {
            "projectId": "test-project-vibe",
            "name": "Test Project Vibe",
            "createdAt": "2025-11-17T00:00:00Z",
        },
        "spec": {
            "vibe": {},
        },
        "status": {
            "projectPhase": "PLANNING",
            "lastUpdate": "2025-11-17T00:00:00Z",
        },
        "artifacts": {},
        "governance": {
            "rules": [],
        },
        "history": {
            "phaseHistory": [],
        },
        "budget": {
            "max_cost_usd": 10.0,
            "current_cost_usd": 0.0,
        },
    }

    with open(workspace_dir / "project_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    return workspace_dir


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


def test_vibe_config_init_development(repo_root):
    """Test VibeConfig initialization (development)"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    assert config.env == "development"
    assert config.repo_root == repo_root
    assert config.validate_schemas is False


def test_vibe_config_init_production(repo_root):
    """Test VibeConfig initialization (production)"""
    config = VibeConfig(env="production", repo_root=repo_root, validate_schemas=False)

    assert config.env == "production"


def test_vibe_config_init_missing_config(tmp_path):
    """Test VibeConfig initialization with missing config files"""
    # vibe_config.yaml doesn't exist in tmp_path
    with pytest.raises(FileNotFoundError) as exc_info:
        VibeConfig(env="development", repo_root=tmp_path)

    assert "vibe_config.yaml" in str(exc_info.value) or "Vibe config not found" in str(
        exc_info.value
    )


def test_vibe_config_init_missing_base_config(tmp_path):
    """Test VibeConfig initialization with missing base.yaml"""
    # Create vibe_config.yaml but not base.yaml
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    vibe_config = {
        "state_files": {},
        "schema_validation": {"enabled": False},
        "environments": {"development": {"base_config": "config/base.yaml"}},
    }

    with open(config_dir / "vibe_config.yaml", "w") as f:
        import yaml

        yaml.dump(vibe_config, f)

    # Should fail because base.yaml missing
    with pytest.raises(FileNotFoundError) as exc_info:
        VibeConfig(env="development", repo_root=tmp_path, validate_schemas=False)

    assert "base.yaml" in str(exc_info.value) or "Base config not found" in str(exc_info.value)


# =============================================================================
# PROJECT MANIFEST TESTS
# =============================================================================


def test_get_project_manifest_exists(repo_root):
    """Test loading existing project manifest"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    # Use test-orchestrator-003 (should exist in workspaces/)
    manifest = config.get_project_manifest("test-orchestrator-003")

    assert manifest is not None
    assert "metadata" in manifest
    assert manifest["metadata"]["projectId"] == "test-orchestrator-003"


def test_get_project_manifest_not_found(vibe_config):
    """Test loading non-existent project manifest"""
    with pytest.raises(FileNotFoundError):
        vibe_config.get_project_manifest("non-existent-project-vibe")


def test_save_project_manifest(vibe_config, test_workspace):
    """Test saving project manifest"""
    # Create config with test workspace
    config = VibeConfig(
        env="development",
        repo_root=test_workspace.parent.parent,
        validate_schemas=False,
    )

    # Load manifest
    manifest = config.get_project_manifest("test-project-vibe")

    # Modify manifest
    manifest["status"]["projectPhase"] = "CODING"

    # Save manifest
    config.save_project_manifest("test-project-vibe", manifest)

    # Reload and verify
    reloaded = config.get_project_manifest("test-project-vibe")
    assert reloaded["status"]["projectPhase"] == "CODING"


# =============================================================================
# SESSION HANDOFF TESTS
# =============================================================================


def test_get_session_handoff_exists(repo_root):
    """Test loading existing session handoff"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    # .session_handoff.json should exist in repo root
    handoff = config.get_session_handoff()

    if handoff is not None:
        assert "sessionInfo" in handoff or "layer0_bedrock" in handoff


def test_get_session_handoff_missing(tmp_path):
    """Test loading missing session handoff"""
    # Create minimal config files
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create minimal vibe_config.yaml
    vibe_config_data = {
        "state_files": {},
        "schema_validation": {"enabled": False},
        "environments": {
            "development": {
                "base_config": "config/base.yaml",
            },
        },
    }

    with open(config_dir / "vibe_config.yaml", "w") as f:
        import yaml

        yaml.dump(vibe_config_data, f)

    # Create minimal base.yaml
    base_config = {
        "project": {"name": "test"},
        "paths": {"repo_root": "."},
    }

    with open(config_dir / "base.yaml", "w") as f:
        import yaml

        yaml.dump(base_config, f)

    config = VibeConfig(env="development", repo_root=tmp_path, validate_schemas=False)
    handoff = config.get_session_handoff()

    assert handoff is None


# =============================================================================
# SYSTEM STATUS TESTS
# =============================================================================


def test_get_system_status(repo_root):
    """Test getting system status"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    status = config.get_system_status()

    assert status is not None
    assert "git" in status or isinstance(status, dict)


# =============================================================================
# ARTIFACT LOADING TESTS
# =============================================================================


def test_load_artifact_json(vibe_config, test_workspace):
    """Test loading JSON artifact"""
    # Create test artifact
    artifact_data = {"test": "data"}
    artifact_path = test_workspace / "test_artifact.json"

    with open(artifact_path, "w") as f:
        json.dump(artifact_data, f)

    # Create config with test workspace
    config = VibeConfig(
        env="development",
        repo_root=test_workspace.parent.parent,
        validate_schemas=False,
    )

    # Load artifact
    loaded = config.load_artifact("test-project-vibe", "test_artifact.json")
    assert loaded == artifact_data


def test_load_artifact_missing(vibe_config, test_workspace):
    """Test loading missing artifact"""
    config = VibeConfig(
        env="development",
        repo_root=test_workspace.parent.parent,
        validate_schemas=False,
    )

    loaded = config.load_artifact("test-project-vibe", "missing_artifact.json")
    assert loaded is None


# =============================================================================
# WORKFLOW LOADING TESTS
# =============================================================================


def test_load_workflow_exists(repo_root):
    """Test loading existing workflow"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    # Load planning workflow (should exist)
    workflow_path = repo_root / "agency_os" / "01_planning_framework" / "workflow.yaml"

    if workflow_path.exists():
        workflow = config.load_workflow(workflow_path)
        assert workflow is not None
        assert "name" in workflow or isinstance(workflow, dict)


def test_load_workflow_missing(vibe_config, tmp_path):
    """Test loading missing workflow"""
    with pytest.raises(FileNotFoundError):
        vibe_config.load_workflow(tmp_path / "missing_workflow.yaml")


# =============================================================================
# INTERFACE COMPLIANCE TESTS
# =============================================================================


def test_implements_config_loader_interface(vibe_config):
    """Test that VibeConfig implements ConfigLoaderInterface"""
    from legacy_config_loader import ConfigLoaderInterface

    # Check that VibeConfig is a subclass
    assert isinstance(vibe_config, ConfigLoaderInterface)

    # Check that all interface methods are implemented
    assert hasattr(vibe_config, "get_project_manifest")
    assert hasattr(vibe_config, "save_project_manifest")
    assert hasattr(vibe_config, "get_session_handoff")
    assert hasattr(vibe_config, "get_system_status")
    assert hasattr(vibe_config, "load_artifact")
    assert hasattr(vibe_config, "load_workflow")


# =============================================================================
# SCHEMA VALIDATION TESTS (GAD-100 Phase 2 integration)
# =============================================================================


def test_schema_validation_enabled(repo_root):
    """Test schema validation when enabled"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=True)

    # Load manifest (should validate against schema)
    # If schema validation fails, should raise ConfigurationError
    try:
        manifest = config.get_project_manifest("test-orchestrator-003")
        # If we get here, validation passed
        assert manifest is not None
    except Exception as e:
        # Validation error or schema not found
        assert "schema" in str(e).lower() or "validation" in str(e).lower()


def test_schema_validation_disabled(repo_root):
    """Test schema validation when disabled"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    # Load manifest (should NOT validate)
    manifest = config.get_project_manifest("test-orchestrator-003")
    assert manifest is not None


# =============================================================================
# ENVIRONMENT OVERLAY TESTS
# =============================================================================


def test_development_environment(repo_root):
    """Test development environment configuration"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    assert config.env == "development"
    # Development environment should load dev.yaml overlay
    assert config.phoenix is not None


def test_production_environment(repo_root):
    """Test production environment configuration"""
    config = VibeConfig(env="production", repo_root=repo_root, validate_schemas=False)

    assert config.env == "production"
    # Production environment should load prod.yaml overlay
    assert config.phoenix is not None


# =============================================================================
# INTEGRATION TESTS (with real workspaces)
# =============================================================================


def test_real_workspace_integration(repo_root):
    """Test VibeConfig with real workspace"""
    config = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

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

                # Test config loader
                loaded = config.get_project_manifest(project_id)

                assert loaded == expected
                break
    else:
        pytest.skip("No workspaces with manifests found")


# =============================================================================
# CONVENIENCE FUNCTIONS TESTS
# =============================================================================


def test_create_vibe_config(repo_root):
    """Test create_vibe_config convenience function"""
    from vibe_config import create_vibe_config

    config = create_vibe_config(env="development", repo_root=repo_root, validate_schemas=False)

    assert isinstance(config, VibeConfig)
    assert config.env == "development"


def test_create_legacy_config(repo_root):
    """Test create_legacy_config convenience function"""
    from vibe_config import create_legacy_config

    config = create_legacy_config(repo_root=repo_root)

    from legacy_config_loader import LegacyConfigLoader

    assert isinstance(config, LegacyConfigLoader)
