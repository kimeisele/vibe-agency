"""Top-level orchestrator alias module to eliminate test-time sys.path hacks.

Loads underlying modules from agency_os/00_system/orchestrator using importlib
without modifying sys.path, exposing key classes for direct import:
    from agency_os_orchestrator import CoreOrchestrator, ProjectPhase, PlanningSubState
Also exposes ToolExecutor and clients when available.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_ORCH_DIR = Path(__file__).resolve().parent / "agency_os" / "00_system" / "orchestrator"


def _load(filename: str, alias: str):
    path = _ORCH_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing orchestrator component: {filename}")
    spec = spec_from_file_location(alias, path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


# Core orchestrator
_core = _load("core_orchestrator.py", "core_orchestrator_original")
CoreOrchestrator = _core.CoreOrchestrator
ProjectPhase = _core.ProjectPhase
PlanningSubState = _core.PlanningSubState
ArtifactNotFoundError = _core.ArtifactNotFoundError
SchemaValidator = _core.SchemaValidator
ProjectManifest = _core.ProjectManifest
KernelViolationError = _core.KernelViolationError
PROMPT_REGISTRY_AVAILABLE = getattr(_core, "PROMPT_REGISTRY_AVAILABLE", False)

# Optional tool layer
try:
    _tools = _load("tools/tool_executor.py", "tool_executor_original")
    ToolExecutor = _tools.ToolExecutor  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - non critical
    ToolExecutor = None  # type: ignore[assignment]

__all__ = [
    "ArtifactNotFoundError",
    "CoreOrchestrator",
    "PlanningSubState",
    "ProjectPhase",
    "SchemaValidator",
    "ToolExecutor",
]
