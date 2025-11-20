"""
Vibe Core Configuration Module

Exports the Phoenix configuration system for use across Vibe OS and applications.
"""

from .phoenix import PhoenixConfig, get_config, reset_config

__all__ = ["PhoenixConfig", "get_config", "reset_config"]
