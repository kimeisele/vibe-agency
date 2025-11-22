#!/usr/bin/env python3
"""
ARCH-032: Unified Entry Point for Vibe Agency OS
==================================================

Single, unified CLI that supports both interactive and autonomous operation.

Modes:
1. Interactive Mode (Default): Human-in-the-loop REPL for development/debugging
2. Mission Mode (--mission): Autonomous operator mode (GAD-000 vision)

Architecture:
- One entry point, two modes (no fragmentation)
- Same kernel, same agents, same tools
- Mode only determines control flow (wait for user vs. autonomous loop)

Usage:
    # Interactive mode (REPL)
    python apps/agency/cli.py

    # Mission mode (autonomous)
    python apps/agency/cli.py --mission "Analyze the codebase and write a report"

Design Principles:
- Single Responsibility: ONE entry point for the entire system
- Separation of Concerns: boot_kernel() creates system, run_*() controls it
- Operator Pattern: The agent IS the operator (GAD-000)
- Testability: Can be imported and tested programmatically

Version: 1.0 (ARCH-032)
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from tests.mocks.llm import MockLLMProvider  # For development (no API keys needed)
from vibe_core.agents.llm_agent import SimpleLLMAgent
from vibe_core.agents.specialist_factory import SpecialistFactoryAgent
from vibe_core.governance import InvariantChecker
from vibe_core.kernel import VibeKernel
from vibe_core.llm.google_adapter import GoogleProvider  # Real AI brain
from vibe_core.llm import StewardProvider  # Claude Code integration fallback (ARCH-033C)
from vibe_core.runtime.providers.base import ProviderNotAvailableError
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard
from vibe_core.scheduling import Task
from vibe_core.tools import DelegateTool, ReadFileTool, ToolRegistry, WriteFileTool
from vibe_core.tools.inspect_result import InspectResultTool

# Import Specialists (ARCH-036: Crew Assembly)
from apps.agency.specialists import (
    CodingSpecialist,
    PlanningSpecialist,
    TestingSpecialist,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def boot_kernel():
    """
    Boot the Vibe Agency OS.

    This function initializes the complete system:
    1. Load environment configuration
    2. Initialize Soul Governance (security layer)
    3. Register Tools (the agent's "hands")
    4. Create Operator Agent (the AI that controls the system)
    5. Boot Kernel (the execution engine)

    Returns:
        VibeKernel: Initialized and ready kernel

    Design:
        - Idempotent: Can be called multiple times
        - Fail-fast: Raises exception if critical components missing
        - Logging: Reports initialization progress
        - Testable: Pure function (no side effects beyond logging)

    Example:
        >>> kernel = boot_kernel()
        >>> kernel.submit(agent_id="vibe-operator", payload={"user_message": "Hello"})
        >>> kernel.tick()
    """
    logger.info("🚀 VIBE AGENCY OS - BOOT SEQUENCE INITIATED")

    # Step 1: Load environment configuration
    load_dotenv()
    logger.info("✅ Environment configuration loaded")

    # Step 2: Initialize Soul Governance (ARCH-029)
    soul_path = os.getenv("SOUL_PATH", "config/soul.yaml")
    try:
        soul = InvariantChecker(soul_path)
        logger.info(f"🛡️  Soul Governance initialized ({soul.rule_count} rules loaded)")
    except Exception as e:
        logger.warning(f"⚠️  Soul Governance unavailable ({e}), continuing without governance")
        soul = None

    # Step 3: Register Basic Tools (ARCH-027)
    # Note: DelegateTool requires kernel reference, so it's registered later (Step 6.5)
    registry = ToolRegistry(invariant_checker=soul)
    registry.register(WriteFileTool())
    registry.register(ReadFileTool())
    logger.info(f"🔧 Tool Registry initialized ({len(registry)} basic tools)")

    # Step 4: Create Operator Agent (GAD-000 Operator Pattern)
    #
    # The agent IS the operator. It has full access to the system via tools.
    # The system prompt defines its mission and constraints.
    #
    # ARCH-037: Operator is the COMMANDER. It delegates to specialists.
    #
    system_prompt = """You are the VIBE OPERATOR - The Mission Commander.

You have access to file system tools AND a crew of domain specialists.

Your capabilities:
- read_file: Read content from files
- write_file: Create or modify files
- delegate_task: Assign work to specialist agents (returns task_id immediately)
- inspect_result: Query the result of a delegated task by its task_id

Your crew (specialists):
- specialist-planning: Expert in project planning, architecture design, requirements analysis
- specialist-coding: Expert in code generation, implementation, testing
- specialist-testing: Expert in QA, test automation, quality gates

Your constraints:
- NEVER modify core system files (vibe_core/kernel.py, etc.)
- NEVER access .git directory
- ALWAYS respect Soul Governance rules
- ALWAYS be transparent about what you're doing

THE DELEGATION LOOP (ARCH-026 Phase 4):
========================================
Delegation is ASYNCHRONOUS. When you delegate, you get a task_id immediately, NOT the result.
To get the result, you must use inspect_result(task_id).

Pattern:
1. DELEGATE: Call delegate_task(...) → Get task_id back
2. INSPECT: Call inspect_result(task_id) → Get status and result
3. READ: Extract the result from inspect_result output
4. DECIDE: Use the result to determine next steps (e.g., read plan → delegate to coder)

Example workflow: Plan → Code
===============================
Step 1: Delegate to planner
  delegate_task(agent_id="specialist-planning", payload={...})
  → Returns: task_id="task-abc-123"

Step 2: Inspect the plan result
  inspect_result(task_id="task-abc-123")
  → Returns: {"status": "COMPLETED", "output": {"plan": "Step 1: ...\nStep 2: ..."}}

Step 3: Read the plan and use it in next delegation
  Extract plan from output, then:
  delegate_task(agent_id="specialist-coding", payload={"plan": plan, ...})
  → Returns: task_id="task-def-456"

Step 4: Inspect the code result
  inspect_result(task_id="task-def-456")
  → Returns: {"status": "COMPLETED", "output": {"code": "..."}}

ERROR RECOVERY & REPAIR LOOP (ARCH-010):
========================================
When testing fails, activate the Repair Loop:
1. specialist-testing fails → returns success=False with error details
2. You detect the failure in inspect_result() output
3. IMMEDIATELY delegate back to specialist-coding with the failure report:
   - Include the qa_report.json from the testing result
   - Tell the coder: "Tests failed with: [error details]. Please analyze and fix."
4. specialist-coding enters REPAIR MODE and generates fixes
5. Delegate back to specialist-testing to re-run tests
6. If tests still fail → Repeat steps 3-5 (MAX 3 REPAIR ATTEMPTS)
7. If max attempts exceeded → FAIL and report root cause

CRITICAL: The repair loop requires your active orchestration!
- Don't assume tests always pass
- Don't skip re-running tests after fixes
- Don't delegate beyond max 3 repair attempts
- Always read the qa_report.json to understand what failed

Your mission strategy:
- DELEGATE complex work to specialists (don't try to be expert at everything)
- For planning tasks → use specialist-planning
- For coding tasks → use specialist-coding (after reading the plan!)
- For testing tasks → use specialist-testing
- Use file tools for simple read/write operations
- ALWAYS use the Delegation Loop: Delegate → Inspect → Read → Decide
- Coordinate specialists to complete multi-phase missions
- ALWAYS activate repair loop on test failures (ARCH-010)

How to delegate (Tool format):
{"tool": "delegate_task", "parameters": {
    "agent_id": "specialist-planning",
    "payload": {
        "mission_id": 1,
        "mission_uuid": "abc-123",
        "phase": "PLANNING",
        "project_root": "/path/to/project",
        "metadata": {}
    }
}}

How to inspect a result (Tool format):
{"tool": "inspect_result", "parameters": {
    "task_id": "task-abc-123",
    "include_input": false
}}

Execute user requests by coordinating your crew efficiently using the Delegation Loop.
"""

    # Step 4.5: Choose Provider (Real AI or Mock for testing)
    # ARCH-033C: Robust fallback chain: Google → Steward (if TTY) → Mock (if CI)
    # The STEWARD is Claude Code (the AI environment managing this sandbox)
    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key:
        # REAL BRAIN: Google Gemini 2.5 Flash (free during preview)
        try:
            provider = GoogleProvider(
                api_key=api_key,
                model="gemini-2.5-flash",
            )
            logger.info("🧠 CONNECTED TO GOOGLE GEMINI (gemini-2.5-flash)")
        except Exception as e:
            # Catch ALL exceptions (ProviderNotAvailableError, ConnectionError, 403, etc.)
            logger.warning(f"⚠️  Google provider failed: {type(e).__name__}: {e}")

            # Fallback chain based on environment
            if sys.stdin.isatty():
                # Interactive terminal → STEWARD becomes the provider (GAD-000 Level 100)
                logger.info("🤖 Delegating cognitive load to STEWARD (Claude Code environment)")
                logger.info("   The AI environment will provide completions via structured prompts")
                provider = StewardProvider()
            else:
                # Non-interactive (CI/CD) → Mock provider
                logger.warning("⚠️  Non-interactive environment, falling back to MockProvider")
                provider = MockLLMProvider(
                    mock_response="I am a mock operator (Google provider unavailable).",
                    system_prompt_text=system_prompt,
                )
    else:
        # MOCK BRAIN: For testing without API keys
        logger.info("ℹ️  No GOOGLE_API_KEY found, using MockProvider")
        provider = MockLLMProvider(
            mock_response="I am the Vibe Operator. How can I help you?",
            system_prompt_text=system_prompt,
        )

    operator_agent = SimpleLLMAgent(
        agent_id="vibe-operator",
        provider=provider,
        system_prompt=system_prompt,
        tool_registry=registry,
    )
    logger.info("🤖 Operator Agent initialized (vibe-operator)")

    # Step 5: Initialize Kernel (ARCH-023)
    # Note: Boot is deferred until after all agents are registered
    ledger_path = os.getenv("LEDGER_DB_PATH", "data/vibe.db")
    kernel = VibeKernel(ledger_path=ledger_path)
    logger.info(f"⚡ Kernel initialized (ledger: {ledger_path})")

    # Step 5.5: Register Operator Agent
    kernel.register_agent(operator_agent)
    logger.info("   - Registered operator agent")

    # Step 6: Register Specialist Crew (ARCH-036: Crew Assembly)
    #
    # The Specialists are the domain experts for each SDLC phase.
    # They are registered as factory agents (create specialist per task).
    #
    # Why Factory Pattern:
    #   - Specialists need mission_id (not available at boot time)
    #   - Factory creates fresh specialist instance per task
    #   - Specialist is task-scoped (discarded after execution)
    #
    guard = ToolSafetyGuard()

    planning_factory = SpecialistFactoryAgent(
        specialist_class=PlanningSpecialist,
        role="planning",
        sqlite_store=kernel.ledger,
        tool_safety_guard=guard,
    )
    kernel.register_agent(planning_factory)
    logger.info("   - Registered specialist: Planning")

    coding_factory = SpecialistFactoryAgent(
        specialist_class=CodingSpecialist,
        role="coding",
        sqlite_store=kernel.ledger,
        tool_safety_guard=guard,
    )
    kernel.register_agent(coding_factory)
    logger.info("   - Registered specialist: Coding")

    testing_factory = SpecialistFactoryAgent(
        specialist_class=TestingSpecialist,
        role="testing",
        sqlite_store=kernel.ledger,
        tool_safety_guard=guard,
    )
    kernel.register_agent(testing_factory)
    logger.info("   - Registered specialist: Testing")

    # Step 6.5: Boot Kernel (ARCH-026 Phase 3: Generate manifests for all agents)
    # Boot is now called after all agents are registered
    kernel.boot()
    logger.info("   - STEWARD manifests generated for all agents")

    # Step 7: Register DelegateTool & InspectResultTool (ARCH-037: The Intercom)
    #
    # Late binding: These tools need kernel reference for task submission/querying.
    # We register them AFTER kernel boot to break circular dependency.
    #
    # Circular dependency:
    #   - Kernel needs Agent (for dispatch)
    #   - Agent needs ToolRegistry (for capabilities)
    #   - DelegateTool/InspectResultTool needs Kernel (for submit/query)
    #
    # Solution: Create tools → Inject kernel via set_kernel() → Register
    #
    delegate_tool = DelegateTool()
    delegate_tool.set_kernel(kernel)
    registry.register(delegate_tool)
    logger.info("📞 Registered DelegateTool (Operator can now delegate to specialists)")

    # Register InspectResultTool (ARCH-026 Phase 4: Result Retrieval)
    inspect_tool = InspectResultTool(kernel)
    registry.register(inspect_tool)
    logger.info("🔍 Registered InspectResultTool (Operator can now query task results)")

    logger.info("✅ BOOT COMPLETE - VIBE AGENCY OS ONLINE")
    logger.info(f"   - Agents: {len(kernel.agent_registry)}")
    logger.info(f"   - Tools: {len(registry)}")
    logger.info(f"   - Soul: {'enabled' if soul else 'disabled'}")
    logger.info("")

    return kernel


async def run_interactive(kernel: VibeKernel):
    """
    Run in interactive mode (REPL).

    This mode is for development, debugging, and human-in-the-loop operation.
    User types commands, agent responds, repeat.

    Flow:
        1. Print welcome message
        2. Loop:
            a. Prompt user for command
            b. Submit to kernel
            c. Execute until no pending tasks
            d. Show result
        3. Exit on 'exit' or Ctrl+C

    Args:
        kernel: Booted VibeKernel instance

    Example:
        >>> kernel = boot_kernel()
        >>> await run_interactive(kernel)
        👤 MISSION/COMMAND: list files
        [agent processes and responds]
        👤 MISSION/COMMAND: exit
    """
    print("=" * 70)
    print("🤖 VIBE OPERATOR ONLINE (Interactive Mode)")
    print("=" * 70)
    print("Type your mission or command. Type 'exit' to quit.")
    print("")

    while True:
        try:
            # Get user input
            cmd = input("\n👤 MISSION/COMMAND: ").strip()

            # Handle exit
            if cmd.lower() in ["exit", "quit", "q"]:
                print("👋 Operator shutting down. Goodbye!")
                break

            # Ignore empty input
            if not cmd:
                continue

            # Submit task to kernel
            task = Task(agent_id="vibe-operator", payload={"user_message": cmd})
            task_id = kernel.submit(task)
            logger.info(f"📤 Submitted task {task_id}")

            # Execute until complete
            steps = 0
            while kernel.scheduler.get_queue_status()["pending_tasks"] > 0:
                kernel.tick()
                steps += 1
                await asyncio.sleep(0.01)  # Prevent CPU spinning

            logger.info(f"✅ Task completed in {steps} steps")

            # TODO: Display agent's response (requires ledger query)
            print(f"   ↳ [Task {task_id} completed]")

        except KeyboardInterrupt:
            print("\n\n👋 Operator interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
            print(f"   ↳ Error: {e}")


def display_status(kernel: VibeKernel, json_format: bool = False):
    """
    Display system status (agents, tools, soul).

    Args:
        kernel: Booted VibeKernel instance
        json_format: If True, output as JSON; otherwise human-readable

    Example:
        >>> kernel = boot_kernel()
        >>> display_status(kernel, json_format=True)
        {"agents": [...], "tools": [...], "soul": {"enabled": true}}
    """
    # Collect agent information
    agents = []
    for agent_id, agent in kernel.agent_registry.items():
        agent_info = {
            "agent_id": agent_id,
            "type": agent.__class__.__name__,
        }

        # Add specialist-specific info if available
        if hasattr(agent, "specialist_class"):
            agent_info["specialist_class"] = agent.specialist_class.__name__
            agent_info["role"] = agent.role

        agents.append(agent_info)

    # Collect tool information (if tool registry is accessible)
    # Note: ToolRegistry is not directly accessible from kernel
    # We'll need to pass it separately or access it via agents
    tools_count = "N/A"  # Placeholder (tools are agent-specific)

    # Soul status (requires access to InvariantChecker)
    # Note: Soul is not stored in kernel, only in agents
    soul_enabled = False  # Placeholder

    if json_format:
        # JSON output (ARCH-035 compliant)
        status = {
            "system": "vibe-agency",
            "version": "1.0",
            "kernel": {
                "ledger_path": str(kernel.ledger.db_path) if hasattr(kernel.ledger, "db_path") else "unknown",
                "agents_count": len(agents),
            },
            "agents": agents,
            "tools": {
                "count": tools_count,
            },
            "soul": {
                "enabled": soul_enabled,
            },
        }
        print(json.dumps(status, indent=2))
    else:
        # Human-readable output
        print("=" * 70)
        print("🤖 VIBE AGENCY OS - SYSTEM STATUS")
        print("=" * 70)
        print(f"\n📊 Kernel:")
        print(f"   - Ledger: {kernel.ledger.db_path if hasattr(kernel.ledger, 'db_path') else 'unknown'}")
        print(f"   - Agents: {len(agents)}")

        print(f"\n🤖 Registered Agents:")
        for agent_info in agents:
            agent_type = agent_info["type"]
            agent_id = agent_info["agent_id"]

            if "specialist_class" in agent_info:
                print(f"   - {agent_id} ({agent_type} → {agent_info['specialist_class']})")
            else:
                print(f"   - {agent_id} ({agent_type})")

        print(f"\n🔧 Tools: {tools_count}")
        print(f"🛡️  Soul Governance: {'enabled' if soul_enabled else 'disabled'}")
        print("")


async def run_mission(kernel: VibeKernel, mission: str):
    """
    Run in mission mode (autonomous operation).

    This mode is for autonomous, unattended execution (GAD-000 vision).
    Agent receives mission, executes autonomously until complete.

    Flow:
        1. Print mission start
        2. Submit mission to kernel
        3. Loop until no pending tasks
        4. Print completion

    Args:
        kernel: Booted VibeKernel instance
        mission: Mission description string

    Example:
        >>> kernel = boot_kernel()
        >>> await run_mission(kernel, "Analyze codebase and write report")
        🤖 MISSION STARTED: Analyze codebase...
        [autonomous execution]
        ✅ MISSION COMPLETE (42 steps)
    """
    print("=" * 70)
    print(f"🤖 VIBE OPERATOR STARTED MISSION")
    print("=" * 70)
    print(f"Mission: {mission}")
    print("")

    # Submit mission
    task = Task(agent_id="vibe-operator", payload={"user_message": mission})
    task_id = kernel.submit(task)
    logger.info(f"📤 Mission submitted (task_id={task_id})")

    # Execute autonomously
    steps = 0
    max_steps = 1000  # Safety limit to prevent infinite loops

    while kernel.scheduler.get_queue_status()["pending_tasks"] > 0 and steps < max_steps:
        kernel.tick()
        steps += 1
        print(f"   ↳ Step {steps} executed...")
        await asyncio.sleep(0.01)  # Prevent CPU spinning

    # Report outcome
    if steps >= max_steps:
        print(f"\n⚠️  MISSION TIMEOUT (stopped after {max_steps} steps)")
        print("   The mission may not have completed. Check ledger for details.")
    else:
        print(f"\n✅ MISSION COMPLETE ({steps} steps)")
        print(f"   Task ID: {task_id}")
        print("   Check ledger for full execution log.")


def main():
    """
    Main entry point for Vibe Agency CLI.

    Parses command-line arguments and starts the appropriate mode:
    - No args: Interactive mode
    - --mission "...": Mission mode
    - --status: Display system status and exit

    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Vibe Agency OS - Unified Entry Point (ARCH-032)",
        epilog="Examples:\n"
        "  Interactive mode:  python apps/agency/cli.py\n"
        "  Mission mode:      python apps/agency/cli.py --mission 'Write a report'\n"
        "  Status check:      python apps/agency/cli.py --status [--json]\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mission",
        "-m",
        type=str,
        help="Mission description for autonomous execution (GAD-000 mode)",
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Display system status (agents, tools, soul) and exit",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (use with --status)",
    )

    args = parser.parse_args()

    # Boot the system
    try:
        kernel = boot_kernel()
    except Exception as e:
        logger.error(f"🔥 BOOT FAILED: {e}", exc_info=True)
        print(f"\n❌ FATAL ERROR: Failed to boot system")
        print(f"   {type(e).__name__}: {e}")
        print(f"\n   Check logs for details.")
        return 1

    # Run appropriate mode
    try:
        if args.status:
            # Status mode (display system info and exit)
            display_status(kernel, json_format=args.json)
            return 0
        elif args.mission:
            # Mission mode (autonomous)
            asyncio.run(run_mission(kernel, args.mission))
        else:
            # Interactive mode (REPL)
            asyncio.run(run_interactive(kernel))

        return 0

    except Exception as e:
        logger.error(f"🔥 RUNTIME ERROR: {e}", exc_info=True)
        print(f"\n❌ FATAL ERROR during execution")
        print(f"   {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
