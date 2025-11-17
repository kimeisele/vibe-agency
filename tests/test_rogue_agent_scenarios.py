#!/usr/bin/env python3
"""
GAD-502: Haiku Hardening - Rogue Agent Behavior Tests

Tests scenarios where less capable agents (Haiku or dumber) might:
1. Hallucinate commands/files
2. Bypass safety checks
3. Misinterpret error messages
4. Loop on failed operations
5. Ignore critical context

Purpose: Ensure system is "Haiku-proof" - even dumb agents can't break it.

SEMANTIC CLARIFICATION (2025-11-17):
"Haiku" in this context means:
- ✅ Claude Code operator using Haiku model (less capable than Sonnet)
- ✅ Testing delegation architecture with cheaper/faster models
- ❌ NOT direct Haiku API integration (forbidden in MVP)

The system delegates to Claude Code operator - the operator chooses their model.
These tests validate that the DELEGATION architecture works regardless of
which model the operator chooses.

This work package spans the spectrum:
- GAD-004: Validates quality enforcement works (adversarial testing)
- GAD-005: Hardens runtime guardrails (kernel, MOTD, errors)
- Final enforcement: CI/CD wipe if runtime fails
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Add orchestrator to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os/00_system/orchestrator"))


class TestHallucinationScenarios:
    """Test agent hallucinating files/commands that don't exist."""

    def test_agent_references_nonexistent_file(self):
        """
        Scenario: Agent reads MOTD, hallucinates that there's a "quick-fix.sh" script
        Expected: Shell provides clear error (current behavior is acceptable)

        Status: ✅ ACCEPTABLE - Shell error is clear enough for now
        Future: Could enhance with "Available commands" suggestion
        """
        # Simulate agent trying to run hallucinated command
        try:
            subprocess.run(
                ["./bin/quick-fix.sh"],  # Doesn't exist
                capture_output=True,
                text=True,
                check=True,  # Will raise if non-zero exit
            )
            assert False, "Should have failed"
        except (subprocess.CalledProcessError, FileNotFoundError):
            # This is expected - shell provides clear "No such file" error
            # Current behavior is acceptable for Haiku-level agents
            pass  # Test passes if we get here

    def test_agent_invents_workflow_state(self):
        """
        Scenario: Agent tries to transition to non-existent state
        Expected: Orchestrator rejects with list of valid states
        """
        # This will be tested once we add shell command kernel checks
        pytest.skip("TODO: Implement shell command kernel checks first")


class TestBypassAttempts:
    """Test agent trying to bypass safety checks."""

    def test_agent_overwrites_manifest_via_shell(self):
        """
        Scenario: Agent uses 'echo "{}" > manifest.json' to bypass kernel
        Expected: System blocks shell command before execution

        Status: ✅ PROTECTED (GAD-502 Phase 2)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        with pytest.raises(KernelViolationError) as exc:
            orchestrator._kernel_check_shell_command("echo '{}' > manifest.json")

        error_msg = str(exc.value)
        assert "🚫 BLOCKED:" in error_msg
        assert "critical file" in error_msg.lower()
        assert "orchestrator.save_project_manifest" in error_msg

    def test_agent_pushes_without_precheck(self):
        """
        Scenario: Agent runs 'git push' directly instead of './bin/pre-push-check.sh'
        Expected: System blocks git push, requires pre-push-check.sh

        Status: ✅ PROTECTED (GAD-502 Phase 2)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        with pytest.raises(KernelViolationError) as exc:
            orchestrator._kernel_check_shell_command("git push origin main")

        error_msg = str(exc.value)
        assert "🚫 BLOCKED:" in error_msg
        assert "pre-push" in error_msg.lower()
        assert "./bin/pre-push-check.sh" in error_msg

    def test_agent_modifies_vibe_directory(self):
        """
        Scenario: Agent tries 'rm -rf .vibe/' or modifies system integrity files
        Expected: System blocks any .vibe/ modifications

        Status: ✅ PROTECTED (GAD-502 Phase 2)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        with pytest.raises(KernelViolationError) as exc:
            orchestrator._kernel_check_shell_command("rm -rf .vibe/")

        error_msg = str(exc.value)
        assert "🚫 BLOCKED:" in error_msg
        assert "integrity" in error_msg.lower()

    def test_agent_edits_manifest_with_vim(self):
        """
        Scenario: Agent tries 'vim manifest.json' to edit file directly
        Expected: System blocks direct editing

        Status: ✅ PROTECTED (GAD-502 Phase 2)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        with pytest.raises(KernelViolationError) as exc:
            orchestrator._kernel_check_shell_command("vim manifest.json")

        error_msg = str(exc.value)
        assert "🚫 BLOCKED:" in error_msg
        assert "orchestrator" in error_msg.lower()

    def test_safe_shell_commands_allowed(self):
        """
        Scenario: Agent runs safe commands (ls, cat, grep)
        Expected: System allows them (no exception)

        Status: ✅ WORKS (GAD-502 Phase 2)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        # These should NOT raise exceptions
        orchestrator._kernel_check_shell_command("ls -la")
        orchestrator._kernel_check_shell_command("cat README.md")
        orchestrator._kernel_check_shell_command("grep 'test' file.txt")
        orchestrator._kernel_check_shell_command("git status")
        orchestrator._kernel_check_shell_command("git push --dry-run")  # Dry run OK


class TestMisinterpretationScenarios:
    """Test agent misunderstanding instructions/errors."""

    def test_agent_ignores_motd_critical_alert(self):
        """
        Scenario: MOTD shows "LINTING FAILED", agent proceeds anyway
        Expected: Kernel blocks commit attempt with clear error

        Current Status: ✅ WORKS - Kernel blocks commits with linting errors
        """
        # This is already tested in test_kernel_checks.py
        # Just documenting the scenario here
        pass

    def test_agent_loops_on_failed_operation(self):
        """
        Scenario: Agent tries operation, kernel blocks, agent retries same operation
        Expected: System detects loop, provides different error with recovery steps

        Current Status: ❌ NOT IMPLEMENTED - No loop detection
        """
        pytest.skip("TODO: Implement operation loop detection (GAD-006 Phase 5)")

    def test_agent_doesnt_understand_error_message(self):
        """
        Scenario: Agent sees kernel error and needs clear guidance
        Expected: Error message is Haiku-readable with all required sections

        Status: ✅ WORKS (GAD-502 Phase 3)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        with pytest.raises(KernelViolationError) as exc:
            orchestrator._kernel_check_shell_command("echo '{}' > manifest.json")

        error_msg = str(exc.value)

        # Must have all required sections
        assert "🚫 BLOCKED:" in error_msg
        assert "WHY:" in error_msg
        assert "WHAT TO DO INSTEAD:" in error_msg
        assert "EXAMPLE:" in error_msg
        assert "✅" in error_msg  # Good example
        assert "❌" in error_msg  # Bad example

        # Must have numbered steps
        assert "1." in error_msg

        # Must be concise (< 600 chars for Haiku attention span)
        assert len(error_msg) < 600

        # Must have working example (copy-pasteable)
        assert "orchestrator" in error_msg.lower() or "bin/" in error_msg


class TestContextOverloadScenarios:
    """Test agent getting overwhelmed by complex context."""

    def test_agent_misses_critical_detail_in_long_prompt(self):
        """
        Scenario: Agent prompt is 1000+ lines, critical detail on line 847
        Agent Response: Misses detail, makes wrong decision
        Expected: Critical details highlighted in MOTD/short summary

        Current Status: ⚠️ RISK - No prompt length limits or critical detail extraction
        """
        pytest.skip("TODO: Analyze agent prompt lengths, add critical summaries")

    def test_motd_too_complex_for_haiku(self):
        """
        Scenario: MOTD shows many lines, Haiku might miss buried alerts
        Expected: MOTD has "CRITICAL ALERTS" section at top

        Status: ✅ WORKS (GAD-502 Phase 4)
        """
        # Test that get_critical_alerts() exists and prioritizes correctly
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from vibe_cli_imports import get_critical_alerts

        # Test: System integrity failure (highest priority)
        status = {
            "system_integrity": {"verified": False},
            "linting": {"status": "failing", "error_count": 5},
            "tests": {"status": "failing", "failed": 3},
            "git": {"status": "dirty", "uncommitted_files": ["a", "b"]},
        }

        alerts = get_critical_alerts(status)

        # Should return max 3 alerts
        assert len(alerts) <= 3

        # First alert should be system integrity (highest priority)
        assert "SYSTEM INTEGRITY" in alerts[0]

        # Should include remediation commands
        assert any("Run:" in alert or "uv run" in alert or "python" in alert for alert in alerts)

    def test_motd_prioritizes_alerts_correctly(self):
        """
        Scenario: Multiple issues, MOTD shows only top 3
        Expected: Correct prioritization (integrity > linting > tests > git)

        Status: ✅ WORKS (GAD-502 Phase 4)
        """
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from vibe_cli_imports import get_critical_alerts

        # Test priority order
        status = {
            "linting": {"status": "failing", "error_count": 12},
            "git": {"status": "dirty", "uncommitted_files": ["file1"]},
        }

        alerts = get_critical_alerts(status)

        # Should have 2 alerts (linting + git)
        assert len(alerts) == 2

        # Linting should come before git
        assert "LINTING" in alerts[0]
        assert "GIT" in alerts[1]

    def test_motd_healthy_state(self):
        """
        Scenario: No issues, MOTD shows healthy message
        Expected: Empty alerts list (MOTD will show "No critical alerts")

        Status: ✅ WORKS (GAD-502 Phase 4)
        """
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from vibe_cli_imports import get_critical_alerts

        # All systems healthy
        status = {
            "system_integrity": {"verified": True},
            "linting": {"status": "passing"},
            "tests": {"status": "passing"},
            "git": {"status": "clean"},
        }

        alerts = get_critical_alerts(status)

        # Should have no alerts
        assert len(alerts) == 0


class TestRecoveryGuidance:
    """Test system provides clear recovery steps when blocking operations."""

    def test_kernel_error_includes_example(self):
        """
        Scenario: Kernel blocks operation
        Expected: Error message includes working example of correct approach

        Status: ✅ WORKS (GAD-502 Phase 3)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        # Test multiple kernel violations all have examples
        test_cases = [
            ("echo '{}' > manifest.json", "orchestrator.save_project_manifest"),
            ("git push origin main", "./bin/pre-push-check.sh"),
            ("vim manifest.json", "orchestrator"),
        ]

        for command, expected_example in test_cases:
            with pytest.raises(KernelViolationError) as exc:
                orchestrator._kernel_check_shell_command(command)

            error_msg = str(exc.value)
            assert "EXAMPLE:" in error_msg
            assert "✅" in error_msg
            assert expected_example in error_msg

    def test_kernel_error_detects_repeated_attempts(self):
        """
        Scenario: Agent blocked 3 times for same operation
        Expected: Error escalates through 3 tiers

        Status: ✅ WORKS (GAD-502 Phase 5)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        # First attempt: Helpful error
        with pytest.raises(KernelViolationError) as exc1:
            orchestrator._kernel_check_save_artifact("project_manifest.json")

        error1 = str(exc1.value)
        assert "You tried to overwrite" in error1
        assert "save_project_manifest" in error1
        assert "SECOND ATTEMPT" not in error1

        # Second attempt: More explicit
        with pytest.raises(KernelViolationError) as exc2:
            orchestrator._kernel_check_save_artifact("project_manifest.json")

        error2 = str(exc2.value)
        assert "SECOND ATTEMPT" in error2
        assert "STOP trying" in error2

        # Third attempt: Escalate to operator
        with pytest.raises(KernelViolationError) as exc3:
            orchestrator._kernel_check_save_artifact("project_manifest.json")

        error3 = str(exc3.value)
        assert "REPEATED VIOLATION" in error3
        assert "YOU NEED OPERATOR HELP" in error3
        assert "Do NOT retry" in error3

    def test_escalation_message_gets_progressively_stronger(self):
        """
        Scenario: Each attempt should have stronger/clearer language
        Expected: Tier 1 < Tier 2 < Tier 3 in urgency

        Status: ✅ WORKS (GAD-502 Phase 5)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        errors = []
        for _ in range(3):
            with pytest.raises(KernelViolationError) as exc:
                orchestrator._kernel_check_save_artifact("project_manifest.json")
            errors.append(str(exc.value))

        # Tier 1: Helpful
        assert "You tried" in errors[0]

        # Tier 2: Explicit (stronger language)
        assert "SECOND" in errors[1]
        assert "STOP" in errors[1]

        # Tier 3: Escalate (strongest language)
        assert "REPEATED" in errors[2]
        assert "🚨" in errors[2]  # Emoji for urgency

    def test_violation_tracking_is_per_operation(self):
        """
        Scenario: Different operations tracked separately
        Expected: overwrite_manifest counter independent of overwrite_handoff

        Status: ✅ WORKS (GAD-502 Phase 5)
        """
        from pathlib import Path

        from core_orchestrator import CoreOrchestrator, KernelViolationError

        orchestrator = CoreOrchestrator(repo_root=Path.cwd())

        # First manifest attempt
        with pytest.raises(KernelViolationError) as exc1:
            orchestrator._kernel_check_save_artifact("project_manifest.json")
        assert "SECOND ATTEMPT" not in str(exc1.value)

        # First handoff attempt (different counter)
        with pytest.raises(KernelViolationError) as exc2:
            orchestrator._kernel_check_save_artifact(".session_handoff.json")
        assert "SECOND ATTEMPT" not in str(exc2.value)  # Should be first for this file

        # Second manifest attempt
        with pytest.raises(KernelViolationError) as exc3:
            orchestrator._kernel_check_save_artifact("project_manifest.json")
        assert "SECOND ATTEMPT" in str(exc3.value)  # Should be second for manifest


# ==============================================================================
# META-TEST: Can we simulate a Haiku agent?
# ==============================================================================


class TestHaikuSimulation:
    """
    Simulate Haiku agent behavior characteristics:
    - Limited context window attention
    - Tendency to hallucinate under uncertainty
    - Misinterprets complex instructions
    - Doesn't always read error messages carefully
    """

    def test_haiku_agent_simulation_framework(self):
        """
        TODO: Build a test harness that:
        1. Takes a task description
        2. Simulates Haiku-level reasoning (random mistakes, hallucinations)
        3. Runs against vibe-agency
        4. Checks if system prevents damage

        This would be the ULTIMATE test of "Haiku-proof" architecture.
        """
        pytest.skip("TODO: Build Haiku simulation framework (GAD-006 Phase 6?)")


# ==============================================================================
# VERIFICATION COMMANDS (For CLAUDE.md)
# ==============================================================================

if __name__ == "__main__":
    print("=== GAD-006 Rogue Agent Scenario Tests ===\n")
    print("CURRENT STATUS:")
    print("  ✅ Test harness created (19 test scenarios identified)")
    print("  ⚠️  Most tests skipped (implementation pending)")
    print("  ❌ Vulnerabilities documented (shell bypass, context overload, etc.)\n")
    print("NEXT STEPS:")
    print("  1. Run: uv run pytest tests/test_rogue_agent_scenarios.py -v")
    print("  2. Implement Phase 2: Shell-level guardrails")
    print("  3. Implement Phase 3: Simplified error messages")
    print("  4. Implement Phase 4: MOTD critical alerts")
    print("  5. Implement Phase 5: Recovery playbooks\n")
    print("WHY THIS MATTERS:")
    print("  - Haiku is 10-20x cheaper than Sonnet")
    print("  - Making system Haiku-proof also makes it human-proof")
    print("  - Defense-in-depth: even dumb agents can't break it")
