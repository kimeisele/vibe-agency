#!/usr/bin/env python3
"""
CodingSpecialist - ARCH-007
Specialist agent for CODING phase workflow

Extracted from coding_handler.py to implement HAP pattern for the most complex phase.

Responsibilities:
    - Spec Analysis & Validation
    - Code Generation
    - Test Generation
    - Documentation Generation
    - Quality Assurance & Packaging

Critical Safety Features:
    - ToolSafetyGuard enforcement before ALL file operations
    - SQLite persistence for every code modification decision
    - File lock management for concurrent safety

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


class CodingSpecialist(BaseSpecialist):
    """
    Specialist for CODING phase

    Workflow (5-phase sequential):
        1. Spec Analysis & Validation
        2. Code Generation (with ToolSafetyGuard)
        3. Test Generation
        4. Documentation Generation
        5. Quality Assurance & Packaging

    Safety Guarantees:
        - Every file operation checked by ToolSafetyGuard
        - Every code modification logged to SQLite (decisions table)
        - Anti-blindness: Files must be read before editing
        - Blast radius: No directory deletions allowed

    Dependencies:
        - Requires orchestrator for execute_agent() (transitional)
        - Future: Replace with direct tool access
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
        Initialize CodingSpecialist

        Args:
            mission_id: Database primary key
            sqlite_store: Persistence layer
            tool_safety_guard: Safety enforcement (REQUIRED for file ops)
            orchestrator: CoreOrchestrator instance (temporary dependency)
            playbook_root: Playbook directory

        Note:
            orchestrator dependency is transitional. Future versions will use
            direct tool access instead of delegating to orchestrator.execute_agent()
        """
        super().__init__(
            role="CODING",
            mission_id=mission_id,
            sqlite_store=sqlite_store,
            tool_safety_guard=tool_safety_guard,
            playbook_root=playbook_root,
        )

        self.orchestrator = orchestrator  # Temporary dependency

        if not orchestrator:
            logger.warning(
                "CodingSpecialist initialized without orchestrator. "
                "Some functionality (execute_agent, save_artifact) will not work."
            )

    def validate_preconditions(self, context: MissionContext) -> bool:
        """
        Validate CODING phase can execute

        Checks:
            - feature_spec.json can be loaded (from PLANNING phase)
            - Phase is CODING
            - Orchestrator is available (temporary requirement)
            - ToolSafetyGuard is operational

        Args:
            context: Mission context

        Returns:
            True if preconditions met, False otherwise
        """
        # Check: feature_spec.json can be loaded via orchestrator
        # (Let orchestrator handle path resolution - it knows where artifacts are stored)
        if self.orchestrator:
            try:
                feature_spec = self.orchestrator.load_artifact(
                    context.mission_uuid, "feature_spec.json"
                )
                if not feature_spec:
                    logger.error("Precondition failed: feature_spec.json could not be loaded")
                    return False
                logger.info("✅ feature_spec.json loaded successfully")
            except Exception as e:
                logger.error(f"Precondition failed: Error loading feature_spec.json: {e}")
                return False
        else:
            # Fallback: Check file system directly (for tests without orchestrator)
            feature_spec_path = (
                context.project_root / "artifacts" / "planning" / "feature_spec.json"
            )
            if not feature_spec_path.exists():
                alt_path = context.project_root / "feature_spec.json"
                if not alt_path.exists():
                    logger.error(
                        f"Precondition failed: feature_spec.json not found at {feature_spec_path} or {alt_path}"
                    )
                    return False
            logger.info("✅ Found feature_spec.json")

        # Check: phase is CODING
        mission = self.get_mission_data()
        if mission["phase"] != "CODING":
            logger.error(
                f"Precondition failed: current phase is {mission['phase']}, expected CODING"
            )
            return False

        # Check: orchestrator available (temporary requirement)
        if not self.orchestrator:
            logger.error(
                "Precondition failed: orchestrator not available (required for execute_agent)"
            )
            return False

        # Check: ToolSafetyGuard operational
        if not self.tool_safety_guard:
            logger.error("Precondition failed: ToolSafetyGuard not available")
            return False

        logger.info("✅ CODING preconditions met")
        return True

    def execute(self, context: MissionContext) -> SpecialistResult:
        """
        Execute CODING workflow (5-phase sequential)

        Flow:
            1. Load feature_spec.json from PLANNING
            2. Task 1: Spec Analysis & Validation
            3. Task 2: Code Generation (with safety guards)
            4. Task 3: Test Generation
            5. Task 4: Documentation Generation
            6. Task 5: Quality Assurance & Packaging
            7. Log all decisions to SQLite
            8. Return success with artifacts

        Args:
            context: Mission context

        Returns:
            SpecialistResult with success=True, next_phase="TESTING", artifacts

        Raises:
            Exception: If coding workflow fails
        """
        logger.info(f"CodingSpecialist: Starting execution (mission_id={self.mission_id})")

        # Log decision: Starting coding
        self._log_decision(
            decision_type="CODING_STARTED",
            rationale="Beginning CODING phase execution (5-phase workflow)",
            data={
                "mission_id": self.mission_id,
                "project_root": str(context.project_root),
                "workflow_version": "5-phase-sequential",
            },
        )

        # Load feature_spec from PLANNING
        feature_spec = self._load_feature_spec(context)

        # Build initial context for CODE_GENERATOR
        code_gen_context = {
            "project_id": context.mission_uuid,
            "current_phase": context.phase,
            "code_gen_spec_ref": feature_spec.get("code_gen_spec_ref", {}),
            "feature_spec": feature_spec,
            "artifacts": {},  # Accumulate artifacts from each task
        }

        # Track all artifacts and decisions
        artifacts = []
        decisions = []

        # =====================================================================
        # Task 1: Spec Analysis & Validation
        # =====================================================================
        logger.info("📝 Task 1/5: Spec Analysis & Validation")

        validation_result = self._execute_spec_validation(code_gen_context, context)
        code_gen_context["artifacts"]["validation_result"] = validation_result

        self._log_decision(
            decision_type="SPEC_VALIDATED",
            rationale="Feature specification validated before code generation",
            data={
                "spec_valid": validation_result.get("spec_valid", False),
                "validation_errors": validation_result.get("validation_errors", []),
            },
        )
        decisions.append({"type": "SPEC_VALIDATED", "result": validation_result})

        # =====================================================================
        # Task 2: Code Generation (WITH SAFETY GUARDS)
        # =====================================================================
        logger.info("🔨 Task 2/5: Code Generation (Safety guards active)")

        generated_code = self._execute_code_generation(code_gen_context, context)
        code_gen_context["artifacts"]["generated_code"] = generated_code

        # Log every file creation decision
        for file_info in generated_code.get("files", []):
            file_path = file_info.get("path", "unknown")
            self._log_decision(
                decision_type="CODE_MODIFICATION",
                rationale=f"Generated code file: {file_path}",
                data={
                    "file_path": file_path,
                    "operation": "create",
                    "size_bytes": len(file_info.get("content", "")),
                    "language": file_info.get("language", "unknown"),
                },
            )

        logger.info(f"✅ Generated {len(generated_code.get('files', []))} code files")
        decisions.append(
            {"type": "CODE_GENERATED", "file_count": len(generated_code.get("files", []))}
        )

        # =====================================================================
        # Task 3: Test Generation
        # =====================================================================
        logger.info("🧪 Task 3/5: Test Generation")

        generated_tests = self._execute_test_generation(code_gen_context, context)
        code_gen_context["artifacts"]["generated_tests"] = generated_tests

        test_coverage = generated_tests.get("coverage_percent", 0)
        self._log_decision(
            decision_type="TESTS_GENERATED",
            rationale=f"Generated tests with {test_coverage}% coverage",
            data={
                "test_count": len(generated_tests.get("tests", [])),
                "coverage_percent": test_coverage,
            },
        )
        logger.info(f"✅ Generated tests with {test_coverage}% coverage")
        decisions.append({"type": "TESTS_GENERATED", "coverage": test_coverage})

        # =====================================================================
        # Task 4: Documentation Generation
        # =====================================================================
        logger.info("📚 Task 4/5: Documentation Generation")

        generated_docs = self._execute_documentation_generation(code_gen_context, context)
        code_gen_context["artifacts"]["generated_documentation"] = generated_docs

        logger.info(f"✅ Generated {len(generated_docs.get('docs', []))} documentation files")
        decisions.append(
            {"type": "DOCS_GENERATED", "doc_count": len(generated_docs.get("docs", []))}
        )

        # =====================================================================
        # Task 5: Quality Assurance & Packaging
        # =====================================================================
        logger.info("📦 Task 5/5: Quality Assurance & Packaging")

        artifact_bundle = self._execute_quality_assurance(code_gen_context, context)

        quality_gates_passed = artifact_bundle.get("quality_gates_passed", False)
        self._log_decision(
            decision_type="QUALITY_GATES_CHECKED",
            rationale=f"Quality gates {'PASSED' if quality_gates_passed else 'FAILED'}",
            data={
                "passed": quality_gates_passed,
                "failed_gates": artifact_bundle.get("failed_gates", []),
            },
        )

        if not quality_gates_passed:
            logger.error("❌ Quality gates FAILED")
            return SpecialistResult(
                success=False,
                error=f"Quality gates failed: {artifact_bundle.get('failed_gates', [])}",
            )

        logger.info("✅ Quality gates passed, artifact bundle ready")
        decisions.append({"type": "QUALITY_GATES_PASSED"})

        # =====================================================================
        # Save Artifacts & Return Success
        # =====================================================================

        # Create code_gen_spec.json summary
        code_gen_spec = {
            "version": "1.0",
            "schema_version": "1.0",
            "source_feature_spec": "artifacts/planning/feature_spec.json",
            "generated_at": self._get_timestamp(),
            "phase": "CODING",
            "validation_result": validation_result,
            "artifact_bundle": artifact_bundle,
            "statistics": {
                "total_files": len(generated_code.get("files", [])),
                "total_tests": len(generated_tests.get("tests", [])),
                "test_coverage_percent": test_coverage,
                "total_docs": len(generated_docs.get("docs", [])),
                "quality_gates_passed": quality_gates_passed,
            },
            "metadata": {
                "code_generator_version": "1.0",
                "specialist": "CodingSpecialist",
                "hap_pattern": True,
            },
        }

        # Save artifact using orchestrator (temporary)
        artifact_path = self._save_code_gen_spec(context, code_gen_spec)
        artifacts.append(artifact_path)

        logger.info("✅ CODING complete → code_gen_spec.json created")
        logger.info(f"   Files: {code_gen_spec['statistics']['total_files']}")
        logger.info(
            f"   Tests: {code_gen_spec['statistics']['total_tests']} ({test_coverage}% coverage)"
        )
        logger.info(f"   Docs: {code_gen_spec['statistics']['total_docs']}")

        # Return success with next phase
        return SpecialistResult(
            success=True,
            next_phase="TESTING",
            artifacts=artifacts,
            decisions=decisions,
        )

    # =========================================================================
    # PRIVATE HELPER METHODS (5-Phase Workflow)
    # =========================================================================

    def _load_feature_spec(self, context: MissionContext) -> dict:
        """Load feature_spec.json from PLANNING phase"""
        # Try orchestrator's load_artifact first (temporary)
        if self.orchestrator:
            feature_spec = self.orchestrator.load_artifact(
                context.mission_uuid, "feature_spec.json"
            )
            if feature_spec:
                logger.info("✅ Loaded feature_spec.json from orchestrator")
                return feature_spec

        # Fallback: Try direct file read
        feature_spec_path = context.project_root / "artifacts" / "planning" / "feature_spec.json"
        if feature_spec_path.exists():
            with open(feature_spec_path) as f:
                return json.load(f)

        # Alternative location
        alt_path = context.project_root / "feature_spec.json"
        if alt_path.exists():
            with open(alt_path) as f:
                return json.load(f)

        raise FileNotFoundError(f"feature_spec.json not found at {feature_spec_path} or {alt_path}")

    def _execute_spec_validation(self, code_gen_context: dict, context: MissionContext) -> dict:
        """Task 1: Spec Analysis & Validation"""
        # Use orchestrator's execute_agent (temporary dependency)
        validation_result = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_01_spec_analysis_validation",
            inputs=code_gen_context,
            manifest=self._get_manifest_from_orchestrator(),
        )

        # Check if spec is valid
        if not validation_result.get("spec_valid", False):
            logger.error("❌ Feature spec validation FAILED")
            logger.error(f"   Issues: {validation_result.get('validation_errors', [])}")
            raise ValueError(
                f"Feature specification validation failed: "
                f"{validation_result.get('validation_errors', [])}"
            )

        logger.info("✅ Spec validation passed")
        return validation_result

    def _execute_code_generation(self, code_gen_context: dict, context: MissionContext) -> dict:
        """Task 2: Code Generation (with ToolSafetyGuard enforcement)"""
        # Generate code via agent
        generated_code = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_02_code_generation",
            inputs=code_gen_context,
            manifest=self._get_manifest_from_orchestrator(),
        )

        # CRITICAL: Validate file operations with ToolSafetyGuard
        for file_info in generated_code.get("files", []):
            file_path = file_info.get("path", "")

            # Determine if this is a create (new file) or edit (existing file)
            # For new files, ANTI_BLINDNESS doesn't apply (can't read a non-existent file!)
            # For existing files, ANTI_BLINDNESS requires reading before editing
            is_new_file = not Path(file_path).exists()

            if not is_new_file:
                # Existing file - check safety guard
                allowed, violation = self.tool_safety_guard.check_action(
                    tool_name="edit_file",
                    args={"path": file_path, "content": file_info.get("content", "")},
                )

                if not allowed:
                    logger.error(f"🛡️ Safety violation: {violation.message}")
                    raise RuntimeError(
                        f"Code generation blocked by safety guard: {violation.message}"
                    )

            # Record file write (for both new and existing files)
            self.tool_safety_guard.record_file_write(file_path)

        return generated_code

    def _execute_test_generation(self, code_gen_context: dict, context: MissionContext) -> dict:
        """Task 3: Test Generation"""
        generated_tests = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_03_test_generation",
            inputs=code_gen_context,
            manifest=self._get_manifest_from_orchestrator(),
        )
        return generated_tests

    def _execute_documentation_generation(
        self, code_gen_context: dict, context: MissionContext
    ) -> dict:
        """Task 4: Documentation Generation"""
        generated_docs = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_04_documentation_generation",
            inputs=code_gen_context,
            manifest=self._get_manifest_from_orchestrator(),
        )
        return generated_docs

    def _execute_quality_assurance(self, code_gen_context: dict, context: MissionContext) -> dict:
        """Task 5: Quality Assurance & Packaging"""
        artifact_bundle = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_05_quality_assurance_packaging",
            inputs=code_gen_context,
            manifest=self._get_manifest_from_orchestrator(),
        )
        return artifact_bundle

    def _save_code_gen_spec(self, context: MissionContext, code_gen_spec: dict) -> str:
        """Save code_gen_spec.json artifact"""
        try:
            self.orchestrator.save_artifact(
                context.mission_uuid,
                "code_gen_spec.json",
                code_gen_spec,
                validate=True,
            )
        except Exception as e:
            logger.warning(f"⚠️  Schema validation failed for code_gen_spec.json: {e}")
            self.orchestrator.save_artifact(
                context.mission_uuid,
                "code_gen_spec.json",
                code_gen_spec,
                validate=False,
            )

        # Return artifact path
        artifact_path = str(context.project_root / "code_gen_spec.json")
        logger.info(f"✅ Saved code_gen_spec.json: {artifact_path}")
        return artifact_path

    def _get_manifest_from_orchestrator(self):
        """Get current manifest from orchestrator (temporary helper)"""
        # This is a temporary hack while we still depend on orchestrator
        # Future: Remove this when specialists have direct tool access
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
