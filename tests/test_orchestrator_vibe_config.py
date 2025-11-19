"""
Tests for CoreOrchestrator VibeConfig integration (GAD-100 Phase 3)

Verifies that the orchestrator correctly integrates with VibeConfig
for system health checks and status reporting.
"""

import json

# Add agency_os to path
from orchestrator.core_orchestrator import CoreOrchestrator


def test_orchestrator_with_vibe_config(tmp_path):
    """Orchestrator should integrate with VibeConfig if available."""
    # Setup .vibe/
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()
    (vibe_dir / "receipts").mkdir()

    manifest = {"status": "VERIFIED", "checksums": {}}
    with open(vibe_dir / "system_integrity_manifest.json", "w") as f:
        json.dump(manifest, f)

    # Setup minimal workflow YAML
    workflows_dir = tmp_path / "agency_os" / "00_system" / "state_machine"
    workflows_dir.mkdir(parents=True)
    workflow_yaml = workflows_dir / "ORCHESTRATION_workflow_design.yaml"
    workflow_yaml.write_text("phases: {}\ntransitions: {}\n")

    # Setup minimal contracts YAML
    contracts_dir = tmp_path / "agency_os" / "00_system" / "contracts"
    contracts_dir.mkdir(parents=True)
    contracts_yaml = contracts_dir / "ORCHESTRATION_data_contracts.yaml"
    contracts_yaml.write_text("manifest_schema: {}\nartifact_schemas: {}\n")

    # Create orchestrator
    orchestrator = CoreOrchestrator(repo_root=tmp_path)

    # Should have VibeConfig
    assert orchestrator.system_self_aware is True
    assert orchestrator.vibe_config is not None

    # Should check health
    assert orchestrator.check_system_health() is True

    # Should get status
    status = orchestrator.get_system_status_summary()
    assert "integrity" in status
    assert status["healthy"] is True


def test_orchestrator_without_vibe_config(tmp_path):
    """Orchestrator should degrade gracefully if VibeConfig unavailable."""
    # No .vibe/ directory

    # Setup minimal workflow YAML
    workflows_dir = tmp_path / "agency_os" / "00_system" / "state_machine"
    workflows_dir.mkdir(parents=True)
    workflow_yaml = workflows_dir / "ORCHESTRATION_workflow_design.yaml"
    workflow_yaml.write_text("phases: {}\ntransitions: {}\n")

    # Setup minimal contracts YAML
    contracts_dir = tmp_path / "agency_os" / "00_system" / "contracts"
    contracts_dir.mkdir(parents=True)
    contracts_yaml = contracts_dir / "ORCHESTRATION_data_contracts.yaml"
    contracts_yaml.write_text("manifest_schema: {}\nartifact_schemas: {}\n")

    orchestrator = CoreOrchestrator(repo_root=tmp_path)

    # Should degrade gracefully
    assert orchestrator.system_self_aware is False
    assert orchestrator.vibe_config is None

    # Health check should return True (fail open)
    assert orchestrator.check_system_health() is True

    # Status should return error dict
    status = orchestrator.get_system_status_summary()
    assert "error" in status
