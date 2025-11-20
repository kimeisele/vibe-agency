#!/usr/bin/env python3
"""
Shared types for the orchestrator and agents

This module contains enums and data structures that are shared between
the orchestrator and specialist agents. By extracting these into a separate
module, we avoid circular import dependencies.

Extracted from: core_orchestrator.py (to break circular imports)
"""

from enum import Enum


class ProjectPhase(Enum):
    """SDLC lifecycle phases"""

    PLANNING = "PLANNING"
    CODING = "CODING"
    TESTING = "TESTING"
    AWAITING_QA_APPROVAL = "AWAITING_QA_APPROVAL"
    DEPLOYMENT = "DEPLOYMENT"
    PRODUCTION = "PRODUCTION"
    MAINTENANCE = "MAINTENANCE"


class PlanningSubState(Enum):
    """Planning phase sub-states"""

    RESEARCH = "RESEARCH"
    BUSINESS_VALIDATION = "BUSINESS_VALIDATION"
    FEATURE_SPECIFICATION = "FEATURE_SPECIFICATION"
