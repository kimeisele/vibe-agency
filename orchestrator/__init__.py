"""Wrapper for orchestrator.core_orchestrator imports."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

_target = Path(__file__).parent.parent / "agency_os" / "00_system" / "orchestrator" / "core_orchestrator.py"
_spec = spec_from_file_location("core_orchestrator_shim", _target)
_mod = module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

CoreOrchestrator = _mod.CoreOrchestrator
ProjectPhase = _mod.ProjectPhase
PlanningSubState = _mod.PlanningSubState
ProjectManifest = _mod.ProjectManifest
ArtifactNotFoundError = _mod.ArtifactNotFoundError
SchemaValidator = _mod.SchemaValidator
KernelViolationError = _mod.KernelViolationError

__all__ = [
    "CoreOrchestrator",
    "ProjectPhase",
    "PlanningSubState",
    "ProjectManifest",
    "ArtifactNotFoundError",
    "SchemaValidator",
    "KernelViolationError",
]
