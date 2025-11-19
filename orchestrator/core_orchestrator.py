"""Compatibility wrapper for legacy import 'from orchestrator.core_orchestrator import CoreOrchestrator'."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_target = (
    Path(__file__).resolve().parent.parent
    / "agency_os"
    / "00_system"
    / "orchestrator"
    / "core_orchestrator.py"
)
_spec = spec_from_file_location("core_orchestrator_original", _target)
module = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(module)  # type: ignore
CoreOrchestrator = module.CoreOrchestrator
ProjectPhase = module.ProjectPhase
PlanningSubState = module.PlanningSubState
ProjectManifest = module.ProjectManifest
ArtifactNotFoundError = module.ArtifactNotFoundError
SchemaValidator = module.SchemaValidator
KernelViolationError = module.KernelViolationError
__all__ = [
    "ArtifactNotFoundError",
    "CoreOrchestrator",
    "KernelViolationError",
    "PlanningSubState",
    "ProjectManifest",
    "ProjectPhase",
    "SchemaValidator",
]
