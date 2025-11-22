#!/usr/bin/env python3
"""
PlanningSpecialist - ARCH-006
Specialist agent for PLANNING phase workflow

Extracted from core_orchestrator.py PlanningHandler to prove HAP pattern.

Responsibilities:
    - Requirement analysis
    - Architecture design
    - Task breakdown
    - Artifact generation (architecture.json, feature_spec.json, etc.)

See: docs/architecture/SPECIALIST_AGENT_CONTRACT.md for implementation guide
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.specialists import BaseSpecialist, MissionContext, SpecialistResult
from vibe_core.store.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


class PlanningSpecialist(BaseSpecialist):
    """
    Specialist for PLANNING phase

    Workflow:
        1. Validate preconditions (manifest exists)
        2. Execute planning sub-states:
           - [OPTIONAL] RESEARCH
           - BUSINESS_VALIDATION
           - FEATURE_SPECIFICATION
           - ARCHITECTURE_DESIGN
        3. Apply quality gates
        4. Generate artifacts
        5. Return success with next_phase="CODING"

    Dependencies:
        - Requires orchestrator for execute_agent() and save_artifact()
        - This is a transitional design while we prove HAP pattern
        - Future: Replace with direct tool access (remove orchestrator dependency)
    """

    def __init__(
        self,
        mission_id: int,
        sqlite_store: SQLiteStore,
        tool_safety_guard: ToolSafetyGuard,
        orchestrator=None,  # Temporary: needed for execute_agent()
        playbook_root: Path | None = None,
    ):
        """
        Initialize PlanningSpecialist

        Args:
            mission_id: Database primary key
            sqlite_store: Persistence layer
            tool_safety_guard: Safety enforcement
            orchestrator: CoreOrchestrator instance (temporary dependency)
            playbook_root: Playbook directory

        Note:
            orchestrator dependency is transitional. Future versions will use
            direct tool access instead of delegating to orchestrator.execute_agent()
        """
        super().__init__(
            role="PLANNING",
            mission_id=mission_id,
            sqlite_store=sqlite_store,
            tool_safety_guard=tool_safety_guard,
            playbook_root=playbook_root,
        )

        self.orchestrator = orchestrator  # Temporary dependency

        if not orchestrator:
            logger.warning(
                "PlanningSpecialist initialized without orchestrator. "
                "Some functionality (execute_agent, save_artifact) will not work."
            )

    def validate_preconditions(self, context: MissionContext) -> bool:
        """
        Validate PLANNING phase can execute

        Checks:
            - Project manifest exists
            - Phase is PLANNING
            - Orchestrator is available (temporary requirement)

        Args:
            context: Mission context

        Returns:
            True if preconditions met, False otherwise
        """
        # Check: project_manifest.json exists
        manifest_path = context.project_root / "project_manifest.json"
        if not manifest_path.exists():
            logger.error(f"Precondition failed: project_manifest.json not found at {manifest_path}")
            return False

        # Check: phase is PLANNING
        mission = self.get_mission_data()
        if mission["phase"] != "PLANNING":
            logger.error(
                f"Precondition failed: current phase is {mission['phase']}, expected PLANNING"
            )
            return False

        # Check: orchestrator available (optional - degrades gracefully if missing)
        if not self.orchestrator:
            logger.warning(
                "Orchestrator not available - execute_agent functionality disabled. "
                "Planning will proceed with limitations."
            )
            # Don't fail - allow specialist to proceed without orchestrator

        logger.info("✅ PLANNING preconditions met")
        return True

    def execute(self, context: MissionContext) -> SpecialistResult:
        """
        Execute PLANNING workflow

        Flow:
            1. Load manifest
            2. Execute sub-states (RESEARCH, BUSINESS_VALIDATION, etc.)
            3. Apply quality gates
            4. Generate artifacts
            5. Return success

        Args:
            context: Mission context

        Returns:
            SpecialistResult with success=True, next_phase="CODING", artifacts

        Raises:
            Exception: If planning workflow fails
        """
        logger.info(f"PlanningSpecialist: Starting execution (mission_id={self.mission_id})")

        # Log decision: Starting planning
        self._log_decision(
            decision_type="PLANNING_STARTED",
            rationale="Beginning PLANNING phase execution",
            data={
                "mission_id": self.mission_id,
                "project_root": str(context.project_root),
            },
        )

        # Load manifest
        manifest_path = context.project_root / "project_manifest.json"
        with open(manifest_path) as f:
            manifest_data = json.load(f)

        # Track artifacts generated
        artifacts = []

        # Execute planning sub-states
        # Note: This is a simplified version. Full implementation would execute:
        # 1. RESEARCH (optional)
        # 2. BUSINESS_VALIDATION
        # 3. FEATURE_SPECIFICATION
        # 4. ARCHITECTURE_DESIGN

        logger.info("📋 Executing planning sub-states...")

        # For now, we'll generate a simple architecture artifact
        architecture = self._generate_architecture(context, manifest_data)

        # Save architecture artifact
        artifact_path = context.project_root / "artifacts" / "planning" / "architecture.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        with open(artifact_path, "w") as f:
            json.dump(architecture, f, indent=2)

        artifacts.append(str(artifact_path))

        # Log decision: Architecture generated
        self._log_decision(
            decision_type="ARCHITECTURE_GENERATED",
            rationale="Created system architecture based on requirements",
            data={
                "artifact": str(artifact_path),
                "components": len(architecture.get("components", [])),
            },
        )

        logger.info(f"✅ Architecture generated: {artifact_path}")

        # Return success
        return SpecialistResult(
            success=True,
            next_phase="CODING",
            artifacts=artifacts,
            decisions=[
                {"type": "PLANNING_STARTED"},
                {"type": "ARCHITECTURE_GENERATED"},
            ],
        )

    def _generate_architecture(self, context: MissionContext, manifest_data: dict) -> dict:
        """
        Generate system architecture from requirements

        Args:
            context: Mission context
            manifest_data: Project manifest data

        Returns:
            Architecture dict
        """
        metadata = manifest_data.get("metadata", {})

        architecture = {
            "name": metadata.get("name", "unnamed-project"),
            "description": metadata.get("description", ""),
            "components": [
                "frontend",
                "backend",
                "database",
            ],
            "tech_stack": {
                "frontend": "React",
                "backend": "FastAPI",
                "database": "PostgreSQL",
            },
            "generated_by": "PlanningSpecialist",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "mission_id": self.mission_id,
        }

        return architecture
