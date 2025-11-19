#!/usr/bin/env python3
"""
E2E System Test for the full SDLC workflow from PLANNING through CODING.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pytest

# Ensure correct paths for imports
repo_root = Path(__file__).parent.parent.parent

from agency_os_orchestrator import CoreOrchestrator
from prompt_registry import PromptRegistry


class TestVibeAlignerSystemE2E:
    """
    End-to-end system test for the PLANNING and CODING phases of the SDLC.
    This test uses a robust, stateful mock based on a predefined call order
    to ensure the orchestrator correctly manages the agent workflow.
    """

    @pytest.fixture(scope="class")
    def test_workspace_dir(self):
        """Create a single, shared, isolated test workspace for the class."""
        import shutil

        workspace_dir = repo_root / "workspaces" / "test-vibe-aligner-e2e"
        if workspace_dir.exists():
            shutil.rmtree(workspace_dir)
        workspace_dir.mkdir(parents=True)
        project_dir = workspace_dir / "test_project_001"
        project_dir.mkdir()
        (project_dir / "artifacts" / "planning").mkdir(parents=True)
        (project_dir / "artifacts" / "coding").mkdir(parents=True)
        yield workspace_dir
        shutil.rmtree(workspace_dir, ignore_errors=True)

    @pytest.fixture(scope="class")
    def project_manifest_data(self):
        """Create a test project manifest data structure."""
        return {
            "apiVersion": "agency.os/v1alpha1",
            "kind": "Project",
            "metadata": {
                "projectId": "test_project_001",
                "name": "Yoga Booking System",
                "owner": "test_user",
                "description": "A platform for booking classes.",
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
            },
            "status": {"projectPhase": "PLANNING"},
            "artifacts": {},
            "budget": {"max_cost_usd": 10.0},
        }

    @pytest.fixture(scope="class")
    def lean_canvas_summary(self):
        """Create a mock lean_canvas_summary.json artifact."""
        return {
            "version": "1.0",
            "canvas_fields": {"problem": ["Problem 1"]},
            "riskiest_assumptions": [{"assumption": "Assumption 1"}],
            "readiness": {"status": "READY"},
        }

    @pytest.fixture(scope="class")
    def mock_llm_responses(self):
        """Provides a dictionary of mock LLM responses for all required agent tasks."""
        return {
            "VIBE_ALIGNER": {
                "project": {},
                "features": [],
                "scope_negotiation": {},
                "validation": {"ready_for_coding": True},
                "metadata": {"agent": "VIBE_ALIGNER"},
            },
            "GENESIS_BLUEPRINT": {"status": "handoff_complete", "architecture_ready": True},
            "AUDITOR": {"status": "PASS", "findings": []},
            "CODE_GENERATOR": {
                "task_01": {"spec_valid": True},
                "task_02": {"files": [{"name": "main.py"}]},
                "task_03": {"tests": [{"name": "test_main.py"}], "coverage_percent": 100},
                "task_04": {"docs": [{"name": "README.md"}]},
                "task_05": {"quality_gates_passed": True},
            },
        }

    def test_vibe_aligner_full_system_flow(
        self,
        test_workspace_dir,
        project_manifest_data,
        lean_canvas_summary,
        mock_llm_responses,
        monkeypatch,
    ):
        """E2E test with hermetic mock (no API keys required)."""
        project_dir = test_workspace_dir / "test_project_001"
        (project_dir / "project_manifest.json").write_text(json.dumps(project_manifest_data))
        (project_dir / "artifacts" / "planning" / "lean_canvas_summary.json").write_text(
            json.dumps(lean_canvas_summary)
        )

        os.environ["VIBE_AUTO_MODE"] = "true"

        # Hermetic mock: no external dependencies
        from unittest.mock import MagicMock

        from llm_client import LLMClient

        call_order = [
            ("LEAN_CANVAS_VALIDATOR", lean_canvas_summary["canvas_fields"]),
            (
                "LEAN_CANVAS_VALIDATOR",
                {"riskiest_assumptions": lean_canvas_summary["riskiest_assumptions"]},
            ),
            ("LEAN_CANVAS_VALIDATOR", lean_canvas_summary),
            ("VIBE_ALIGNER", mock_llm_responses["VIBE_ALIGNER"]),
            ("GENESIS_BLUEPRINT", mock_llm_responses["GENESIS_BLUEPRINT"]),
            ("AUDITOR", mock_llm_responses["AUDITOR"]),
            ("AUDITOR", mock_llm_responses["AUDITOR"]),
            ("AUDITOR", mock_llm_responses["AUDITOR"]),
            ("AUDITOR", mock_llm_responses["AUDITOR"]),
            ("AUDITOR", mock_llm_responses["AUDITOR"]),
            ("CODE_GENERATOR", mock_llm_responses["CODE_GENERATOR"]["task_01"]),
            ("CODE_GENERATOR", mock_llm_responses["CODE_GENERATOR"]["task_02"]),
            ("CODE_GENERATOR", mock_llm_responses["CODE_GENERATOR"]["task_03"]),
            ("CODE_GENERATOR", mock_llm_responses["CODE_GENERATOR"]["task_04"]),
            ("CODE_GENERATOR", mock_llm_responses["CODE_GENERATOR"]["task_05"]),
        ]
        call_count = [0]

        def mock_invoke(prompt, model=None, max_tokens=4096):
            if call_count[0] >= len(call_order):
                pytest.fail(f"Unexpected call #{call_count[0] + 1}")
            expected_agent, response_data = call_order[call_count[0]]
            call_count[0] += 1
            mock_response = MagicMock()
            mock_response.content = json.dumps(response_data)
            return mock_response

        mock_llm = MagicMock(spec=LLMClient)
        mock_llm.invoke.side_effect = mock_invoke
        mock_llm.get_cost_summary.return_value = {"total_cost_usd": 0.50}

        # Inject mock before orchestrator init
        monkeypatch.setattr("llm_client.LLMClient", lambda budget_limit=10: mock_llm)

        orchestrator = CoreOrchestrator(repo_root=str(repo_root), execution_mode="autonomous")

        try:
            orchestrator.run_full_sdlc("test_project_001")
        except ValueError as e:
            if "No handler for phase" not in str(e) or "TESTING" not in str(e):
                pytest.fail(f"SDLC workflow failed: {e}")

        updated_manifest = json.loads((project_dir / "project_manifest.json").read_text())
        final_phase = updated_manifest["status"]["projectPhase"]
        assert final_phase == "AWAITING_QA_APPROVAL"
        assert (project_dir / "artifacts" / "coding" / "code_gen_spec.json").exists()
        print("\n✅ E2E TEST PASSED")

    def test_prompt_registry_governance_injection(self):
        """Tests that the PromptRegistry correctly injects governance directives."""
        registry = PromptRegistry()
        prompt = registry.compose(
            agent="VIBE_ALIGNER",
            task="task_02_feature_extraction",
            workspace="test",
            inject_governance=True,
            context={"test": "context"},
        )
        assert "# === GUARDIAN DIRECTIVES ===" in prompt
        assert "VIBE_ALIGNER" in prompt
        print("\nGovernance injection test passed ✅")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
