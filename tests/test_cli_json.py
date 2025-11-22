#!/usr/bin/env python3
"""
ARCH-035: CLI JSON Output Tests
================================

Tests for the JSON output interface of bin/vibe (GAD-000 compliance).

This ensures that:
1. `vibe status --json` outputs valid, parseable JSON
2. JSON contains all required keys for AI consumption
3. Logic is properly separated from presentation
4. Output is stable and predictable

Author: ARCH-035 Implementation
Version: 1.0
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add repo root to path
repo_root = Path(__file__).parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import VibeWrapper by directly executing the bin/vibe script
import types

vibe_script_path = repo_root / "bin" / "vibe"

# Check if file exists
if not vibe_script_path.exists():
    raise FileNotFoundError(f"bin/vibe not found at {vibe_script_path}")

# Read and execute the vibe script
vibe_module = types.ModuleType("vibe")
vibe_module.__file__ = str(vibe_script_path)
sys.modules["vibe"] = vibe_module

with open(vibe_script_path) as f:
    code = compile(f.read(), str(vibe_script_path), "exec")
    exec(code, vibe_module.__dict__)  # noqa: S102

VibeWrapper = vibe_module.VibeWrapper


class TestCLIJSONOutput:
    """Test suite for CLI JSON output (ARCH-035)."""

    @pytest.fixture
    def vibe_wrapper(self):
        """Create a VibeWrapper instance for testing."""
        return VibeWrapper()

    def test_status_json_parseable(self, vibe_wrapper):
        """Test that status --json produces valid JSON."""
        # Capture stdout
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # Run status with JSON output
            vibe_wrapper.cmd_status(json_output=True)

            # Get output
            output = captured_output.getvalue()

            # Parse JSON
            data = json.loads(output)

            # Verify it's a dict
            assert isinstance(data, dict), "JSON output should be a dictionary"

        finally:
            sys.stdout = sys.__stdout__

    def test_status_json_has_required_keys(self, vibe_wrapper):
        """Test that JSON output contains all required keys."""
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=True)
            output = captured_output.getvalue()
            data = json.loads(output)

            # Required keys from ARCH-035 spec
            required_keys = [
                "status",
                "timestamp",
                "version",
                "provider",
                "health",
                "cartridges",
                "errors",
                "next_actions",
            ]

            for key in required_keys:
                assert key in data, f"JSON output missing required key: {key}"

        finally:
            sys.stdout = sys.__stdout__

    def test_status_json_health_key_structure(self, vibe_wrapper):
        """Test that health key has correct structure."""
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=True)
            output = captured_output.getvalue()
            data = json.loads(output)

            assert "health" in data
            assert isinstance(data["health"], dict)

            # Each health check should have status and message
            for check_name, check_data in data["health"].items():
                assert "status" in check_data, f"Health check {check_name} missing status"
                assert "message" in check_data, f"Health check {check_name} missing message"
                assert check_data["status"] in ["ok", "error"], (
                    f"Health check {check_name} has invalid status: {check_data['status']}"
                )

        finally:
            sys.stdout = sys.__stdout__

    def test_status_json_provider_key_structure(self, vibe_wrapper):
        """Test that provider key has correct structure."""
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=True)
            output = captured_output.getvalue()
            data = json.loads(output)

            assert "provider" in data
            provider = data["provider"]

            # Required provider fields
            assert "name" in provider, "Provider missing 'name' field"
            assert "available" in provider, "Provider missing 'available' field"
            assert "api_key_set" in provider, "Provider missing 'api_key_set' field"

            # Provider name should be one of the supported types
            valid_providers = ["google", "anthropic", "openai", "noop"]
            assert provider["name"] in valid_providers, f"Invalid provider name: {provider['name']}"

        finally:
            sys.stdout = sys.__stdout__

    def test_status_json_version_key_structure(self, vibe_wrapper):
        """Test that version key has correct structure."""
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=True)
            output = captured_output.getvalue()
            data = json.loads(output)

            assert "version" in data
            version = data["version"]

            # Required version fields
            assert "vibe" in version, "Version missing 'vibe' field"
            assert "python" in version, "Version missing 'python' field"

            # Optional git fields
            # git_branch and git_commit may or may not be present
            if "git_branch" in version:
                assert isinstance(version["git_branch"], str)
            if "git_commit" in version:
                assert isinstance(version["git_commit"], str)

        finally:
            sys.stdout = sys.__stdout__

    def test_status_json_cartridges_structure(self, vibe_wrapper):
        """Test that cartridges key has correct structure."""
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=True)
            output = captured_output.getvalue()
            data = json.loads(output)

            assert "cartridges" in data
            assert isinstance(data["cartridges"], list)

            # Each cartridge should have name and description
            for cartridge in data["cartridges"]:
                assert "name" in cartridge, "Cartridge missing 'name' field"
                assert "description" in cartridge, "Cartridge missing 'description' field"

        finally:
            sys.stdout = sys.__stdout__

    def test_status_json_no_extraneous_output(self, vibe_wrapper):
        """Test that JSON mode outputs ONLY JSON (no banners, emojis, etc.)."""
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=True)
            output = captured_output.getvalue()

            # Output should start with { and end with }
            stripped = output.strip()
            assert stripped.startswith("{"), "JSON output should start with {"
            assert stripped.endswith("}"), "JSON output should end with }"

            # Should be valid JSON (no extra text)
            json.loads(output)

        finally:
            sys.stdout = sys.__stdout__

    def test_status_json_timestamp_format(self, vibe_wrapper):
        """Test that timestamp is in ISO 8601 format."""
        import sys
        from datetime import datetime
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=True)
            output = captured_output.getvalue()
            data = json.loads(output)

            assert "timestamp" in data

            # Parse ISO 8601 timestamp
            timestamp = datetime.fromisoformat(data["timestamp"])
            assert isinstance(timestamp, datetime)

        finally:
            sys.stdout = sys.__stdout__

    def test_status_json_overall_status_values(self, vibe_wrapper):
        """Test that overall status is either 'healthy' or 'degraded'."""
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=True)
            output = captured_output.getvalue()
            data = json.loads(output)

            assert "status" in data
            assert data["status"] in ["healthy", "degraded"], (
                f"Invalid status value: {data['status']}"
            )

        finally:
            sys.stdout = sys.__stdout__

    def test_get_system_status_returns_dict(self, vibe_wrapper):
        """Test that _get_system_status() returns a dictionary."""
        status_data = vibe_wrapper._get_system_status()

        assert isinstance(status_data, dict)
        assert "status" in status_data
        assert "health" in status_data
        assert "provider" in status_data
        assert "version" in status_data

    def test_separation_of_logic_and_presentation(self, vibe_wrapper):
        """Test that logic is separated from presentation."""
        # _get_system_status should return pure data
        status_data = vibe_wrapper._get_system_status()

        # Should not contain any formatting characters (emojis, ASCII art)
        json_str = json.dumps(status_data)
        assert "🟢" not in json_str, "Logic should not contain emojis"
        assert "✅" not in json_str, "Logic should not contain emojis"
        assert "=" * 70 not in json_str, "Logic should not contain ASCII art"

    def test_detect_active_provider_google(self, vibe_wrapper):
        """Test provider detection with Google API key."""
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "valid-key-123"}):
            provider = vibe_wrapper._detect_active_provider()

            assert provider["name"] == "google"
            assert provider["available"] is True
            assert provider["api_key_set"] is True

    def test_detect_active_provider_anthropic(self, vibe_wrapper):
        """Test provider detection with Anthropic API key."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-valid"}, clear=True):
            provider = vibe_wrapper._detect_active_provider()

            assert provider["name"] == "anthropic"
            assert provider["available"] is True
            assert provider["api_key_set"] is True

    def test_detect_active_provider_noop(self, vibe_wrapper):
        """Test provider detection with no API keys."""
        with patch.dict("os.environ", {}, clear=True):
            provider = vibe_wrapper._detect_active_provider()

            assert provider["name"] == "noop"
            assert provider["available"] is True
            assert provider["api_key_set"] is False

    def test_get_version_info_structure(self, vibe_wrapper):
        """Test version info structure."""
        version = vibe_wrapper._get_version_info()

        assert "vibe" in version
        assert "python" in version
        assert version["vibe"] == "2.1"
        assert isinstance(version["python"], str)

    def test_errors_list_populated_on_failure(self, vibe_wrapper):
        """Test that errors list is populated when health checks fail."""
        # Mock a failing health check
        with patch.object(vibe_wrapper, "_check_system_health") as mock_health:
            mock_health.return_value = {"Test Check": (False, "Failure message")}

            status_data = vibe_wrapper._get_system_status()

            assert "errors" in status_data
            assert len(status_data["errors"]) > 0
            assert "Test Check" in status_data["errors"][0]

    def test_print_status_json_outputs_valid_json(self, vibe_wrapper):
        """Test that _print_status_json outputs valid JSON."""
        import sys
        from io import StringIO

        test_data = {
            "status": "healthy",
            "timestamp": "2025-11-22T12:00:00",
            "version": {"vibe": "2.1"},
            "provider": {"name": "google"},
            "health": {},
            "cartridges": [],
            "errors": [],
            "next_actions": [],
        }

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper._print_status_json(test_data)
            output = captured_output.getvalue()

            # Should be valid JSON
            parsed = json.loads(output)
            assert parsed == test_data

        finally:
            sys.stdout = sys.__stdout__

    def test_cli_integration_status_json(self, tmp_path):
        """Integration test: Run bin/vibe status --json via subprocess."""
        vibe_script = Path(__file__).parent.parent / "bin" / "vibe"

        if not vibe_script.exists():
            pytest.skip("bin/vibe not found")

        result = subprocess.run(
            [sys.executable, str(vibe_script), "status", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should succeed
        assert result.returncode in [0, 1], f"Unexpected return code: {result.returncode}"

        # Output should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert "status" in data
            assert "health" in data
            assert "provider" in data
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}\n{result.stdout}")


class TestCLIHumanOutput:
    """Test suite for CLI human-friendly output."""

    @pytest.fixture
    def vibe_wrapper(self):
        """Create a VibeWrapper instance for testing."""
        return VibeWrapper()

    def test_status_human_has_emojis(self, vibe_wrapper):
        """Test that human output contains emojis."""
        import sys
        from io import StringIO

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper.cmd_status(json_output=False)
            output = captured_output.getvalue()

            # Should contain emojis and ASCII art
            assert "🟢" in output or "✅" in output
            assert "=" * 70 in output

        finally:
            sys.stdout = sys.__stdout__

    def test_print_status_human_outputs_formatted_text(self, vibe_wrapper):
        """Test that _print_status_human outputs formatted text."""
        import sys
        from io import StringIO

        test_data = {
            "status": "healthy",
            "timestamp": "2025-11-22T12:00:00",
            "version": {"vibe": "2.1", "python": "3.11.0"},
            "provider": {
                "name": "google",
                "available": True,
                "api_key_set": True,
                "model": "gemini-2.5-flash-exp",
            },
            "health": {"Git Status": {"status": "ok", "message": "Clean"}},
            "cartridges": [{"name": "test-cartridge", "description": "Test description"}],
            "errors": [],
            "next_actions": [],
        }

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            vibe_wrapper._print_status_human(test_data)
            output = captured_output.getvalue()

            # Should contain human-friendly elements
            assert "VIBE AGENCY" in output
            assert "Version: 2.1" in output
            assert "LLM Provider: google" in output
            assert "test-cartridge" in output

        finally:
            sys.stdout = sys.__stdout__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
