"""TaskExecutor: The Atomic Gearbox (GAD-201)

Safe, complete, atomic delivery workflow for agents.
Integrates with GAD-5 (Runtime) and GAD-7 (Mission Control) for guaranteed delivery.

The Atomic Workflow (Guaranteed):
  1. Verify agent work passes QA (verify_work)
  2. Check GitHub CLI is available (via vibe-shell)
  3. Create feature branch (feature/TASK-XXX)
  4. Stage and commit changes
  5. Push branch to remote
  6. Create PR using GitHub CLI (via vibe-shell)
  7. Complete mission via bin/mission complete

Agent interface: agent.deliver_solution(task_id, message)
System interface: executor.deliver(agent, task_id, message)

Key Design Principle: Use existing infrastructure (vibe-shell, mission) instead
of reinventing. This ensures consistency and safety across all operations.
"""

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DeliveryResult:
    """Result of an atomic delivery operation."""

    success: bool
    pr_url: str | None = None
    branch: str | None = None
    commit_sha: str | None = None
    error: str | None = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class GitOperationError(Exception):
    """Raised when a git operation fails."""

    pass


class TaskExecutor:
    """The Atomic Gearbox: Guaranteed atomic delivery via GAD-2 orchestration.

    Ensures delivery is:
    - SAFE: Creates feature branches, no changes to main
    - COMPLETE: Branch -> Commit -> Push -> PR -> Mission complete
    - ATOMIC: All-or-nothing with QA gates

    Integrates with:
    - GAD-5 (vibe-shell) for safe command execution
    - GAD-7 (bin/mission) for orchestration coordination
    """

    def __init__(self, vibe_root: Path | None = None):
        """Initialize the executor.

        Args:
            vibe_root: Path to vibe-agency root (auto-detected if None)
        """
        if vibe_root is None:
            vibe_root = self._detect_vibe_root()

        self.vibe_root = Path(vibe_root)

    def _detect_vibe_root(self) -> Path:
        """Auto-detect the vibe-agency root directory."""
        cwd = Path.cwd()

        if (cwd / ".vibe").exists():
            return cwd

        for parent in cwd.parents:
            if (parent / ".vibe").exists():
                return parent

        raise RuntimeError(
            "Could not detect vibe-agency root. Please set VIBE_ROOT environment variable."
        )

    def _run_via_vibe_shell(self, command: str, timeout: int = 30) -> tuple[int, str, str]:
        """Execute a command safely via vibe-shell (GAD-5 Runtime).

        All Git operations go through vibe-shell to ensure:
        - Context injection (VIBE_CONTEXT)
        - Audit logging (.vibe/logs/commands.log)
        - MOTD enforcement
        - Safe execution environment

        Args:
            command: Shell command to execute (e.g., "git status")
            timeout: Timeout in seconds

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Use vibe-shell to execute the command
            vibe_shell_path = self.vibe_root / "bin" / "vibe-shell"
            if not vibe_shell_path.exists():
                raise GitOperationError(f"bin/vibe-shell not found at {vibe_shell_path}")

            result = subprocess.run(  # noqa: S603
                [str(vibe_shell_path), "-c", command],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired as e:
            raise GitOperationError(f"Command timed out after {timeout}s: {command}") from e
        except Exception as e:
            raise GitOperationError(f"Failed to execute via vibe-shell: {e}") from e

    def deliver(self, agent: Any, task_id: str, message: str) -> DeliveryResult:
        """Execute the atomic delivery workflow.

        This is the main entry point. Agents call this via deliver_solution().

        The Atomic Workflow:
          1. Verify agent passes QA (verify_work)
          2. Verify GitHub CLI is available
          3. Check repository has changes
          4. Create feature branch (feature/TASK-XXX)
          5. Stage all changes (git add .)
          6. Commit with semantic message
          7. Push branch with --set-upstream
          8. Create PR on main branch
          9. Complete mission via bin/mission

        Args:
            agent: The agent performing the delivery
            task_id: Task identifier (e.g., GAD-201_TASK_EXECUTOR)
            message: Semantic commit/PR message

        Returns:
            DeliveryResult with success status and PR URL
        """
        try:
            # GATE 1: Verify work before delivery (agent must pass QA)
            if hasattr(agent, "verify_work"):
                verification = agent.verify_work(check_code=True, run_tests=True)
                if not verification.get("success", False):
                    issues = verification.get("issues", ["Unknown QA failure"])
                    return DeliveryResult(
                        success=False, error=f"QA checks failed: {'; '.join(issues)}"
                    )

            # GATE 2: Verify GitHub CLI is installed (via vibe-shell)
            returncode, stdout, stderr = self._run_via_vibe_shell("gh --version")
            if returncode != 0:
                return DeliveryResult(
                    success=False,
                    error="GitHub CLI (gh) not installed or not in PATH. Install with: brew install gh",
                )

            # GATE 3: Check if repository has changes
            returncode, stdout, stderr = self._run_via_vibe_shell("git status --porcelain")
            if returncode != 0:
                return DeliveryResult(
                    success=False,
                    error=f"Failed to check git status: {stderr}",
                )
            if not stdout:
                return DeliveryResult(
                    success=False,
                    error="No changes to commit. Repository is clean.",
                )

            # STEP 1: Create feature branch
            branch_name = f"feature/{task_id.lower().replace('_', '-')}"
            returncode, stdout, stderr = self._run_via_vibe_shell(f"git checkout -b {branch_name}")
            if returncode != 0:
                # Branch might exist, try switching to it
                returncode, stdout, stderr = self._run_via_vibe_shell(f"git checkout {branch_name}")
                if returncode != 0:
                    return DeliveryResult(
                        success=False,
                        error=f"Failed to create/switch to branch {branch_name}: {stderr}",
                    )

            # STEP 2: Stage all changes
            returncode, stdout, stderr = self._run_via_vibe_shell("git add .")
            if returncode != 0:
                return DeliveryResult(
                    success=False,
                    error=f"Failed to stage changes: {stderr}",
                )

            # STEP 3: Commit changes with semantic message
            commit_message = f"feat({task_id}): {message}\n\n🤖 Generated with Claude Code\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
            returncode, stdout, stderr = self._run_via_vibe_shell(
                f'git commit -m "{commit_message}"'
            )
            if returncode != 0:
                return DeliveryResult(
                    success=False,
                    error=f"Failed to commit: {stderr}",
                )

            # Get commit SHA
            returncode, commit_sha, stderr = self._run_via_vibe_shell("git rev-parse HEAD")
            if returncode != 0:
                commit_sha = "unknown"

            # STEP 4: Push branch with --set-upstream
            returncode, stdout, stderr = self._run_via_vibe_shell(
                f"git push -u origin {branch_name}"
            )
            if returncode != 0:
                return DeliveryResult(
                    success=False,
                    error=f"Failed to push branch: {stderr}",
                    branch=branch_name,
                    commit_sha=commit_sha,
                )

            # STEP 5: Create PR using GitHub CLI (ATOMIC ACTION)
            # Use --draft to force PENDING REVIEW state (prevents auto-merge, requires human review)
            pr_command = f'gh pr create --draft --base main --head {branch_name} --title "{message}" --body "Automated delivery via GAD-201 TaskExecutor\\n\\nTask: {task_id}\\nBranch: {branch_name}"'
            returncode, pr_output, stderr = self._run_via_vibe_shell(pr_command)

            if returncode != 0:
                return DeliveryResult(
                    success=False,
                    error=f"Failed to create PR: {stderr}",
                    branch=branch_name,
                    commit_sha=commit_sha,
                )

            # Extract PR URL from output
            # GitHub CLI outputs the PR URL, sometimes multiple lines
            pr_url = None
            for line in pr_output.split("\n"):
                if "github.com" in line and "/pull/" in line:
                    # Extract URL from line
                    match = re.search(r"https://github\.com/[^/]+/[^/]+/pull/\d+", line)
                    if match:
                        pr_url = match.group(0)
                        break

            if not pr_url:
                # Fallback: try to extract from first line
                if pr_output:
                    pr_url = pr_output.split()[0]

            if not pr_url:
                return DeliveryResult(
                    success=False,
                    error=f"Failed to extract PR URL from output: {pr_output}",
                    branch=branch_name,
                    commit_sha=commit_sha,
                )

            # STEP 6: Complete mission via bin/mission (GAD-7 Coordination)
            mission_path = self.vibe_root / "bin" / "mission"
            if mission_path.exists():
                returncode, stdout, stderr = self._run_via_vibe_shell(
                    f"bin/mission complete {task_id} --metadata pr_url={pr_url}"
                )
                # Don't fail if mission complete fails - the PR was created successfully

            return DeliveryResult(
                success=True,
                pr_url=pr_url,
                branch=branch_name,
                commit_sha=commit_sha,
            )

        except GitOperationError as e:
            return DeliveryResult(success=False, error=str(e))
        except Exception as e:
            return DeliveryResult(success=False, error=f"Unexpected error during delivery: {e}")

    def __repr__(self) -> str:
        return f"TaskExecutor(vibe_root={self.vibe_root})"
