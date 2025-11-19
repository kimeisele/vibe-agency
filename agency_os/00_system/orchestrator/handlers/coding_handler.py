"""
Coding Phase Handler
====================

Handles CODING phase execution by invoking the CODE_GENERATOR agent.

Implements GAD-002 Phase 4: Full CODE_GENERATOR integration
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CodingHandler:
    """
    Handler for CODING phase execution.

    Invokes CODE_GENERATOR agent with 5-phase sequential workflow:
    1. Spec Analysis & Validation
    2. Code Generation
    3. Test Generation
    4. Documentation Generation
    5. Quality Assurance & Packaging

    Phase 4 Implementation: Full CODE_GENERATOR integration using llm_client.py
    """

    def __init__(self, orchestrator):
        """Initialize handler"""
        self.orchestrator = orchestrator

    def execute(self, manifest) -> None:
        """
        Execute CODING phase.

        Flow:
        1. Load feature_spec.json from PLANNING
        2. Execute CODE_GENERATOR 5-phase workflow
        3. Save artifact_bundle
        4. Transition to TESTING
        """
        logger.info("💻 Starting CODING phase")

        # Load feature spec from PLANNING
        feature_spec = self.orchestrator.load_artifact(manifest.project_id, "feature_spec.json")

        if not feature_spec:
            try:
                from core_orchestrator import ArtifactNotFoundError  # legacy relative
            except ModuleNotFoundError:
                try:
                    from orchestrator.core_orchestrator import ArtifactNotFoundError  # shim
                except ModuleNotFoundError:
                    from agency_os_orchestrator import ArtifactNotFoundError  # top-level alias
            raise ArtifactNotFoundError(
                "feature_spec.json not found - PLANNING phase must complete first"
            )

        logger.info("✓ Loaded feature_spec.json from PLANNING phase")

        # Build initial context for CODE_GENERATOR
        code_gen_context = {
            "project_id": manifest.project_id,
            "current_phase": manifest.current_phase.value,
            "code_gen_spec_ref": feature_spec.get("code_gen_spec_ref", {}),
            "feature_spec": feature_spec,
            "artifacts": {},  # Will accumulate artifacts from each task
        }

        # =====================================================================
        # Task 1: Spec Analysis & Validation
        # =====================================================================
        logger.info("📝 Task 1/5: Spec Analysis & Validation")

        validation_result = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_01_spec_analysis_validation",
            inputs=code_gen_context,
            manifest=manifest,
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
        code_gen_context["artifacts"]["validation_result"] = validation_result

        # =====================================================================
        # Task 2: Code Generation
        # =====================================================================
        logger.info("🔨 Task 2/5: Code Generation")

        generated_code = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_02_code_generation",
            inputs=code_gen_context,
            manifest=manifest,
        )

        logger.info(f"✅ Generated {len(generated_code.get('files', []))} code files")
        code_gen_context["artifacts"]["generated_code"] = generated_code

        # =====================================================================
        # Task 3: Test Generation
        # =====================================================================
        logger.info("🧪 Task 3/5: Test Generation")

        generated_tests = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_03_test_generation",
            inputs=code_gen_context,
            manifest=manifest,
        )

        test_coverage = generated_tests.get("coverage_percent", 0)
        logger.info(f"✅ Generated tests with {test_coverage}% coverage")
        code_gen_context["artifacts"]["generated_tests"] = generated_tests

        # =====================================================================
        # Task 4: Documentation Generation
        # =====================================================================
        logger.info("📚 Task 4/5: Documentation Generation")

        generated_docs = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_04_documentation_generation",
            inputs=code_gen_context,
            manifest=manifest,
        )

        logger.info(f"✅ Generated {len(generated_docs.get('docs', []))} documentation files")
        code_gen_context["artifacts"]["generated_documentation"] = generated_docs

        # =====================================================================
        # Task 5: Quality Assurance & Packaging
        # =====================================================================
        logger.info("📦 Task 5/5: Quality Assurance & Packaging")

        artifact_bundle = self.orchestrator.execute_agent(
            agent_name="CODE_GENERATOR",
            task_id="task_05_quality_assurance_packaging",
            inputs=code_gen_context,
            manifest=manifest,
        )

        # Check quality gates
        quality_gates_passed = artifact_bundle.get("quality_gates_passed", False)
        if not quality_gates_passed:
            logger.error("❌ Quality gates FAILED")
            logger.error(f"   Failed gates: {artifact_bundle.get('failed_gates', [])}")
            raise ValueError(
                f"Code generation quality gates failed: {artifact_bundle.get('failed_gates', [])}"
            )

        logger.info("✅ Quality gates passed, artifact bundle ready")

        # =====================================================================
        # Save Artifacts
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
            "metadata": {"code_generator_version": "1.0", "orchestrator_version": "1.0"},
        }

        # Save code_gen_spec artifact
        try:
            self.orchestrator.save_artifact(
                manifest.project_id,
                "code_gen_spec.json",
                code_gen_spec,
                validate=True,
            )
        except Exception as e:
            logger.warning(f"⚠️  Schema validation failed for code_gen_spec.json: {e}")
            self.orchestrator.save_artifact(
                manifest.project_id,
                "code_gen_spec.json",
                code_gen_spec,
                validate=False,
            )

        manifest.artifacts["code_gen_spec"] = code_gen_spec

        logger.info("✅ CODING complete → code_gen_spec.json created")
        logger.info(f"   Files: {code_gen_spec['statistics']['total_files']}")
        logger.info(
            f"   Tests: {code_gen_spec['statistics']['total_tests']} ({test_coverage}% coverage)"
        )
        logger.info(f"   Docs: {code_gen_spec['statistics']['total_docs']}")

        # Transition to TESTING
        try:
            from core_orchestrator import ProjectPhase  # legacy
        except ModuleNotFoundError:
            try:
                from orchestrator.core_orchestrator import ProjectPhase
            except ModuleNotFoundError:
                from agency_os_orchestrator import ProjectPhase
        manifest.current_phase = ProjectPhase.TESTING

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.utcnow().isoformat() + "Z"
