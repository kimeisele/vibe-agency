"""
Universal Configuration Loading

Configuration loading utilities for YAML files and environment variables.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Union

import yaml

from .validators import ConfigurationError

if TYPE_CHECKING:
    from .core import UniversalConfig


class ConfigLoader:
    """Universal configuration loader."""

    @staticmethod
    def from_file(config_path: Union[str, Path]) -> "UniversalConfig":
        """Load configuration from YAML file."""
        config_path = Path(config_path)

        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Error reading config file: {e}") from e

        return ConfigLoader._from_dict(data)

    @staticmethod
    def from_env() -> "UniversalConfig":
        """Load configuration from environment variables."""
        config_data = {
            "environment": os.getenv("APP_ENV", "production"),
            "project_root": os.getenv("APP_PROJECT_ROOT", str(Path.cwd())),
            "database": {
                "url": os.getenv("DATABASE_URL"),
                "echo": os.getenv("DB_ECHO", "false").lower() == "true",
                "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
            },
            "api": {
                "host": os.getenv("API_HOST", "localhost"),
                "port": int(os.getenv("API_PORT", "8000")),
                "debug": os.getenv("DEBUG", "false").lower() == "true",
                "workers": int(os.getenv("API_WORKERS", "1")),
            },
            "shell": {
                "timeout": int(os.getenv("SHELL_TIMEOUT", "60")),
                "max_output_lines": int(os.getenv("MAX_OUTPUT_LINES", "1000")),
                "respect_gitignore": os.getenv("RESPECT_GITIGNORE", "true").lower() == "true",
            },
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "format": os.getenv("LOG_FORMAT", "json"),
                "log_file": os.getenv("LOG_FILE"),
            },
            "security": {
                "enable_session_persistence": os.getenv("ENABLE_SESSIONS", "true").lower()
                == "true",
                "audit_log_retention_days": int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "90")),
            },
            "performance": {
                "enable_caching": os.getenv("ENABLE_CACHING", "true").lower() == "true",
                "max_concurrent_operations": int(os.getenv("MAX_CONCURRENT", "10")),
            },
            "cache": {
                "backend": os.getenv("CACHE_BACKEND", "memory"),
                "url": os.getenv("CACHE_URL"),
                "ttl_seconds": int(os.getenv("CACHE_TTL", "300")),
            },
            "task": {
                "max_workers": int(os.getenv("TASK_MAX_WORKERS", "4")),
                "queue_size": int(os.getenv("TASK_QUEUE_SIZE", "1000")),
                "retry_attempts": int(os.getenv("TASK_RETRY_ATTEMPTS", "3")),
            },
        }

        return ConfigLoader._from_dict(config_data)

    @staticmethod
    def _from_dict(data: Dict[str, Any]) -> "UniversalConfig":
        """Create configuration from dictionary data."""
        from .config_classes import (
            DatabaseConfig,
            APIConfig,
            ShellConfig,
            LoggingConfig,
            SecurityConfig,
            PerformanceConfig,
            CacheConfig,
            TaskConfig,
        )
        from .core import UniversalConfig

        # Extract component configs
        database_data = data.get("database", {})
        api_data = data.get("api", {})
        shell_data = data.get("shell", {})
        logging_data = data.get("logging", {})
        security_data = data.get("security", {})
        performance_data = data.get("performance", {})
        cache_data = data.get("cache", {})
        task_data = data.get("task", {})

        # Create component configs
        database = DatabaseConfig(**database_data)
        api = APIConfig(**api_data)
        shell = ShellConfig(**shell_data)
        logging = LoggingConfig(**logging_data)
        security = SecurityConfig(**security_data)
        performance = PerformanceConfig(**performance_data)
        cache = CacheConfig(**cache_data)
        task = TaskConfig(**task_data)

        # Create main config
        config_file_path = data.get("config_file")
        config = UniversalConfig(
            environment=data.get("environment", "production"),
            project_root=Path(data.get("project_root", Path.cwd())),
            config_file=Path(config_file_path) if config_file_path else None,
            database=database,
            api=api,
            shell=shell,
            logging=logging,
            security=security,
            performance=performance,
            cache=cache,
            task=task,
        )

        return config
