#!/usr/bin/env python3
"""
Tests for Unavoidable MOTD (GAD-005 Component A)

Verifies that Message of the Day is displayed before vibe-cli execution
and includes critical system context.
"""

import subprocess
from pathlib import Path


def test_motd_displays():
    """Verify MOTD is shown before vibe-cli execution"""
    result = subprocess.run(
        ["uv", "run", "./vibe-cli", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # MOTD should appear in stdout
    assert "VIBE AGENCY" in result.stdout, "MOTD header missing"
    assert "RUNTIME ENGINEERING SESSION" in result.stdout, "MOTD title missing"
    assert "SYSTEM HEALTH" in result.stdout, "System health section missing"

    print("✅ MOTD displayed successfully")


def test_motd_shows_system_status():
    """Verify MOTD includes system status (git, linting, tests)"""
    # Ensure system status exists
    status_file = Path(".system_status.json")
    assert status_file.exists(), ".system_status.json missing"

    result = subprocess.run(
        ["uv", "run", "./vibe-cli", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Should show all three status indicators
    assert "Git:" in result.stdout, "Git status missing"
    assert "Linting:" in result.stdout, "Linting status missing"
    assert "Tests:" in result.stdout, "Test status missing"

    print("✅ MOTD shows system status")


def test_motd_shows_session_handoff():
    """Verify MOTD shows session handoff if exists"""
    handoff_file = Path(".session_handoff.json")

    if handoff_file.exists():
        result = subprocess.run(
            ["uv", "run", "./vibe-cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should show session handoff section
        assert "SESSION HANDOFF" in result.stdout, "Session handoff section missing"
        assert "From:" in result.stdout, "From agent missing"
        assert "Date:" in result.stdout, "Date missing"

        print("✅ MOTD shows session handoff")
    else:
        print("⚠️  No session handoff file - skipping handoff test")


def test_motd_shows_quick_commands():
    """Verify MOTD shows quick command references"""
    result = subprocess.run(
        ["uv", "run", "./vibe-cli", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    # Should show quick commands
    assert "QUICK COMMANDS" in result.stdout, "Quick commands section missing"
    assert "show-context.sh" in result.stdout, "show-context command missing"
    assert "pre-push-check.sh" in result.stdout, "pre-push-check command missing"

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
            ["uv", "run", "./vibe-cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should still execute successfully (exit code 0)
        # This is the critical test - vibe-cli MUST not fail even if MOTD breaks
        assert result.returncode == 0, f"vibe-cli failed (exit {result.returncode})"

        # MOTD should still attempt to display (even with corrupted data)
        # The key is that it doesn't crash the program
        assert "VIBE AGENCY" in result.stdout or "usage:" in result.stdout, "Program didn't execute"

        print("✅ MOTD failure is non-fatal")

    finally:
        # Restore
        if backup:
            status_file.write_text(backup)
        else:
            if status_file.exists():
                status_file.unlink()


if __name__ == "__main__":
    try:
        print("🧪 Testing GAD-005 Unavoidable MOTD")
        print("=" * 60)

        test_motd_displays()
        test_motd_shows_system_status()
        test_motd_shows_session_handoff()
        test_motd_shows_quick_commands()
        test_motd_non_fatal()

        print("=" * 60)
        print("\n✅ ALL MOTD TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
