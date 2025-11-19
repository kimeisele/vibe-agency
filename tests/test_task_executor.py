#!/usr/bin/env python3
"""
Unit tests for TaskExecutor (GAD-201): The Atomic Gearbox.

Tests verify the atomic delivery workflow:
  1. Verification gate: agent.verify_work() must pass
  2. Dependency gate: gh --version must succeed
  3. Changes gate: repo must have uncommitted changes
  4. Branching Guard: git checkout -b feature/TASK-XXX
  5. Staging: git add .
  6. Commit: git commit with semantic message
  7. Push: git push -u origin feature/TASK-XXX
  8. PR Creation: gh pr create --base main (ATOMIC)
  9. Mission Complete: bin/mission complete

All operations go through bin/vibe-shell (GAD-5 Runtime) for safety.
"""

# Dynamic import for numeric directory names
import importlib.util
from pathlib import Path
from unittest import mock

import pytest

spec = importlib.util.spec_from_file_location(
    "task_executor_module",
    Path(__file__).parent.parent / "agency_os" / "02_orchestration" / "task_executor.py",
)
task_executor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(task_executor_module)

TaskExecutor = task_executor_module.TaskExecutor
DeliveryResult = task_executor_module.DeliveryResult
GitOperationError = task_executor_module.GitOperationError


@pytest.fixture
def executor(tmp_path):
    """Create a TaskExecutor instance with mocked vibe_root."""
    # Create fake bin/vibe-shell
    bin_path = tmp_path / "bin"
    bin_path.mkdir(exist_ok=True)
    (bin_path / "vibe-shell").touch()
    (bin_path / "mission").touch()

    executor = TaskExecutor(vibe_root=tmp_path)
    return executor


class TestQAGates:
    """Test verification gates before delivery."""

    def test_delivery_fails_if_qa_fails(self, executor):
        """Test that delivery fails if agent QA checks fail."""
        agent = mock.Mock()
        agent.verify_work.return_value = {
            "success": False,
            "issues": ["Test failed", "Linting error"],
        }

        result = executor.deliver(agent, "TEST-001", "Test commit")

        assert result.success is False
        assert "QA checks failed" in result.error

    def test_delivery_calls_verify_work(self, executor):
        """Test that verify_work() is called before delivery."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            # Mock all vibe-shell calls
            mock_run.side_effect = [
                # verify_work happens in agent, so skip
                # gh --version
                (0, "gh version 1.0.0", ""),
                # git status --porcelain
                (0, "M file.txt", ""),
                # git checkout -b
                (0, "", ""),
                # git add .
                (0, "", ""),
                # git commit
                (0, "", ""),
                # git rev-parse HEAD
                (0, "abc123", ""),
                # git push
                (0, "", ""),
                # gh pr create
                (0, "https://github.com/owner/repo/pull/42", ""),
                # mission complete (optional)
                (0, "Mission completed", ""),
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            executor.deliver(agent, "TEST-001", "Test")

            agent.verify_work.assert_called_once()

    def test_delivery_fails_if_gh_not_installed(self, executor):
        """Test that delivery fails if GitHub CLI is not available."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            # gh --version fails
            mock_run.return_value = (127, "", "gh: command not found")

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            result = executor.deliver(agent, "TEST-001", "Test")

            assert result.success is False
            assert "GitHub CLI (gh) not installed" in result.error

    def test_delivery_fails_if_no_changes(self, executor):
        """Test that delivery fails if repository is clean."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            mock_run.side_effect = [
                # gh --version
                (0, "gh version 1.0.0", ""),
                # git status --porcelain (empty = no changes)
                (0, "", ""),
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            result = executor.deliver(agent, "TEST-001", "Test")

            assert result.success is False
            assert "No changes to commit" in result.error


class TestAtomicWorkflow:
    """Test the complete atomic delivery workflow."""

    def test_branching_creates_feature_branch(self, executor):
        """Test that feature branch is created with correct name."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            mock_run.side_effect = [
                # gh --version
                (0, "gh version 1.0.0", ""),
                # git status --porcelain
                (0, "M file.txt", ""),
                # git checkout -b (BRANCH CREATION)
                (0, "Switched to new branch 'feature/test-001'", ""),
                # git add .
                (0, "", ""),
                # git commit
                (0, "", ""),
                # git rev-parse HEAD
                (0, "abc123", ""),
                # git push
                (0, "", ""),
                # gh pr create
                (0, "https://github.com/owner/repo/pull/42", ""),
                # mission complete
                (0, "Mission completed", ""),
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            executor.deliver(agent, "TEST-001", "Test")

            # Verify git checkout -b was called
            branch_call = [c for c in mock_run.call_args_list if "git checkout -b" in str(c)]
            assert len(branch_call) > 0
            assert "feature/test-001" in str(branch_call[0])

    def test_atomic_workflow_sequence(self, executor):
        """Test that atomic workflow runs in correct sequence."""
        call_sequence = []

        def track_calls(command, *args, **kwargs):
            call_sequence.append(command.split()[0:3])  # Track first 3 words

            # Return appropriate responses
            if "gh --version" in command:
                return (0, "gh version 1.0.0", "")
            elif "git status" in command:
                return (0, "M file.txt", "")
            elif "git checkout -b" in command:
                return (0, "Switched to new branch", "")
            elif "git add" in command or "git commit" in command:
                return (0, "", "")
            elif "git rev-parse" in command:
                return (0, "abc123def456", "")
            elif "git push" in command:
                return (0, "", "")
            elif "gh pr create" in command:
                return (0, "https://github.com/owner/repo/pull/42", "")
            elif "mission complete" in command:
                return (0, "Mission completed", "")
            return (0, "", "")

        with mock.patch.object(executor, "_run_via_vibe_shell", side_effect=track_calls):
            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            result = executor.deliver(agent, "TEST-001", "Test message")

            assert result.success is True
            assert result.branch == "feature/test-001"
            assert result.commit_sha == "abc123def456"
            assert "github.com" in result.pr_url

    def test_delivery_returns_pr_url(self, executor):
        """Test that successful delivery returns PR URL."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            expected_pr_url = "https://github.com/owner/repo/pull/42"
            mock_run.side_effect = [
                # gh --version
                (0, "gh version 1.0.0", ""),
                # git status
                (0, "M file.txt", ""),
                # git checkout -b
                (0, "", ""),
                # git add .
                (0, "", ""),
                # git commit
                (0, "", ""),
                # git rev-parse HEAD
                (0, "abc123", ""),
                # git push
                (0, "", ""),
                # gh pr create (returns PR URL)
                (0, expected_pr_url, ""),
                # mission complete
                (0, "Mission completed", ""),
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            result = executor.deliver(agent, "TEST-001", "Test")

            assert result.success is True
            assert result.pr_url == expected_pr_url

    def test_push_uses_upstream_flag(self, executor):
        """Test that push is called with --set-upstream flag."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            mock_run.side_effect = [
                (0, "gh version 1.0.0", ""),
                (0, "M file.txt", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "abc123", ""),
                (0, "", ""),
                (0, "https://github.com/owner/repo/pull/42", ""),
                (0, "Mission completed", ""),
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            executor.deliver(agent, "TEST-001", "Test")

            # Check that git push -u was called
            push_calls = [c for c in mock_run.call_args_list if "git push -u" in str(c)]
            assert len(push_calls) > 0

    def test_pr_created_on_main_branch(self, executor):
        """Test that PR is created against main branch."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            mock_run.side_effect = [
                (0, "gh version 1.0.0", ""),
                (0, "M file.txt", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "abc123", ""),
                (0, "", ""),
                (0, "https://github.com/owner/repo/pull/42", ""),
                (0, "Mission completed", ""),
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            executor.deliver(agent, "TEST-001", "Test commit message")

            # Check that gh pr create was called with --base main
            pr_calls = [c for c in mock_run.call_args_list if "gh pr create" in str(c)]
            assert len(pr_calls) > 0
            assert "--base main" in str(pr_calls[0])

    def test_pr_created_with_draft_flag(self, executor):
        """Test that PR is created with --draft flag to prevent auto-merge."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            mock_run.side_effect = [
                (0, "gh version 1.0.0", ""),
                (0, "M file.txt", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "abc123", ""),
                (0, "", ""),
                (0, "https://github.com/owner/repo/pull/42", ""),
                (0, "Mission completed", ""),
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            result = executor.deliver(agent, "TEST-001", "Test commit message")

            # Check that gh pr create was called with --draft flag
            pr_calls = [c for c in mock_run.call_args_list if "gh pr create" in str(c)]
            assert len(pr_calls) > 0
            # Verify --draft flag is present (forces PENDING REVIEW state, prevents auto-merge)
            assert "--draft" in str(pr_calls[0])
            assert result.success is True

    def test_mission_complete_called_with_pr_url(self, executor):
        """Test that bin/mission complete is called with PR metadata."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            pr_url = "https://github.com/owner/repo/pull/42"
            mock_run.side_effect = [
                (0, "gh version 1.0.0", ""),
                (0, "M file.txt", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "abc123", ""),
                (0, "", ""),
                (0, pr_url, ""),
                (0, "Mission completed", ""),  # mission complete call
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            executor.deliver(agent, "TEST-001", "Test")

            # Check that mission complete was called with PR URL
            mission_calls = [c for c in mock_run.call_args_list if "mission complete" in str(c)]
            assert len(mission_calls) > 0
            # Verify PR URL is in the call
            assert pr_url in str(mission_calls[0])


class TestErrorHandling:
    """Test error handling and recovery."""

    def test_delivery_fails_if_push_fails(self, executor):
        """Test that delivery fails if push fails."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            mock_run.side_effect = [
                (0, "gh version 1.0.0", ""),
                (0, "M file.txt", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "abc123", ""),
                (128, "", "fatal: permission denied"),  # push fails
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            result = executor.deliver(agent, "TEST-001", "Test")

            assert result.success is False
            assert "Failed to push branch" in result.error
            # But we still have branch and commit info
            assert result.branch == "feature/test-001"
            assert result.commit_sha == "abc123"

    def test_delivery_fails_if_pr_creation_fails(self, executor):
        """Test that delivery fails if PR creation fails."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            mock_run.side_effect = [
                (0, "gh version 1.0.0", ""),
                (0, "M file.txt", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "abc123", ""),
                (0, "", ""),
                (1, "", "fatal: API error"),  # pr create fails
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            result = executor.deliver(agent, "TEST-001", "Test")

            assert result.success is False
            assert "Failed to create PR" in result.error


class TestVibeshellIntegration:
    """Test integration with bin/vibe-shell (GAD-5)."""

    def test_all_git_ops_via_vibe_shell(self, executor):
        """Test that all Git operations go through vibe-shell."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            mock_run.side_effect = [
                (0, "gh version 1.0.0", ""),
                (0, "M file.txt", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "", ""),
                (0, "abc123", ""),
                (0, "", ""),
                (0, "https://github.com/owner/repo/pull/42", ""),
                (0, "Mission completed", ""),
            ]

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            executor.deliver(agent, "TEST-001", "Test")

            # Verify _run_via_vibe_shell was called multiple times
            # (all git ops should use it)
            assert mock_run.call_count >= 7  # At least: gh, status, checkout, add, commit, push, pr

    def test_vibe_shell_timeout_handled(self, executor):
        """Test that vibe-shell timeout is handled gracefully."""
        with mock.patch.object(executor, "_run_via_vibe_shell") as mock_run:
            # Simulate timeout on git push
            mock_run.side_effect = GitOperationError("Command timed out after 30s: git push...")

            agent = mock.Mock()
            agent.verify_work.return_value = {"success": True}

            result = executor.deliver(agent, "TEST-001", "Test")

            assert result.success is False
            assert "timed out" in result.error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
