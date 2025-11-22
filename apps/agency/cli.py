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

from dotenv import load_dotenv  # noqa: E402

# Import Specialists (ARCH-036: Crew Assembly)
from apps.agency.prompts import compose_steward_prompt  # noqa: E402
from apps.agency.specialists import (  # noqa: E402
    CodingSpecialist,
    PlanningSpecialist,
    TestingSpecialist,
)
from vibe_core.agents.llm_agent import SimpleLLMAgent  # noqa: E402
from vibe_core.agents.specialist_factory import SpecialistFactoryAgent  # noqa: E402
from vibe_core.agents.system_maintenance import SystemMaintenanceAgent  # noqa: E402
from vibe_core.governance import InvariantChecker  # noqa: E402
from vibe_core.introspection import SystemIntrospector  # noqa: E402
from vibe_core.kernel import VibeKernel  # noqa: E402
from vibe_core.llm import ChainProvider, StewardProvider  # noqa: E402
from vibe_core.llm.google_adapter import GoogleProvider  # noqa: E402
from vibe_core.llm.smart_local_provider import (  # noqa: E402
    SmartLocalProvider,  # Offline orchestration (ARCH-041)
)
from vibe_core.runtime.tool_safety_guard import ToolSafetyGuard  # noqa: E402
from vibe_core.scheduling import Task  # noqa: E402
from vibe_core.tools import (  # noqa: E402
    AddTaskTool,
    CompleteTaskTool,
    DelegateTool,
    ListTasksTool,
    ReadFileTool,
    ToolRegistry,
    WriteFileTool,
)
from vibe_core.tools.inspect_result import InspectResultTool  # noqa: E402
from vibe_core.tools.list_directory import ListDirectoryTool  # noqa: E402
from vibe_core.tools.search_file import SearchFileTool  # noqa: E402
from vibe_core.config import get_config  # noqa: E402
from vibe_core.runtime.oracle import KernelOracle  # noqa: E402
from vibe_core.runtime.prompt_context import get_prompt_context  # noqa: E402
from vibe_core.runtime.interface import InterfaceManager, InterfaceMode  # noqa: E402, ARCH-065

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
    # ARCH-063: Use environment variable (SOUL_PATH) or config default
    try:
        config = get_config()
        soul_path = os.getenv("SOUL_PATH")
        if not soul_path:
            # Fallback to project root config path
            soul_path = str(PROJECT_ROOT / "config" / "soul.yaml")

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
    registry.register(ListDirectoryTool())
    registry.register(SearchFileTool())
    # Step 3.5: Register Agenda Tools (ARCH-045)
    registry.register(AddTaskTool())
    registry.register(ListTasksTool())
    registry.register(CompleteTaskTool())
    logger.info(f"🔧 Tool Registry initialized ({len(registry)} tools including agenda)")

    # Step 4: Create Operator Agent (GAD-000 Operator Pattern)
    #
    # The agent IS the operator. It has full access to the system via tools.
    # The system prompt defines its mission and constraints.
    #
    # ARCH-037: Operator is the COMMANDER. It delegates to specialists.
    # ARCH-060: Dynamic Cortex - Prompt is compiled from live kernel state
    #
    logger.info("🧠 Composing dynamic system prompt (ARCH-060: The Cortex)")
    system_prompt = compose_steward_prompt(include_reasoning=True)

    # Step 4.5: Choose Provider (ARCH-067: Runtime Immortality - Provider Cascade)
    # The ChainProvider implements Phoenix resilience at RUNTIME.
    # If one provider fails during execution, the system cascades to the next.
    # This ensures the agent NEVER goes silent - it always finds a working brain.
    #
    # Cascade Order:
    # 1. Google Gemini (Real cloud AI)
    # 2. StewardProvider (Claude Code environment)
    # 3. SmartLocalProvider (Offline SDLC templates)
    #
    try:
        config = get_config()
        model_name = config.model.model_name  # From PhoenixConfig
    except Exception:
        # Fallback to environment or hardcoded default
        model_name = os.getenv("VIBE_MODEL_NAME", "gemini-2.5-flash")

    api_key = os.getenv("GOOGLE_API_KEY")

    # Build provider chain
    providers = []

    # Primary: Google Gemini (if API key available)
    if api_key:
        try:
            google_provider = GoogleProvider(
                api_key=api_key,
                model=model_name,
            )
            providers.append(google_provider)
            logger.info(f"🧠 Provider 1: Google Gemini ({model_name})")
        except Exception as e:
            logger.warning(f"⚠️  Google provider initialization failed: {type(e).__name__}")
            # Don't add to chain; fall through to other providers

    # Secondary: STEWARD (Claude Code integration)
    steward = StewardProvider()
    providers.append(steward)
    logger.info("🧠 Provider 2: STEWARD (Claude Code environment)")

    # Tertiary: SmartLocalProvider (Offline SDLC mode)
    smart_local = SmartLocalProvider()
    providers.append(smart_local)
    logger.info("🧠 Provider 3: SmartLocalProvider (Offline orchestration)")

    # Create chain
    if len(providers) == 1:
        # Single provider, use directly (backwards compat)
        provider = providers[0]
        logger.info("🔗 Single provider mode (no cascade needed)")
    else:
        # Multiple providers, create chain for runtime resilience
        provider = ChainProvider(providers)
        logger.info(f"🔗 Provider chain created with {len(providers)} provider(s)")
        logger.info("   System will auto-cascade on runtime failures")

    operator_agent = SimpleLLMAgent(
        agent_id="vibe-operator",
        provider=provider,
        system_prompt=system_prompt,
        tool_registry=registry,
    )
    logger.info("🤖 Operator Agent initialized (vibe-operator)")

    # Step 5: Initialize Kernel (ARCH-023)
    # Note: Boot is deferred until after all agents are registered
    # ARCH-063: Use environment variable or config-based path
    try:
        config = get_config()
        ledger_path = str(PROJECT_ROOT / config.paths.data_dir / "vibe.db")
    except Exception:
        # Fallback to environment or relative path
        ledger_path = os.getenv("LEDGER_DB_PATH", str(PROJECT_ROOT / "data" / "vibe.db"))

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

    # Step 6.5: Register System Maintenance Agent (ARCH-044: Git-Ops Strategy)
    #
    # The System Maintenance Agent handles system-level operations like git sync,
    # dependency updates, and system integrity checks. Unlike Specialists,
    # it's a singleton agent (not factory-based) since it doesn't need mission_id.
    #
    maintenance_agent = SystemMaintenanceAgent(project_root=PROJECT_ROOT)
    kernel.register_agent(maintenance_agent)
    logger.info("   - Registered system maintenance agent")

    # Step 7: Boot Kernel (ARCH-026 Phase 3: Generate manifests for all agents)
    # Boot is now called after all agents are registered
    kernel.boot()
    logger.info("   - STEWARD manifests generated for all agents")

    # Step 7.5: ARCH-064 - Set kernel on prompt context for Oracle resolver
    # This allows kernel_capabilities to be resolved in system prompt
    prompt_context = get_prompt_context()
    prompt_context.set_kernel(kernel)
    logger.info("   - Kernel Oracle initialized (ARCH-064)")

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


def print_kernel_help(kernel: VibeKernel) -> None:
    """
    Print kernel-level help (ARCH-063/064: Kernel Oracle).

    This is deterministic, offline help that doesn't require LLM.
    It uses the KernelOracle to read from kernel registries and display:
    1. Available cartridges
    2. Available tools
    3. Meta commands

    This is the "kernel truth" - not subject to LLM hallucination.
    Works offline and without API keys.

    Design:
    - Visually consistent with HUD (ARCH-062)
    - Uses same emoji indicators and styling
    - Deterministic output based on kernel state
    - Uses KernelOracle as single source of truth (ARCH-064)

    Args:
        kernel: Booted VibeKernel instance
    """
    # ARCH-064: Use KernelOracle for single source of truth
    oracle = KernelOracle(kernel, PROJECT_ROOT)
    print(oracle.get_help_text())


async def _run_interactive_repl(kernel: VibeKernel):
    """
    Run the interactive REPL loop (user input → agent → result).

    This is the internal implementation of interactive mode.
    Shows HUD, waits for user input, processes commands.

    Args:
        kernel: Booted VibeKernel instance
    """
    # ARCH-062: Display HUD (Heads-Up Display)
    from vibe_core.runtime.hud import StatusBar, CapabilitiesMenu, HintSystem

    print("")
    # Render status bar with user info and system state
    status_bar = StatusBar(PROJECT_ROOT)
    print(status_bar.render())
    print("")

    # Render capabilities menu (what can you do?)
    capabilities = CapabilitiesMenu()
    print(capabilities.render())
    print("")
    print("─" * 70)
    print("")

    # Load personalized greeting from StewardCartridge (ARCH-051)
    try:
        from vibe_core.cartridges.steward import StewardCartridge

        steward = StewardCartridge()
        user_name = steward.get_user_name()
        print(f"Hi {user_name}. Systems are green.")
    except Exception as e:
        logger.warning(f"Could not load personalized greeting: {e}")
        print("Hi there. Systems are green.")

    print("What would you like to do?")
    print("")

    while True:
        try:
            # Get user input
            cmd = input("\n👤 MISSION/COMMAND: ").strip()

            # ARCH-063: Kernel Help Interceptor (Pre-flight check)
            # If user asks for help, bypass LLM and show kernel truth directly
            if cmd.lower() in ["help", "/help", "man", "?", "kernel help"]:
                print_kernel_help(kernel)
                continue

            # Handle exit
            if cmd.lower() in ["exit", "quit", "q"]:
                print("👋 Operator shutting down. Goodbye!")
                break

            # Ignore empty input
            if not cmd:
                # ARCH-062: Proactive hints for idle user
                hint = HintSystem.get_contextual_hint()
                if hint:
                    print(f"\n{hint}")
                continue

            # ARCH-062: Hints for unclear input
            hint = HintSystem.get_hint_for_input(cmd)
            if hint:
                print(f"\n{hint}")
                continue

            # ARCH-060: Hot Reload - Recompile prompt with fresh kernel state
            # This enables inbox messages, agenda changes, and git sync status
            # to be detected mid-session without restart
            logger.debug("🔄 Recompiling system prompt with fresh context (ARCH-060)")
            fresh_prompt = compose_steward_prompt(include_reasoning=True)
            operator_agent = kernel.agent_registry.get("vibe-operator")
            if operator_agent and hasattr(operator_agent, "update_system_prompt"):
                operator_agent.update_system_prompt(fresh_prompt)
                logger.debug("✅ System prompt updated with live kernel state")

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


async def run_interactive(kernel: VibeKernel):
    """
    Run in appropriate interface mode (ARCH-065: Polymorphic Interface).

    This function detects the runtime environment and switches between modes:

    INTERACTIVE: TTY detected (human at terminal)
    - Shows HUD with status bar and capabilities
    - Waits for user input in REPL loop
    - For development, debugging, human-in-the-loop operation

    HEADLESS: Pipe/CI detected (automated context)
    - No HUD, no input waiting
    - Outputs boot success message
    - Exits cleanly so parent process (Claude) can continue
    - For automation, CI/CD, Claude Code integration

    STEWARD: Protocol-based operation (future)
    - Reads from .steward/active_session.json
    - Processes task queue autonomously

    Design:
    - Physics-based detection (not configuration)
    - Solves boot hang issue: system auto-detects when to wait vs. exit
    - Enables GAD-000 vision: seamless human/AI hybrid operation

    Args:
        kernel: Booted VibeKernel instance
    """
    # ARCH-065: Detect interface mode
    mode = InterfaceManager.detect_mode()

    if mode == InterfaceMode.INTERACTIVE:
        # TTY detected: Show HUD and start REPL loop
        logger.info("🎨 Interactive mode detected (TTY connected)")
        await _run_interactive_repl(kernel)

    elif mode == InterfaceMode.HEADLESS:
        # Pipe/CI detected: Boot and exit cleanly
        logger.info("🤖 Headless mode detected (piped input or CI)")
        print("✅ Vibe OS: Headless mode detected. System is READY.")
        print("ℹ️  Use CLI arguments to execute missions.")
        logger.info("   [No input loop in headless mode - parent can continue]")
        # Exit without waiting for input

    elif mode == InterfaceMode.STEWARD:
        # Steward protocol detected: Process autonomous queue
        logger.info("🏛️  Steward mode detected (protocol-based operation)")
        print("🏛️  Vibe OS: Steward mode detected. Processing queue...")
        # TODO (GAD-000 Phase 2): Implement steward queue processing


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
                "ledger_path": str(kernel.ledger.db_path)
                if hasattr(kernel.ledger, "db_path")
                else "unknown",
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
        print("\n📊 Kernel:")
        print(
            f"   - Ledger: {kernel.ledger.db_path if hasattr(kernel.ledger, 'db_path') else 'unknown'}"
        )
        print(f"   - Agents: {len(agents)}")

        print("\n🤖 Registered Agents:")
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


def handle_task_command(command: str, args_list: list[str] | None = None):
    """
    Handle task management commands (add, list, complete).

    This provides a CLI interface to the agenda/backlog system (ARCH-045).

    Args:
        command: Subcommand ('add', 'list', 'complete')
        args_list: Additional arguments for the subcommand

    Example:
        >>> handle_task_command('add', ['Fix Phoenix Config', 'HIGH'])
        >>> handle_task_command('list', ['pending'])
        >>> handle_task_command('complete', ['Fix Phoenix Config'])
    """
    if args_list is None:
        args_list = []

    try:
        if command == "add":
            if len(args_list) < 1:
                print("❌ Usage: task add <description> [priority]")
                print("   Priority: HIGH, MEDIUM, LOW (default: MEDIUM)")
                return

            description = args_list[0]
            priority = args_list[1].upper() if len(args_list) > 1 else "MEDIUM"

            tool = AddTaskTool()
            result = tool.execute({"description": description, "priority": priority})

            if result.success:
                print(f"✅ {result.output}")
            else:
                print(f"❌ Error: {result.error}")

        elif command == "list":
            status = args_list[0].lower() if args_list else "pending"

            tool = ListTasksTool()
            result = tool.execute({"status": status})

            if result.success:
                print(result.output)
            else:
                print(f"❌ Error: {result.error}")

        elif command == "complete":
            if len(args_list) < 1:
                print("❌ Usage: task complete <task_description>")
                return

            description = args_list[0]

            tool = CompleteTaskTool()
            result = tool.execute({"task_description": description})

            if result.success:
                print(f"✅ {result.output}")
            else:
                print(f"❌ Error: {result.error}")

        else:
            print(f"❌ Unknown task command: {command}")
            print("   Valid commands: add, list, complete")

    except Exception as e:
        logger.error(f"Task command error: {e}", exc_info=True)
        print(f"❌ Error: {e}")


def display_snapshot(kernel: VibeKernel, json_format: bool = False, write_file: bool = False):
    """
    Display system introspection snapshot (ARCH-038).

    Generates a high-density system snapshot optimized for external intelligences.

    Args:
        kernel: Booted VibeKernel instance
        json_format: If True, output as JSON; otherwise markdown
        write_file: If True, write snapshot to file

    Example:
        >>> kernel = boot_kernel()
        >>> display_snapshot(kernel, json_format=False, write_file=True)
    """
    introspector = SystemIntrospector(kernel)

    # Generate snapshot in requested format
    output = introspector.to_json() if json_format else introspector.generate_snapshot()

    print(output)

    # Optionally write to file
    if write_file:
        timestamp = introspector.snapshot_timestamp.replace(":", "-").split(".")[0]
        filename = (
            f"vibe-snapshot-{timestamp}.md"
            if not json_format
            else f"vibe-snapshot-{timestamp}.json"
        )
        try:
            with open(filename, "w") as f:
                f.write(output)
            logger.info(f"📸 Snapshot written to {filename}")
            print(f"\n✅ Snapshot saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to write snapshot: {e}")
            print(f"\n❌ Failed to write snapshot: {e}")


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
    print("🤖 VIBE OPERATOR STARTED MISSION")
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
        "  Status check:      python apps/agency/cli.py --status [--json]\n"
        "  System snapshot:   python apps/agency/cli.py --snapshot [--json] [--snapshot-file]\n",
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

    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Generate system introspection snapshot (ARCH-038) and exit",
    )

    parser.add_argument(
        "--snapshot-file",
        action="store_true",
        help="Write snapshot to file (use with --snapshot)",
    )

    # Task management subcommand (ARCH-045)
    parser.add_argument(
        "task_command",
        nargs="?",
        help="Task management command (task add|list|complete)",
    )

    parser.add_argument(
        "task_args",
        nargs="*",
        help="Arguments for task command",
    )

    args = parser.parse_args()

    # Handle task management commands (ARCH-045) - doesn't require kernel boot
    if args.task_command == "task" and args.task_args:
        # Format: task add|list|complete [args...]
        subcommand = args.task_args[0] if args.task_args else None
        subcommand_args = args.task_args[1:] if len(args.task_args) > 1 else []

        if subcommand:
            handle_task_command(subcommand, subcommand_args)
            return 0
        else:
            print("❌ Usage: task add|list|complete [args...]")
            return 1

    # Boot the system
    try:
        kernel = boot_kernel()
    except Exception as e:
        logger.error(f"🔥 BOOT FAILED: {e}", exc_info=True)
        print("\n❌ FATAL ERROR: Failed to boot system")
        print(f"   {type(e).__name__}: {e}")
        print("\n   Check logs for details.")
        return 1

    # Run appropriate mode
    try:
        if args.snapshot:
            # Snapshot mode (introspection and exit)
            display_snapshot(kernel, json_format=args.json, write_file=args.snapshot_file)
            return 0
        elif args.status:
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
        print("\n❌ FATAL ERROR during execution")
        print(f"   {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
