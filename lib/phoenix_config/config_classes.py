"""
Universal Configuration Classes

Individual configuration dataclasses for different system components.
These are designed to be reusable across different types of applications.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///app.db"))
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    auto_create_tables: bool = True


@dataclass
class ShellConfig:
    """Shell command execution configuration."""

    timeout: int = 60
    max_output_lines: int = 1000
    respect_gitignore: bool = True
    filesystem_sync_delay: float = 0.1
    check_process_completion: bool = True
    retry_on_timeout: bool = False
    max_retries: int = 0
    ensure_output_completeness: bool = True


@dataclass
class LoggingConfig:
    """Structured logging configuration."""

    level: str = "INFO"
    format: str = "json"  # json, console, or structured
    include_timestamp: bool = True
    include_logger_name: bool = True
    include_log_level: bool = True
    include_stack_info: bool = False
    log_file: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class SecurityConfig:
    """Security and compliance configuration."""

    enable_constitutional_validation: bool = True
    enable_session_persistence: bool = True
    audit_log_retention_days: int = 90
    max_session_duration_hours: int = 24
    enable_input_sanitization: bool = True


@dataclass
class PerformanceConfig:
    """Performance and optimization settings."""

    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    max_concurrent_operations: int = 10
    enable_parallel_processing: bool = True
    max_worker_threads: int = 4


@dataclass
class APIConfig:
    """API server configuration."""

    host: str = field(default_factory=lambda: os.getenv("API_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    workers: int = 1
    reload: bool = False
    access_log: bool = True
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class CacheConfig:
    """Cache configuration."""

    backend: str = "memory"  # memory, redis, memcached
    url: Optional[str] = None
    ttl_seconds: int = 300
    max_size: int = 1000
    prefix: str = "app"


@dataclass
class TaskConfig:
    """Background task configuration."""

    max_workers: int = 4
    queue_size: int = 1000
    retry_attempts: int = 3
    retry_delay_seconds: int = 60
    timeout_seconds: int = 300
