#!/usr/bin/env python3
"""
LEGACY CONFIG LOADER - GAD-100 Phase 3
=======================================

This module isolates ALL pre-GAD-100 configuration loading logic.

PURPOSE:
- Freeze old config loading code in ONE location
- Enable clean adapter pattern in core_orchestrator
- Allow side-by-side comparison with VibeConfig
- Facilitate safe migration and rollback

DESIGN:
- Implements ConfigLoader interface (same as VibeConfig)
- Contains NO new features (frozen legacy code only)
- All code extracted from:
  - core_orchestrator.py (load_project_manifest, save_project_manifest, etc.)
  - show-context.py (session_handoff, system_status loading)
  - vibe-cli (any config loading there)

USAGE:
```python
# Old way (before GAD-100):
with open("workspaces/project/project_manifest.json") as f:
    manifest = json.load(f)

# New way (GAD-100 Phase 3 - legacy path):
loader = LegacyConfigLoader(workspace_root="workspaces/project")
manifest = loader.get_project_manifest()
```

MIGRATION:
- Phase 3: Use LegacyConfigLoader (default)
- Phase 4: Toggle between Legacy and VibeConfig (feature flag)
- Phase 5: Migration tools + lossless verification
- Phase 6: VibeConfig becomes default, LegacyConfigLoader deprecated

Version: 1.0 (GAD-100 Phase 3)
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIG LOADER INTERFACE (implemented by both Legacy + VibeConfig)
# =============================================================================


class ConfigLoaderInterface:
    """Base interface for all config loaders (Legacy + VibeConfig)"""

    def get_project_manifest(self, project_id: str) -> dict[str, Any]:
        """Load project manifest"""
        raise NotImplementedError

    def save_project_manifest(self, project_id: str, manifest: dict[str, Any]) -> None:
        """Save project manifest"""
        raise NotImplementedError

    def get_session_handoff(self) -> dict[str, Any] | None:
        """Load session handoff"""
        raise NotImplementedError

    def get_system_status(self) -> dict[str, Any]:
        """Get/generate system status"""
        raise NotImplementedError

    def load_artifact(self, project_id: str, artifact_name: str) -> dict[str, Any] | None:
        """Load artifact file"""
        raise NotImplementedError

    def load_workflow(self, workflow_path: Path) -> dict[str, Any]:
        """Load workflow YAML"""
        raise NotImplementedError


# =============================================================================
# LEGACY CONFIG LOADER (Frozen pre-GAD-100 code)
# =============================================================================


class LegacyConfigLoader(ConfigLoaderInterface):
    """
    Legacy configuration loader (pre-GAD-100)

    Isolates ALL old config loading logic in one class.
    This code is FROZEN - no new features, only bug fixes.

    Args:
        repo_root: Repository root directory
        workspaces_dir: Workspaces directory (default: {repo_root}/workspaces)
    """

    def __init__(self, repo_root: Path, workspaces_dir: Path | None = None):
        self.repo_root = Path(repo_root)
        self.workspaces_dir = (
            Path(workspaces_dir) if workspaces_dir else self.repo_root / "workspaces"
        )

        if not self.repo_root.exists():
            raise ValueError(f"Repository root not found: {self.repo_root}")

    # -------------------------------------------------------------------------
    # PROJECT MANIFEST LOADING (extracted from core_orchestrator.py:346-409)
    # -------------------------------------------------------------------------

    def get_project_manifest(self, project_id: str) -> dict[str, Any]:
        """
        Load project manifest from workspace

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from core_orchestrator.py:load_project_manifest()
        """
        manifest_path = self._get_manifest_path(project_id)

        if not manifest_path.exists():
            raise FileNotFoundError(f"Project manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            data = json.load(f)

        logger.info(f"Loaded project manifest (legacy): {project_id}")
        return data

    def save_project_manifest(self, project_id: str, manifest: dict[str, Any]) -> None:
        """
        Save project manifest to workspace

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from core_orchestrator.py:save_project_manifest()
        """
        manifest_path = self._get_manifest_path(project_id)

        # Write to disk
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Saved project manifest (legacy): {project_id}")

    def _get_manifest_path(self, project_id: str) -> Path:
        """
        Get path to project manifest (robust search)

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from core_orchestrator.py:_get_manifest_path()

        Searches:
          - workspaces/ (non-recursive and recursive)
          - repo root (recursive) as a fallback

        Accepts a match when either:
          - metadata.projectId == project_id OR
          - parent directory name == project_id
        """
        searched_paths = []
        search_bases = []

        # Prefer explicit workspaces dir, but fall back to repo root
        if self.workspaces_dir.exists():
            search_bases.append(self.workspaces_dir)
        else:
            logger.warning(
                f"Workspaces directory not found at {self.workspaces_dir}; "
                f"falling back to repo root search"
            )
            search_bases.append(self.repo_root)

        # Always add repo_root as secondary fallback (avoids missing test fixtures)
        if self.repo_root not in search_bases:
            search_bases.append(self.repo_root)

        # Search strategy:
        # 1. Direct child: workspaces/{project_id}/project_manifest.json
        # 2. Recursive search (anywhere in workspaces/ or repo_root/)
        for base in search_bases:
            # 1. Try direct child first (fast path)
            direct = base / project_id / "project_manifest.json"
            if direct.exists():
                # Verify project_id matches (either metadata.projectId or parent dir)
                if self._manifest_matches_project_id(direct, project_id):
                    logger.debug(f"Found manifest (direct): {direct}")
                    return direct

            # 2. Recursive search
            for manifest_path in base.rglob("project_manifest.json"):
                searched_paths.append(str(manifest_path))
                if self._manifest_matches_project_id(manifest_path, project_id):
                    logger.debug(f"Found manifest (recursive): {manifest_path}")
                    return manifest_path

        # Not found
        raise FileNotFoundError(
            f"Project manifest not found for project_id='{project_id}'. "
            f"Searched {len(searched_paths)} locations:\n"
            + "\n".join(f"  - {p}" for p in searched_paths[:10])
            + (f"\n  ... and {len(searched_paths) - 10} more" if len(searched_paths) > 10 else "")
        )

    def _manifest_matches_project_id(self, manifest_path: Path, project_id: str) -> bool:
        """Check if manifest matches project_id (metadata.projectId or parent dir name)"""
        try:
            with open(manifest_path) as f:
                data = json.load(f)
            manifest_project_id = data.get("metadata", {}).get("projectId", "")
            parent_dir = manifest_path.parent.name
            return manifest_project_id == project_id or parent_dir == project_id
        except (json.JSONDecodeError, KeyError):
            # Invalid JSON or missing fields - not a match
            return False

    # -------------------------------------------------------------------------
    # SESSION HANDOFF LOADING (extracted from show-context.py:24)
    # -------------------------------------------------------------------------

    def get_session_handoff(self) -> dict[str, Any] | None:
        """
        Load session handoff from .session_handoff.json

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from show-context.py:24
        """
        handoff_file = self.repo_root / ".session_handoff.json"

        if not handoff_file.exists():
            logger.debug("Session handoff not found (legacy)")
            return None

        with open(handoff_file) as f:
            data = json.load(f)

        logger.info("Loaded session handoff (legacy)")
        return data

    # -------------------------------------------------------------------------
    # SYSTEM STATUS LOADING (extracted from show-context.py:25)
    # -------------------------------------------------------------------------

    def get_system_status(self) -> dict[str, Any]:
        """
        Get system status from .system_status.json (or generate if missing)

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from show-context.py:25 + core_orchestrator.py:_get_system_status()
        """
        status_file = self.repo_root / ".system_status.json"

        if status_file.exists():
            with open(status_file) as f:
                data = json.load(f)
            logger.info("Loaded system status (legacy)")
            return data

        # Generate if missing (fallback behavior from core_orchestrator.py)
        logger.debug("System status not found, generating (legacy)")
        return self._generate_system_status()

    def _generate_system_status(self) -> dict[str, Any]:
        """
        Generate system status (fallback)

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from core_orchestrator.py:_get_system_status()
        """
        git_status = self._get_git_status()
        linting_status = self._get_linting_status()

        return {
            "git": git_status,
            "linting": linting_status,
            "tests": {"status": "unknown"},  # Placeholder
        }

    def _get_git_status(self) -> dict[str, Any]:
        """
        Get git status

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from core_orchestrator.py:_get_git_status()
        """
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

            # Check if working directory is clean
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            is_clean = (
                len(status_result.stdout.strip()) == 0 if status_result.returncode == 0 else False
            )

            return {"branch": branch, "working_directory_clean": is_clean}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"branch": "unknown", "working_directory_clean": False}

    def _get_linting_status(self) -> dict[str, Any]:
        """
        Get linting status

        This is the LEGACY implementation (pre-GAD-100).
        Simplified version (full implementation in bin/update-system-status.sh)
        """
        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--quiet"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "status": "passing" if result.returncode == 0 else "failing",
                "errors_count": 0 if result.returncode == 0 else -1,  # Unknown count
            }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"status": "unknown", "errors_count": -1}

    # -------------------------------------------------------------------------
    # ARTIFACT LOADING (extracted from core_orchestrator.py:545)
    # -------------------------------------------------------------------------

    def load_artifact(self, project_id: str, artifact_name: str) -> dict[str, Any] | None:
        """
        Load artifact file from workspace

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from core_orchestrator.py:load_artifact()
        """
        manifest_path = self._get_manifest_path(project_id)
        workspace_root = manifest_path.parent
        artifact_path = workspace_root / artifact_name

        if not artifact_path.exists():
            logger.warning(f"Artifact not found (legacy): {artifact_name}")
            return None

        # Determine file type and load accordingly
        if artifact_path.suffix == ".json":
            with open(artifact_path) as f:
                return json.load(f)
        elif artifact_path.suffix in [".yaml", ".yml"]:
            with open(artifact_path) as f:
                return yaml.safe_load(f)
        else:
            # Text file - return as string
            with open(artifact_path) as f:
                return {"content": f.read()}

    # -------------------------------------------------------------------------
    # WORKFLOW LOADING (extracted from core_orchestrator.py:301)
    # -------------------------------------------------------------------------

    def load_workflow(self, workflow_path: Path) -> dict[str, Any]:
        """
        Load workflow YAML

        This is the LEGACY implementation (pre-GAD-100).
        Code extracted from core_orchestrator.py:_load_workflow()
        """
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")

        with open(workflow_path) as f:
            data = yaml.safe_load(f)

        logger.info(f"Loaded workflow (legacy): {workflow_path}")
        return data
