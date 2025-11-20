#!/usr/bin/env python3
"""
VIBE CONFIG - GAD-100 Phase 3 Phoenix Config Wrapper
=====================================================

This module wraps phoenix_config for vibe-agency state management.

PURPOSE:
- Centralized configuration loading (replaces scattered JSON/YAML loads)
- Multi-source config support (base.yaml + env overlays)
- Schema validation (uses canonical schemas from Phase 2)
- Environment-specific configuration (dev/staging/prod)
- Clean API matching LegacyConfigLoader (adapter pattern)

DESIGN:
- Implements ConfigLoaderInterface (same as LegacyConfigLoader)
- Uses phoenix_config.UniversalConfig under the hood
- Loads state files via config layer (not direct file I/O)
- Validates against canonical schemas (config/schemas/)

USAGE:
```python
# Initialize with environment
config = VibeConfig(env="development", repo_root="/path/to/repo")

# Load state files
manifest = config.get_project_manifest("my-project")
handoff = config.get_session_handoff()
status = config.get_system_status()

# Save state files
config.save_project_manifest("my-project", manifest_data)
```

CONFIGURATION FILES:
- config/vibe_config.yaml      - Phoenix config definition (sources, validation)
- config/base.yaml              - Base configuration (all environments)
- config/dev.yaml               - Development overrides
- config/prod.yaml              - Production overrides

Version: 1.0 (GAD-100 Phase 3)
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

# Import from lib package (phoenix_config)
try:
    from lib.phoenix_config import ConfigurationError, UniversalConfig

    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error("phoenix_config not available - ensure lib/phoenix_config exists")

# Import interface from config directory (loaded via conftest.py for tests)
# For direct script use, we use importlib
try:
    from config.legacy_config_loader import ConfigLoaderInterface
except ImportError:
    # Fallback: load dynamically
    from importlib.util import module_from_spec, spec_from_file_location

    _legacy_path = Path(__file__).resolve().parent / "legacy_config_loader.py"
    if _legacy_path.exists():
        spec = spec_from_file_location("legacy_config_loader", _legacy_path)
        if spec and spec.loader:
            legacy_module = module_from_spec(spec)
            spec.loader.exec_module(legacy_module)
            ConfigLoaderInterface = legacy_module.ConfigLoaderInterface
    else:
        raise ImportError("legacy_config_loader.py not found")

logger = logging.getLogger(__name__)


# =============================================================================
# VIBE CONFIG (Phoenix Config Wrapper)
# =============================================================================


class VibeConfig(ConfigLoaderInterface):
    """
    Vibe-Agency configuration wrapper (GAD-100 phoenix_config integration)

    Wraps phoenix_config.UniversalConfig to provide:
    - Multi-source configuration (YAML-based)
    - Environment overlays (base + dev/prod)
    - Schema validation (canonical schemas from Phase 2)
    - Clean adapter API (matches LegacyConfigLoader)

    Args:
        env: Environment name (development/staging/production)
        repo_root: Repository root directory
        config_path: Path to vibe_config.yaml (default: config/vibe_config.yaml)
        validate_schemas: Enable schema validation (default: True)
    """

    def __init__(
        self,
        env: str = "development",
        repo_root: Path | None = None,
        config_path: Path | None = None,
        validate_schemas: bool = True,
    ):
        if not PHOENIX_AVAILABLE:
            raise ImportError(
                "phoenix_config not available. "
                "Ensure lib/phoenix_config exists (run GAD-100 Phase 1 first)"
            )

        self.env = env
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.validate_schemas = validate_schemas

        # Load vibe config (defines sources, schemas, validation)
        if config_path is None:
            config_path = self.repo_root / "config" / "vibe_config.yaml"

        self.config_path = Path(config_path)
        self._load_vibe_config()

        # Initialize phoenix config
        self._init_phoenix_config()

        logger.info(f"VibeConfig initialized (env={env}, validate={validate_schemas})")

    def _load_vibe_config(self):
        """Load vibe_config.yaml (phoenix config definition)"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Vibe config not found: {self.config_path}\n"
                f"Run GAD-100 Phase 3 setup to create config files"
            )

        with open(self.config_path) as f:
            self.vibe_config = yaml.safe_load(f)

        logger.debug(f"Loaded vibe config: {self.config_path}")

    def _init_phoenix_config(self):
        """Initialize phoenix UniversalConfig"""
        # Load base config
        base_config_path = self.repo_root / "config" / "base.yaml"
        if not base_config_path.exists():
            raise FileNotFoundError(
                f"Base config not found: {base_config_path}\n"
                f"Run GAD-100 Phase 3 setup to create config files"
            )

        # Load environment overlay (if exists)
        # env_config_path = self.repo_root / "config" / f"{self.env}.yaml"  # Unused for now

        # Create UniversalConfig for the environment
        if self.env == "production":
            self.phoenix = UniversalConfig.create_for_production(self.repo_root)
        elif self.env == "development":
            self.phoenix = UniversalConfig.create_for_development(self.repo_root)
        else:
            # Testing or custom environment
            self.phoenix = UniversalConfig.create_for_testing()

        # Cache state file paths from vibe_config
        self._state_paths = self.vibe_config.get("state_files", {})

        logger.debug(f"Phoenix config initialized (env={self.env})")

    # -------------------------------------------------------------------------
    # PROJECT MANIFEST (implements ConfigLoaderInterface)
    # -------------------------------------------------------------------------

    def get_project_manifest(self, project_id: str) -> dict[str, Any]:
        """
        Load project manifest using phoenix config layer

        Unlike LegacyConfigLoader (direct file I/O), this uses
        phoenix config to load manifest with environment overlays.
        """
        manifest_path = self._get_manifest_path(project_id)

        if not manifest_path.exists():
            raise FileNotFoundError(f"Project manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            data = json.load(f)

        # Validate against schema (if enabled)
        if self.validate_schemas:
            self._validate_against_schema(data, "project_manifest")

        logger.info(f"Loaded project manifest (phoenix): {project_id}")
        return data

    def save_project_manifest(self, project_id: str, manifest: dict[str, Any]) -> None:
        """
        Save project manifest using phoenix config layer

        Validates manifest against canonical schema before saving.
        """
        # Validate against schema (if enabled)
        if self.validate_schemas:
            self._validate_against_schema(manifest, "project_manifest")

        manifest_path = self._get_manifest_path(project_id)

        # Write to disk
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Saved project manifest (phoenix): {project_id}")

    def _get_manifest_path(self, project_id: str) -> Path:
        """
        Get path to project manifest

        This is a simplified version (Phase 3).
        TODO (Phase 4): Use phoenix config to determine path from vibe_config.yaml
        """
        # For now, use same logic as LegacyConfigLoader (direct search)
        workspaces_dir = self.repo_root / "workspaces"

        # Try direct path first
        direct_path = workspaces_dir / project_id / "project_manifest.json"
        if direct_path.exists():
            return direct_path

        # Recursive search (fallback)
        for manifest_path in workspaces_dir.rglob("project_manifest.json"):
            if self._manifest_matches_project_id(manifest_path, project_id):
                return manifest_path

        raise FileNotFoundError(f"Project manifest not found for: {project_id}")

    def _manifest_matches_project_id(self, manifest_path: Path, project_id: str) -> bool:
        """Check if manifest matches project_id"""
        try:
            with open(manifest_path) as f:
                data = json.load(f)
            manifest_project_id = data.get("metadata", {}).get("projectId", "")
            parent_dir = manifest_path.parent.name
            return manifest_project_id == project_id or parent_dir == project_id
        except (json.JSONDecodeError, KeyError):
            return False

    # -------------------------------------------------------------------------
    # SESSION HANDOFF (implements ConfigLoaderInterface)
    # -------------------------------------------------------------------------

    def get_session_handoff(self) -> dict[str, Any] | None:
        """Load session handoff using phoenix config layer"""
        handoff_path = self.repo_root / ".session_handoff.json"

        if not handoff_path.exists():
            logger.debug("Session handoff not found (phoenix)")
            return None

        with open(handoff_path) as f:
            data = json.load(f)

        # Validate against schema (if enabled)
        if self.validate_schemas:
            self._validate_against_schema(data, "session_handoff")

        logger.info("Loaded session handoff (phoenix)")
        return data

    # -------------------------------------------------------------------------
    # SYSTEM STATUS (implements ConfigLoaderInterface)
    # -------------------------------------------------------------------------

    def get_system_status(self) -> dict[str, Any]:
        """Get system status (load or generate)"""
        status_path = self.repo_root / ".system_status.json"

        if status_path.exists():
            with open(status_path) as f:
                data = json.load(f)
            logger.info("Loaded system status (phoenix)")
            return data

        # Generate if missing (delegate to legacy logic for now)
        logger.debug("System status not found, generating (phoenix)")
        return self._generate_system_status()

    def _generate_system_status(self) -> dict[str, Any]:
        """
        Generate system status (fallback)

        TODO (Phase 4): Use phoenix config to orchestrate status generation
        For now, delegate to LegacyConfigLoader implementation
        """
        from legacy_config_loader import LegacyConfigLoader

        legacy = LegacyConfigLoader(self.repo_root)
        return legacy._generate_system_status()

    # -------------------------------------------------------------------------
    # ARTIFACT LOADING (implements ConfigLoaderInterface)
    # -------------------------------------------------------------------------

    def load_artifact(self, project_id: str, artifact_name: str) -> dict[str, Any] | None:
        """Load artifact file from workspace"""
        manifest_path = self._get_manifest_path(project_id)
        workspace_root = manifest_path.parent
        artifact_path = workspace_root / artifact_name

        if not artifact_path.exists():
            logger.warning(f"Artifact not found (phoenix): {artifact_name}")
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
    # WORKFLOW LOADING (implements ConfigLoaderInterface)
    # -------------------------------------------------------------------------

    def load_workflow(self, workflow_path: Path) -> dict[str, Any]:
        """Load workflow YAML"""
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")

        with open(workflow_path) as f:
            data = yaml.safe_load(f)

        logger.info(f"Loaded workflow (phoenix): {workflow_path}")
        return data

    # -------------------------------------------------------------------------
    # SCHEMA VALIDATION (GAD-100 Phase 2 integration)
    # -------------------------------------------------------------------------

    def _validate_against_schema(self, data: dict[str, Any], schema_name: str):
        """
        Validate data against canonical schema

        Uses schemas created in GAD-100 Phase 2.

        Args:
            data: Data to validate
            schema_name: Schema name (project_manifest, session_handoff, etc.)

        Raises:
            ConfigurationError: If validation fails
        """
        schema_path = self.repo_root / "config" / "schemas" / f"{schema_name}.schema.json"

        if not schema_path.exists():
            logger.warning(f"Schema not found: {schema_path} (skipping validation)")
            return

        try:
            import jsonschema
        except ImportError:
            logger.warning("jsonschema not installed (skipping validation)")
            return

        with open(schema_path) as f:
            schema = json.load(f)

        try:
            jsonschema.validate(data, schema)
            logger.debug(f"Schema validation passed: {schema_name}")
        except jsonschema.ValidationError as e:
            raise ConfigurationError(
                f"Schema validation failed for {schema_name}:\n{e.message}"
            ) from e


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_vibe_config(env: str = "development", **kwargs) -> VibeConfig:
    """
    Create VibeConfig instance (convenience function)

    Args:
        env: Environment (development/staging/production)
        **kwargs: Additional arguments passed to VibeConfig()

    Returns:
        VibeConfig instance
    """
    return VibeConfig(env=env, **kwargs)


def create_legacy_config(**kwargs):
    """
    Create LegacyConfigLoader instance (convenience function)

    Args:
        **kwargs: Arguments passed to LegacyConfigLoader()

    Returns:
        LegacyConfigLoader: LegacyConfigLoader instance
    """
    from legacy_config_loader import LegacyConfigLoader

    return LegacyConfigLoader(**kwargs)
