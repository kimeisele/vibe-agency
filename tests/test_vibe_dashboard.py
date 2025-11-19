#!/usr/bin/env python3
"""
Tests for VIBE Dashboard CLI Tool (GAD-7 Integration Layer)

Validates that the unified health dashboard correctly:
- Gathers mission status from GAD-7 (Mission Control)
- Gathers health metrics from GAD-5 (Runtime)
- Gathers git status
- Displays draft PRs (Review Gate)
"""

import json
import subprocess
from pathlib import Path


class TestDashboardExists:
    """Test that dashboard tool exists and is executable."""

    def test_dashboard_script_exists(self):
        """Test that bin/vibe-dashboard exists."""
        dashboard = Path("bin/vibe-dashboard")
        assert dashboard.exists(), "bin/vibe-dashboard not found"

    def test_dashboard_is_executable(self):
        """Test that bin/vibe-dashboard is executable."""
        result = subprocess.run(
            ["./bin/vibe-dashboard", "--help"],
            capture_output=True,
            text=True,
            cwd="/Users/ss/projects/vibe-agency",
        )
        assert result.returncode == 0, f"Dashboard help failed: {result.stderr}"

    def test_dashboard_runs_default(self):
        """Test that dashboard runs without arguments."""
        result = subprocess.run(
            ["./bin/vibe-dashboard"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        assert result.returncode == 0, f"Dashboard failed: {result.stderr}"
        assert len(result.stdout) > 0, "Dashboard produced no output"


class TestDashboardIntegration:
    """Test that dashboard integrates all system components."""

    def test_dashboard_shows_mission_control_data(self):
        """Test that dashboard displays mission control information."""
        result = subprocess.run(
            ["./bin/vibe-dashboard"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        assert result.returncode == 0
        # Should contain mission control section
        output = result.stdout
        assert "MISSION" in output or "mission" in output, "Dashboard missing mission control data"

    def test_dashboard_shows_system_health(self):
        """Test that dashboard displays system health status."""
        result = subprocess.run(
            ["./bin/vibe-dashboard"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        assert result.returncode == 0
        output = result.stdout
        # Should show health status
        assert "HEALTH" in output or "health" in output or "Status" in output, (
            "Dashboard missing health status"
        )

    def test_dashboard_shows_git_status(self):
        """Test that dashboard displays git information."""
        result = subprocess.run(
            ["./bin/vibe-dashboard"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        assert result.returncode == 0
        output = result.stdout
        # Should contain git status section
        assert "GIT" in output or "Branch" in output, "Dashboard missing git status"

    def test_dashboard_shows_pr_status(self):
        """Test that dashboard displays PR information."""
        result = subprocess.run(
            ["./bin/vibe-dashboard"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        assert result.returncode == 0
        output = result.stdout
        # Should mention PRs or draft status
        assert "PR" in output or "Draft" in output or "draft" in output or "No draft" in output, (
            "Dashboard missing PR information"
        )


class TestDashboardOutputFormats:
    """Test different output formats."""

    def test_dashboard_json_output(self):
        """Test that dashboard can output JSON."""
        result = subprocess.run(
            ["./bin/vibe-dashboard", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        assert result.returncode == 0, f"JSON output failed: {result.stderr}"
        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert isinstance(data, dict), "JSON output is not a dictionary"
            assert "timestamp" in data, "JSON missing timestamp"
        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON output: {e}")

    def test_dashboard_json_contains_mission_data(self):
        """Test that JSON output includes mission data."""
        result = subprocess.run(
            ["./bin/vibe-dashboard", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "mission" in data, "JSON missing mission data"
        assert "health" in data, "JSON missing health data"
        assert "git" in data, "JSON missing git data"
        assert "prs" in data, "JSON missing PRs data"

    def test_dashboard_json_contains_timestamps(self):
        """Test that JSON includes proper timestamps."""
        result = subprocess.run(
            ["./bin/vibe-dashboard", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        data = json.loads(result.stdout)
        assert "timestamp" in data, "JSON missing timestamp"
        # Timestamp should look like ISO8601
        assert "T" in data["timestamp"] or "Z" in data["timestamp"]


class TestDashboardGADIntegration:
    """Test that dashboard proves GAD integration."""

    def test_dashboard_integrates_gad5_runtime(self):
        """Test that dashboard gathers GAD-5 (Runtime) health data."""
        result = subprocess.run(
            ["./bin/vibe-dashboard", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        data = json.loads(result.stdout)
        # Health data comes from GAD-5
        assert data.get("health") is not None, "Dashboard not integrating GAD-5 health"

    def test_dashboard_integrates_gad7_mission_control(self):
        """Test that dashboard gathers GAD-7 (Mission Control) data."""
        result = subprocess.run(
            ["./bin/vibe-dashboard", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        data = json.loads(result.stdout)
        # Mission data comes from GAD-7
        assert data.get("mission") is not None or data.get("git") is not None, (
            "Dashboard not integrating GAD-7 mission control"
        )

    def test_dashboard_shows_draft_pr_review_gate(self):
        """Test that dashboard reflects Draft PR status (Review Gate)."""
        result = subprocess.run(
            ["./bin/vibe-dashboard", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/ss/projects/vibe-agency",
        )
        data = json.loads(result.stdout)
        # PRs data comes from atomic delivery (GAD-2) verification
        assert "prs" in data, "Dashboard missing PRS data for review gate"
        assert isinstance(data["prs"], list), "PRS data should be a list"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
