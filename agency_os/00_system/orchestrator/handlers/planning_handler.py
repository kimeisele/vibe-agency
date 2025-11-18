"""
Planning Phase Handler
======================

Handles PLANNING phase execution with sub-states:
1. RESEARCH (optional)
2. BUSINESS_VALIDATION
3. FEATURE_SPECIFICATION

Extracted from original orchestrator.py for GAD-002 hierarchical architecture.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PlanningHandler:
    """
    Handler for PLANNING phase execution.

    Manages:
    - Optional RESEARCH sub-state
    - BUSINESS_VALIDATION (Lean Canvas)
    - FEATURE_SPECIFICATION (Vibe Aligner)
    """

    def __init__(self, orchestrator):
        """
        Initialize handler.

        Args:
            orchestrator: CoreOrchestrator instance (parent)
        """
        self.orchestrator = orchestrator
        self.repo_root = orchestrator.repo_root

    def execute(self, manifest) -> None:
        """
        Execute PLANNING phase with all sub-states.

        Flow:
        1. [OPTIONAL] RESEARCH → research_brief.json
        2. BUSINESS_VALIDATION → lean_canvas_summary.json
        3. FEATURE_SPECIFICATION → feature_spec.json
        """
        logger.info("📋 Starting PLANNING phase")

        # Get planning sub-states from workflow
        substates = self._get_planning_substates()

        # Execute each sub-state
        for substate in substates:
            if substate.get("optional") and not self._should_execute_optional_state(substate):
                logger.info(f"⏭️  Skipping optional state: {substate['name']}")
                continue

            logger.info(f"▶️  Executing state: {substate['name']}")

            if substate["name"] == "RESEARCH":
                self._execute_research_state(manifest)
            elif substate["name"] == "BUSINESS_VALIDATION":
                self._execute_business_validation_state(manifest)
            elif substate["name"] == "FEATURE_SPECIFICATION":
                self._execute_feature_specification_state(manifest)
            elif substate["name"] == "ARCHITECTURE_DESIGN":
                self._execute_architecture_design_state(manifest)

        # Apply quality gates before transitioning to CODING (GAD-002 Decision 2)
        from core_orchestrator import ProjectPhase

        logger.info("🔒 Applying quality gates for PLANNING → CODING transition...")

        try:
            self.orchestrator.apply_quality_gates(
                transition_name="T1_StartCoding", manifest=manifest
            )
        except Exception as e:
            logger.error(f"❌ Quality gate BLOCKED transition to CODING: {e}")
            raise

        # Transition to CODING
        manifest.current_phase = ProjectPhase.CODING
        manifest.current_sub_state = None

        logger.info("✅ PLANNING phase complete → transitioning to CODING")

    def _get_planning_substates(self):
        """Get PLANNING sub-states from workflow YAML"""
        for state in self.orchestrator.workflow.get("states", []):
            if state["name"] == "PLANNING":
                return state.get("sub_states", [])
        return []

    def _should_execute_optional_state(self, state: dict) -> bool:
        """
        Determine if optional state should be executed.

        In auto mode (default): Skip all optional states
        In interactive mode: Ask user for each optional state

        Control via environment variable: VIBE_AUTO_MODE=true|false
        """
        import os

        auto_mode = os.getenv("VIBE_AUTO_MODE", "true").lower() == "true"

        if state["name"] == "RESEARCH":
            if auto_mode:
                logger.info(
                    "⏭️  Auto-skipping optional state: RESEARCH (set VIBE_AUTO_MODE=false for interactive)"
                )
                return False

            # Interactive mode
            print("\n" + "=" * 60)
            print("OPTIONAL: Research Phase")
            print("=" * 60)
            print("The Research phase provides fact-based market, technical, and user validation.")
            print(
                "It includes: Competitor analysis, API evaluation, citation enforcement, personas."
            )
            print("Estimated time: 1-2 hours")
            print()
            response = input("Do you want to run the Research phase? (y/n): ").strip().lower()
            return response in ["y", "yes"]

        return False

    # -------------------------------------------------------------------------
    # RESEARCH STATE EXECUTION
    # -------------------------------------------------------------------------

    def _execute_research_state(self, manifest) -> None:
        """
        Execute RESEARCH sub-state.

        Flow:
        1. MARKET_RESEARCHER → market_analysis
        2. TECH_RESEARCHER → tech_analysis
        3. FACT_VALIDATOR → fact_validation (BLOCKING)
        4. [OPTIONAL] USER_RESEARCHER → user_insights
        5. Compile → research_brief.json
        """
        logger.info("🔬 Starting RESEARCH sub-state...")

        # Execute agents in sequence using orchestrator.execute_agent()
        market_analysis = self.orchestrator.execute_agent(
            agent_name="MARKET_RESEARCHER",
            task_id="competitor_identification",  # Main task
            inputs={"project_context": manifest.metadata},
            manifest=manifest,
        )

        tech_analysis = self.orchestrator.execute_agent(
            agent_name="TECH_RESEARCHER",
            task_id="api_evaluation",  # Main task
            inputs={"project_context": manifest.metadata},
            manifest=manifest,
        )

        # FACT_VALIDATOR (blocking quality gate)
        fact_validation = self.orchestrator.execute_agent(
            agent_name="FACT_VALIDATOR",
            task_id="knowledge_base_audit",
            inputs={"market_analysis": market_analysis, "tech_analysis": tech_analysis},
            manifest=manifest,
        )

        # Check quality gate
        quality_score = fact_validation.get("quality_score", 0)
        if quality_score < 50:
            from core_orchestrator import QualityGateFailure

            raise QualityGateFailure(
                f"FACT_VALIDATOR blocked research. Quality score: {quality_score}/100. "
                f"Issues: {fact_validation.get('flagged_issues', [])}"
            )

        logger.info(f"✓ Quality gate passed (score: {quality_score}/100)")

        # USER_RESEARCHER (optional)
        user_insights = None
        if self._ask_user_researcher():
            user_insights = self.orchestrator.execute_agent(
                agent_name="USER_RESEARCHER",
                task_id="persona_generation",
                inputs={"project_context": manifest.metadata},
                manifest=manifest,
            )

        # Compile research brief
        research_brief = {
            "version": "1.0",
            "market_analysis": market_analysis,
            "tech_analysis": tech_analysis,
            "fact_validation": fact_validation,
            "user_insights": user_insights,
            "handoff_to_lean_canvas": {
                "status": "READY",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        }

        # Save artifact
        self.orchestrator.save_artifact(
            manifest.project_id,
            "research_brief.json",
            research_brief,
            validate=True,  # Schema validation
        )

        manifest.artifacts["research_brief"] = research_brief

        logger.info("✅ RESEARCH complete → research_brief.json")

    def _ask_user_researcher(self) -> bool:
        """Ask if user wants USER_RESEARCHER (optional within RESEARCH)"""
        print("\n📋 USER_RESEARCHER is optional (generates personas, interview scripts)")
        response = input("Include USER_RESEARCHER? (y/n): ").strip().lower()
        return response in ["y", "yes"]

    # -------------------------------------------------------------------------
    # BUSINESS VALIDATION STATE
    # -------------------------------------------------------------------------

    def _execute_business_validation_state(self, manifest) -> None:
        """
        Execute BUSINESS_VALIDATION sub-state.

        Flow (FULL SEQUENCE - Production Ready):
        1. Load optional research_brief.json (if exists)
        2. Task 01: Canvas Interview (collect all 9 fields)
        3. Task 02: Risk Analysis (identify riskiest assumptions)
        4. Task 03: Handoff (generate lean_canvas_summary.json)
        """
        logger.info("💼 Starting BUSINESS_VALIDATION sub-state...")

        # Load research brief if exists
        research_brief = self.orchestrator.load_artifact(manifest.project_id, "research_brief.json")

        # -------------------------------------------------------------------------
        # TASK 01: Canvas Interview
        # -------------------------------------------------------------------------
        logger.info("📋 Step 1/3: Canvas Interview (collecting 9 Lean Canvas fields)...")

        canvas_responses = self.orchestrator.execute_agent(
            agent_name="LEAN_CANVAS_VALIDATOR",
            task_id="01_canvas_interview",
            inputs={
                "project_context": manifest.metadata,
                "research_brief": research_brief,  # May be None
                "user_initial_idea": manifest.metadata.get("description", "New project"),
            },
            manifest=manifest,
        )

        logger.info("✓ Canvas interview complete")

        # -------------------------------------------------------------------------
        # TASK 02: Risk Analysis
        # -------------------------------------------------------------------------
        logger.info("🔍 Step 2/3: Risk Analysis (identifying riskiest assumptions)...")

        risk_analysis = self.orchestrator.execute_agent(
            agent_name="LEAN_CANVAS_VALIDATOR",
            task_id="02_risk_analysis",
            inputs={"canvas_responses": canvas_responses, "project_context": manifest.metadata},
            manifest=manifest,
        )

        logger.info("✓ Risk analysis complete")

        # -------------------------------------------------------------------------
        # TASK 03: Handoff Artifact
        # -------------------------------------------------------------------------
        logger.info("📦 Step 3/3: Generating lean_canvas_summary.json artifact...")

        lean_canvas = self.orchestrator.execute_agent(
            agent_name="LEAN_CANVAS_VALIDATOR",
            task_id="03_handoff",
            inputs={
                "canvas_responses": canvas_responses,
                "riskiest_assumptions": risk_analysis.get("riskiest_assumptions", []),
                "project_context": manifest.metadata,
                "research_brief": research_brief,
            },
            manifest=manifest,
        )

        # Check readiness
        readiness = lean_canvas.get("readiness", {})
        if readiness.get("status") != "READY":
            missing = readiness.get("missing_inputs", [])
            logger.warning(f"⚠️  Business validation not ready. Missing: {', '.join(missing)}")
            # Continue anyway (user can iterate)

        # Save artifact
        self.orchestrator.save_artifact(
            manifest.project_id, "lean_canvas_summary.json", lean_canvas, validate=True
        )

        manifest.artifacts["lean_canvas_summary"] = lean_canvas

        # Write handoff for next agent (VIBE_ALIGNER)
        import json

        workspace_path = self.orchestrator._get_manifest_path(manifest.project_id).parent
        handoff = {
            "from_agent": "LEAN_CANVAS_VALIDATOR",
            "to_agent": "VIBE_ALIGNER",
            "completed": "Business validation (Lean Canvas)",
            "todos": [
                "Extract customer segments from lean_canvas_summary.json",
                "Map features to customer problems and solutions",
                "Calculate complexity using FAE_constraints.yaml",
                "Start interactive scope negotiation with user",
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        handoff_path = workspace_path / "handoff.json"
        with open(handoff_path, "w") as f:
            json.dump(handoff, f, indent=2)

        logger.info(
            "✅ BUSINESS_VALIDATION complete → lean_canvas_summary.json + handoff.json (full sequence: 01→02→03)"
        )

    # -------------------------------------------------------------------------
    # FEATURE SPECIFICATION STATE
    # -------------------------------------------------------------------------

    def _execute_feature_specification_state(self, manifest) -> None:
        """
        Execute FEATURE_SPECIFICATION sub-state.

        Flow:
        1. Load lean_canvas_summary.json
        2. Execute VIBE_ALIGNER
        3. Save feature_spec.json
        """
        logger.info("⚙️  Starting FEATURE_SPECIFICATION sub-state...")

        # Load lean canvas (required)
        lean_canvas = self.orchestrator.load_artifact(
            manifest.project_id, "lean_canvas_summary.json"
        )

        if not lean_canvas:
            from core_orchestrator import ArtifactNotFoundError

            raise ArtifactNotFoundError(
                "lean_canvas_summary.json not found - BUSINESS_VALIDATION must run first"
            )

        # Load handoff from previous agent
        import json

        workspace_path = self.orchestrator._get_manifest_path(manifest.project_id).parent
        handoff_path = workspace_path / "handoff.json"

        handoff_todos = None
        if handoff_path.exists():
            with open(handoff_path) as f:
                handoff = json.load(f)
                todos_list = handoff.get("todos", [])
                handoff_todos = "\n".join(f"- {todo}" for todo in todos_list)
                logger.info(f"📝 Loaded {len(todos_list)} TODOs from previous agent")
        else:
            handoff_todos = "No handoff found (starting fresh)"
            logger.info("📝 No handoff found, agent starting fresh")

        # Execute VIBE_ALIGNER
        feature_spec = self.orchestrator.execute_agent(
            agent_name="VIBE_ALIGNER",
            task_id="05_scope_negotiation",
            inputs={
                "project_context": manifest.metadata,
                "lean_canvas_summary": lean_canvas,
                "handoff_todos": handoff_todos,
            },
            manifest=manifest,
        )

        # Check validation
        validation = feature_spec.get("validation", {})
        if not validation.get("ready_for_genesis", False):
            logger.warning(
                "⚠️  Feature specification validation incomplete. "
                "Genesis Blueprint may need additional information."
            )

        # Save artifact
        self.orchestrator.save_artifact(
            manifest.project_id, "feature_spec.json", feature_spec, validate=True
        )

        manifest.artifacts["feature_spec"] = feature_spec

        # Write handoff for next agent (GENESIS_BLUEPRINT)
        workspace_path = self.orchestrator._get_manifest_path(manifest.project_id).parent
        handoff = {
            "from_agent": "VIBE_ALIGNER",
            "to_agent": "GENESIS_BLUEPRINT",
            "completed": "Feature specification and scope negotiation",
            "todos": [
                "Select core modules from feature_spec.json",
                "Design extension modules for complex features",
                "Generate config schema (genesis.yaml)",
                "Validate architecture against FAE constraints",
                "Create code_gen_spec.json for CODING phase",
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        handoff_path = workspace_path / "handoff.json"
        with open(handoff_path, "w") as f:
            json.dump(handoff, f, indent=2)

        logger.info("✅ FEATURE_SPECIFICATION complete → feature_spec.json + handoff.json")

    # -------------------------------------------------------------------------
    # ARCHITECTURE DESIGN STATE
    # -------------------------------------------------------------------------

    def _execute_architecture_design_state(self, manifest) -> None:
        """
        Execute ARCHITECTURE_DESIGN sub-state.

        Flow:
        1. Load feature_spec.json
        2. Execute GENESIS_BLUEPRINT
        3. Save architecture.json + code_gen_spec.json
        """
        logger.info("🏗️  Starting ARCHITECTURE_DESIGN sub-state...")

        # Load feature spec (required)
        feature_spec = self.orchestrator.load_artifact(manifest.project_id, "feature_spec.json")

        if not feature_spec:
            from core_orchestrator import ArtifactNotFoundError

            raise ArtifactNotFoundError(
                "feature_spec.json not found - FEATURE_SPECIFICATION must run first"
            )

        # Check if ready for architecture design
        validation = feature_spec.get("validation", {})
        if not validation.get("ready_for_genesis", False):
            logger.warning(
                "⚠️  Feature spec validation incomplete but continuing with architecture design. "
                "GENESIS_BLUEPRINT may request additional clarifications."
            )

        # Load handoff from previous agent
        import json

        workspace_path = self.orchestrator._get_manifest_path(manifest.project_id).parent
        handoff_path = workspace_path / "handoff.json"

        handoff_todos = None
        if handoff_path.exists():
            with open(handoff_path) as f:
                handoff = json.load(f)
                todos_list = handoff.get("todos", [])
                handoff_todos = "\n".join(f"- {todo}" for todo in todos_list)
                logger.info(f"📝 Loaded {len(todos_list)} TODOs from previous agent")
        else:
            handoff_todos = "No handoff found (starting fresh)"
            logger.info("📝 No handoff found, agent starting fresh")

        # Execute GENESIS_BLUEPRINT
        architecture_output = self.orchestrator.execute_agent(
            agent_name="GENESIS_BLUEPRINT",
            task_id="05_handoff",
            inputs={
                "feature_spec": feature_spec,
                "project_context": manifest.metadata,
                "handoff_todos": handoff_todos,
            },
            manifest=manifest,
        )

        # GENESIS_BLUEPRINT should return both architecture.json and code_gen_spec.json
        # (either as separate fields or as a combined output - we'll handle both)

        if (
            isinstance(architecture_output, dict)
            and "architecture" in architecture_output
            and "code_gen_spec" in architecture_output
        ):
            # Separate outputs
            architecture = architecture_output["architecture"]
            code_gen_spec = architecture_output["code_gen_spec"]
        else:
            # Combined output (GENESIS_BLUEPRINT returns everything in one object)
            # Split it based on schema expectations
            architecture = architecture_output
            code_gen_spec = {
                "modules": architecture_output.get("modules", []),
                "dependencies": architecture_output.get("dependencies", []),
                "build_config": architecture_output.get("build_config", {}),
                "test_strategy": architecture_output.get("test_strategy", {}),
            }

        # Save architecture.json
        self.orchestrator.save_artifact(
            manifest.project_id,
            "architecture.json",
            architecture,
            validate=False,  # TODO: Add schema validation in Phase 4
        )

        # Save code_gen_spec.json (CRITICAL for CODING phase!)
        self.orchestrator.save_artifact(
            manifest.project_id,
            "code_gen_spec.json",
            code_gen_spec,
            validate=False,  # TODO: Add schema validation in Phase 4
        )

        manifest.artifacts["architecture"] = architecture
        manifest.artifacts["code_gen_spec"] = code_gen_spec

        logger.info("✅ ARCHITECTURE_DESIGN complete → architecture.json + code_gen_spec.json")
