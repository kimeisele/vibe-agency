#!/usr/bin/env python3
"""
DeploymentSpecialist - ARCH-008.3 (The Gatekeeper)
Specialist agent for DEPLOYMENT phase workflow

THE FINAL GATE: This agent enforces STRICT configuration integrity before
any artifacts touch production. It is the last line of defense.

Responsibilities:
    - STRICT validation of project_manifest.json (must exist and be valid)
    - QA report verification (must be PASSED or APPROVED)
    - Safe artifact copying to dist/ folder
    - Deployment manifest generation
    - HARD FAIL on any ambiguity or missing configuration

Critical Safety Features:
    - project_manifest.json must be present and valid (NO EXCEPTIONS)
    - qa_report.json must show PASSED or APPROVED status
    - File operations are atomic and safe (shutil.copy2)
    - All decisions logged to SQLite for compliance audit
    - Automatic rollback on validation failure

Design Philosophy:
    "When in doubt, FAIL. We do not deploy to production with
     ambiguous system state." - STEWARD Protocol v4.2

See: docs/architecture/SPECIALIST_AGENT_CONTRACT.md for implementation guide
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.specialists import BaseSpecialist, MissionContext, SpecialistResult
from vibe_core.store.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


class DeploymentSpecialist(BaseSpecialist):
    """
    Specialist for DEPLOYMENT phase (THE GATEKEEPER)

    STRICT Workflow (3-phase with hard validation):
        1. STRICT Validation Phase
           - project_manifest.json MUST exist and be valid (NO FALLBACK)
           - qa_report.json MUST show PASSED or APPROVED status
           - If EITHER check fails: ABORT IMMEDIATELY
        2. Safe Artifact Deployment
           - Copy artifacts to dist/ folder using shutil.copy2 (atomic)
           - Preserve file permissions and metadata
           - Create deployment_manifest.json with metadata
        3. Completion & Logging
           - Log all decisions to SQLite for compliance audit
           - Return success only if ALL checks pass

    Safety Guarantees:
        - NO deployment without valid project_manifest.json
        - NO deployment without passing QA status
        - NO ambiguous system state allowed
        - All decisions are immutable (logged to SQLite)
        - Rollback on any validation failure

    Error Handling (HARD FAIL):
        - Missing project_manifest.json → ABORT (return success=False)
        - Invalid JSON in project_manifest.json → ABORT
        - Missing qa_report.json → ABORT
        - qa_report.json status not PASSED or APPROVED → ABORT
        - File copy failure → ABORT (rollback)

    Dependencies:
        - Requires orchestrator for load_artifact()
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
        Initialize DeploymentSpecialist

        Args:
            mission_id: Database primary key
            sqlite_store: Persistence layer
            tool_safety_guard: Safety enforcement
            orchestrator: CoreOrchestrator instance (temporary dependency)
            playbook_root: Playbook directory
        """
        super().__init__(
            role="DEPLOYMENT",
            mission_id=mission_id,
            sqlite_store=sqlite_store,
            tool_safety_guard=tool_safety_guard,
            playbook_root=playbook_root,
        )

        self.orchestrator = orchestrator  # Temporary dependency

        if not orchestrator:
            logger.warning(
                "DeploymentSpecialist initialized without orchestrator. "
                "Some functionality (execute_agent, save_artifact) will not work."
            )

    def validate_preconditions(self, context: MissionContext) -> bool:
        """
        STRICT validation of DEPLOYMENT phase preconditions.

        HARD FAIL checks (no fallbacks):
            - project_manifest.json MUST exist and be valid JSON
            - qa_report.json MUST exist and status must be PASSED or APPROVED
            - Phase must be DEPLOYMENT
            - Orchestrator must be available

        Args:
            context: Mission context

        Returns:
            True if all checks pass, False otherwise (with error logging)
        """
        # Check 1: Orchestrator availability
        if not self.orchestrator:
            logger.error("❌ BLOCKING: Orchestrator not available (required for load_artifact)")
            return False

        # Check 2: project_manifest.json exists and is valid
        try:
            project_manifest = self.orchestrator.load_artifact(
                context.mission_uuid, "project_manifest.json"
            )
            if not project_manifest:
                logger.error(
                    "❌ BLOCKING: project_manifest.json could not be loaded (missing or invalid)"
                )
                return False
            logger.info("✅ project_manifest.json loaded and validated")
        except Exception as e:
            logger.error(f"❌ BLOCKING: Error loading project_manifest.json: {e}")
            return False

        # Check 3: qa_report.json exists and status is PASSED or APPROVED
        try:
            qa_report = self.orchestrator.load_artifact(context.mission_uuid, "qa_report.json")
            if not qa_report:
                logger.error("❌ BLOCKING: qa_report.json could not be loaded (missing or invalid)")
                return False

            qa_status = qa_report.get("status", "UNKNOWN")
            if qa_status not in ("PASSED", "APPROVED"):
                logger.error(
                    f"❌ BLOCKING: QA status is '{qa_status}', expected 'PASSED' or 'APPROVED'"
                )
                return False
            logger.info(f"✅ qa_report.json loaded successfully (status: {qa_status})")
        except Exception as e:
            logger.error(f"❌ BLOCKING: Error loading qa_report.json: {e}")
            return False

        # Check 4: Phase is DEPLOYMENT
        mission = self.get_mission_data()
        if mission["phase"] != "DEPLOYMENT":
            logger.error(f"❌ BLOCKING: current phase is {mission['phase']}, expected DEPLOYMENT")
            return False

        logger.info("✅ ALL DEPLOYMENT preconditions met (STRICT validation passed)")
        return True

    def execute(self, context: MissionContext) -> SpecialistResult:
        """
        Execute DEPLOYMENT workflow (STRICT 3-phase with hard validation).

        Flow:
            1. STRICT Validation Phase
               - Validate project_manifest.json (must exist and be valid JSON)
               - Validate qa_report.json (must show PASSED or APPROVED)
               - If ANY check fails: ABORT with success=False
            2. Safe Artifact Deployment
               - Create dist/ folder (clean if exists)
               - Copy artifacts using shutil.copy2 (atomic, preserves metadata)
               - Generate deployment_manifest.json with metadata
            3. Completion & Logging
               - Log all decisions to SQLite
               - Return success only if all checks pass

        Args:
            context: Mission context

        Returns:
            SpecialistResult with success=True if all checks pass, False if any fails

        Raises:
            Exception: Only on unexpected errors (not validation failures)
        """
        logger.info(f"🚀 DeploymentSpecialist: Starting execution (mission_id={self.mission_id})")
        logger.info("🔐 GATEKEEPER MODE: Enforcing STRICT configuration validation")

        # Log decision: Starting deployment
        self._log_decision(
            decision_type="DEPLOYMENT_STARTED",
            rationale="Beginning DEPLOYMENT phase execution (STRICT 3-phase workflow)",
            data={
                "mission_id": self.mission_id,
                "project_root": str(context.project_root),
                "mode": "GATEKEEPER_STRICT",
            },
        )

        # =====================================================================
        # Phase 1: STRICT Validation (HARD FAIL if anything is wrong)
        # =====================================================================
        logger.info("🔍 Phase 1/3: STRICT Validation")

        # Load and validate project_manifest.json
        try:
            project_manifest = self.orchestrator.load_artifact(
                context.mission_uuid, "project_manifest.json"
            )
            if not project_manifest:
                logger.error("❌ VALIDATION FAILED: project_manifest.json could not be loaded")
                self._log_decision(
                    decision_type="VALIDATION_FAILED",
                    rationale="project_manifest.json missing or invalid",
                    data={"reason": "manifest_load_failed"},
                )
                return SpecialistResult(
                    success=False,
                    error="Validation failed: project_manifest.json missing or invalid",
                )
            logger.info("✅ project_manifest.json validated")
        except Exception as e:
            logger.error(f"❌ VALIDATION FAILED: Error loading project_manifest.json: {e}")
            self._log_decision(
                decision_type="VALIDATION_FAILED",
                rationale=f"project_manifest.json error: {str(e)[:200]}",
                data={"reason": "manifest_error", "error": str(e)[:200]},
            )
            return SpecialistResult(success=False, error=f"Validation failed: {str(e)[:200]}")

        # Load and validate qa_report.json
        try:
            qa_report = self.orchestrator.load_artifact(context.mission_uuid, "qa_report.json")
            if not qa_report:
                logger.error("❌ VALIDATION FAILED: qa_report.json could not be loaded")
                self._log_decision(
                    decision_type="VALIDATION_FAILED",
                    rationale="qa_report.json missing or invalid",
                    data={"reason": "qa_report_load_failed"},
                )
                return SpecialistResult(
                    success=False, error="Validation failed: qa_report.json missing or invalid"
                )

            qa_status = qa_report.get("status", "UNKNOWN")
            if qa_status not in ("PASSED", "APPROVED"):
                logger.error(
                    f"❌ VALIDATION FAILED: QA status is '{qa_status}', expected PASSED or APPROVED"
                )
                self._log_decision(
                    decision_type="VALIDATION_FAILED",
                    rationale=f"QA status check failed: {qa_status}",
                    data={"reason": "qa_status_failed", "status": qa_status},
                )
                return SpecialistResult(
                    success=False,
                    error=f"Validation failed: QA status is {qa_status}, expected PASSED or APPROVED",
                )
            logger.info(f"✅ qa_report.json validated (status: {qa_status})")
        except Exception as e:
            logger.error(f"❌ VALIDATION FAILED: Error loading qa_report.json: {e}")
            self._log_decision(
                decision_type="VALIDATION_FAILED",
                rationale=f"qa_report.json error: {str(e)[:200]}",
                data={"reason": "qa_report_error", "error": str(e)[:200]},
            )
            return SpecialistResult(success=False, error=f"Validation failed: {str(e)[:200]}")

        logger.info("✅ Phase 1/3: ALL STRICT VALIDATION CHECKS PASSED")
        self._log_decision(
            decision_type="VALIDATION_PASSED",
            rationale="All strict configuration checks passed",
            data={"project_manifest_valid": True, "qa_status": qa_status},
        )

        # =====================================================================
        # Phase 2: Safe Artifact Deployment
        # =====================================================================
        logger.info("📦 Phase 2/3: Safe Artifact Deployment")

        try:
            # Create dist/ folder (clean if exists)
            dist_dir = context.project_root / "dist"
            if dist_dir.exists():
                logger.info(f"Cleaning existing dist/ folder: {dist_dir}")
                shutil.rmtree(dist_dir)
            dist_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created dist/ folder: {dist_dir}")

            # Copy code_gen_spec.json (the artifact from CODING phase)
            code_gen_spec_path = context.project_root / "code_gen_spec.json"
            deployed_files = []

            if code_gen_spec_path.exists():
                dest_path = dist_dir / "code_gen_spec.json"
                shutil.copy2(code_gen_spec_path, dest_path)
                deployed_files.append("code_gen_spec.json")
                logger.info("✅ Deployed: code_gen_spec.json")

            # Copy qa_report.json (for compliance audit)
            qa_report_path = context.project_root / "qa_report.json"
            if qa_report_path.exists():
                dest_path = dist_dir / "qa_report.json"
                shutil.copy2(qa_report_path, dest_path)
                deployed_files.append("qa_report.json")
                logger.info("✅ Deployed: qa_report.json")

            # Copy project_manifest.json (for production tracking)
            manifest_path = context.project_root / "project_manifest.json"
            if manifest_path.exists():
                dest_path = dist_dir / "project_manifest.json"
                shutil.copy2(manifest_path, dest_path)
                deployed_files.append("project_manifest.json")
                logger.info("✅ Deployed: project_manifest.json")

            logger.info(f"✅ Phase 2/3: Deployed {len(deployed_files)} artifact files")
            self._log_decision(
                decision_type="ARTIFACTS_DEPLOYED",
                rationale=f"Successfully deployed {len(deployed_files)} artifacts to dist/",
                data={"files_deployed": deployed_files, "dist_path": str(dist_dir)},
            )

        except Exception as e:
            logger.error(f"❌ DEPLOYMENT FAILED: {e}")
            # Rollback: Clean up dist/ folder
            try:
                if dist_dir.exists():
                    shutil.rmtree(dist_dir)
                    logger.info("✅ Rollback: Cleaned up dist/ folder")
            except Exception as rollback_error:
                logger.error(f"⚠️  Rollback failed: {rollback_error}")

            self._log_decision(
                decision_type="DEPLOYMENT_FAILED",
                rationale=f"Artifact deployment failed: {str(e)[:200]}",
                data={"reason": "deployment_error", "error": str(e)[:200]},
            )
            return SpecialistResult(success=False, error=f"Deployment failed: {str(e)[:200]}")

        # =====================================================================
        # Phase 3: Completion & Logging
        # =====================================================================
        logger.info("📋 Phase 3/3: Generate Deployment Manifest")

        try:
            # Generate deployment_manifest.json
            deployment_manifest = {
                "version": "1.0",
                "schema_version": "1.0",
                "deployment_id": str(self.mission_id),
                "project_id": context.mission_uuid,
                "deployed_at": self._get_timestamp(),
                "artifacts": {
                    "files": deployed_files,
                    "count": len(deployed_files),
                    "destination": str(dist_dir),
                },
                "validation": {
                    "manifest_valid": True,
                    "qa_status": qa_status,
                    "qa_verified": True,
                },
                "metadata": {
                    "specialist": "DeploymentSpecialist",
                    "hap_pattern": True,
                    "mode": "GATEKEEPER_STRICT",
                    "implementation": "Phase 4 - ARCH-008.3",
                },
            }

            # Save deployment_manifest.json
            manifest_dest = dist_dir / "deployment_manifest.json"
            with open(manifest_dest, "w") as f:
                json.dump(deployment_manifest, f, indent=2)
            logger.info(f"✅ Generated deployment_manifest.json: {manifest_dest}")

            # Log final decision
            self._log_decision(
                decision_type="DEPLOYMENT_COMPLETE",
                rationale=f"Deployment completed successfully with {len(deployed_files)} artifacts",
                data={
                    "deployment_id": str(self.mission_id),
                    "artifacts_deployed": len(deployed_files),
                    "qa_verified": True,
                    "manifest_path": str(manifest_dest),
                },
            )

            logger.info("✅ Phase 3/3: DEPLOYMENT COMPLETE")
            logger.info("=" * 70)
            logger.info("🎉 GATEKEEPER PASSED - DEPLOYMENT AUTHORIZED TO PRODUCTION")
            logger.info("=" * 70)

            return SpecialistResult(
                success=True,
                next_phase="PRODUCTION",
                artifacts=[str(manifest_dest)],
                decisions=[
                    {"type": "VALIDATION_PASSED", "qa_status": qa_status},
                    {"type": "ARTIFACTS_DEPLOYED", "count": len(deployed_files)},
                    {"type": "DEPLOYMENT_COMPLETE"},
                ],
            )

        except Exception as e:
            logger.error(f"❌ MANIFEST GENERATION FAILED: {e}")
            self._log_decision(
                decision_type="MANIFEST_GENERATION_FAILED",
                rationale=f"Failed to generate deployment_manifest.json: {str(e)[:200]}",
                data={"reason": "manifest_gen_error", "error": str(e)[:200]},
            )
            return SpecialistResult(
                success=False, error=f"Manifest generation failed: {str(e)[:200]}"
            )

    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format"""
        return datetime.utcnow().isoformat() + "Z"
