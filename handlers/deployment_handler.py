"""Wrapper for legacy import 'from handlers.deployment_handler import DeploymentHandler'."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_target = (
    Path(__file__).resolve().parent.parent
    / "agency_os"
    / "00_system"
    / "orchestrator"
    / "handlers"
    / "deployment_handler.py"
)
_spec = spec_from_file_location("deployment_handler_original", _target)
module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(module)  # type: ignore
DeploymentHandler = module.DeploymentHandler
__all__ = ["DeploymentHandler"]
