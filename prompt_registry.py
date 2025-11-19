"""Import shim: PromptRegistry."""
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

_path = Path(__file__).parent / "agency_os" / "00_system" / "runtime" / "prompt_registry.py"
_spec = spec_from_file_location("prompt_registry_orig", _path)
_mod = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

PromptRegistry = _mod.PromptRegistry
__all__ = ["PromptRegistry"]
