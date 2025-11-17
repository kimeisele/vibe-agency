"""
Universal Configuration Package

Professional-grade configuration system for any Python application.
Provides centralized, validated, environment-specific configuration.
"""

from .core import UniversalConfig
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
from .loaders import ConfigLoader
from .validators import ConfigurationError

__all__ = [
    "UniversalConfig",
    "DatabaseConfig",
    "APIConfig",
    "ShellConfig",
    "LoggingConfig",
    "SecurityConfig",
    "PerformanceConfig",
    "CacheConfig",
    "TaskConfig",
    "ConfigLoader",
    "ConfigurationError",
]


# Convenience functions for backward compatibility
def load_config(config_path=None):
    """Load configuration from file or environment."""
    if config_path:
        return ConfigLoader.from_file(config_path)
    return ConfigLoader.from_env()


def create_default_config():
    """Create default configuration."""
    return UniversalConfig.create_default()


def create_production_config(project_root=None):
    """Create production configuration."""
    return UniversalConfig.create_for_production(project_root)


def create_development_config(project_root):
    """Create development configuration."""
    return UniversalConfig.create_for_development(project_root)


def create_test_config(**overrides):
    """Create test configuration."""
    return UniversalConfig.create_for_testing(**overrides)
