#!/usr/bin/env python3
"""
Specialists Package - ARCH-007
Hierarchical Agent Pattern (HAP) specialist agents

Contains phase-specific specialist agents:
    - CodingSpecialist: CODING phase workflow
    - (More specialists to be added as HAP pattern scales)
"""

from .coding import CodingSpecialist

__all__ = ["CodingSpecialist"]
