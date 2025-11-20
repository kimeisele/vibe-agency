#!/usr/bin/env python3
"""
Specialists Package - ARCH-008
Hierarchical Agent Pattern (HAP) specialist agents

Contains phase-specific specialist agents for all SDLC phases:
    - CodingSpecialist: CODING phase workflow (5-phase sequential)
    - TestingSpecialist: TESTING phase workflow (QA validation)
    - DeploymentSpecialist: DEPLOYMENT phase workflow (4-phase sequential)
    - MaintenanceSpecialist: MAINTENANCE phase workflow (monitoring)
"""

from .coding import CodingSpecialist
from .deployment import DeploymentSpecialist
from .maintenance import MaintenanceSpecialist
from .testing import TestingSpecialist

__all__ = [
    "CodingSpecialist",
    "DeploymentSpecialist",
    "MaintenanceSpecialist",
    "TestingSpecialist",
]
