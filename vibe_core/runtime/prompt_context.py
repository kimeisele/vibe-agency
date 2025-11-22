#!/usr/bin/env python3
"""
Prompt Context Engine - The Flesh (GAD-909)
============================================

Provides dynamic context injection for prompts - the "flesh" that makes
the skeleton (workflows) and voice (prompts) come alive with real system data.

This module enables "Permeable Prompts" - prompts with placeholders like
{git_status}, {project_structure}, {system_time} that get filled with
live system data at execution time.

Architecture:
    Resolvers (functions) → PromptContext → Context Dict → PromptRegistry

Usage:
    from vibe_core.runtime.prompt_context import get_prompt_context

    context_engine = get_prompt_context()
    context = context_engine.resolve(["git_status", "system_time"])
    # Returns: {"git_status": "...", "system_time": "2025-11-19 10:30:00"}

    # Pass to prompt registry
    prompt = PromptRegistry.get("research.analyze_topic", context)

Created: 2025-11-19
Version: 1.0 (MVP - Core Resolvers)
"""

import logging
import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptContext:
    """
    Dynamic context engine for prompt injection.

    Manages a registry of "resolvers" - functions that return live system data.
    Resolvers are called on-demand and their results injected into prompt templates.
    """

    def __init__(self, vibe_root: Path | None = None):
        """
        Initialize the prompt context engine.

        Args:
            vibe_root: Root directory of vibe-agency. If None, auto-detected.
        """
        if vibe_root is None:
            # Auto-detect: We're in vibe_core/runtime/prompt_context.py
            # Go up 2 levels: runtime -> vibe_core -> project_root
            vibe_root = Path(__file__).parent.parent.parent

        self.vibe_root = Path(vibe_root)
        self._resolvers: dict[str, Callable[[], str]] = {}

        # Register core resolvers
        self._register_core_resolvers()

    def _register_core_resolvers(self) -> None:
        """Register the built-in core resolvers."""
        self.register("git_status", self._resolve_git_status)
        self.register("project_structure", self._resolve_project_structure)
        self.register("system_time", self._resolve_system_time)
        self.register("current_branch", self._resolve_current_branch)
        self.register("recent_commits", self._resolve_recent_commits)

        # ARCH-060: Kernel state resolvers (data only, no interpretation)
        self.register("inbox_count", self._resolve_inbox_count)
        self.register("agenda_summary", self._resolve_agenda_summary)
        self.register("git_sync_status", self._resolve_git_sync_status)

        logger.debug("✅ Registered 8 core context resolvers (5 legacy + 3 kernel state)")

    def register(self, key: str, resolver: Callable[[], str]) -> None:
        """
        Register a new context resolver.

        Args:
            key: Context key (e.g., "git_status")
            resolver: Function that returns a string value
        """
        self._resolvers[key] = resolver
        logger.debug(f"Registered context resolver: {key}")

    def resolve(self, keys: list[str] | None = None) -> dict[str, str]:
        """
        Resolve context values for specified keys.

        Args:
            keys: List of context keys to resolve. If None, resolves all registered keys.

        Returns:
            Dictionary mapping keys to resolved values
        """
        if keys is None:
            keys = list(self._resolvers.keys())

        context = {}

        for key in keys:
            if key not in self._resolvers:
                logger.warning(f"⚠️  Unknown context key: {key}")
                context[key] = f"[Unknown context key: {key}]"
                continue

            try:
                value = self._resolvers[key]()
                context[key] = value
                logger.debug(f"✅ Resolved context: {key} ({len(value)} chars)")
            except Exception as e:
                logger.warning(f"⚠️  Failed to resolve context '{key}': {e}")
                context[key] = f"[Error resolving {key}: {e}]"

        return context

    # ========================================================================
    # Core Resolvers
    # ========================================================================

    def _resolve_git_status(self) -> str:
        """
        Resolve git status.

        Returns:
            Git status output (branch, changes, etc.)
        """
        try:
            result = subprocess.run(
                ["git", "status", "--short", "--branch"],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"[Git error: {result.stderr.strip()}]"
        except subprocess.TimeoutExpired:
            return "[Git timeout]"
        except FileNotFoundError:
            return "[Git not installed]"
        except Exception as e:
            return f"[Git error: {e}]"

    def _resolve_project_structure(self) -> str:
        """
        Resolve project structure.

        Returns:
            Directory tree (limited to 2 levels)
        """
        try:
            # Try using 'tree' command first (cleaner output)
            result = subprocess.run(
                ["tree", "-L", "2", "-d", "--noreport"],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return result.stdout.strip()

            # Fallback: Python implementation
            return self._python_tree(self.vibe_root, max_depth=2)

        except FileNotFoundError:
            # 'tree' not installed, use Python fallback
            return self._python_tree(self.vibe_root, max_depth=2)
        except subprocess.TimeoutExpired:
            return "[Tree timeout]"
        except Exception as e:
            return f"[Tree error: {e}]"

    def _python_tree(self, root: Path, max_depth: int = 2) -> str:
        """
        Python-based directory tree implementation (fallback).

        Args:
            root: Root directory
            max_depth: Maximum depth to traverse

        Returns:
            Tree representation as string
        """
        lines = [str(root)]

        def _walk(path: Path, depth: int, prefix: str = ""):
            if depth > max_depth:
                return

            try:
                entries = sorted([e for e in path.iterdir() if e.is_dir()], key=lambda x: x.name)

                for i, entry in enumerate(entries):
                    is_last = i == len(entries) - 1

                    # Skip hidden and common ignore dirs
                    if entry.name.startswith(".") or entry.name in ["__pycache__", "node_modules"]:
                        continue

                    connector = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{connector}{entry.name}/")

                    extension = "    " if is_last else "│   "
                    _walk(entry, depth + 1, prefix + extension)
            except PermissionError:
                pass

        _walk(root, 0)
        return "\n".join(lines)

    def _resolve_system_time(self) -> str:
        """
        Resolve current system time.

        Returns:
            ISO 8601 formatted timestamp
        """
        return datetime.now().isoformat(timespec="seconds")

    def _resolve_current_branch(self) -> str:
        """
        Resolve current git branch.

        Returns:
            Current branch name
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "[Not a git repository]"
        except Exception as e:
            return f"[Error: {e}]"

    def _resolve_recent_commits(self) -> str:
        """
        Resolve recent git commits.

        Returns:
            Last 3 commits (oneline format)
        """
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-3"],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "[No commits]"
        except Exception as e:
            return f"[Error: {e}]"

    # ========================================================================
    # ARCH-060: Kernel State Resolvers (Data Layer - No Interpretation)
    # ========================================================================

    def _resolve_inbox_count(self) -> str:
        """
        Resolve inbox message count (GAD-006: Asynchronous Intent).

        Returns:
            Raw count as string (e.g., "3" or "0")
        """
        try:
            inbox_path = self.vibe_root / "workspace" / "inbox"

            if not inbox_path.exists():
                return "0"

            # Count markdown files (inbox messages)
            message_files = list(inbox_path.glob("*.md"))
            return str(len(message_files))

        except Exception as e:
            logger.warning(f"Failed to resolve inbox_count: {e}")
            return "0"

    def _resolve_agenda_summary(self) -> str:
        """
        Resolve agenda task summary (ARCH-045: Agenda System).

        Returns:
            JSON string with task counts by priority, e.g.:
            '{"HIGH": 2, "MEDIUM": 1, "LOW": 0, "total": 3}'
        """
        try:
            import json

            backlog_path = self.vibe_root / "workspace" / "BACKLOG.md"

            if not backlog_path.exists():
                return '{"HIGH": 0, "MEDIUM": 0, "LOW": 0, "total": 0}'

            content = backlog_path.read_text()

            # Extract Outstanding Tasks section only
            outstanding_idx = content.find("## Outstanding Tasks")
            completed_idx = content.find("## Completed Tasks")

            if outstanding_idx == -1 or completed_idx == -1:
                return '{"HIGH": 0, "MEDIUM": 0, "LOW": 0, "total": 0}'

            outstanding_section = content[
                outstanding_idx + len("## Outstanding Tasks") : completed_idx
            ]

            # Count tasks by priority
            counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

            for line in outstanding_section.split("\n"):
                line = line.strip()
                if line.startswith("- [ ]"):
                    # Extract priority from [PRIORITY] tag
                    if "[HIGH]" in line:
                        counts["HIGH"] += 1
                    elif "[MEDIUM]" in line:
                        counts["MEDIUM"] += 1
                    elif "[LOW]" in line:
                        counts["LOW"] += 1

            counts["total"] = counts["HIGH"] + counts["MEDIUM"] + counts["LOW"]

            return json.dumps(counts)

        except Exception as e:
            logger.warning(f"Failed to resolve agenda_summary: {e}")
            return '{"HIGH": 0, "MEDIUM": 0, "LOW": 0, "total": 0}'

    def _resolve_git_sync_status(self) -> str:
        """
        Resolve git sync status (ARCH-044: Git-Ops Strategy).

        Returns:
            Raw status string from VIBE_GIT_STATUS env var, or "UNKNOWN"
            Possible values: "SYNCED", "BEHIND_BY_N", "DIVERGED", "FETCH_FAILED", "NO_REPO"
        """
        try:
            import os

            status = os.getenv("VIBE_GIT_STATUS", "UNKNOWN")
            return status

        except Exception as e:
            logger.warning(f"Failed to resolve git_sync_status: {e}")
            return "UNKNOWN"


# ========================================================================
# Global Instance (Singleton Pattern)
# ========================================================================

_default_context: PromptContext | None = None


def get_prompt_context() -> PromptContext:
    """
    Get the global prompt context instance (singleton).

    Returns:
        PromptContext instance
    """
    global _default_context

    if _default_context is None:
        _default_context = PromptContext()
        logger.info("🔌 Prompt Context Engine initialized")

    return _default_context


# ========================================================================
# CLI Interface (for testing)
# ========================================================================

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    print("\n" + "=" * 80)
    print("🧪 PROMPT CONTEXT ENGINE TEST (GAD-909)")
    print("=" * 80)

    # Initialize context engine
    context_engine = PromptContext()

    # Test: Resolve all contexts
    print("\n📍 Resolving all registered contexts...")
    context = context_engine.resolve()

    print("\n✅ Context Resolution Results:")
    print("=" * 80)

    for key, value in context.items():
        print(f"\n{key}:")
        print("-" * 40)
        # Truncate long values for display
        display_value = value if len(value) < 200 else value[:200] + "..."
        print(display_value)

    print("\n" + "=" * 80)
    print(f"✅ Successfully resolved {len(context)} context keys")
    print("=" * 80)
