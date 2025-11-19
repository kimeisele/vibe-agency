#!/usr/bin/env python3
"""
OPERATION FIRST BREATH: Neural Link Simulation
===============================================
Demonstrates GAD-904 Agent Routing in action.

Simulates:
1. Real agent instances with declared capabilities
2. Semantic actions requiring specific skills
3. Router selecting best agent per action
4. Executor dispatching via router
5. Mocked execution results (no LLM calls)

Evidence: Table showing action → agent mapping
"""

import sys
from pathlib import Path

# Setup path to access modules (must be before imports)
playbook_dir = Path(__file__).parent.parent / "agency_os" / "00_system" / "playbook"
runtime_dir = Path(__file__).parent.parent / "agency_os" / "00_system" / "runtime"
personas_dir = Path(__file__).parent.parent / "agency_os" / "03_agents" / "personas"

sys.path.insert(0, str(playbook_dir))
sys.path.insert(0, str(runtime_dir))
sys.path.insert(0, str(personas_dir))

from coder import CoderAgent  # noqa: E402
from executor import (  # noqa: E402
    ExecutionStatus,
    GraphExecutor,
    WorkflowEdge,
    WorkflowGraph,
    WorkflowNode,
)
from researcher import ResearcherAgent  # noqa: E402
from reviewer import ReviewerAgent  # noqa: E402
from router import AgentRouter  # noqa: E402


# ============================================================================
# SIMULATION
# ============================================================================
def simulate_neural_link():
    """Run the neural link simulation with routing table output"""

    print("\n" + "=" * 90)
    print("🧠 OPERATION FIRST BREATH: Neural Link Simulation (GAD-904)")
    print("=" * 90)

    # 1. INSTANTIATE AGENTS
    print("\n📍 STEP 1: Instantiating Real Agents")
    print("-" * 90)
    try:
        coder = CoderAgent(vibe_root=Path.cwd())
        researcher = ResearcherAgent(vibe_root=Path.cwd())
        reviewer = ReviewerAgent(vibe_root=Path.cwd())
    except RuntimeError:
        # Fallback to mocks if infrastructure missing
        print("  ⚠️  Real agents require .vibe infrastructure. Using mock agents...")

        class SimpleMockAgent:
            def __init__(self, name, capabilities):
                self.name = name
                self.capabilities = capabilities

        coder = SimpleMockAgent("CoderAgent", ["coding", "debugging", "python", "refactoring"])
        researcher = SimpleMockAgent(
            "ResearcherAgent",
            [
                "research",
                "search",
                "synthesis",
                "reasoning",
                "documentation",
                "pattern_recognition",
            ],
        )
        reviewer = SimpleMockAgent(
            "ReviewerAgent",
            [
                "audit",
                "security",
                "qa",
                "code_analysis",
                "testing",
                "pattern_knowledge",
                "validation",
            ],
        )

    print(f"  ✅ {coder.name:20s} → capabilities: {', '.join(coder.capabilities)}")
    print(f"  ✅ {researcher.name:20s} → capabilities: {', '.join(researcher.capabilities)}")
    print(f"  ✅ {reviewer.name:20s} → capabilities: {', '.join(reviewer.capabilities)}")

    # 2. INITIALIZE ROUTER
    print("\n📍 STEP 2: Initializing Agent Router (GAD-904)")
    print("-" * 90)
    router = AgentRouter([coder, researcher, reviewer])
    print(f"  ✅ Router initialized with {len(router.list_agents())} agents")
    print(f"  ✅ Capability matrix: {router.get_capability_matrix()}")

    # 3. DEFINE WORKFLOW (auto_debug workflow from GAD-903)
    print("\n📍 STEP 3: Loading Workflow (auto_debug from GAD-903)")
    print("-" * 90)

    nodes = {
        "analyze_logs": WorkflowNode(
            id="analyze_logs",
            action="analyze",
            description="Analyze test failure logs",
            required_skills=["code_analysis", "debugging"],
            timeout_seconds=600,
        ),
        "identify_root_cause": WorkflowNode(
            id="identify_root_cause",
            action="investigate",
            description="Identify root cause of failure",
            required_skills=["reasoning", "pattern_recognition"],
            timeout_seconds=600,
        ),
        "generate_fix": WorkflowNode(
            id="generate_fix",
            action="implement",
            description="Generate fix for issue",
            required_skills=["coding", "testing"],
            timeout_seconds=900,
        ),
        "verify_fix": WorkflowNode(
            id="verify_fix",
            action="validate",
            description="Verify fix passes tests",
            required_skills=["testing", "qa", "validation"],
            timeout_seconds=600,
        ),
    }

    edges = [
        WorkflowEdge("analyze_logs", "identify_root_cause"),
        WorkflowEdge("identify_root_cause", "generate_fix"),
        WorkflowEdge("generate_fix", "verify_fix"),
    ]

    workflow = WorkflowGraph(
        id="auto_debug",
        name="Automated Debug & Fix Workflow",
        intent="Investigate test failures and propose fixes",
        nodes=nodes,
        edges=edges,
        entry_point="analyze_logs",
        exit_points=["verify_fix"],
        estimated_cost_usd=1.50,
    )

    print(f"  ✅ Workflow loaded: {workflow.name} ({workflow.id})")
    print(f"  ✅ Entry point: {workflow.entry_point}")
    print(f"  ✅ Exit points: {workflow.exit_points}")
    print(f"  ✅ Nodes: {list(nodes.keys())}")
    print(f"  ✅ Edges: {len(edges)} dependencies defined")

    # 4. INITIALIZE EXECUTOR WITH ROUTER
    print("\n📍 STEP 4: Initializing Graph Executor with Router (Neural Link)")
    print("-" * 90)
    executor = GraphExecutor()
    executor.set_router(router)
    print("  ✅ Executor initialized")
    print("  ✅ Router attached (neural link active)")

    # 5. VALIDATE WORKFLOW
    print("\n📍 STEP 5: Validating Workflow Structure")
    print("-" * 90)
    is_valid, message = executor.validate_workflow(workflow)
    print(f"  {'✅' if is_valid else '❌'} Validation: {message}")

    if not is_valid:
        print("  ❌ Workflow validation failed!")
        return False

    # 6. ROUTING TABLE: Show which agent gets which action
    print("\n📍 STEP 6: Routing Table (Agent Selection per Node)")
    print("-" * 90)
    print(f"{'Node ID':<25} {'Required Skills':<40} {'Selected Agent':<20} {'Match':<10}")
    print("-" * 95)

    routing_map = {}
    all_routed = True

    for node_id, node in nodes.items():
        selected = router.find_best_agent_for_skills(node.required_skills)
        if selected is None:
            selected_name = "❌ NO MATCH"
            match = "FAIL"
            all_routed = False
        else:
            selected_name = selected.name
            match = "✅ OK"

        skills_str = ", ".join(node.required_skills)
        print(f"{node_id:<25} {skills_str:<40} {selected_name:<20} {match:<10}")
        routing_map[node_id] = selected

    print("-" * 95)

    if not all_routed:
        print("  ❌ Some nodes have no matching agent!")
        return False

    # 7. EXECUTE WORKFLOW THROUGH NEURAL LINK
    print("\n📍 STEP 7: Executing Workflow Through Neural Link")
    print("-" * 90)

    execution_log = []
    for node_id in ["analyze_logs", "identify_root_cause", "generate_fix", "verify_fix"]:
        selected_agent = routing_map[node_id]
        node = nodes[node_id]

        result = executor.execute_step(workflow, node_id)
        execution_log.append(
            {
                "node_id": node_id,
                "action": node.action,
                "required_skills": node.required_skills,
                "agent": selected_agent.name if selected_agent else "NONE",
                "status": result.status.value,
                "cost_usd": result.cost_usd,
            }
        )

        status_icon = "✅" if result.status == ExecutionStatus.SUCCESS else "❌"
        print(f"  {status_icon} [{node_id}] via {selected_agent.name} → {result.status.value}")

    # 8. EXECUTION SUMMARY TABLE
    print("\n📍 STEP 8: Execution Summary")
    print("-" * 90)
    print(f"{'Step':<3} {'Node ID':<25} {'Action':<15} {'Agent':<20} {'Status':<10} {'Cost':<10}")
    print("-" * 90)

    for i, log in enumerate(execution_log, 1):
        print(
            f"{i:<3} {log['node_id']:<25} {log['action']:<15} "
            f"{log['agent']:<20} {log['status']:<10} ${log['cost_usd']:.2f}"
        )

    print("-" * 90)

    # 10. ROUTING CONFIRMATION
    print("\n📍 STEP 9: Routing Verification (Evidence)")
    print("-" * 90)

    # Check specific routing requirements (checking class type and required skill match)
    checks = [
        (
            "analyze_logs → CoderAgent",
            "debug" in routing_map["analyze_logs"].name
            or "coder" in routing_map["analyze_logs"].name.lower(),
        ),
        (
            "identify_root_cause → ResearcherAgent",
            "research" in routing_map["identify_root_cause"].name.lower(),
        ),
        (
            "generate_fix → CoderAgent",
            "debug" in routing_map["generate_fix"].name
            or "coder" in routing_map["generate_fix"].name.lower(),
        ),
        ("verify_fix → ReviewerAgent", "review" in routing_map["verify_fix"].name.lower()),
    ]

    all_passed = True
    for check_name, result in checks:
        icon = "✅" if result else "❌"
        print(f"  {icon} {check_name}")
        if not result:
            all_passed = False

    # 10. FINAL VERDICT
    print("\n" + "=" * 90)
    if all_passed and all(log["status"] == "success" for log in execution_log):
        print("🎉 OPERATION FIRST BREATH: SUCCESS!")
        print("Neural Link is operational. The Brain is connected to the Body.")
        print("=" * 90)
        return True
    else:
        print("⚠️  OPERATION FIRST BREATH: PARTIAL SUCCESS")
        print("Some checks failed. See details above.")
        print("=" * 90)
        return False


if __name__ == "__main__":
    success = simulate_neural_link()
    sys.exit(0 if success else 1)
