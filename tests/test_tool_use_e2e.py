#!/usr/bin/env python3
"""
End-to-End Test: Tool Use Loop with Real Anthropic API
=======================================================

Tests arch_007 implementation: Multi-turn tool use loop in vibe-cli.

Requirements:
- ANTHROPIC_API_KEY environment variable must be set
- Google Search API keys must be configured (optional, mocked if not available)

Test Flow:
1. Initialize VibeCLI
2. Execute MARKET_RESEARCHER agent with a task requiring google_search
3. Verify multi-turn conversation works (prompt → tool_use → tool_result → response)
4. Verify tool results are correctly formatted
5. Verify final response is valid JSON

This test validates GAD-003 (Research Tool Integration) is complete.
"""

import importlib.machinery
import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add vibe-cli to path
repo_root = Path(__file__).parent.parent

# Import VibeCLI (handle file without .py extension)
vibe_cli_path = repo_root / "vibe-cli"
spec = importlib.util.spec_from_loader(
    "vibe_cli", importlib.machinery.SourceFileLoader("vibe_cli", str(vibe_cli_path))
)
vibe_cli_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vibe_cli_module)
VibeCLI = vibe_cli_module.VibeCLI


class TestToolUseE2E:
    """End-to-end tests for tool use loop"""

    @pytest.fixture
    def vibe_cli(self):
        """Initialize VibeCLI instance (works WITHOUT API key via mocks)"""
        # Use dummy key for testing - real API calls will be mocked
        return VibeCLI(repo_root=repo_root)  # File-based delegation - no API key needed

    @pytest.fixture
    def mock_tool_executor(self):
        """Mock tool executor for tests"""
        # Return a simple mock - don't patch the import
        executor = Mock()
        executor.execute_tool = Mock(
            return_value={
                "results": [
                    {
                        "title": "AI Startups 2024 - TechCrunch",
                        "snippet": "Top AI startups in 2024 include OpenAI, Anthropic, and Mistral.",
                        "url": "https://techcrunch.com/ai-startups-2024",
                    }
                ]
            }
        )
        return executor

    def test_load_tools_for_agent_market_researcher(self, vibe_cli):
        """Test: _load_tools_for_agent() loads correct tools for MARKET_RESEARCHER"""
        tools = vibe_cli._load_tools_for_agent("MARKET_RESEARCHER")

        assert len(tools) == 2, f"Expected 2 tools, got {len(tools)}"
        assert tools[0]["name"] in ["google_search", "web_fetch"]
        assert tools[1]["name"] in ["google_search", "web_fetch"]

        # Verify schema format
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert tool["input_schema"]["type"] == "object"
            assert "properties" in tool["input_schema"]
            assert "required" in tool["input_schema"]

    def test_load_tools_for_agent_no_tools(self, vibe_cli):
        """Test: Agents without tools return empty list"""
        tools = vibe_cli._load_tools_for_agent("VIBE_ALIGNER")
        assert tools == []

    def test_convert_yaml_to_anthropic_schema(self, vibe_cli):
        """Test: YAML tool definitions convert correctly to Anthropic schema"""
        yaml_tool = {
            "name": "test_tool",
            "description": "Test tool description",
            "parameters": {
                "query": {"type": "string", "required": True, "description": "Search query"},
                "limit": {
                    "type": "integer",
                    "required": False,
                    "default": 10,
                    "description": "Result limit",
                },
            },
        }

        anthropic_schema = vibe_cli._convert_yaml_to_anthropic_schema("test_tool", yaml_tool)

        assert anthropic_schema["name"] == "test_tool"
        assert anthropic_schema["description"] == "Test tool description"
        assert anthropic_schema["input_schema"]["type"] == "object"
        assert "query" in anthropic_schema["input_schema"]["properties"]
        assert "limit" in anthropic_schema["input_schema"]["properties"]
        assert anthropic_schema["input_schema"]["required"] == ["query"]
        assert anthropic_schema["input_schema"]["properties"]["limit"]["default"] == 10

    @pytest.mark.skip(
        reason="File-based delegation: vibe-cli no longer executes tools directly. "
        "Tool execution is delegated to Claude Code operator. "
        "See tests/test_file_based_delegation.py for delegation tests."
    )
    def test_execute_tools_with_mock(self, vibe_cli, mock_tool_executor):
        """Test: _execute_tools() executes tools and formats results correctly"""
        # NOTE: This test is for autonomous mode (removed in file-based delegation)
        # In file-based delegation, Claude Code executes tools, not vibe-cli
        pass

    @pytest.mark.skip(
        reason="File-based delegation: vibe-cli no longer makes API calls directly. "
        "Multi-turn conversation handled by Claude Code operator. "
        "See tests/test_file_based_delegation.py for delegation tests."
    )
    def test_multi_turn_conversation_with_mocked_api(self, vibe_cli, mock_tool_executor):
        """
        Test: Multi-turn conversation with MOCKED Anthropic API

        NOTE: This test is for autonomous mode (removed in file-based delegation).
        In file-based delegation:
        - vibe-cli writes delegation request to file
        - Claude Code operator reads file, makes API calls, writes response
        - vibe-cli polls for and reads response file
        """
        pass

    @pytest.mark.skip(
        reason="File-based delegation: vibe-cli no longer has _execute_prompt() method. "
        "Prompt execution delegated to Claude Code operator."
    )
    def test_agent_without_tools_works(self, vibe_cli):
        """Test: Agents without tools use simple request/response (no tool loop)"""
        # NOTE: This test is for autonomous mode (removed in file-based delegation)
        pass

    @pytest.mark.skip(
        reason="File-based delegation: vibe-cli no longer has _extract_final_response() method. "
        "Response extraction handled by Claude Code operator."
    )
    def test_extract_final_response_json(self, vibe_cli):
        """Test: _extract_final_response() parses JSON correctly"""
        # NOTE: This test is for autonomous mode (removed in file-based delegation)
        pass

    @pytest.mark.skip(
        reason="File-based delegation: vibe-cli no longer has _extract_final_response() method. "
        "Response extraction handled by Claude Code operator."
    )
    def test_extract_final_response_non_json(self, vibe_cli):
        """Test: _extract_final_response() wraps non-JSON in dict"""
        # NOTE: This test is for autonomous mode (removed in file-based delegation)
        pass

    @pytest.mark.skip(
        reason="File-based delegation: vibe-cli no longer has _execute_prompt() or _execute_tools() methods. "
        "Multi-turn conversation and tool execution delegated to Claude Code operator. "
        "Max turns enforcement now handled by operator."
    )
    def test_max_turns_limit(self, vibe_cli):
        """Test: Conversation stops after max_turns to prevent infinite loops"""
        # NOTE: This test is for autonomous mode (removed in file-based delegation)
        # In file-based delegation, Claude Code operator handles multi-turn conversation
        pass


def test_integration_vibe_cli_initialization():
    """Test: VibeCLI initializes correctly with valid repo_root"""
    cli = VibeCLI(repo_root=repo_root)

    assert cli.repo_root == repo_root
    assert cli.orchestrator_path.exists()
    assert cli.tool_definitions_path.exists()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
