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
from vibe_core.governance import InvariantChecker
from vibe_core.kernel import VibeKernel
from vibe_core.llm.google_adapter import GoogleProvider  # Real AI brain
from vibe_core.runtime.providers.base import ProviderNotAvailableError
from vibe_core.scheduling import Task
from vibe_core.tools import ReadFileTool, ToolRegistry, WriteFileTool

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

    # Step 3: Register Tools (ARCH-027)
    registry = ToolRegistry(invariant_checker=soul)
    registry.register(WriteFileTool())
    registry.register(ReadFileTool())
    logger.info(f"🔧 Tool Registry initialized ({len(registry)} tools)")

    # Step 4: Create Operator Agent (GAD-000 Operator Pattern)
    #
    # The agent IS the operator. It has full access to the system via tools.
    # The system prompt defines its mission and constraints.
    #
    system_prompt = """You are the VIBE OPERATOR.

You have access to file system tools and are responsible for executing user missions autonomously.

Your capabilities:
- read_file: Read content from files
- write_file: Create or modify files

Your constraints:
- NEVER modify core system files (vibe_core/kernel.py, etc.)
- NEVER access .git directory
- ALWAYS respect Soul Governance rules
- ALWAYS be transparent about what you're doing

Your mission:
- Execute user requests safely and efficiently
- Use tools when appropriate
- Explain your actions clearly
- Complete tasks autonomously when possible

When you use a tool, respond with valid JSON:
{"tool": "tool_name", "parameters": {...}}

Otherwise, respond with natural language to the user.
"""

    # Step 4.5: Choose Provider (Real AI or Mock for testing)
    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key:
        # REAL BRAIN: Google Gemini 2.5 Flash (free during preview)
        try:
            provider = GoogleProvider(
                api_key=api_key,
                model="gemini-2.5-flash-exp",
            )
            logger.info("🧠 CONNECTED TO GOOGLE GEMINI (gemini-2.5-flash-exp)")
        except ProviderNotAvailableError as e:
            logger.warning(f"⚠️  Google provider unavailable: {e}")
            logger.warning("⚠️  Falling back to MockProvider")
            provider = MockLLMProvider(
                mock_response="I am a mock operator (no API key available).",
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

    # Step 5: Boot Kernel (ARCH-023)
    ledger_path = os.getenv("LEDGER_DB_PATH", "data/vibe.db")
    kernel = VibeKernel(ledger_path=ledger_path)
    kernel.boot()
    kernel.register_agent(operator_agent)
    logger.info(f"⚡ Kernel booted (ledger: {ledger_path})")

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

    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Vibe Agency OS - Unified Entry Point (ARCH-032)",
        epilog="Examples:\n"
        "  Interactive mode:  python apps/agency/cli.py\n"
        "  Mission mode:      python apps/agency/cli.py --mission 'Write a report'\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mission",
        "-m",
        type=str,
        help="Mission description for autonomous execution (GAD-000 mode)",
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
        if args.mission:
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
