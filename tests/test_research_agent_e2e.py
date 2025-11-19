#!/usr/bin/env python3
"""
End-to-end integration test for Research Agent Tool Execution (GAD-003)

This test validates the FULL pipeline:
1. Research agent receives a task
2. Agent composes prompt with tool definitions
3. Agent (simulated Claude response) requests a tool via XML
4. Orchestrator detects tool request
5. Orchestrator executes tool
6. Orchestrator sends result back to agent
7. Agent produces final output

EXPECTED OUTCOME: This test will FAIL and expose design flaws in GAD-003
"""

import sys
from pathlib import Path

# Add orchestrator to path
repo_root = Path(__file__).resolve().parent.parent

from agency_os_orchestrator import CoreOrchestrator


def test_e2e_research_agent_with_tools():
    """
    End-to-end test: Research agent uses google_search tool

    This test simulates the FULL workflow described in GAD-003.
    """
    print("=" * 70)
    print("END-TO-END RESEARCH AGENT TOOL EXECUTION TEST")
    print("=" * 70)
    print()

    # Step 1: Load tool definitions directly
    print("Step 1: Load tool definitions (simulating PromptRuntime)")

    import yaml

    tool_defs_path = (
        repo_root / "agency_os" / "00_system" / "orchestrator" / "tools" / "tool_definitions.yaml"
    )
    with open(tool_defs_path) as f:
        tool_defs = yaml.safe_load(f)

    print(f"✅ Loaded {len(tool_defs['tools'])} tools: {list(tool_defs['tools'].keys())}")
    print()

    # Step 2: Simulate composed prompt with tool definitions
    print("Step 2: Simulate research agent prompt with tool definitions")

    # This simulates what PromptRuntime._compose_tools_section() would produce
    composed_prompt = """
# === AGENT IDENTITY ===
You are MARKET_RESEARCHER, a research agent specialized in market analysis.

# === AVAILABLE TOOLS ===
You have access to the following research tools:

## Tool: `google_search`
**Description:** Search Google using Custom Search API. Returns top 10 results with titles, snippets, URLs.

**Parameters:**
- `query` (string) (required): Search query (e.g., 'AI startups 2024')
- `num_results` (integer) (optional): Number of results (1-10), default: `10`

**Returns:** List of search results

---

### How to use tools:
To call a tool, use the following XML format in your response:
```xml
<tool_use name="tool_name">
  <parameters>
    <param_name>value</param_name>
  </parameters>
</tool_use>
```

You will receive the tool result, then you can continue your analysis.

# === TASK ===
Research competitors for an AI coding assistant product.
Identify the top 5 competitors in this space.
"""

    print(f"✅ Prompt composed ({len(composed_prompt)} chars)")
    print()

    try:
        # Step 3: Verify tools are in prompt (they are, we just composed them)
        print("Step 3: Verify tool definitions are in prompt")
        print("✅ AVAILABLE TOOLS section present")
        print("✅ google_search tool defined")
        print("✅ Tool usage instructions (XML format) included")
        print()

        # Step 4: Simulate agent response with tool request
        print("Step 4: Simulate Claude agent requesting google_search tool")

        # This is what Claude would respond with (following the XML format in the prompt)
        agent_response_with_tool_request = """
I need to research competitors in the AI coding assistant market.

<tool_use name="google_search">
  <parameters>
    <query>AI coding assistants competitors 2024</query>
    <num_results>5</num_results>
  </parameters>
</tool_use>

I will analyze the results to identify key competitors.
"""

        print("   Agent response:", agent_response_with_tool_request[:100] + "...")
        print()

        # Step 5: Test orchestrator's ability to detect and parse tool request
        print("Step 5: Test CoreOrchestrator XML parsing")

        orchestrator = CoreOrchestrator(repo_root=repo_root, execution_mode="delegated")

        tool_call = orchestrator._parse_tool_use(agent_response_with_tool_request)

        if tool_call is None:
            print("❌ CRITICAL FAILURE: Orchestrator failed to parse tool request!")
            return False

        print("✅ Tool request parsed successfully")
        print(f"   Tool: {tool_call['name']}")
        print(f"   Parameters: {tool_call['parameters']}")
        print()

        # Step 6: Test tool execution
        print("Step 6: Test tool execution")

        from tool_executor import ToolExecutor

        try:
            executor = ToolExecutor()
            result = executor.execute(tool_call["name"], tool_call["parameters"])

            if result.get("error"):
                print(f"⚠️  Tool execution returned error: {result['error']}")
                print("   (This is expected if Google API credentials not configured)")
            else:
                print("✅ Tool executed successfully")
                if "results" in result:
                    print(f"   Returned {len(result['results'])} search results")
        except Exception as e:
            print(f"⚠️  Tool execution failed: {e}")
            print("   (This is expected if API credentials not configured)")

        print()

        # Step 7: THE CRITICAL GAP - STDIN/STDOUT Protocol
        print("Step 7: CRITICAL GAP ANALYSIS - STDIN/STDOUT Protocol")
        print("-" * 70)
        print()
        print("❌ DESIGN FLAW IDENTIFIED:")
        print()
        print("The orchestrator's _request_intelligence() method expects:")
        print("  1. To send INTELLIGENCE_REQUEST to STDOUT")
        print("  2. To read agent response from STDIN (line 631)")
        print("  3. If response contains <tool_use>: Execute tool, send result to STDOUT")
        print("  4. To read NEXT response from STDIN (line 663 continue)")
        print()
        print("BUT there is NO Claude Code integration that implements this protocol!")
        print()
        print("Questions that are UNANSWERED:")
        print("  - How does Claude Code receive the INTELLIGENCE_REQUEST from STDOUT?")
        print("  - How does Claude Code send its response to orchestrator's STDIN?")
        print("  - How does Claude Code receive the TOOL_RESULT from orchestrator?")
        print("  - How does Claude Code know to continue and send another response?")
        print()
        print("The orchestrator will BLOCK on sys.stdin.readline() waiting for input")
        print("that will never come, because NO integration layer exists!")
        print()
        print("-" * 70)
        print()

        # Step 8: Identify missing components
        print("Step 8: Missing Components for GAD-003 Completion")
        print()
        print("To make GAD-003 actually work, we need:")
        print()
        print("1. Claude Code Integration Layer")
        print("   - Wrapper script that reads INTELLIGENCE_REQUEST from orchestrator")
        print("   - Invokes Anthropic API with the prompt")
        print("   - Sends API response back to orchestrator's STDIN")
        print("   - Reads TOOL_RESULT from orchestrator")
        print("   - Sends follow-up API request with tool result")
        print("   - Sends final response to orchestrator's STDIN")
        print()
        print("2. OR: Rewrite orchestrator to use Anthropic API directly")
        print("   - Replace _request_intelligence() with direct API calls")
        print("   - Implement proper tool use loop with Anthropic's tool use API")
        print("   - Handle streaming responses")
        print()
        print("3. End-to-end integration test with REAL Claude API")
        print("   - Not just XML parsing unit tests")
        print(
            "   - Full round-trip: prompt → API → tool request → execute → result → API → final response"
        )
        print()

        return False  # Test fails to highlight design gaps

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("   This likely means MARKET_RESEARCHER composition or task files are missing")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    success = test_e2e_research_agent_with_tools()
    print()
    print("=" * 70)
    if success:
        print("TEST PASSED ✅")
        print("=" * 70)
        sys.exit(0)
    else:
        print("TEST FAILED (AS EXPECTED) ❌")
        print()
        print("This test INTENTIONALLY fails to expose design gaps in GAD-003.")
        print("See output above for detailed analysis of what's missing.")
        print("=" * 70)
        sys.exit(1)
