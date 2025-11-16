"""
Deployment Phase Handler
=========================

Handles DEPLOYMENT phase execution by invoking the DEPLOY_MANAGER agent.

Implements Phase 4: Full DEPLOY_MANAGER integration
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DeploymentHandler:
    """
    Handler for DEPLOYMENT phase execution.

    Invokes DEPLOY_MANAGER agent with 4-phase sequential workflow:
    1. Pre-Deployment Checks
    2. Deployment Execution
    3. Post-Deployment Validation
    4. Report Generation

    Phase 4 Implementation: Full DEPLOY_MANAGER integration using llm_client.py
    """

    def __init__(self, orchestrator):
        """Initialize handler"""
        self.orchestrator = orchestrator

    def execute(self, manifest) -> None:
        """
        Execute DEPLOYMENT phase.

        Flow:
        1. Load qa_report.json (must be APPROVED)
        2. Execute DEPLOY_MANAGER 4-phase workflow
        3. Save deploy_receipt.json
        4. Transition to PRODUCTION (or MAINTENANCE on failure)
        """
        logger.info("🚀 Starting DEPLOYMENT phase")

        # Load QA report from TESTING
        qa_report = self.orchestrator.load_artifact(manifest.project_id, "qa_report.json")

        if not qa_report:
            from core_orchestrator import ArtifactNotFoundError

            raise ArtifactNotFoundError(
                "qa_report.json not found - TESTING phase must complete first"
            )

        # Check if QA approved
        qa_status = qa_report.get("status", "UNKNOWN")
        if qa_status != "APPROVED":
            logger.error(f"❌ QA report status is '{qa_status}', expected 'APPROVED'")
            raise ValueError(
                f"Cannot deploy: QA report must be APPROVED (current status: {qa_status})"
            )

        logger.info("✓ Loaded qa_report.json from TESTING phase (status: APPROVED)")

        # Build initial context for DEPLOY_MANAGER
        deploy_context = {
            "project_id": manifest.project_id,
            "current_phase": manifest.current_phase.value,
            "qa_report": qa_report,
            "artifacts": {},  # Will accumulate artifacts from each task
        }

        # =====================================================================
        # Task 1: Pre-Deployment Checks
        # =====================================================================
        logger.info("🔍 Task 1/4: Pre-Deployment Checks")

        pre_deploy_result = self.orchestrator.execute_agent(
            agent_name="DEPLOY_MANAGER",
            task_id="task_01_pre_deployment_checks",
            inputs=deploy_context,
            manifest=manifest,
        )

        # Check if environment is ready
        if not pre_deploy_result.get("environment_ready", False):
            logger.error("❌ Pre-deployment checks FAILED")
            logger.error(f"   Issues: {pre_deploy_result.get('readiness_issues', [])}")
            raise ValueError(
                f"Pre-deployment checks failed: {pre_deploy_result.get('readiness_issues', [])}"
            )

        logger.info("✅ Pre-deployment checks passed")
        deploy_context["artifacts"]["pre_deploy_result"] = pre_deploy_result

        # =====================================================================
        # Task 2: Deployment Execution
        # =====================================================================
        logger.info("🚢 Task 2/4: Deployment Execution")

        deployment_result = self.orchestrator.execute_agent(
            agent_name="DEPLOY_MANAGER",
            task_id="task_02_deployment_execution",
            inputs=deploy_context,
            manifest=manifest,
        )

        deployment_status = deployment_result.get("deployment_status", "UNKNOWN")
        if deployment_status != "SUCCESS":
            logger.error(f"❌ Deployment FAILED with status: {deployment_status}")
            logger.error(f"   Error: {deployment_result.get('error_message', 'Unknown error')}")

            # Create bug report for MAINTENANCE transition
            self._create_deployment_failure_bug_report(manifest, deployment_result)

            raise ValueError(
                f"Deployment failed: {deployment_result.get('error_message', 'Unknown error')}"
            )

        logger.info("✅ Deployment executed successfully")
        deploy_context["artifacts"]["deployment_result"] = deployment_result

        # =====================================================================
        # Task 3: Post-Deployment Validation
        # =====================================================================
        logger.info("🩺 Task 3/4: Post-Deployment Validation")

        validation_result = self.orchestrator.execute_agent(
            agent_name="DEPLOY_MANAGER",
            task_id="task_03_post_deployment_validation",
            inputs=deploy_context,
            manifest=manifest,
        )

        # Check if health checks passed
        if not validation_result.get("health_checks_passed", False):
            logger.error("❌ Post-deployment validation FAILED")
            logger.error(f"   Failed checks: {validation_result.get('failed_checks', [])}")

            # Trigger rollback
            logger.warning("⚠️  Triggering automatic rollback...")
            self._trigger_rollback(manifest, validation_result)

            # Create bug report for MAINTENANCE transition
            self._create_deployment_failure_bug_report(manifest, validation_result)

            raise ValueError(
                f"Post-deployment validation failed: {validation_result.get('failed_checks', [])}"
            )

        logger.info("✅ Post-deployment validation passed")
        deploy_context["artifacts"]["validation_result"] = validation_result

        # =====================================================================
        # Task 4: Report Generation
        # =====================================================================
        logger.info("📋 Task 4/4: Report Generation")

        deploy_receipt = self.orchestrator.execute_agent(
            agent_name="DEPLOY_MANAGER",
            task_id="task_04_report_generation",
            inputs=deploy_context,
            manifest=manifest,
        )

        logger.info("✅ Deploy receipt generated")

        # =====================================================================
        # Save Artifacts
        # =====================================================================

        # Ensure deploy_receipt has required fields
        deploy_receipt.setdefault("version", "1.0")
        deploy_receipt.setdefault("schema_version", "1.0")
        deploy_receipt.setdefault("status", "SUCCESS")
        deploy_receipt.setdefault("deployed_at", self._get_timestamp())

        # Save deploy_receipt artifact
        self.orchestrator.save_artifact(
            manifest.project_id,
            "deploy_receipt.json",
            deploy_receipt,
            validate=False,  # TODO: Add schema validation in future
        )

        manifest.artifacts["deploy_receipt"] = deploy_receipt

        logger.info("✅ DEPLOYMENT complete → deploy_receipt.json created")
        logger.info(f"   Status: {deploy_receipt.get('status', 'SUCCESS')}")
        logger.info(f"   Version: {deploy_receipt.get('artifact_version_deployed', 'unknown')}")
        logger.info(f"   Health: {deploy_receipt.get('health_check_status', 'OK')}")

        # Transition to PRODUCTION
        from core_orchestrator import ProjectPhase

        manifest.current_phase = ProjectPhase.PRODUCTION

        logger.info("🎉 Project deployed to PRODUCTION")

    def _trigger_rollback(self, manifest, validation_result) -> None:
        """
        Trigger automatic rollback on failed validation.

        Args:
            manifest: Project manifest
            validation_result: Post-deployment validation result
        """
        logger.warning("🔄 Initiating rollback procedure...")

        # In a real implementation, this would:
        # 1. Call deployment platform's rollback API
        # 2. Restore previous version
        # 3. Verify rollback succeeded
        # 4. Update monitoring/alerting

        # For now, log the intent
        rollback_info = {
            "triggered_at": self._get_timestamp(),
            "reason": "Post-deployment validation failed",
            "failed_checks": validation_result.get("failed_checks", []),
            "rollback_status": "INITIATED",
        }

        logger.warning(f"   Rollback info: {rollback_info}")

        # Save rollback artifact for audit trail
        self.orchestrator.save_artifact(
            manifest.project_id,
            "rollback_info.json",
            rollback_info,
            validate=False,
        )

    def _create_deployment_failure_bug_report(self, manifest, failure_result) -> None:
        """
        Create bug report for deployment failure to transition to MAINTENANCE.

        Args:
            manifest: Project manifest
            failure_result: Deployment or validation failure result
        """
        bug_report = {
            "version": "1.0",
            "severity": "P1_CRITICAL",
            "title": "Deployment Failure - Automatic Rollback",
            "description": f"Deployment failed: {failure_result.get('error_message', 'Unknown')}",
            "context": {
                "project_id": manifest.project_id,
                "failed_phase": "DEPLOYMENT",
                "failure_details": failure_result,
                "created_at": self._get_timestamp(),
            },
            "status": "OPEN",
        }

        # Save bug report
        self.orchestrator.save_artifact(
            manifest.project_id, "bug_report.json", bug_report, validate=False
        )

        manifest.artifacts["bug_report"] = bug_report

        logger.warning("⚠️  Created P1 bug report for MAINTENANCE workflow")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.utcnow().isoformat() + "Z"
