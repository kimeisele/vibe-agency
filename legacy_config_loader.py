"""Import shim: LegacyConfigLoader from config package."""
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

_config_loader = Path(__file__).parent / "config" / "legacy_config_loader.py"
_spec = spec_from_file_location("legacy_config_loader_orig", _config_loader)
_config_module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_config_module)

LegacyConfigLoader = _config_module.LegacyConfigLoader
ConfigLoaderInterface = _config_module.ConfigLoaderInterface

__all__ = ["LegacyConfigLoader", "ConfigLoaderInterface"]
