#!/usr/bin/env python3
"""
Tests for Layer 1: Session-Scoped Enforcement (GAD-004)

Verifies:
1. System status includes linting and formatting fields
2. Pre-push check passes on clean code
3. Pre-push check fails on linting errors
"""

import json
import subprocess
from pathlib import Path


def test_system_status_has_linting_field():
    """Verify .system_status.json contains linting status"""
    # Run update script
    result = subprocess.run(["./bin/update-system-status.sh"], capture_output=True, text=True)
    assert result.returncode == 0, "update-system-status.sh failed"

    # Load status file
    status_file = Path(".system_status.json")
    assert status_file.exists(), ".system_status.json not found"

    with open(status_file) as f:
        status = json.load(f)

    # Verify linting field exists
    assert "linting" in status, "linting field missing from system status"
    assert "status" in status["linting"], "linting.status missing"
    assert status["linting"]["status"] in [
        "passing",
        "failing",
        "uv_not_available",
    ]

    if status["linting"]["status"] == "failing":
        assert "errors_count" in status["linting"]
        assert status["linting"]["errors_count"] > 0


def test_system_status_has_formatting_field():
    """Verify .system_status.json contains formatting status"""
    # Run update script
    result = subprocess.run(["./bin/update-system-status.sh"], capture_output=True, text=True)
    assert result.returncode == 0, "update-system-status.sh failed"

    # Load status file
    status_file = Path(".system_status.json")
    assert status_file.exists(), ".system_status.json not found"

    with open(status_file) as f:
        status = json.load(f)

    # Verify formatting field exists
    assert "formatting" in status, "formatting field missing from system status"
    assert "status" in status["formatting"], "formatting.status missing"
    assert status["formatting"]["status"] in [
        "passing",
        "failing",
        "uv_not_available",
    ]


def test_pre_push_check_passes_on_clean_code():
    """Verify pre-push-check.sh passes when code is clean"""
    # First, ensure code is clean
    subprocess.run(["uv", "run", "ruff", "check", ".", "--fix"], check=True)
    subprocess.run(["uv", "run", "ruff", "format", "."], check=True)

    # Run pre-push check
    result = subprocess.run(["./bin/pre-push-check.sh"], capture_output=True, text=True)

    assert result.returncode == 0, f"pre-push-check.sh failed on clean code:\n{result.stdout}"
    assert "✅ ALL PRE-PUSH CHECKS PASSED" in result.stdout


def test_pre_push_check_fails_on_linting_errors():
    """Verify pre-push-check.sh fails when linting errors exist"""
    # Create temporary file with linting error
    test_file = Path("temp_test_linting.py")
    test_file.write_text("import unused_module  # F401 error\n")

    try:
        # Run pre-push check
        result = subprocess.run(["./bin/pre-push-check.sh"], capture_output=True, text=True)

        assert result.returncode == 1, "pre-push-check.sh should have failed"
        assert "❌ PRE-PUSH CHECKS FAILED" in result.stdout
        assert "LINTING FAILED" in result.stdout

    finally:
        # Cleanup
        test_file.unlink(missing_ok=True)


if __name__ == "__main__":
    import sys

    print("Running Session Enforcement Tests...")

    try:
        test_system_status_has_linting_field()
        print("✅ test_system_status_has_linting_field")

        test_system_status_has_formatting_field()
        print("✅ test_system_status_has_formatting_field")

        test_pre_push_check_passes_on_clean_code()
        print("✅ test_pre_push_check_passes_on_clean_code")

        test_pre_push_check_fails_on_linting_errors()
        print("✅ test_pre_push_check_fails_on_linting_errors")

        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
