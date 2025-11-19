"""Alias shim for PromptRegistry."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_path = (
    Path(__file__).resolve().parent / "agency_os" / "00_system" / "runtime" / "prompt_registry.py"
)
_spec = spec_from_file_location("prompt_registry_original", _path)
module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(module)  # type: ignore
PromptRegistry = module.PromptRegistry
__all__ = ["PromptRegistry"]
