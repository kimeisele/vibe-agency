"""Top-level import shim for CoreOrchestrator (minimal, no hacks)."""
import sys
from pathlib import Path

_orchestrator_path = Path(__file__).parent / "agency_os" / "00_system" / "orchestrator"
sys.path.insert(0, str(_orchestrator_path))

from core_orchestrator import (
    CoreOrchestrator,
    ProjectPhase,
    PlanningSubState,
    ProjectManifest,
    ArtifactNotFoundError,
    SchemaValidator,
    KernelViolationError,
)

sys.path.pop(0)

__all__ = [
    "CoreOrchestrator",
    "ProjectPhase",
    "PlanningSubState",
    "ProjectManifest",
    "ArtifactNotFoundError",
    "SchemaValidator",
    "KernelViolationError",
]
