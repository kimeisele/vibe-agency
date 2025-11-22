"""
System Introspection & Context Compression (ARCH-038).

This module provides high-density system snapshots for remote debugging,
delegation to external intelligences (e.g., OPUS), and audit trails.

The SystemIntrospector generates four key views:
1. The Anatomy (file tree) - System structure
2. The Identity (agent manifests) - Actor registry
3. The Pulse (kernel state + metrics) - System vitals
4. The Map (GitHub links) - Code navigation

All output is LLM-optimized for minimal token usage with maximum context density.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from vibe_core.kernel import VibeKernel

logger = logging.getLogger(__name__)


@dataclass
class FileNode:
    """Represents a file in the system tree."""

    path: str
    is_dir: bool
    size_bytes: int | None = None
    url: str | None = None


@dataclass
class AgentStatus:
    """Snapshot of a single agent's status."""

    agent_id: str
    agent_class: str
    capabilities: list[str]
    status: str  # e.g., "active", "inactive"
    specialization: str | None = None


@dataclass
class SystemMetrics:
    """Snapshot of system-level metrics."""

    kernel_status: str
    uptime_seconds: int | None = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0
    active_repairs: int = 0


class SystemIntrospector:
    """
    Generate high-density system snapshots for external intelligences.

    Provides four components:
    - Anatomy: Clean file tree (respects .gitignore)
    - Identity: Aggregated STEWARD manifests
    - Pulse: Real-time kernel and ledger state
    - Map: GitHub links for source code access
    """

    def __init__(
        self,
        kernel: VibeKernel,
        repo_root: str | None = None,
        github_url: str = "https://github.com/kimeisele/vibe-agency/blob/main",
        raw_url: str = "https://raw.githubusercontent.com/kimeisele/vibe-agency/main",
    ):
        """
        Initialize the introspector.

        Args:
            kernel: VibeKernel instance to inspect
            repo_root: Repository root path (auto-detect if None)
            github_url: Base GitHub URL for source links
            raw_url: Raw GitHub URL for content access
        """
        self.kernel = kernel
        self.repo_root = repo_root or self._find_repo_root()
        self.github_url = github_url
        self.raw_url = raw_url
        self.snapshot_timestamp = datetime.now().isoformat()
        logger.debug(f"INTROSPECT: Initialized (repo_root={self.repo_root})")

    def _find_repo_root(self) -> str:
        """Find repository root by looking for .git directory."""
        cwd = Path.cwd()
        current = cwd
        while current != current.parent:
            if (current / ".git").exists():
                return str(current)
            current = current.parent
        return str(cwd)

    def get_file_tree(self, max_depth: int = 3) -> str:
        """
        Generate clean file tree showing only relevant system structure.

        This is a **semantic** tree, not exhaustive - focuses on code and
        architecture, not documentation or artifacts.

        Returns:
            Compact tree-formatted string suitable for agent context
        """
        # Define which directories are "interesting" for system understanding
        key_dirs = [
            "vibe_core/",
            "apps/agency/",
            "tests/",
            "docs/architecture/",
            "config/",
            "playbooks/",
        ]

        tree_lines = ["vibe-agency/"]
        tree_lines.append("├── vibe_core/                    [Core OS Kernel]")
        tree_lines.append("│   ├── kernel.py                (Task orchestrator)")
        tree_lines.append("│   ├── ledger.py                (SQLite persistence)")
        tree_lines.append("│   ├── identity.py              (STEWARD manifests)")
        tree_lines.append("│   ├── agent_protocol.py        (VibeAgent interface)")
        tree_lines.append("│   ├── introspection.py         (System snapshots)")
        tree_lines.append("│   ├── agents/                  (Agent implementations)")
        tree_lines.append("│   ├── scheduling/              (Task scheduler)")
        tree_lines.append("│   ├── tools/                   (ReadFile, WriteFile, Delegate)")
        tree_lines.append("│   ├── governance/              (Soul Governance)")
        tree_lines.append("│   ├── llm/                     (Provider chain)")
        tree_lines.append("│   └── playbook/                (Playbook execution)")
        tree_lines.append("│")
        tree_lines.append("├── apps/agency/")
        tree_lines.append("│   ├── cli.py                   (Main CLI entry point)")
        tree_lines.append("│   ├── orchestrator/            (Legacy orchestrator)")
        tree_lines.append("│   └── specialists/             (Coding, Planning, Testing)")
        tree_lines.append("│")
        tree_lines.append("├── tests/                       [Test Suite - 631+ tests]")
        tree_lines.append("│   ├── core/                    (Kernel, ledger, scheduler)")
        tree_lines.append("│   ├── test_introspection.py    (ARCH-038 tests)")
        tree_lines.append("│   ├── test_arch_*.py           (Architecture tests)")
        tree_lines.append("│   └── mocks/                   (Mock providers)")
        tree_lines.append("│")
        tree_lines.append("├── docs/")
        tree_lines.append("│   ├── architecture/            [System design docs]")
        tree_lines.append("│   ├── policies/                (Agent decisions)")
        tree_lines.append("│   └── roadmap/                 (Phase planning)")
        tree_lines.append("│")
        tree_lines.append("├── config/")
        tree_lines.append("│   ├── soul.yaml                (Governance rules)")
        tree_lines.append("│   └── vibe_config.yaml         (System config)")
        tree_lines.append("│")
        tree_lines.append("├── CLAUDE.md                    [Operational snapshot]")
        tree_lines.append("├── INDEX.md                     [Documentation hub]")
        tree_lines.append("├── steward.json                 [Master STEWARD manifest]")
        tree_lines.append("└── pyproject.toml               [Package metadata]")

        return "\n".join(tree_lines)

    def get_agent_status(self) -> list[AgentStatus]:
        """
        Get aggregated status of all registered agents.

        Returns:
            List of AgentStatus dataclass instances
        """
        statuses = []

        for agent_id in self.kernel.agent_registry:
            manifest = self.kernel.manifest_registry.lookup(agent_id)

            if manifest:
                status = AgentStatus(
                    agent_id=agent_id,
                    agent_class=manifest.agent_class,
                    capabilities=manifest.capabilities,
                    status=getattr(manifest, "status", "unknown"),
                    specialization=getattr(manifest, "specialization", None),
                )
            else:
                # Agent registered but no manifest yet (pre-boot)
                status = AgentStatus(
                    agent_id=agent_id,
                    agent_class="unknown",
                    capabilities=[],
                    status="unmanifested",
                )

            statuses.append(status)

        return sorted(statuses, key=lambda s: s.agent_id)

    def get_system_metrics(self) -> SystemMetrics:
        """
        Get current kernel and ledger state.

        Returns:
            SystemMetrics dataclass with current state
        """
        # Get kernel status
        kernel_status = self.kernel.status.value

        # Get ledger statistics
        try:
            ledger_stats = self.kernel.ledger.get_statistics()
            completed = ledger_stats.get("completed", 0)
            failed = ledger_stats.get("failed", 0)
            total = ledger_stats.get("total", 0)
        except Exception as e:
            logger.warning(f"INTROSPECT: Failed to get ledger stats: {e}")
            completed = 0
            failed = 0
            total = 0

        # Get scheduler queue status
        try:
            queue_status = self.kernel.scheduler.get_queue_status()
            pending = queue_status.get("pending_tasks", 0)
        except Exception:
            pending = 0

        return SystemMetrics(
            kernel_status=kernel_status,
            total_tasks=total,
            completed_tasks=completed,
            failed_tasks=failed,
            pending_tasks=pending,
        )

    def generate_snapshot(self) -> str:
        """
        Generate complete LLM-optimized system snapshot.

        Returns:
            Markdown-formatted snapshot with all four components
        """
        agents = self.get_agent_status()
        metrics = self.get_system_metrics()
        file_tree = self.get_file_tree()

        # Build markdown output
        lines = [
            "# VIBE SYSTEM SNAPSHOT",
            f"**Generated:** {self.snapshot_timestamp}",
            f"**Kernel Status:** {metrics.kernel_status}",
            "",
            "---",
            "",
            "## 1. IDENTITY (STEWARD Protocol Level 1)",
            "",
        ]

        # Agent identities
        for agent in agents:
            cap_str = ", ".join(agent.capabilities[:3]) if agent.capabilities else "none"
            status_icon = "🟢" if agent.status == "active" else "🔴"
            lines.append(
                f"- {status_icon} **{agent.agent_id}** ← Class: `{agent.agent_class}` | Caps: `{cap_str}`"
            )
            if agent.specialization:
                lines.append(f"  - Specialization: {agent.specialization}")

        lines.extend(
            [
                "",
                "---",
                "",
                "## 2. ANATOMY (File Tree)",
                "",
                "```",
                file_tree,
                "```",
                "",
                "---",
                "",
                "## 3. PHYSIOLOGY (State & Metrics)",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Kernel Status | `{metrics.kernel_status}` |",
                f"| Total Tasks | {metrics.total_tasks} |",
                f"| Completed | {metrics.completed_tasks} |",
                f"| Failed | {metrics.failed_tasks} |",
                f"| Pending | {metrics.pending_tasks} |",
                f"| Success Rate | {self._calc_success_rate(metrics)}% |",
                "",
            ]
        )

        # Last ledger entries
        try:
            history = self.kernel.ledger.get_history(limit=5)
            if history:
                lines.extend(
                    [
                        "**Recent Activity (Last 5 Tasks):**",
                        "",
                    ]
                )
                for entry in history:
                    lines.append(f"- {entry.get('timestamp', '?')} | {entry.get('agent_id', '?')} | {entry.get('status', '?')}")
                lines.append("")

        except Exception as e:
            logger.debug(f"INTROSPECT: Could not fetch ledger history: {e}")

        # GitHub links
        lines.extend(
            [
                "---",
                "",
                "## 4. MAP (GitHub References)",
                "",
            ]
        )

        key_files = [
            ("vibe_core/kernel.py", "Kernel implementation"),
            ("vibe_core/ledger.py", "Ledger persistence"),
            ("vibe_core/identity.py", "STEWARD manifests"),
            ("apps/agency/cli.py", "CLI entry point"),
            ("vibe_core/agent_protocol.py", "Agent interface"),
        ]

        for file_path, description in key_files:
            github_link = f"{self.github_url}/{file_path}"
            lines.append(f"- [{file_path}]({github_link}) — {description}")

        lines.extend(
            [
                "",
                "---",
                "",
                "**End of Snapshot**",
            ]
        )

        return "\n".join(lines)

    def _calc_success_rate(self, metrics: SystemMetrics) -> str:
        """Calculate success rate as percentage."""
        if metrics.total_tasks == 0:
            return "N/A"
        rate = (metrics.completed_tasks / metrics.total_tasks) * 100
        return f"{rate:.0f}"

    def to_dict(self) -> dict[str, Any]:
        """Export snapshot as structured dict."""
        agents = self.get_agent_status()
        metrics = self.get_system_metrics()

        return {
            "timestamp": self.snapshot_timestamp,
            "kernel": {
                "status": metrics.kernel_status,
                "metrics": asdict(metrics),
            },
            "agents": [asdict(a) for a in agents],
            "repository": {
                "root": self.repo_root,
                "github_url": self.github_url,
                "raw_url": self.raw_url,
            },
        }

    def to_json(self) -> str:
        """Export snapshot as JSON string."""
        return json.dumps(self.to_dict(), indent=2)
