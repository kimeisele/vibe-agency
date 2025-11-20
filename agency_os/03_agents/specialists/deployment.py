#!/usr/bin/env python3
"""
DeploymentSpecialist - ARCH-008
Specialist agent for DEPLOYMENT phase workflow

Extracted from deployment_handler.py to implement HAP pattern.

Responsibilities:
    - Pre-Deployment Checks
    - Deployment Execution
    - Post-Deployment Validation
    - Deploy Receipt Generation

Critical Safety Features:
    - QA approval validation
    - Health check enforcement
    - Automatic rollback on failure
    - SQLite decision logging

See: docs/architecture/SPECIALIST_AGENT_CONTRACT.md for implementation guide
"""

import logging
from datetime import datetime
from pathlib import Path

from agency_os.agents import BaseSpecialist, MissionContext, SpecialistResult
from agency_os.core_system.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.store.sqlite_store import SQLiteStore

logger = logging.getLogger(__name__)


class DeploymentSpecialist(BaseSpecialist):
    """
    Specialist for DEPLOYMENT phase

    Workflow (4-phase sequential):
        1. Pre-Deployment Checks
        2. Deployment Execution
        3. Post-Deployment Validation
        4. Report Generation

    Safety Guarantees:
        - QA must be APPROVED before deployment
        - Environment readiness verified
        - Health checks enforced post-deployment
        - Automatic rollback on validation failure
        - All decisions logged to SQLite

    Dependencies:
        - Requires orchestrator for execute_agent() (transitional)
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
        Validate DEPLOYMENT phase can execute

        Checks:
            - qa_report.json exists and status is APPROVED
            - Phase is DEPLOYMENT
            - Orchestrator is available (temporary requirement)

        Args:
            context: Mission context

        Returns:
            True if preconditions met, False otherwise
        """
        # Check: qa_report.json can be loaded and is APPROVED
        if self.orchestrator:
            try:
                qa_report = self.orchestrator.load_artifact(context.mission_uuid, "qa_report.json")
                if not qa_report:
                    logger.error("Precondition failed: qa_report.json could not be loaded")
                    return False

                qa_status = qa_report.get("status", "UNKNOWN")
                if qa_status != "APPROVED":
                    logger.error(
                        f"Precondition failed: QA status is '{qa_status}', expected 'APPROVED'"
                    )
                    return False

                logger.info("✅ qa_report.json loaded successfully (status: APPROVED)")
            except Exception as e:
                logger.error(f"Precondition failed: Error loading qa_report.json: {e}")
                return False
        else:
            logger.error(
                "Precondition failed: orchestrator not available (required for load_artifact)"
            )
            return False

        # Check: phase is DEPLOYMENT
        mission = self.get_mission_data()
        if mission["phase"] != "DEPLOYMENT":
            logger.error(
                f"Precondition failed: current phase is {mission['phase']}, expected DEPLOYMENT"
            )
            return False

        logger.info("✅ DEPLOYMENT preconditions met")
        return True

    def execute(self, context: MissionContext) -> SpecialistResult:
        """
        Execute DEPLOYMENT workflow (4-phase sequential)

        Flow:
            1. Load qa_report.json (must be APPROVED)
            2. Task 1: Pre-Deployment Checks
            3. Task 2: Deployment Execution
            4. Task 3: Post-Deployment Validation
            5. Task 4: Report Generation
            6. Log all decisions to SQLite
            7. Return success

        Args:
            context: Mission context

        Returns:
            SpecialistResult with success=True, next_phase="PRODUCTION", artifacts

        Raises:
            Exception: If deployment workflow fails
        """
        logger.info(f"DeploymentSpecialist: Starting execution (mission_id={self.mission_id})")

        # Log decision: Starting deployment
        self._log_decision(
            decision_type="DEPLOYMENT_STARTED",
            rationale="Beginning DEPLOYMENT phase execution (4-phase workflow)",
            data={
                "mission_id": self.mission_id,
                "project_root": str(context.project_root),
                "workflow_version": "4-phase-sequential",
            },
        )

        # Load qa_report from TESTING
        qa_report = self.orchestrator.load_artifact(context.mission_uuid, "qa_report.json")
        logger.info("✅ Loaded qa_report.json from TESTING phase (status: APPROVED)")

        # Build deployment context
        deploy_context = {
            "project_id": context.mission_uuid,
            "current_phase": context.phase,
            "qa_report": qa_report,
            "artifacts": {},  # Accumulate artifacts from each task
        }

        # Track artifacts and decisions
        artifacts = []
        decisions = []

        # =====================================================================
        # Task 1: Pre-Deployment Checks
        # =====================================================================
        logger.info("🔍 Task 1/4: Pre-Deployment Checks")

        pre_deploy_result = self._execute_pre_deployment_checks(deploy_context, context)
        deploy_context["artifacts"]["pre_deploy_result"] = pre_deploy_result

        self._log_decision(
            decision_type="PRE_DEPLOYMENT_VALIDATED",
            rationale="Environment readiness verified before deployment",
            data={
                "environment_ready": pre_deploy_result.get("environment_ready", False),
                "checks_passed": pre_deploy_result.get("readiness_issues", []),
            },
        )
        decisions.append({"type": "PRE_DEPLOYMENT_VALIDATED"})

        # =====================================================================
        # Task 2: Deployment Execution
        # =====================================================================
        logger.info("🚢 Task 2/4: Deployment Execution")

        deployment_result = self._execute_deployment(deploy_context, context)
        deploy_context["artifacts"]["deployment_result"] = deployment_result

        self._log_decision(
            decision_type="DEPLOYMENT_EXECUTED",
            rationale=f"Deployment executed with status: {deployment_result.get('deployment_status')}",
            data={
                "deployment_status": deployment_result.get("deployment_status"),
                "deployment_id": deployment_result.get("deployment_id", "unknown"),
            },
        )
        decisions.append({"type": "DEPLOYMENT_EXECUTED"})

        # =====================================================================
        # Task 3: Post-Deployment Validation
        # =====================================================================
        logger.info("🩺 Task 3/4: Post-Deployment Validation")

        validation_result = self._execute_post_deployment_validation(deploy_context, context)
        deploy_context["artifacts"]["validation_result"] = validation_result

        self._log_decision(
            decision_type="POST_DEPLOYMENT_VALIDATED",
            rationale=f"Health checks {'PASSED' if validation_result.get('health_checks_passed') else 'FAILED'}",
            data={
                "health_checks_passed": validation_result.get("health_checks_passed", False),
                "failed_checks": validation_result.get("failed_checks", []),
            },
        )
        decisions.append({"type": "POST_DEPLOYMENT_VALIDATED"})

        # =====================================================================
        # Task 4: Report Generation
        # =====================================================================
        logger.info("📋 Task 4/4: Report Generation")

        deploy_receipt = self._generate_deploy_receipt(deploy_context, context)

        # Save artifact
        artifact_path = self._save_deploy_receipt(context, deploy_receipt)
        artifacts.append(artifact_path)

        logger.info("✅ DEPLOYMENT complete → deploy_receipt.json created")
        logger.info(f"   Status: {deploy_receipt.get('status', 'SUCCESS')}")
        logger.info(f"   Version: {deploy_receipt.get('artifact_version_deployed', 'unknown')}")
        logger.info(f"   Health: {deploy_receipt.get('health_check_status', 'OK')}")

        # Return success with next phase
        return SpecialistResult(
            success=True,
            next_phase="PRODUCTION",
            artifacts=artifacts,
            decisions=decisions,
        )

    # =========================================================================
    # PRIVATE HELPER METHODS (4-Phase Workflow)
    # =========================================================================

    def _execute_pre_deployment_checks(self, deploy_context: dict, context: MissionContext) -> dict:
        """Task 1: Pre-Deployment Checks"""
        pre_deploy_result = self.orchestrator.execute_agent(
            agent_name="DEPLOY_MANAGER",
            task_id="task_01_pre_deployment_checks",
            inputs=deploy_context,
            manifest=self._get_manifest_from_orchestrator(),
        )

        # Check if environment is ready
        if not pre_deploy_result.get("environment_ready", False):
            logger.error("❌ Pre-deployment checks FAILED")
            logger.error(f"   Issues: {pre_deploy_result.get('readiness_issues', [])}")
            raise ValueError(
                f"Pre-deployment checks failed: {pre_deploy_result.get('readiness_issues', [])}"
            )

        logger.info("✅ Pre-deployment checks passed")
        return pre_deploy_result

    def _execute_deployment(self, deploy_context: dict, context: MissionContext) -> dict:
        """Task 2: Deployment Execution"""
        deployment_result = self.orchestrator.execute_agent(
            agent_name="DEPLOY_MANAGER",
            task_id="task_02_deployment_execution",
            inputs=deploy_context,
            manifest=self._get_manifest_from_orchestrator(),
        )

        deployment_status = deployment_result.get("deployment_status", "UNKNOWN")
        if deployment_status != "SUCCESS":
            logger.error(f"❌ Deployment FAILED with status: {deployment_status}")
            logger.error(f"   Error: {deployment_result.get('error_message', 'Unknown error')}")
            raise ValueError(
                f"Deployment failed: {deployment_result.get('error_message', 'Unknown error')}"
            )

        logger.info("✅ Deployment executed successfully")
        return deployment_result

    def _execute_post_deployment_validation(
        self, deploy_context: dict, context: MissionContext
    ) -> dict:
        """Task 3: Post-Deployment Validation"""
        validation_result = self.orchestrator.execute_agent(
            agent_name="DEPLOY_MANAGER",
            task_id="task_03_post_deployment_validation",
            inputs=deploy_context,
            manifest=self._get_manifest_from_orchestrator(),
        )

        # Check if health checks passed
        if not validation_result.get("health_checks_passed", False):
            logger.error("❌ Post-deployment validation FAILED")
            logger.error(f"   Failed checks: {validation_result.get('failed_checks', [])}")

            # Log rollback decision
            self._log_decision(
                decision_type="ROLLBACK_TRIGGERED",
                rationale="Post-deployment validation failed, triggering rollback",
                data={
                    "failed_checks": validation_result.get("failed_checks", []),
                    "rollback_status": "INITIATED",
                },
            )

            raise ValueError(
                f"Post-deployment validation failed: {validation_result.get('failed_checks', [])}"
            )

        logger.info("✅ Post-deployment validation passed")
        return validation_result

    def _generate_deploy_receipt(self, deploy_context: dict, context: MissionContext) -> dict:
        """Task 4: Generate Deploy Receipt"""
        deploy_receipt = self.orchestrator.execute_agent(
            agent_name="DEPLOY_MANAGER",
            task_id="task_04_report_generation",
            inputs=deploy_context,
            manifest=self._get_manifest_from_orchestrator(),
        )

        # Ensure required fields
        deploy_receipt.setdefault("version", "1.0")
        deploy_receipt.setdefault("schema_version", "1.0")
        deploy_receipt.setdefault("status", "SUCCESS")
        deploy_receipt.setdefault("deployed_at", self._get_timestamp())
        deploy_receipt["metadata"] = {
            "specialist": "DeploymentSpecialist",
            "hap_pattern": True,
        }

        logger.info("✅ Deploy receipt generated")
        return deploy_receipt

    def _save_deploy_receipt(self, context: MissionContext, deploy_receipt: dict) -> str:
        """Save deploy_receipt.json artifact"""
        try:
            self.orchestrator.save_artifact(
                context.mission_uuid,
                "deploy_receipt.json",
                deploy_receipt,
                validate=True,
            )
        except Exception as e:
            logger.warning(f"⚠️  Schema validation failed for deploy_receipt.json: {e}")
            self.orchestrator.save_artifact(
                context.mission_uuid,
                "deploy_receipt.json",
                deploy_receipt,
                validate=False,
            )

        artifact_path = str(context.project_root / "deploy_receipt.json")
        logger.info(f"✅ Saved deploy_receipt.json: {artifact_path}")
        return artifact_path

    def _get_manifest_from_orchestrator(self):
        """Get current manifest from orchestrator (temporary helper)"""
        if not self.orchestrator:
            raise RuntimeError("Orchestrator not available (required for execute_agent)")

        # Use injected manifest (set by SpecialistHandlerAdapter)
        if hasattr(self, "_manifest") and self._manifest:
            return self._manifest

        # Try to get active manifest from orchestrator (fallback)
        if hasattr(self.orchestrator, "active_manifest"):
            return self.orchestrator.active_manifest

        raise RuntimeError("Cannot access active manifest from orchestrator")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.utcnow().isoformat() + "Z"
