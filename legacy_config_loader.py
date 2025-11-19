"""Alias shim mapping LegacyConfigLoader import to new implementation location.

Tests still import legacy_config_loader.LegacyConfigLoader. This forwards to config.legacy_config_loader.
"""

from importlib import import_module

_mod = import_module("config.legacy_config_loader")
LegacyConfigLoader = _mod.LegacyConfigLoader
ConfigLoaderInterface = getattr(_mod, "ConfigLoaderInterface", None)
__all__ = ["ConfigLoaderInterface", "LegacyConfigLoader"]
