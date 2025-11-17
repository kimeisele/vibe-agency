"""
Tests for lib/vibe_config.py

These tests verify that VibeConfig correctly reads .vibe/ state
and provides the expected API.
"""

import json
import pytest
from pathlib import Path
from lib.vibe_config import VibeConfig


def test_vibe_config_requires_vibe_dir(tmp_path):
    """VibeConfig should fail fast if .vibe/ doesn't exist."""
    with pytest.raises(FileNotFoundError, match=".vibe/ directory not found"):
        VibeConfig(repo_root=tmp_path)


def test_get_system_integrity_missing_manifest(tmp_path):
    """Should return UNKNOWN status if manifest missing."""
    # Create .vibe/ but no manifest
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()

    config = VibeConfig(repo_root=tmp_path)
    integrity = config.get_system_integrity()

    assert integrity["status"] == "UNKNOWN"
    assert "not found" in integrity["error"]


def test_get_system_integrity_valid(tmp_path):
    """Should parse valid integrity manifest."""
    # Create .vibe/ with manifest
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()

    manifest = {
        "status": "VERIFIED",
        "checksums": {
            "vibe-cli": "abc123",
            "project_manifest.json": "def456"
        },
        "last_verified": "2025-11-17T18:30:00Z",
        "violations": []
    }

    manifest_file = vibe_dir / "system_integrity_manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f)

    config = VibeConfig(repo_root=tmp_path)
    integrity = config.get_system_integrity()

    assert integrity["status"] == "VERIFIED"
    assert len(integrity["checksums"]) == 2
    assert integrity["violations"] == []


def test_is_system_healthy(tmp_path):
    """Should return True only if status is VERIFIED."""
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()

    # VERIFIED = healthy
    manifest = {"status": "VERIFIED", "checksums": {}}
    with open(vibe_dir / "system_integrity_manifest.json", "w") as f:
        json.dump(manifest, f)

    config = VibeConfig(repo_root=tmp_path)
    assert config.is_system_healthy() is True

    # COMPROMISED = not healthy
    manifest["status"] = "COMPROMISED"
    with open(vibe_dir / "system_integrity_manifest.json", "w") as f:
        json.dump(manifest, f)

    assert config.is_system_healthy() is False


def test_get_recent_receipts_empty(tmp_path):
    """Should return empty list if no receipts."""
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()
    (vibe_dir / "receipts").mkdir()

    config = VibeConfig(repo_root=tmp_path)
    receipts = config.get_recent_receipts()

    assert receipts == []


def test_get_recent_receipts_sorted(tmp_path):
    """Should return receipts sorted by timestamp (newest first)."""
    vibe_dir = tmp_path / ".vibe"
    receipts_dir = vibe_dir / "receipts"
    receipts_dir.mkdir(parents=True)

    # Create 3 receipts with different timestamps
    import time
    for i in range(3):
        receipt = {
            "agent": f"Agent{i}",
            "task": f"Task{i}",
            "timestamp": f"2025-11-17T18:3{i}:00Z"
        }
        receipt_file = receipts_dir / f"receipt_{i}.json"
        with open(receipt_file, "w") as f:
            json.dump(receipt, f)
        time.sleep(0.01)  # Ensure different mtime

    config = VibeConfig(repo_root=tmp_path)
    receipts = config.get_recent_receipts(limit=2)

    # Should return newest 2
    assert len(receipts) == 2
    assert receipts[0]["agent"] == "Agent2"  # Newest
    assert receipts[1]["agent"] == "Agent1"


def test_get_session_handoff_missing(tmp_path):
    """Should return None if handoff file missing."""
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()

    config = VibeConfig(repo_root=tmp_path)
    handoff = config.get_session_handoff()

    assert handoff is None


def test_get_session_handoff_valid(tmp_path):
    """Should parse valid 4-layer handoff."""
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()

    handoff = {
        "_schema_version": "2.0_4layer",
        "layer0_bedrock": {
            "from": "Claude Code",
            "date": "2025-11-17",
            "state": "complete",
            "blocker": None
        },
        "layer1_runtime": {
            "completed_summary": "Test work completed",
            "todos": ["Task 1", "Task 2"],
            "critical_files": []
        },
        "layer2_detail": {
            "completed": [],
            "key_decisions": [],
            "warnings": [],
            "next_steps_detail": []
        }
    }

    handoff_file = tmp_path / ".session_handoff.json"
    with open(handoff_file, "w") as f:
        json.dump(handoff, f)

    config = VibeConfig(repo_root=tmp_path)
    result = config.get_session_handoff()

    assert result["_schema_version"] == "2.0_4layer"
    assert result["layer0_bedrock"]["state"] == "complete"


def test_get_handoff_summary(tmp_path):
    """Should extract human-friendly summary from 4-layer handoff."""
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()

    handoff = {
        "_schema_version": "2.0_4layer",
        "layer0_bedrock": {
            "from": "Claude Code - Test",
            "date": "2025-11-17",
            "state": "blocked",
            "blocker": "Waiting for approval"
        },
        "layer1_runtime": {
            "completed_summary": "Phase 1 complete",
            "todos": ["Fix bug", "Write tests"],
            "critical_files": []
        },
        "layer2_detail": {
            "completed": [],
            "key_decisions": [],
            "warnings": [],
            "next_steps_detail": []
        }
    }

    handoff_file = tmp_path / ".session_handoff.json"
    with open(handoff_file, "w") as f:
        json.dump(handoff, f)

    config = VibeConfig(repo_root=tmp_path)
    summary = config.get_handoff_summary()

    assert summary["state"] == "blocked"
    assert summary["from"] == "Claude Code - Test"
    assert summary["blocker"] == "Waiting for approval"
    assert len(summary["todos"]) == 2


def test_get_full_status(tmp_path):
    """Should combine all status sources."""
    vibe_dir = tmp_path / ".vibe"
    vibe_dir.mkdir()
    (vibe_dir / "receipts").mkdir()

    # Add minimal integrity manifest
    manifest = {"status": "VERIFIED", "checksums": {}}
    with open(vibe_dir / "system_integrity_manifest.json", "w") as f:
        json.dump(manifest, f)

    config = VibeConfig(repo_root=tmp_path)
    status = config.get_full_status()

    assert "integrity" in status
    assert "receipts" in status
    assert "handoff" in status
    assert "healthy" in status
    assert "timestamp" in status
    assert status["healthy"] is True
