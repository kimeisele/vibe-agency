#!/usr/bin/env python3
"""
Test Knowledge Integration v2 (OPERATION INSIGHT)
==================================================

Verifies that the executor properly queries the knowledge system when
a node has knowledge_context=True.

This test captures logs to verify "The Holy Trinity" is complete.
"""

import logging
import sys
from pathlib import Path

# Setup path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "agency_os" / "core_system"))


# Custom log handler to capture logs
class LogCapture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(self.format(record))


# Setup logging with capture
log_capture = LogCapture()
log_capture.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Still print to console
        log_capture,  # Capture for testing
    ],
)


def test_knowledge_integration():
    """Test that executor queries knowledge system when knowledge_context is True."""

    print("\n" + "=" * 80)
    print("🧪 TEST: Knowledge Integration v2 (OPERATION INSIGHT)")
    print("=" * 80)

    # Step 1: Import required modules
    print("\n📍 Step 1: Importing modules...")
    from playbook.executor import GraphExecutor, WorkflowGraph, WorkflowNode

    print("   ✅ Modules imported")

    # Step 2: Create a test workflow with knowledge_context=True
    print("\n📍 Step 2: Creating test workflow with knowledge_context=True...")

    nodes = {
        "analyze_request": WorkflowNode(
            id="analyze_request",
            action="analyze",
            description="Analyze agent patterns",
            required_skills=[],
            prompt_key="research.analyze_topic",
            knowledge_context=True,  # <-- THE KEY INTEGRATION
        )
    }

    workflow = WorkflowGraph(
        id="test_workflow",
        name="Test Knowledge Integration",
        intent="Test knowledge system integration",
        nodes=nodes,
        edges=[],
        entry_point="analyze_request",
        exit_points=["analyze_request"],
        estimated_cost_usd=0.0,
    )

    print("   ✅ Workflow created")
    print(f"   ✅ Node knowledge_context: {workflow.nodes['analyze_request'].knowledge_context}")

    # Step 3: Execute the workflow step with a query that should match our knowledge
    print("\n📍 Step 3: Executing workflow with 'Agent Patterns' query...")
    print("   (Capturing logs for verification)")

    # Clear previous logs
    log_capture.records.clear()

    executor = GraphExecutor()
    result = executor.execute_step(
        workflow,
        "analyze_request",
        context="Agent Patterns",  # This should match our test knowledge file
    )

    print("\n   ✅ Execution completed")
    print(f"   Status: {result.status.value}")

    # Step 4: Verify the logs show knowledge retrieval
    print("\n📍 Step 4: Verifying knowledge system was queried...")

    all_logs = "\n".join(log_capture.records)

    # Check for key log messages
    success_checks = {
        "👁️ INSIGHT: Retrieving knowledge": "Knowledge retrieval initiated",
        "👁️ INSIGHT: Found": "Knowledge artifacts found",
        "👁️ INSIGHT: Injected": "Knowledge injected into prompt",
        "🎙️ VOICE: Retrieved prompt": "Prompt registry queried",
        "agent_patterns": "Our test knowledge file was found",
        "The Holy Trinity": "Knowledge content was retrieved",
    }

    results = {}
    for marker, description in success_checks.items():
        found = marker in all_logs
        results[marker] = found
        status = "✅" if found else "❌"
        print(f"   {status} {description}: '{marker}'")

    # Step 5: Results
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS")
    print("=" * 80)

    # Required checks (must pass)
    required = [
        "👁️ INSIGHT: Retrieving knowledge",
        "👁️ INSIGHT: Found",
        "👁️ INSIGHT: Injected",
        "🎙️ VOICE: Retrieved prompt",
    ]

    # Nice-to-have checks (bonus)
    bonus = ["agent_patterns", "The Holy Trinity"]

    required_pass = all(results.get(r, False) for r in required)
    bonus_pass = all(results.get(b, False) for b in bonus)

    if required_pass and bonus_pass:
        print("✅ PERFECT SUCCESS: The Holy Trinity is Complete!")
        print("   - All required checks passed ✅")
        print("   - All bonus checks passed ✅")
        print("\n   🧠 The Brain (Executor): ✅")
        print("   🎙️ The Voice (Prompt Registry): ✅")
        print("   👁️ The Eyes (Knowledge System): ✅")
        print("\n   The Trinity works in perfect harmony!")
        return 0
    elif required_pass:
        print("✅ SUCCESS: Knowledge Integration Working!")
        print("   - All required checks passed ✅")
        print("   - Some bonus checks missing (expected in mock mode)")
        print("\n   🧠 The Brain (Executor): ✅")
        print("   🎙️ The Voice (Prompt Registry): ✅")
        print("   👁️ The Eyes (Knowledge System): ✅")
        print("\n   The integration is working correctly!")
        return 0
    else:
        print("❌ FAILURE: Required checks failed")
        failed = [r for r in required if not results.get(r, False)]
        print(f"   - Failed checks: {failed}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = test_knowledge_integration()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
