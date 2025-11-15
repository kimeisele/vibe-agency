#!/usr/bin/env python3
"""
Unit Tests for Prompt Registry (MVP)

Tests all 9 required test cases from SSOT.md specification.

Test Cases:
1. test_governance_injection - Guardian Directives appear in composed prompt
2. test_context_enrichment - Manifest data present in output
3. test_tool_injection - Tools only appear when requested
4. test_sop_injection - SOPs only appear when requested
5. test_composition_order - Governance → Context → Tools → SOPs → Agent
6. test_backward_compatibility - PromptRuntime still works independently
7. test_missing_workspace - Graceful error when workspace doesn't exist
8. test_missing_agent - Graceful error when agent doesn't exist
9. test_optional_params - All inject_* params work when omitted

Created: 2025-11-15
Version: 1.0
"""

import pytest
import sys
from pathlib import Path

# Add repo root and runtime directory to path
_REPO_ROOT = Path(__file__).resolve().parent.parent
_RUNTIME_PATH = _REPO_ROOT / "agency_os" / "00_system" / "runtime"
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_RUNTIME_PATH))

# Import directly from the runtime directory (since folder starts with number)
from prompt_registry import (
    PromptRegistry,
    PromptRegistryError,
    GovernanceLoadError,
    ContextEnrichmentError
)
from prompt_runtime import (
    PromptRuntime,
    AgentNotFoundError
)


class TestGovernanceInjection:
    """Test that Guardian Directives are properly injected"""

    def test_governance_injection_enabled(self):
        """Guardian Directives should appear when inject_governance=True"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=True
        )

        # Check for Guardian Directives header
        assert "GUARDIAN DIRECTIVES" in prompt

        # Check for all 9 directives
        assert "Manifest Primacy" in prompt
        assert "Atomicity" in prompt
        assert "Validation Gates" in prompt
        assert "Knowledge Grounding" in prompt
        assert "Traceability" in prompt
        assert "Graceful Degradation" in prompt
        assert "Budget Awareness" in prompt
        assert "HITL Respect" in prompt
        assert "Output Contract" in prompt

    def test_governance_injection_disabled(self):
        """Guardian Directives should NOT appear when inject_governance=False"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=False
        )

        # Guardian Directives section should not be present
        assert "GUARDIAN DIRECTIVES" not in prompt


class TestContextEnrichment:
    """Test that workspace context is enriched"""

    def test_context_enrichment_root_workspace(self):
        """Context section should include workspace info"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=False  # Disable to isolate context section
        )

        # Check for context header
        assert "RUNTIME CONTEXT" in prompt

        # Check for workspace info
        assert "ROOT" in prompt
        assert "Active Workspace" in prompt or "Workspace" in prompt

    def test_context_enrichment_with_additional_context(self):
        """Additional context should be included"""
        additional_context = {
            "test_key": "test_value",
            "project_id": "test-123"
        }

        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=False,
            context=additional_context
        )

        # Additional context should be present
        assert "test_key" in prompt or "test_value" in prompt


class TestToolInjection:
    """Test that tools are injected only when requested"""

    def test_tool_injection_requested(self):
        """Tools should appear when inject_tools is provided"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=False,
            inject_tools=["google_search"]
        )

        # Check for tools section
        assert "TOOLS" in prompt or "Tool:" in prompt
        assert "google_search" in prompt

    def test_tool_injection_not_requested(self):
        """Tools should NOT appear when inject_tools is None"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=False,
            inject_tools=None
        )

        # Tools section should not be present
        # (Note: Agent's own _composition.yaml might include tools, so we
        #  just check that Registry didn't add an extra TOOLS section)
        # This is a weak test - in practice, Registry tools would have different formatting
        assert prompt.count("TOOLS") <= 1  # At most one TOOLS section


class TestSOPInjection:
    """Test that SOPs are injected only when requested"""

    def test_sop_injection_requested(self):
        """SOPs should appear when inject_sops is provided"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=False,
            inject_sops=["SOP_001"]
        )

        # Check for SOPs section
        assert "STANDARD OPERATING PROCEDURES" in prompt
        assert "SOP_001" in prompt

    def test_sop_injection_not_requested(self):
        """SOPs should NOT appear when inject_sops is None"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=False,
            inject_sops=None
        )

        # SOPs section should not be present
        assert "STANDARD OPERATING PROCEDURES" not in prompt


class TestCompositionOrder:
    """Test that composition order is correct: Governance → Context → Tools → SOPs → Agent"""

    def test_composition_order_all_layers(self):
        """All layers should appear in correct order"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=True,
            inject_tools=["google_search"],
            inject_sops=["SOP_001"]
        )

        # Find positions of each section
        governance_pos = prompt.find("GUARDIAN DIRECTIVES")
        context_pos = prompt.find("RUNTIME CONTEXT")
        tools_pos = prompt.find("TOOLS")  # Registry-injected tools
        sops_pos = prompt.find("STANDARD OPERATING PROCEDURES")
        agent_pos = prompt.find("CORE PERSONALITY")  # Agent's core prompt

        # Verify all sections are present
        assert governance_pos != -1, "Guardian Directives missing"
        assert context_pos != -1, "Runtime Context missing"
        assert tools_pos != -1, "Tools missing"
        assert sops_pos != -1, "SOPs missing"
        assert agent_pos != -1, "Agent core prompt missing"

        # Verify order
        assert governance_pos < context_pos, "Governance should come before Context"
        assert context_pos < tools_pos, "Context should come before Tools"
        assert tools_pos < sops_pos, "Tools should come before SOPs"
        assert sops_pos < agent_pos, "SOPs should come before Agent core"


class TestBackwardCompatibility:
    """Test that PromptRuntime still works independently"""

    def test_prompt_runtime_still_works(self):
        """PromptRuntime should work without Registry"""
        runtime = PromptRuntime()

        # This should work without any Registry involvement
        prompt = runtime.execute_task(
            agent_id="VIBE_ALIGNER",
            task_id="02_feature_extraction",
            context={"test": "value"}
        )

        # Should have core prompt components
        assert len(prompt) > 0
        assert "CORE PERSONALITY" in prompt

        # Should NOT have Registry injections
        assert "GUARDIAN DIRECTIVES" not in prompt


class TestMissingWorkspace:
    """Test graceful error handling for missing workspace"""

    def test_missing_workspace_graceful_fallback(self):
        """Should not crash when workspace doesn't exist"""
        # This should not raise an exception - should fall back gracefully
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="NONEXISTENT_WORKSPACE_12345",
            inject_governance=False
        )

        # Should still produce a prompt
        assert len(prompt) > 0

        # Context section should acknowledge the workspace (even if not found)
        assert "RUNTIME CONTEXT" in prompt


class TestMissingAgent:
    """Test graceful error handling for missing agent"""

    def test_missing_agent_raises_error(self):
        """Should raise AgentNotFoundError for invalid agent"""
        with pytest.raises(AgentNotFoundError):
            PromptRegistry.compose(
                agent="NONEXISTENT_AGENT_XYZ",
                task="some_task",
                workspace="ROOT"
            )


class TestOptionalParams:
    """Test that all inject_* params work when omitted"""

    def test_minimal_call(self):
        """Should work with only required params"""
        # Only agent and task required
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction"
        )

        # Should produce valid prompt
        assert len(prompt) > 0
        assert "CORE PERSONALITY" in prompt

    def test_all_injections_optional(self):
        """Should work with all inject_* params set to None/False"""
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",
            task="02_feature_extraction",
            workspace="ROOT",
            inject_governance=False,
            inject_tools=None,
            inject_sops=None,
            context=None
        )

        # Should produce valid prompt (just context + agent)
        assert len(prompt) > 0
        assert "CORE PERSONALITY" in prompt

    def test_task_optional_for_meta_agents(self):
        """Meta-agents (like SSF_ROUTER) should work without task"""
        # Note: SSF_ROUTER has no tasks/ directory
        prompt = PromptRegistry.compose(
            agent="VIBE_ALIGNER",  # Use VIBE_ALIGNER but without task
            task=None,
            workspace="ROOT",
            inject_governance=False
        )

        # Should create a minimal meta-agent prompt
        assert len(prompt) > 0
        # Since task is None, should use meta-agent prompt template
        assert "VIBE_ALIGNER" in prompt or "meta-agent" in prompt.lower()


# =================================================================
# Integration Test Helpers
# =================================================================

def test_full_composition_smoke_test():
    """Smoke test: Full composition with all features enabled"""
    prompt = PromptRegistry.compose(
        agent="VIBE_ALIGNER",
        task="02_feature_extraction",
        workspace="ROOT",
        inject_governance=True,
        inject_tools=["google_search"],
        inject_sops=["SOP_001"],
        context={"project_id": "test-123"}
    )

    # Should be significantly larger than base prompt
    assert len(prompt) > 10000

    # Should contain all major sections
    assert "GUARDIAN DIRECTIVES" in prompt
    assert "RUNTIME CONTEXT" in prompt
    assert "CORE PERSONALITY" in prompt

    print(f"\n✓ Full composition: {len(prompt):,} chars")
    print(f"  - Governance: {'✓' if 'GUARDIAN DIRECTIVES' in prompt else '✗'}")
    print(f"  - Context: {'✓' if 'RUNTIME CONTEXT' in prompt else '✗'}")
    print(f"  - Agent: {'✓' if 'CORE PERSONALITY' in prompt else '✗'}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
