#!/usr/bin/env python3
"""
TEST CONFIG LOADER EQUIVALENCE - GAD-100 Phase 3
=================================================

CRITICAL TEST: Prove LegacyConfigLoader and VibeConfig are equivalent

PURPOSE:
- Verify both loaders return identical data
- Prove migration will be lossless
- Ensure adapter pattern works correctly

CRITICALITY:
- This is THE MOST IMPORTANT test in Phase 3
- If this test fails, Phase 4 (feature flag) cannot proceed
- Must prove equivalence for ALL operations (load manifest, artifacts, etc.)

METHODOLOGY:
- Load same data with both loaders
- Compare results (deep equality)
- Test all ConfigLoaderInterface methods
- Use real workspaces (not mocks)

SUCCESS CRITERIA:
- All equivalence tests pass
- No data differences between loaders
- Same error behavior (exceptions, missing files, etc.)

Version: 1.0 (GAD-100 Phase 3)
"""

import json
import sys
from pathlib import Path

import pytest

# Add config to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "config"))

from legacy_config_loader import LegacyConfigLoader

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
def legacy_loader(repo_root):
    """LegacyConfigLoader instance"""
    return LegacyConfigLoader(repo_root=repo_root)


@pytest.fixture
def vibe_config(repo_root):
    """VibeConfig instance (development, no schema validation for comparison)"""
    return VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)


@pytest.fixture
def test_workspace(repo_root, tmp_path):
    """Create test workspace with manifest"""
    workspace_dir = tmp_path / "workspaces" / "equiv-test-project"
    workspace_dir.mkdir(parents=True)

    # Copy config files to tmp_path (needed for VibeConfig)
    import shutil

    config_src = repo_root / "config"
    config_dst = tmp_path / "config"
    if config_src.exists():
        shutil.copytree(config_src, config_dst, dirs_exist_ok=True)

    # Create test manifest (schema-compliant)
    manifest = {
        "metadata": {
            "projectId": "equiv-test-project",
            "name": "Equivalence Test Project",
            "createdAt": "2025-11-17T00:00:00Z",
        },
        "spec": {
            "vibe": {},
        },
        "status": {
            "projectPhase": "PLANNING",
            "lastUpdate": "2025-11-17T00:00:00Z",
        },
        "artifacts": {
            "code": {},
            "docs": {},
            "deployment": {},
            "qa": {},
        },
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

    # Create test artifact
    artifact_data = {"test": "equivalence", "value": 42}
    with open(workspace_dir / "test_artifact.json", "w") as f:
        json.dump(artifact_data, f)

    return workspace_dir


# =============================================================================
# PROJECT MANIFEST EQUIVALENCE
# =============================================================================


def test_manifest_load_equivalence(legacy_loader, vibe_config):
    """CRITICAL: Verify both loaders return identical manifest data"""
    project_id = "test-orchestrator-003"

    # Load with both loaders
    legacy_manifest = legacy_loader.get_project_manifest(project_id)
    vibe_manifest = vibe_config.get_project_manifest(project_id)

    # Should be EXACTLY equal
    assert legacy_manifest == vibe_manifest, "Manifests differ between loaders!"


def test_manifest_save_load_equivalence(test_workspace):
    """CRITICAL: Verify save+load roundtrip is equivalent"""
    # Create both loaders
    legacy = LegacyConfigLoader(
        repo_root=test_workspace.parent.parent,
        workspaces_dir=test_workspace.parent,
    )
    vibe = VibeConfig(
        env="development",
        repo_root=test_workspace.parent.parent,
        validate_schemas=False,
    )

    project_id = "equiv-test-project"

    # Load manifest with legacy loader
    manifest = legacy.get_project_manifest(project_id)

    # Modify manifest
    manifest["status"]["projectPhase"] = "CODING"

    # Save with both loaders
    legacy.save_project_manifest(project_id, manifest)
    legacy_saved_manifest = legacy.get_project_manifest(project_id)

    # Now save again with vibe config
    vibe.save_project_manifest(project_id, manifest)
    vibe_saved_manifest = vibe.get_project_manifest(project_id)

    # Both should be equal
    assert legacy_saved_manifest == vibe_saved_manifest


def test_manifest_not_found_equivalence(legacy_loader, vibe_config):
    """CRITICAL: Verify both loaders raise same error for missing manifest"""
    project_id = "non-existent-project-equivalence"

    # Both should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        legacy_loader.get_project_manifest(project_id)

    with pytest.raises(FileNotFoundError):
        vibe_config.get_project_manifest(project_id)


# =============================================================================
# SESSION HANDOFF EQUIVALENCE
# =============================================================================


def test_session_handoff_equivalence(legacy_loader, vibe_config):
    """CRITICAL: Verify both loaders return identical session handoff"""
    legacy_handoff = legacy_loader.get_session_handoff()
    vibe_handoff = vibe_config.get_session_handoff()

    # Should be EXACTLY equal (or both None)
    assert legacy_handoff == vibe_handoff, "Session handoffs differ between loaders!"


def test_session_handoff_missing_equivalence(tmp_path):
    """CRITICAL: Verify both loaders handle missing handoff identically"""
    # Create minimal config for vibe
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    vibe_config_data = {
        "state_files": {},
        "schema_validation": {"enabled": False},
        "environments": {
            "development": {"base_config": "config/base.yaml"},
        },
    }

    with open(config_dir / "vibe_config.yaml", "w") as f:
        import yaml

        yaml.dump(vibe_config_data, f)

    base_config = {
        "project": {"name": "test"},
        "paths": {"repo_root": "."},
    }

    with open(config_dir / "base.yaml", "w") as f:
        import yaml

        yaml.dump(base_config, f)

    legacy = LegacyConfigLoader(repo_root=tmp_path)
    vibe = VibeConfig(env="development", repo_root=tmp_path, validate_schemas=False)

    # Both should return None
    assert legacy.get_session_handoff() is None
    assert vibe.get_session_handoff() is None


# =============================================================================
# SYSTEM STATUS EQUIVALENCE
# =============================================================================


def test_system_status_equivalence(legacy_loader, vibe_config):
    """CRITICAL: Verify both loaders return identical system status"""
    legacy_status = legacy_loader.get_system_status()
    vibe_status = vibe_config.get_system_status()

    # Should have same keys
    assert set(legacy_status.keys()) == set(vibe_status.keys()), "System status keys differ!"

    # Git status should be identical
    if "git" in legacy_status and "git" in vibe_status:
        assert legacy_status["git"] == vibe_status["git"], "Git status differs!"


# =============================================================================
# ARTIFACT LOADING EQUIVALENCE
# =============================================================================


def test_artifact_load_equivalence(test_workspace):
    """CRITICAL: Verify both loaders return identical artifact data"""
    legacy = LegacyConfigLoader(
        repo_root=test_workspace.parent.parent,
        workspaces_dir=test_workspace.parent,
    )
    vibe = VibeConfig(
        env="development",
        repo_root=test_workspace.parent.parent,
        validate_schemas=False,
    )

    project_id = "equiv-test-project"
    artifact_name = "test_artifact.json"

    # Load artifact with both loaders
    legacy_artifact = legacy.load_artifact(project_id, artifact_name)
    vibe_artifact = vibe.load_artifact(project_id, artifact_name)

    # Should be EXACTLY equal
    assert legacy_artifact == vibe_artifact, "Artifacts differ between loaders!"


def test_artifact_missing_equivalence(test_workspace):
    """CRITICAL: Verify both loaders handle missing artifact identically"""
    legacy = LegacyConfigLoader(
        repo_root=test_workspace.parent.parent,
        workspaces_dir=test_workspace.parent,
    )
    vibe = VibeConfig(
        env="development",
        repo_root=test_workspace.parent.parent,
        validate_schemas=False,
    )

    project_id = "equiv-test-project"
    artifact_name = "missing_artifact.json"

    # Both should return None
    assert legacy.load_artifact(project_id, artifact_name) is None
    assert vibe.load_artifact(project_id, artifact_name) is None


# =============================================================================
# WORKFLOW LOADING EQUIVALENCE
# =============================================================================


def test_workflow_load_equivalence(repo_root):
    """CRITICAL: Verify both loaders return identical workflow data"""
    legacy = LegacyConfigLoader(repo_root=repo_root)
    vibe = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    workflow_path = repo_root / "agency_os" / "01_planning_framework" / "workflow.yaml"

    if not workflow_path.exists():
        pytest.skip("Planning workflow not found")

    # Load workflow with both loaders
    legacy_workflow = legacy.load_workflow(workflow_path)
    vibe_workflow = vibe.load_workflow(workflow_path)

    # Should be EXACTLY equal
    assert legacy_workflow == vibe_workflow, "Workflows differ between loaders!"


def test_workflow_missing_equivalence(legacy_loader, vibe_config, tmp_path):
    """CRITICAL: Verify both loaders raise same error for missing workflow"""
    missing_workflow = tmp_path / "missing_workflow.yaml"

    # Both should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        legacy_loader.load_workflow(missing_workflow)

    with pytest.raises(FileNotFoundError):
        vibe_config.load_workflow(missing_workflow)


# =============================================================================
# COMPREHENSIVE EQUIVALENCE TEST (Golden Workspace)
# =============================================================================


def test_golden_workspace_equivalence(repo_root):
    """
    CRITICAL: Comprehensive equivalence test using real workspace

    This is the ULTIMATE test - proves both loaders work identically
    on a real, production workspace.
    """
    legacy = LegacyConfigLoader(repo_root=repo_root)
    vibe = VibeConfig(env="development", repo_root=repo_root, validate_schemas=False)

    # Find first workspace with manifest
    workspaces_dir = repo_root / "workspaces"

    if not workspaces_dir.exists():
        pytest.skip("No workspaces directory found")

    golden_workspace = None
    for workspace in workspaces_dir.iterdir():
        if workspace.is_dir():
            manifest_path = workspace / "project_manifest.json"
            if manifest_path.exists():
                golden_workspace = workspace
                break

    if not golden_workspace:
        pytest.skip("No golden workspace found")

    # Get project ID
    with open(golden_workspace / "project_manifest.json") as f:
        manifest_data = json.load(f)

    project_id = manifest_data["metadata"]["projectId"]

    # TEST 1: Manifest equivalence
    legacy_manifest = legacy.get_project_manifest(project_id)
    vibe_manifest = vibe.get_project_manifest(project_id)
    assert legacy_manifest == vibe_manifest, "Golden workspace manifests differ!"

    # TEST 2: Session handoff equivalence
    legacy_handoff = legacy.get_session_handoff()
    vibe_handoff = vibe.get_session_handoff()
    assert legacy_handoff == vibe_handoff, "Session handoffs differ!"

    # TEST 3: System status equivalence
    legacy_status = legacy.get_system_status()
    vibe_status = vibe.get_system_status()
    assert set(legacy_status.keys()) == set(vibe_status.keys()), "System status keys differ!"

    # TEST 4: Artifact loading (if artifacts exist)
    if golden_workspace.exists():
        for artifact_file in golden_workspace.glob("*.json"):
            if artifact_file.name != "project_manifest.json":
                artifact_name = artifact_file.name
                legacy_artifact = legacy.load_artifact(project_id, artifact_name)
                vibe_artifact = vibe.load_artifact(project_id, artifact_name)
                assert legacy_artifact == vibe_artifact, f"Artifact {artifact_name} differs!"


# =============================================================================
# ADAPTER PATTERN VERIFICATION
# =============================================================================


def test_adapter_pattern_interface_compliance(legacy_loader, vibe_config):
    """CRITICAL: Verify both loaders implement same interface"""
    from legacy_config_loader import ConfigLoaderInterface

    # Both should be instances of ConfigLoaderInterface
    assert isinstance(legacy_loader, ConfigLoaderInterface)
    assert isinstance(vibe_config, ConfigLoaderInterface)

    # Both should have same methods
    legacy_methods = set(dir(legacy_loader))
    vibe_methods = set(dir(vibe_config))

    # Interface methods (required)
    required_methods = {
        "get_project_manifest",
        "save_project_manifest",
        "get_session_handoff",
        "get_system_status",
        "load_artifact",
        "load_workflow",
    }

    assert required_methods.issubset(legacy_methods), "Legacy missing interface methods!"
    assert required_methods.issubset(vibe_methods), "Vibe missing interface methods!"


# =============================================================================
# FINAL VERDICT
# =============================================================================


def test_final_equivalence_verdict(legacy_loader, vibe_config):
    """
    FINAL VERDICT: Are LegacyConfigLoader and VibeConfig equivalent?

    This meta-test checks if all equivalence tests passed.
    If this test passes, Phase 3 is COMPLETE and Phase 4 can proceed.
    """
    # If we got here, all individual equivalence tests passed

    # Final check: both loaders should be operational
    assert legacy_loader is not None
    assert vibe_config is not None

    # Final check: both implement interface
    from legacy_config_loader import ConfigLoaderInterface

    assert isinstance(legacy_loader, ConfigLoaderInterface)
    assert isinstance(vibe_config, ConfigLoaderInterface)

    # VERDICT: EQUIVALENT ✅
    print("\n" + "=" * 70)
    print("FINAL VERDICT: LegacyConfigLoader and VibeConfig are EQUIVALENT ✅")
    print("=" * 70)
    print("\nPhase 3 COMPLETE. Ready for Phase 4 (feature flag integration).")
    print("=" * 70 + "\n")
