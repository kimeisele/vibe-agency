"""
Core SDLC Orchestrator Package
===============================

GAD-002 Phase 3 Implementation

This package contains the hierarchical orchestrator architecture:
- core_orchestrator.py: Master orchestrator (state machine, transitions)
- handlers/: Phase-specific handlers (PLANNING, CODING, TESTING, etc.)
"""

from .core_orchestrator import (
    ArtifactNotFoundError,
    CoreOrchestrator,
    KernelViolationError,
    PROMPT_REGISTRY_AVAILABLE,
    PlanningSubState,
    ProjectManifest,
    ProjectPhase,
    SchemaValidator,
)

__all__ = [
    "ArtifactNotFoundError",
    "CoreOrchestrator",
    "KernelViolationError",
    "PROMPT_REGISTRY_AVAILABLE",
    "PlanningSubState",
    "ProjectManifest",
    "ProjectPhase",
    "SchemaValidator",
]
