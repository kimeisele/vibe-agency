"""
Specialist Agents - HAP Framework (Hierarchical Agent Pattern)
================================================================

Base classes and registry for phase-specific specialist agents.

Classes:
  - BaseSpecialist: Abstract base class for all specialists
  - AgentRegistry: Global registry for specialist instances
"""

from .base_specialist import BaseSpecialist, MissionContext, SpecialistResult
from .registry import AgentRegistry

__all__ = [
    "AgentRegistry",
    "BaseSpecialist",
    "MissionContext",
    "SpecialistResult",
]
