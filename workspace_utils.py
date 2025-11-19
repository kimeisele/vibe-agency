"""Alias shim for workspace_utils used by PromptRegistry."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_path = Path(__file__).resolve().parent / "scripts" / "workspace_utils.py"
_spec = spec_from_file_location("workspace_utils_original", _path)
module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(module)  # type: ignore
get_active_workspace = getattr(module, "get_active_workspace", None)
load_workspace_manifest = getattr(module, "load_workspace_manifest", None)
resolve_manifest_path = getattr(module, "resolve_manifest_path", None)
__all__ = ["get_active_workspace", "load_workspace_manifest", "resolve_manifest_path"]
