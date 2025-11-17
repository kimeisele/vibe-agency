#!/usr/bin/env python3
"""Tests for Unavoidable MOTD (GAD-005 Component A)"""

import subprocess
from pathlib import Path


def test_motd_displays():
    """Verify MOTD is shown before vibe-cli execution"""
    result = subprocess.run(
        ["uv", "run", "./vibe-cli", "--help"],  # Simple command
        capture_output=True,
        text=True,
        timeout=30,
    )

    # MOTD should appear in stdout
    assert "VIBE AGENCY" in result.stdout, "MOTD header not found"
    assert "SYSTEM HEALTH" in result.stdout, "System health section not found"
    assert "RUNTIME ENGINEERING SESSION" in result.stdout, "Session title not found"

    print("✅ MOTD displayed successfully")


def test_motd_shows_linting_status():
    """Verify MOTD includes linting status"""
    # Ensure system status exists (should be created by update-system-status.sh)
    status_file = Path(".system_status.json")

    # Run update script if status file doesn't exist
    if not status_file.exists():
        update_script = Path("bin/update-system-status.sh")
        if update_script.exists():
            subprocess.run([str(update_script)], check=True, capture_output=True)

    result = subprocess.run(
        ["uv", "run", "./vibe-cli", "--help"], capture_output=True, text=True, timeout=30
    )

    # Should show linting status
    assert "Linting:" in result.stdout, "Linting status not found in MOTD"

    print("✅ MOTD shows linting status")


def test_motd_shows_git_status():
    """Verify MOTD includes git status"""
    result = subprocess.run(
        ["uv", "run", "./vibe-cli", "--help"], capture_output=True, text=True, timeout=30
    )

    # Should show git status
    assert "Git:" in result.stdout, "Git status not found in MOTD"

    print("✅ MOTD shows git status")


def test_motd_shows_test_status():
    """Verify MOTD includes test status"""
    result = subprocess.run(
        ["uv", "run", "./vibe-cli", "--help"], capture_output=True, text=True, timeout=30
    )

    # Should show test status
    assert "Tests:" in result.stdout, "Test status not found in MOTD"

    print("✅ MOTD shows test status")


def test_motd_shows_session_handoff():
    """Verify MOTD shows session handoff if available"""
    handoff_file = Path(".session_handoff.json")

    if handoff_file.exists():
        result = subprocess.run(
            ["uv", "run", "./vibe-cli", "--help"], capture_output=True, text=True, timeout=30
        )

        # Should show session handoff section
        assert "SESSION HANDOFF" in result.stdout, "Session handoff section not found"
        print("✅ MOTD shows session handoff (when available)")
    else:
        print("⚠️  Skipped: No session handoff file present")


def test_motd_shows_quick_commands():
    """Verify MOTD shows quick commands section"""
    result = subprocess.run(
        ["uv", "run", "./vibe-cli", "--help"], capture_output=True, text=True, timeout=30
    )

    # Should show quick commands
    assert "QUICK COMMANDS" in result.stdout, "Quick commands section not found"
    assert "show-context.py" in result.stdout, "show-context.py not mentioned"
    assert "pre-push-check.sh" in result.stdout, "pre-push-check.sh not mentioned"

    print("✅ MOTD shows quick commands")


def test_motd_non_fatal():
    """Verify MOTD failure doesn't block execution"""
    # Temporarily corrupt system status
    status_file = Path(".system_status.json")
    backup = status_file.read_text() if status_file.exists() else None

    try:
        # Write invalid JSON
        status_file.write_text("{invalid json")

        result = subprocess.run(
            ["uv", "run", "./vibe-cli", "--help"], capture_output=True, text=True, timeout=30
        )

        # Should still execute (exit code 0)
        # Note: --help exits with 0, even if MOTD fails
        # The key point is: MOTD failure doesn't block execution
        assert result.returncode == 0, (
            f"vibe-cli failed when MOTD errored (exit {result.returncode})"
        )

        print("✅ MOTD failure is non-fatal")

    finally:
        # Restore
        if backup:
            status_file.write_text(backup)
        elif status_file.exists():
            status_file.unlink()


if __name__ == "__main__":
    try:
        test_motd_displays()
        test_motd_shows_linting_status()
        test_motd_shows_git_status()
        test_motd_shows_test_status()
        test_motd_shows_session_handoff()
        test_motd_shows_quick_commands()
        test_motd_non_fatal()

        print("\n✅ ALL MOTD TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
