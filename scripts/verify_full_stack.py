#!/usr/bin/env python3
"""
OPERATION GOLDEN THREAD: Full Stack Integration Verification
=============================================================

Validates the unbroken line from User Intent → LLM Execution.

This script verifies:
1. Phoenix Config loads correctly
2. Provider Factory selects appropriate LLM provider (Google/Anthropic)
3. Workflow Loader parses auto_debug.yaml
4. GraphExecutor routes to appropriate agent
5. Agent invokes LLM with real or mock execution
6. Complete trace from input to AI-generated output

Version: 1.0 (GAD-100/511/904 Integration Test)
"""

import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_section(title: str, char: str = "=") -> None:
    """Print formatted section header"""
    print(f"\n{char * 80}")
    print(f"{title}")
    print(f"{char * 80}\n")


def check_api_keys() -> dict[str, bool]:
    """Check which API keys are available"""
    keys = {
        "GOOGLE_API_KEY": bool(os.environ.get("GOOGLE_API_KEY")),
        "ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
    }

    print_section("🔑 API KEY DETECTION", "-")
    for key, available in keys.items():
        status = "✅ FOUND" if available else "❌ NOT FOUND"
        print(f"  {key}: {status}")

    return keys


def test_provider_factory() -> str:
    """Test provider factory auto-detection"""
    print_section("🏭 PROVIDER FACTORY TEST", "-")

    try:
        # Import using proper path for modules starting with numbers
        import importlib

        factory_module = importlib.import_module("agency_os.00_system.runtime.providers.factory")
        _detect_provider = factory_module._detect_provider
        _get_api_key_for_provider = factory_module._get_api_key_for_provider
        create_provider = factory_module.create_provider

        # Auto-detect provider
        detected = _detect_provider()
        print(f"  Auto-detected provider: {detected}")

        # Get API key for provider
        api_key = _get_api_key_for_provider(detected)
        key_status = "AVAILABLE" if api_key else "MISSING"
        print(f"  API key status: {key_status}")

        # Create provider
        provider = create_provider(provider_name=detected, api_key=api_key)
        provider_type = type(provider).__name__
        print(f"  Created provider: {provider_type}")

        return detected

    except Exception as e:
        logger.error(f"Provider factory test failed: {e}")
        raise


def test_workflow_loader() -> object:
    """Test workflow loader with auto_debug.yaml"""
    print_section("📋 WORKFLOW LOADER TEST", "-")

    try:
        # Import using proper path for modules starting with numbers
        import importlib

        sys.path.insert(0, str(project_root / "agency_os" / "00_system" / "playbook"))

        loader_module = importlib.import_module("agency_os.00_system.playbook.loader")
        WorkflowLoader = loader_module.WorkflowLoader

        # Load workflow
        workflow_path = (
            project_root / "agency_os" / "00_system" / "playbook" / "workflows" / "auto_debug.yaml"
        )

        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")

        print(f"  Loading: {workflow_path.name}")

        loader = WorkflowLoader()
        workflow = loader.load_workflow(workflow_path)

        print(f"  ✅ Loaded: {workflow.name}")
        print(f"     ID: {workflow.id}")
        print(f"     Intent: {workflow.intent}")
        print(f"     Nodes: {len(workflow.nodes)}")
        print(f"     Entry point: {workflow.entry_point}")

        return workflow

    except Exception as e:
        logger.error(f"Workflow loader test failed: {e}")
        raise


def test_graph_executor(workflow: object, provider_name: str) -> dict:
    """Test GraphExecutor with the workflow"""
    print_section("⚙️  GRAPH EXECUTOR TEST", "-")

    try:
        # Import using proper path for modules starting with numbers
        import importlib

        executor_module = importlib.import_module("agency_os.00_system.playbook.executor")
        GraphExecutor = executor_module.GraphExecutor

        # Create executor
        executor = GraphExecutor()
        print("  Created GraphExecutor")

        # Check live fire mode
        live_fire = os.getenv("VIBE_LIVE_FIRE", "false").lower() == "true"
        mode = "🔥 LIVE FIRE" if live_fire else "🧪 MOCK MODE"
        print(f"  Execution mode: {mode}")

        # Validate workflow
        is_valid, msg = executor.validate_workflow(workflow)
        validation = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"  Workflow validation: {validation}")
        print(f"  Message: {msg}")

        # Get execution plan
        plan = executor._topological_sort(workflow)
        print(f"  Execution order: {' → '.join(plan.execution_order)}")

        return {
            "executor": executor,
            "workflow": workflow,
            "plan": plan,
            "is_valid": is_valid,
            "live_fire": live_fire,
        }

    except Exception as e:
        logger.error(f"Graph executor test failed: {e}")
        raise


def test_first_step_execution(exec_context: dict) -> dict:
    """Execute first workflow step (analyze_logs)"""
    print_section("🚀 FIRST STEP EXECUTION (analyze_logs)", "-")

    executor = exec_context["executor"]
    workflow = exec_context["workflow"]

    try:
        # Get first step
        first_step = workflow.entry_point
        first_node = workflow.nodes[first_step]

        print(f"  Node ID: {first_step}")
        print(f"  Action: {first_node.action}")
        print(f"  Required skills: {', '.join(first_node.required_skills)}")
        print(f"  Description: {first_node.description[:100]}...")

        # Execute first step
        print("\n  Executing...")
        result = executor.execute_step(workflow, first_step)

        print("\n  ✅ Execution completed")
        print(f"     Status: {result.status.value}")
        print(f"     Cost: ${result.cost_usd:.4f}")
        print(f"     Duration: {result.duration_seconds:.2f}s")

        # Show output
        if result.output:
            print("\n  📊 OUTPUT:")
            if isinstance(result.output, dict):
                for key, value in result.output.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"     {key}: {value[:100]}...")
                    else:
                        print(f"     {key}: {value}")
            else:
                output_str = str(result.output)
                if len(output_str) > 200:
                    print(f"     {output_str[:200]}...")
                else:
                    print(f"     {output_str}")

        if result.error:
            print(f"\n  ⚠️  ERROR: {result.error}")

        return {
            "node_id": first_step,
            "status": result.status.value,
            "output": result.output,
            "error": result.error,
            "cost_usd": result.cost_usd,
            "duration_seconds": result.duration_seconds,
        }

    except Exception as e:
        logger.error(f"Step execution failed: {e}")
        raise


def generate_report(
    api_keys: dict,
    provider_name: str,
    workflow: object,
    exec_context: dict,
    step_result: dict,
) -> dict:
    """Generate final integration report"""
    print_section("📋 INTEGRATION REPORT", "=")

    report = {
        "test_timestamp": None,
        "environment": {
            "api_keys_available": api_keys,
            "selected_provider": provider_name,
            "live_fire_enabled": exec_context["live_fire"],
        },
        "workflow": {
            "id": workflow.id,
            "name": workflow.name,
            "intent": workflow.intent,
            "nodes_count": len(workflow.nodes),
            "is_valid": exec_context["is_valid"],
        },
        "execution": {
            "first_step": step_result["node_id"],
            "status": step_result["status"],
            "cost_usd": step_result["cost_usd"],
            "duration_seconds": step_result["duration_seconds"],
            "has_output": bool(step_result["output"]),
            "has_error": bool(step_result["error"]),
        },
        "golden_thread_status": "VERIFIED" if step_result["status"] == "success" else "FAILED",
    }

    # Add timestamp
    from datetime import datetime

    report["test_timestamp"] = datetime.utcnow().isoformat()

    # Print summary
    print("GOLDEN THREAD VERIFICATION SUMMARY")
    print("-" * 80)
    print(f"Provider: {provider_name}")
    print(f"Workflow: {workflow.name}")
    print(f"First Step Status: {step_result['status']}")
    print(f"Golden Thread: {report['golden_thread_status']}")
    print(f"Cost: ${step_result['cost_usd']:.4f}")

    # Determine if we saw "the ghost in the shell"
    if exec_context["live_fire"] and step_result["output"]:
        print("\n🎉 SUCCESS: The machine is ALIVE!")
        print("   Real AI-generated output detected.")
    elif not exec_context["live_fire"]:
        print("\n🧪 MOCK MODE: Integration flow verified")
        print("   Set VIBE_LIVE_FIRE=true for real AI execution")
    else:
        print("\n⚠️  WARNING: No output received")

    print("\n" + "=" * 80)

    return report


def main() -> int:
    """Main verification flow"""
    try:
        print_section("⚡ OPERATION GOLDEN THREAD", "=")
        print("Full Stack Integration Verification")
        print("Testing: User Intent → LLM Execution")

        # Step 1: Check API keys
        api_keys = check_api_keys()

        # Step 2: Test provider factory
        provider_name = test_provider_factory()

        # Step 3: Test workflow loader
        workflow = test_workflow_loader()

        # Step 4: Test graph executor
        exec_context = test_graph_executor(workflow, provider_name)

        # Step 5: Execute first step
        step_result = test_first_step_execution(exec_context)

        # Step 6: Generate report
        report = generate_report(api_keys, provider_name, workflow, exec_context, step_result)

        # Save report
        report_path = project_root / "golden_thread_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {report_path}")

        # Exit code based on golden thread status
        if report["golden_thread_status"] == "VERIFIED":
            print("\n✅ GOLDEN THREAD VERIFIED: All systems operational")
            return 0
        else:
            print("\n❌ GOLDEN THREAD FAILED: Check errors above")
            return 1

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        logger.exception("Full stack verification failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
