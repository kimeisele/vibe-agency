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
import yaml
from pathlib import Path
from typing import Dict, Any
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
            if substate.get('optional') and not self._should_execute_optional_state(substate):
                logger.info(f"⏭️  Skipping optional state: {substate['name']}")
                continue

            logger.info(f"▶️  Executing state: {substate['name']}")

            if substate['name'] == "RESEARCH":
                self._execute_research_state(manifest)
            elif substate['name'] == "BUSINESS_VALIDATION":
                self._execute_business_validation_state(manifest)
            elif substate['name'] == "FEATURE_SPECIFICATION":
                self._execute_feature_specification_state(manifest)

        # Transition to CODING
        from core_orchestrator import ProjectPhase
        manifest.current_phase = ProjectPhase.CODING
        manifest.current_sub_state = None

        logger.info("✅ PLANNING phase complete → transitioning to CODING")

    def _get_planning_substates(self):
        """Get PLANNING sub-states from workflow YAML"""
        for state in self.orchestrator.workflow.get('states', []):
            if state['name'] == 'PLANNING':
                return state.get('sub_states', [])
        return []

    def _should_execute_optional_state(self, state: Dict) -> bool:
        """
        Ask user if they want to execute optional state.
        """
        if state['name'] == "RESEARCH":
            print("\n" + "="*60)
            print("OPTIONAL: Research Phase")
            print("="*60)
            print("The Research phase provides fact-based market, technical, and user validation.")
            print("It includes: Competitor analysis, API evaluation, citation enforcement, personas.")
            print("Estimated time: 1-2 hours")
            print()
            response = input("Do you want to run the Research phase? (y/n): ").strip().lower()
            return response in ['y', 'yes']

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
            inputs={'project_context': manifest.metadata},
            manifest=manifest
        )

        tech_analysis = self.orchestrator.execute_agent(
            agent_name="TECH_RESEARCHER",
            task_id="api_evaluation",  # Main task
            inputs={'project_context': manifest.metadata},
            manifest=manifest
        )

        # FACT_VALIDATOR (blocking quality gate)
        fact_validation = self.orchestrator.execute_agent(
            agent_name="FACT_VALIDATOR",
            task_id="knowledge_base_audit",
            inputs={
                'market_analysis': market_analysis,
                'tech_analysis': tech_analysis
            },
            manifest=manifest
        )

        # Check quality gate
        quality_score = fact_validation.get('quality_score', 0)
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
                inputs={'project_context': manifest.metadata},
                manifest=manifest
            )

        # Compile research brief
        research_brief = {
            'version': '1.0',
            'market_analysis': market_analysis,
            'tech_analysis': tech_analysis,
            'fact_validation': fact_validation,
            'user_insights': user_insights,
            'handoff_to_lean_canvas': {
                'status': 'READY',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }

        # Save artifact
        self.orchestrator.save_artifact(
            manifest.project_id,
            'research_brief.json',
            research_brief,
            validate=True  # Schema validation
        )

        manifest.artifacts['research_brief'] = research_brief

        logger.info("✅ RESEARCH complete → research_brief.json")

    def _ask_user_researcher(self) -> bool:
        """Ask if user wants USER_RESEARCHER (optional within RESEARCH)"""
        print("\n📋 USER_RESEARCHER is optional (generates personas, interview scripts)")
        response = input("Include USER_RESEARCHER? (y/n): ").strip().lower()
        return response in ['y', 'yes']

    # -------------------------------------------------------------------------
    # BUSINESS VALIDATION STATE
    # -------------------------------------------------------------------------

    def _execute_business_validation_state(self, manifest) -> None:
        """
        Execute BUSINESS_VALIDATION sub-state.

        Flow:
        1. Load optional research_brief.json (if exists)
        2. Execute LEAN_CANVAS_VALIDATOR (uses research if available)
        3. Save lean_canvas_summary.json
        """
        logger.info("💼 Starting BUSINESS_VALIDATION sub-state...")

        # Load research brief if exists
        research_brief = self.orchestrator.load_artifact(
            manifest.project_id,
            'research_brief.json'
        )

        # Execute LEAN_CANVAS_VALIDATOR
        lean_canvas = self.orchestrator.execute_agent(
            agent_name="LEAN_CANVAS_VALIDATOR",
            task_id="lean_canvas_creation",
            inputs={
                'project_context': manifest.metadata,
                'research_brief': research_brief  # May be None
            },
            manifest=manifest
        )

        # Check readiness
        readiness = lean_canvas.get('readiness', {})
        if readiness.get('status') != 'READY':
            missing = readiness.get('missing_inputs', [])
            logger.warning(
                f"⚠️  Business validation not ready. Missing: {', '.join(missing)}"
            )
            # Continue anyway (user can iterate)

        # Save artifact
        self.orchestrator.save_artifact(
            manifest.project_id,
            'lean_canvas_summary.json',
            lean_canvas,
            validate=True
        )

        manifest.artifacts['lean_canvas_summary'] = lean_canvas

        logger.info("✅ BUSINESS_VALIDATION complete → lean_canvas_summary.json")

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
            manifest.project_id,
            'lean_canvas_summary.json'
        )

        if not lean_canvas:
            from core_orchestrator import ArtifactNotFoundError
            raise ArtifactNotFoundError(
                "lean_canvas_summary.json not found - BUSINESS_VALIDATION must run first"
            )

        # Execute VIBE_ALIGNER
        feature_spec = self.orchestrator.execute_agent(
            agent_name="VIBE_ALIGNER",
            task_id="scope_negotiation",
            inputs={
                'project_context': manifest.metadata,
                'lean_canvas_summary': lean_canvas
            },
            manifest=manifest
        )

        # Check validation
        validation = feature_spec.get('validation', {})
        if not validation.get('ready_for_genesis', False):
            logger.warning(
                "⚠️  Feature specification validation incomplete. "
                "Genesis Blueprint may need additional information."
            )

        # Save artifact
        self.orchestrator.save_artifact(
            manifest.project_id,
            'feature_spec.json',
            feature_spec,
            validate=True
        )

        manifest.artifacts['feature_spec'] = feature_spec

        logger.info("✅ FEATURE_SPECIFICATION complete → feature_spec.json")
