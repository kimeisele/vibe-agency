"""Wrapper for legacy import 'from handlers.planning_handler import PlanningHandler'."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_target = (
    Path(__file__).resolve().parent.parent
    / "agency_os"
    / "00_system"
    / "orchestrator"
    / "handlers"
    / "planning_handler.py"
)
_spec = spec_from_file_location("planning_handler_original", _target)
module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(module)  # type: ignore
PlanningHandler = module.PlanningHandler
__all__ = ["PlanningHandler"]
