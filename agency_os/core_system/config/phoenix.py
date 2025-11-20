#!/usr/bin/env python3
"""
GAD-100: Phoenix Configuration System
======================================

Unified configuration management for vibe-agency.

This module centralizes all system configuration, replacing:
- os.getenv() calls scattered throughout codebase
- Pydantic-based BaseSettings for strict typing
- Environment-based override capability
- Self-documenting configuration schema

Key sections:
- System: Core operational parameters
- Paths: File system locations
- Quotas: Rate limiting and cost controls
- Safety: Execution modes and guardrails

Usage:
    from agency_os.config import get_config
    config = get_config()

    # Access config safely
    live_fire = config.safety.live_fire_enabled
    rpm_limit = config.quotas.requests_per_minute
    home_dir = config.paths.home

Design Principles:
1. Single source of truth for all configuration
2. Strict typing via Pydantic (validation on load)
3. Environment variable override support
4. Safe defaults (conservative quotas, no live fire)
5. Self-documenting (every field has a description)

Version: 1.0 (GAD-100)
"""

import logging
from pathlib import Path

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class SystemConfig(BaseSettings):
    """Core system operational parameters"""

    environment: str = "development"
    """Execution environment: development, staging, production"""

    debug: bool = False
    """Enable debug logging and verbose output"""

    log_level: str = "INFO"
    """Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"""

    class Config:
        env_prefix = "VIBE_SYSTEM_"
        case_sensitive = False


class PathsConfig(BaseSettings):
    """File system paths used by the system"""

    home: Path = Path.home() / ".vibe"
    """Home directory for vibe data (user config, cache, etc.)"""

    project_root: Path = Path(__file__).parent.parent.parent.parent
    """Project root directory"""

    agency_os: Path = Path(__file__).parent.parent
    """agency_os module directory"""

    data_dir: Path = Path.home() / ".vibe" / "data"
    """Data directory for persistent storage"""

    cache_dir: Path = Path.home() / ".vibe" / "cache"
    """Cache directory for temporary data"""

    logs_dir: Path = Path.home() / ".vibe" / "logs"
    """Logs directory"""

    class Config:
        env_prefix = "VIBE_PATH_"
        case_sensitive = False


class QuotaConfig(BaseSettings):
    """Operational quota limits and controls"""

    requests_per_minute: int = 10
    """Maximum requests per minute (RPM limit)"""

    tokens_per_minute: int = 10000
    """Maximum tokens per minute (TPM limit)"""

    concurrent_requests: int = 10
    """Maximum concurrent parallel requests"""

    cost_per_request_usd: float = 0.50
    """Alert/block if single request exceeds this cost (USD)"""

    cost_per_hour_usd: float = 2.0
    """Maximum hourly cost limit (USD)"""

    cost_per_day_usd: float = 5.0
    """Maximum daily cost limit (USD)"""

    class Config:
        env_prefix = "VIBE_QUOTA_"
        case_sensitive = False

    @staticmethod
    def _parse_env_var(value: str, field_type: type) -> object:
        """Custom parser for environment variables"""
        if field_type is int:
            return int(value)
        elif field_type is float:
            return float(value)
        return value


class SafetyConfig(BaseSettings):
    """Safety controls and execution modes"""

    live_fire_enabled: bool = False
    """DANGER: Enable live execution (real tokens, real cost)

    When False (default): All agent executions are mocked (0 cost)
    When True: Real agent execution with real API calls and billing

    ONLY enable for authorized production deployments.
    """

    enable_quota_enforcement: bool = True
    """Enforce quota limits before request execution"""

    enable_cost_tracking: bool = True
    """Track and report API costs"""

    max_single_request_cost_usd: float = 1.0
    """Absolute maximum cost for any single request (USD)"""

    enable_audit_logging: bool = True
    """Log all requests and results for audit trail"""

    class Config:
        env_prefix = "VIBE_SAFETY_"
        case_sensitive = False


class PhoenixConfig(BaseSettings):
    """
    Master configuration for vibe-agency.

    Loads from environment variables with safe defaults.
    Provides centralized access to all system configuration.
    """

    system: SystemConfig = SystemConfig()
    """System-level configuration"""

    paths: PathsConfig = PathsConfig()
    """File system paths"""

    quotas: QuotaConfig = QuotaConfig()
    """Rate limiting and cost controls"""

    safety: SafetyConfig = SafetyConfig()
    """Execution modes and safety guardrails"""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def validate_configuration(self) -> tuple[bool, list[str]]:
        """
        Validate configuration for consistency and safety.

        Returns:
            (is_valid: bool, issues: list[str])
        """
        issues = []

        # Check path consistency
        if not self.paths.project_root.exists():
            issues.append(f"Project root does not exist: {self.paths.project_root}")

        # Check quota sanity
        if self.quotas.requests_per_minute < 1:
            issues.append("requests_per_minute must be >= 1")

        if self.quotas.tokens_per_minute < 100:
            issues.append("tokens_per_minute must be >= 100")

        if self.quotas.cost_per_hour_usd < 0.1:
            issues.append("cost_per_hour_usd must be >= $0.1")

        if self.quotas.cost_per_day_usd < 0.5:
            issues.append("cost_per_day_usd must be >= $0.5")

        # Check cost consistency
        if self.quotas.cost_per_hour_usd > self.quotas.cost_per_day_usd:
            issues.append("hourly cost limit should not exceed daily limit")

        # Safety warning for live fire
        if self.safety.live_fire_enabled:
            logger.warning(
                "🔥 LIVE FIRE ENABLED: Real API calls are active. "
                "This will incur actual costs. Ensure authorization."
            )

        return (len(issues) == 0, issues)

    def to_dict(self) -> dict:
        """Export configuration as dictionary"""
        return {
            "system": self.system.model_dump(),
            "paths": {
                k: str(v) if isinstance(v, Path) else v for k, v in self.paths.model_dump().items()
            },
            "quotas": self.quotas.model_dump(),
            "safety": self.safety.model_dump(),
        }


# Global singleton instance
_config: PhoenixConfig | None = None


def get_config() -> PhoenixConfig:
    """
    Get or create the global Phoenix configuration instance.

    This is a lazy-loading singleton. The first call initializes
    the config from environment variables, subsequent calls return
    the cached instance.

    Returns:
        PhoenixConfig: The global configuration instance
    """
    global _config
    if _config is None:
        _config = PhoenixConfig()
        is_valid, issues = _config.validate_configuration()

        if not is_valid:
            logger.warning(f"Configuration validation issues: {issues}")

        logger.debug(f"Phoenix configuration loaded: {_config.system.environment}")

    return _config


def reset_config() -> None:
    """Reset the global configuration (for testing)"""
    global _config
    _config = None


if __name__ == "__main__":
    # Test configuration loading

    config = get_config()
    is_valid, issues = config.validate_configuration()

    print("Phoenix Configuration System")
    print("=" * 60)
    print(f"\nEnvironment: {config.system.environment}")
    print(f"Debug: {config.system.debug}")
    print(f"Log Level: {config.system.log_level}")

    print("\n📁 Paths:")
    print(f"  Home: {config.paths.home}")
    print(f"  Project Root: {config.paths.project_root}")
    print(f"  Data Dir: {config.paths.data_dir}")

    print("\n⚡ Quotas:")
    print(f"  RPM: {config.quotas.requests_per_minute}")
    print(f"  TPM: {config.quotas.tokens_per_minute}")
    print(f"  Hourly Limit: ${config.quotas.cost_per_hour_usd}")
    print(f"  Daily Limit: ${config.quotas.cost_per_day_usd}")

    print("\n🔐 Safety:")
    print(f"  Live Fire Enabled: {config.safety.live_fire_enabled}")
    print(f"  Quota Enforcement: {config.safety.enable_quota_enforcement}")
    print(f"  Cost Tracking: {config.safety.enable_cost_tracking}")
    print(f"  Audit Logging: {config.safety.enable_audit_logging}")

    print(f"\n✅ Configuration Valid: {is_valid}")
    if issues:
        print("⚠️  Issues Found:")
        for issue in issues:
            print(f"  - {issue}")

    print("\n" + "=" * 60)
