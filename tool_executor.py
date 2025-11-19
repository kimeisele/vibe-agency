"""Alias shim for ToolExecutor."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_path = (
    Path(__file__).resolve().parent
    / "agency_os"
    / "00_system"
    / "orchestrator"
    / "tools"
    / "tool_executor.py"
)
_spec = spec_from_file_location("tool_executor_original", _path)
module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(module)  # type: ignore
ToolExecutor = module.ToolExecutor
__all__ = ["ToolExecutor"]
