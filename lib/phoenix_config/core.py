"""
Universal Configuration Core

Core configuration classes and constants for universal application configuration.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

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
from .validators import (
    ConfigurationError,
    validate_database_config,
    validate_api_config,
    validate_logging_config,
)


@dataclass
class UniversalConfig:
    """
    Universal configuration system for any Python application.

    Manages settings for all major components with validation,
    environment variable support, and YAML file loading.
    """

    # Environment identification
    environment: str = "production"

    # Core paths
    project_root: Path = field(default_factory=Path.cwd)
    config_file: Optional[Path] = None

    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    shell: ShellConfig = field(default_factory=ShellConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    task: TaskConfig = field(default_factory=TaskConfig)

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration values."""
        errors = []

        # Environment validation
        if self.environment not in ["production", "development", "test"]:
            errors.append("environment must be one of: production, development, test")

        # Component validation
        errors.extend(validate_database_config(self.database))
        errors.extend(validate_api_config(self.api))
        errors.extend(validate_logging_config(self.logging))

        # Shell validation
        if self.shell.timeout <= 0:
            errors.append("shell.timeout must be positive")
        if self.shell.max_output_lines <= 0:
            errors.append("shell.max_output_lines must be positive")
        if self.shell.max_retries < 0:
            errors.append("shell.max_retries must be non-negative")

        # Performance validation
        if self.performance.max_concurrent_operations <= 0:
            errors.append("performance.max_concurrent_operations must be positive")
        if self.performance.max_worker_threads <= 0:
            errors.append("performance.max_worker_threads must be positive")

        # Cache validation
        if self.cache.ttl_seconds <= 0:
            errors.append("cache.ttl_seconds must be positive")
        if self.cache.max_size <= 0:
            errors.append("cache.max_size must be positive")

        # Task validation
        if self.task.max_workers <= 0:
            errors.append("task.max_workers must be positive")
        if self.task.queue_size <= 0:
            errors.append("task.queue_size must be positive")
        if self.task.retry_attempts < 0:
            errors.append("task.retry_attempts must be non-negative")

        if errors:
            raise ConfigurationError(
                "Configuration validation failed",
                config_path=str(self.config_file) if self.config_file else None,
                validation_errors=errors,
            )

    @classmethod
    def create_default(cls) -> "UniversalConfig":
        """Create default configuration."""
        return cls()

    @classmethod
    def create_for_production(cls, project_root: Optional[Path] = None) -> "UniversalConfig":
        """Create production-optimized configuration."""
        return cls(
            environment="production",
            project_root=project_root or Path.cwd(),
            logging=LoggingConfig(level="INFO", format="json"),
            api=APIConfig(debug=False, workers=4),
            performance=PerformanceConfig(
                enable_caching=True, max_concurrent_operations=20, max_worker_threads=8
            ),
        )

    @classmethod
    def create_for_development(cls, project_root: Path) -> "UniversalConfig":
        """Create development-optimized configuration."""
        return cls(
            environment="development",
            project_root=project_root,
            logging=LoggingConfig(level="DEBUG", format="console"),
            api=APIConfig(debug=True, reload=True),
            database=DatabaseConfig(echo=True),
        )

    @classmethod
    def create_for_testing(cls, **overrides) -> "UniversalConfig":
        """Create testing-optimized configuration."""
        test_config = cls(
            environment="test",
            logging=LoggingConfig(level="WARNING"),
            database=DatabaseConfig(url="sqlite:///:memory:"),
            performance=PerformanceConfig(enable_caching=False),
            cache=CacheConfig(backend="memory"),
        )

        # Apply any overrides
        for key, value in overrides.items():
            if hasattr(test_config, key):
                setattr(test_config, key, value)

        return test_config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment,
            "project_root": str(self.project_root),
            "config_file": str(self.config_file) if self.config_file else None,
            "database": self.database.__dict__,
            "api": self.api.__dict__,
            "shell": self.shell.__dict__,
            "logging": self.logging.__dict__,
            "security": self.security.__dict__,
            "performance": self.performance.__dict__,
            "cache": self.cache.__dict__,
            "task": self.task.__dict__,
        }

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        file_path = Path(file_path)

        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> "UniversalConfig":
        """Load configuration from YAML file."""
        from .loaders import ConfigLoader

        return ConfigLoader.from_file(file_path)

    @classmethod
    def load_from_env(cls) -> "UniversalConfig":
        """Load configuration from environment variables."""
        from .loaders import ConfigLoader

        return ConfigLoader.from_env()

    def get_database_url(self) -> str:
        """Get database URL with environment variable substitution."""
        url = self.database.url
        if url and "${" in url:
            # Simple environment variable substitution
            import re

            def replace_env_var(match):
                var_name = match.group(1)
                return os.getenv(var_name, match.group(0))

            url = re.sub(r"\$\{([^}]+)\}", replace_env_var, url)
        return url

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.environment == "test"
