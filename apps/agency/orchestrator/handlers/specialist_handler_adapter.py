#!/usr/bin/env python3
"""
Specialist Handler Adapter - ARCH-006

Bridges the gap between legacy handler interface and new specialist interface.

This is a transitional adapter while we migrate from monolithic handlers to
the Hierarchical Agent Pattern (HAP). Future versions will eliminate this adapter
once all phases use specialists.

Legacy Handler Interface:
    - execute(manifest: ProjectManifest) -> None
    - Mutates manifest directly
    - No return value

New Specialist Interface:
    - execute(context: MissionContext) -> SpecialistResult
    - Immutable operation
    - Returns result with next_phase, artifacts, decisions

The adapter converts ProjectManifest → MissionContext, calls the specialist,
and applies the result back to the manifest.
"""

import logging
from pathlib import Path

from vibe_core.specialists import BaseSpecialist, MissionContext

logger = logging.getLogger(__name__)


class SpecialistHandlerAdapter:
    """
    Adapter that allows specialists to be used as phase handlers.

    Wraps a specialist and provides the handler interface expected by
    CoreOrchestrator, while delegating actual work to the specialist.

    The adapter creates the specialist lazily on first execute() call,
    after the mission_id is available from the manifest.
    """

    def __init__(self, specialist_class: type[BaseSpecialist], orchestrator):
        """
        Initialize adapter.

        Args:
            specialist_class: BaseSpecialist subclass to instantiate
            orchestrator: CoreOrchestrator instance (for context)
        """
        self.specialist_class = specialist_class
        self.orchestrator = orchestrator
        self._specialist = None  # Lazy initialization

    def execute(self, manifest) -> None:
        """
        Execute specialist workflow (handler interface).

        Converts manifest to MissionContext, calls specialist.execute(),
        and applies result back to manifest.

        Args:
            manifest: ProjectManifest to execute

        Raises:
            Exception: If specialist execution fails
        """
        # Import here to avoid circular imports

        # Lazy initialization: Create specialist on first execute()
        if self._specialist is None:
            self._specialist = self._create_specialist(manifest)

        logger.info(f"🔄 Delegating to {self._specialist.__class__.__name__}")

        # Convert ProjectManifest to MissionContext
        context = self._manifest_to_context(manifest)

        # Validate preconditions
        if not self._specialist.validate_preconditions(context):
            raise RuntimeError(
                f"Preconditions failed for {self._specialist.role} phase. Check logs for details."
            )

        # Inject manifest for specialists that need it (temporary hack)
        # TODO: Remove this once specialists have direct tool access
        self._specialist._manifest = manifest

        # Call specialist lifecycle hooks
        self._specialist.on_start(context)

        try:
            # Execute specialist workflow
            result = self._specialist.execute(context)

            # Check if execution was successful
            if not result.success:
                error_msg = result.error or "Unknown error"
                raise RuntimeError(f"Specialist execution failed: {error_msg}")

            # Apply result to manifest
            self._apply_result_to_manifest(result, manifest)

            # Call completion hook
            self._specialist.on_complete(context, result)

            logger.info(f"✅ {self._specialist.role} phase complete via specialist")

        except Exception as e:
            # Call error hook
            self._specialist.on_error(context, e)
            logger.error(f"❌ Specialist execution failed: {e}")
            raise

    def _create_specialist(self, manifest) -> BaseSpecialist:
        """
        Create specialist instance for this phase.

        Args:
            manifest: ProjectManifest containing project_id

        Returns:
            Instantiated specialist

        Raises:
            RuntimeError: If mission_id cannot be found
        """
        # Look up mission_id from SQLite using project_id
        mission = self.orchestrator.sqlite_store.get_mission_by_uuid(manifest.project_id)

        if mission is None:
            # Mission not found - create it now (dual-write)
            mission_id = self.orchestrator.sqlite_store.import_project_manifest(manifest.metadata)
            logger.info(f"✅ Created mission in SQLite: mission_id={mission_id}")
        else:
            mission_id = mission["id"]
            logger.debug(f"✅ Found existing mission: mission_id={mission_id}")

        # Instantiate specialist
        # Note: PlanningSpecialist requires orchestrator as temporary dependency
        specialist = self.specialist_class(
            mission_id=mission_id,
            sqlite_store=self.orchestrator.sqlite_store,
            tool_safety_guard=self.orchestrator.tool_safety_guard,
            orchestrator=self.orchestrator,  # Temporary dependency for execute_agent()
        )

        logger.info(f"✅ Created {specialist.__class__.__name__} (mission_id={mission_id})")

        return specialist

    def _manifest_to_context(self, manifest) -> MissionContext:
        """
        Convert ProjectManifest to MissionContext.

        Args:
            manifest: ProjectManifest to convert

        Returns:
            MissionContext for specialist
        """
        # Get project root from orchestrator
        project_root = (
            Path(self.orchestrator.repo_root) / ".vibe" / "projects" / manifest.project_id
        )

        # Create context
        context = MissionContext(
            mission_id=self._specialist.mission_id,
            mission_uuid=manifest.project_id,
            phase=manifest.current_phase.value,
            project_root=project_root,
            metadata=manifest.metadata,
        )

        return context

    def _apply_result_to_manifest(self, result, manifest) -> None:
        """
        Apply specialist result to manifest.

        Args:
            result: SpecialistResult from specialist
            manifest: ProjectManifest to update
        """
        from ..types import ProjectPhase

        # Update artifacts
        if result.artifacts:
            if "planning_artifacts" not in manifest.artifacts:
                manifest.artifacts["planning_artifacts"] = []
            manifest.artifacts["planning_artifacts"].extend(result.artifacts)

        # Apply quality gates before phase transition
        if result.next_phase:
            logger.info(
                f"🔒 Applying quality gates for {manifest.current_phase.value} → {result.next_phase} transition..."
            )

            try:
                # Determine transition name
                transition_name = self._get_transition_name(
                    manifest.current_phase, result.next_phase
                )

                # Apply quality gates
                self.orchestrator.apply_quality_gates(
                    transition_name=transition_name, manifest=manifest
                )
            except Exception as e:
                logger.error(f"❌ Quality gate BLOCKED transition to {result.next_phase}: {e}")
                raise

            # Transition to next phase
            try:
                manifest.current_phase = ProjectPhase[result.next_phase]
                manifest.current_sub_state = None
                logger.info(
                    f"✅ Phase transition: {manifest.current_phase.value} → {result.next_phase}"
                )
            except KeyError:
                logger.error(f"Invalid next_phase: {result.next_phase}")
                raise ValueError(f"Invalid phase: {result.next_phase}")

    def _get_transition_name(self, current_phase, next_phase: str) -> str:
        """
        Get transition name for quality gate lookup.

        Args:
            current_phase: Current ProjectPhase
            next_phase: Next phase name (string)

        Returns:
            Transition name (e.g., "T1_StartCoding")
        """
        # Map phase transitions to transition names
        transition_map = {
            ("PLANNING", "CODING"): "T1_StartCoding",
            ("CODING", "TESTING"): "T2_StartTesting",
            ("TESTING", "DEPLOYMENT"): "T3_StartDeployment",
            ("DEPLOYMENT", "PRODUCTION"): "T4_GoLive",
        }

        key = (current_phase.value, next_phase)
        return transition_map.get(key, f"T_Unknown_{current_phase.value}_to_{next_phase}")
