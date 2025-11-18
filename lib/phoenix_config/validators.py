"""
Universal Configuration Validation

Configuration validation utilities and error definitions.
"""

from typing import Any

from .config_classes import APIConfig, DatabaseConfig, LoggingConfig


class ConfigurationError(Exception):
    """Raised when configuration validation fails or configuration cannot be loaded."""

    def __init__(
        self,
        message: str,
        config_path: str | None = None,
        validation_errors: list[str] | None = None,
        **kwargs,
    ):
        super().__init__(message)
        self.message = message
        self.config_path = config_path
        self.validation_errors = validation_errors or []

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "config_path": self.config_path,
            "validation_errors": self.validation_errors,
        }


def validate_database_config(config: DatabaseConfig) -> list[str]:
    """Validate database configuration."""
    errors = []

    if not config.url:
        errors.append("Database URL is required")

    if config.pool_size <= 0:
        errors.append("Database pool_size must be positive")

    if config.max_overflow < 0:
        errors.append("Database max_overflow cannot be negative")

    return errors


def validate_api_config(config: APIConfig) -> list[str]:
    """Validate API configuration."""
    errors = []

    if config.port < 1 or config.port > 65535:
        errors.append("API port must be between 1 and 65535")

    if config.workers < 1:
        errors.append("API workers must be at least 1")

    return errors


def validate_logging_config(config: LoggingConfig) -> list[str]:
    """Validate logging configuration."""
    errors = []

    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.level.upper() not in valid_levels:
        errors.append(f"Log level must be one of: {valid_levels}")

    valid_formats = ["json", "console", "structured"]
    if config.format not in valid_formats:
        errors.append(f"Log format must be one of: {valid_formats}")

    if config.max_file_size <= 0:
        errors.append("Log max_file_size must be positive")

    return errors
