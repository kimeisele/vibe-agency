"""
Core Kernel for vibe-agency OS.

This module implements the VibeKernel (ARCH-022), which wraps the
scheduler and provides the main execution loop (tick mechanism).

The Kernel is the central "System Object" - before this, vibe was
just a collection of scripts. Now, VibeKernel IS the application.
"""

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any

from vibe_core.agent_protocol import AgentNotFoundError, VibeAgent
from vibe_core.identity import AgentRegistry, generate_manifest_for_agent
from vibe_core.ledger import VibeLedger
from vibe_core.scheduling import Task, VibeScheduler

logger = logging.getLogger(__name__)


class KernelStatus(str, Enum):
    """Kernel operational states."""

    STOPPED = "STOPPED"
    BOOTING = "BOOTING"
    RUNNING = "RUNNING"
    HALTED = "HALTED"


class VibeKernel:
    """
    The central Kernel that orchestrates task execution.

    VibeKernel owns the scheduler and provides the main execution
    loop through the tick() mechanism. This is the "Game Loop" pattern
    applied to an OS context.

    Architecture:
    - Owns a VibeScheduler instance
    - Maintains an agent registry for task dispatch (ARCH-023)
    - Records all executions to ledger (ARCH-024)
    - Manages kernel lifecycle (boot/shutdown)
    - Provides tick() for incremental task processing
    - Serves as the single point of coordination

    Design Principles:
    - Single-threaded execution (for now)
    - Explicit tick() calls (no hidden threads)
    - Clear state machine (STOPPED -> RUNNING -> STOPPED)
    - Defensive programming (graceful idle handling)
    - Pluggable agents via VibeAgent protocol
    - Persistent observability via ledger
    """

    def __init__(self, ledger_path: str = "vibe_ledger.db"):
        """
        Initialize the kernel with scheduler, agent registry, and ledger.

        Args:
            ledger_path: Path to SQLite ledger database. Use ":memory:"
                         for in-memory database (useful for testing).

        Example:
            >>> kernel = VibeKernel()  # Uses "vibe_ledger.db"
            >>> test_kernel = VibeKernel(":memory:")  # In-memory for tests
        """
        self.scheduler = VibeScheduler()
        self.agent_registry: dict[str, VibeAgent] = {}
        self.manifest_registry = AgentRegistry()  # STEWARD manifest registry (ARCH-026)
        self.ledger = VibeLedger(ledger_path)
        self.status = KernelStatus.STOPPED
        self.inbox_messages: list[dict[str, str]] = []  # GAD-006: Asynchronous Intent
        self.agenda_tasks: list[str] = []  # ARCH-045: Agenda system (pending tasks)
        self.git_status: str | None = None  # ARCH-044: Git-Ops sync status
        logger.debug("KERNEL: Initialized (status=STOPPED)")

    def _scan_inbox(self) -> None:
        """
        Scan workspace/inbox/ for pending messages (GAD-006).

        This implements the Asynchronous Intent system. Messages are loaded
        as "High Priority Context" for the operator. Empty inbox = standard mode.

        The inbox is a file-based message queue that survives crashes
        (Linux philosophy: files are the universal interface).

        Example:
            >>> kernel._scan_inbox()
            >>> if kernel.inbox_messages:
            ...     print(f"Found {len(kernel.inbox_messages)} messages")
        """
        inbox_path = Path("workspace/inbox")

        if not inbox_path.exists():
            logger.debug("KERNEL: inbox directory not found (standard mode)")
            return

        md_files = sorted(inbox_path.glob("*.md"))

        if not md_files:
            logger.debug("KERNEL: inbox empty (standard mode)")
            return

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                self.inbox_messages.append(
                    {
                        "filename": md_file.name,
                        "content": content,
                    }
                )
                logger.info(f"KERNEL: Loaded inbox message: {md_file.name}")
            except Exception as e:
                logger.error(
                    f"KERNEL: Failed to load inbox message {md_file.name}: {e}",
                    exc_info=True,
                )

    def _check_git_status(self) -> None:
        """
        Check git synchronization status from environment variable (ARCH-044).

        This reads VIBE_GIT_STATUS set by system-boot.sh and stores it
        for operator context injection. The status indicates whether the
        local repository is synced, behind, diverged, or offline.

        Possible values:
        - "SYNCED": Local is up-to-date with remote
        - "BEHIND_BY_N": Local is N commits behind remote
        - "DIVERGED": Local and remote have diverged
        - "FETCH_FAILED": Could not fetch (offline or no remote)
        - "NO_REPO": Not a git repository
        - None: VIBE_GIT_STATUS not set (legacy boot)

        Example:
            >>> kernel._check_git_status()
            >>> if kernel.git_status and kernel.git_status.startswith("BEHIND"):
            ...     print("Repository is out of sync")
        """
        self.git_status = os.environ.get("VIBE_GIT_STATUS")

        if self.git_status:
            logger.debug(f"KERNEL: Git status detected: {self.git_status}")
        else:
            logger.debug("KERNEL: No git status available (VIBE_GIT_STATUS not set)")

    def _scan_backlog(self) -> None:
        """
        Scan workspace/BACKLOG.md for pending agenda tasks (ARCH-045).

        This implements the Agenda System for long-term task persistence.
        Outstanding tasks are loaded as "Current Agenda" context for the operator.
        Empty backlog = no pending agenda items.

        The backlog is a file-based task queue that survives crashes
        (Linux philosophy: files are the universal interface).

        Example:
            >>> kernel._scan_backlog()
            >>> if kernel.agenda_tasks:
            ...     print(f"Found {len(kernel.agenda_tasks)} pending tasks")
        """
        backlog_path = Path("workspace/BACKLOG.md")

        if not backlog_path.exists():
            logger.debug("KERNEL: BACKLOG.md not found (no agenda)")
            return

        try:
            content = backlog_path.read_text(encoding="utf-8")

            # Extract Outstanding Tasks section
            outstanding_idx = content.find("## Outstanding Tasks")
            completed_idx = content.find("## Completed Tasks")

            if outstanding_idx == -1 or completed_idx == -1:
                logger.warning("KERNEL: Invalid BACKLOG.md format")
                return

            section_content = content[
                outstanding_idx + len("## Outstanding Tasks") : completed_idx
            ]

            # Parse task lines (markdown checkboxes)
            tasks = []
            for line in section_content.split("\n"):
                line = line.strip()
                if line.startswith("- [ ]"):
                    # Extract the task description
                    task_desc = line.replace("- [ ]", "").strip()
                    tasks.append(task_desc)

            if tasks:
                self.agenda_tasks = tasks
                logger.info(
                    f"KERNEL: Loaded {len(self.agenda_tasks)} pending task(s) from agenda"
                )
                for i, task in enumerate(self.agenda_tasks[:3], 1):
                    logger.info(f"KERNEL: >> AGENDA[{i}]: {task[:80]}...")

            else:
                logger.debug("KERNEL: No pending tasks in backlog (agenda empty)")

        except Exception as e:
            logger.error(f"KERNEL: Failed to scan backlog: {e}", exc_info=True)

    def boot(self) -> None:
        """
        Boot the kernel and transition to RUNNING state.

        This prepares the kernel for task processing. After boot(),
        the kernel is ready to accept tasks and process them via tick().

        During boot:
        1. Transition to RUNNING state
        2. Scan inbox for pending messages (GAD-006)
        3. Scan backlog for pending agenda tasks (ARCH-045)
        4. Generate STEWARD manifests for all registered agents (ARCH-026)
        5. Populate the manifest registry
        6. Log agent identity information

        Example:
            >>> kernel = VibeKernel()
            >>> kernel.boot()
            >>> print(kernel.status)  # KernelStatus.RUNNING
            >>> manifest = kernel.manifest_registry.lookup("agent-id")
        """
        self.status = KernelStatus.RUNNING
        logger.info("KERNEL: ONLINE")

        # Check git sync status (ARCH-044: Git-Ops Strategy)
        self._check_git_status()
        if self.git_status and self.git_status != "SYNCED":
            logger.warning(f"KERNEL: Git sync status: {self.git_status}")
            logger.info("KERNEL: >> Check STEWARD.md for update policy")

        # Scan inbox for pending messages (GAD-006: Asynchronous Intent)
        self._scan_inbox()
        if self.inbox_messages:
            logger.info(f"KERNEL: Inbox has {len(self.inbox_messages)} message(s) [HIGH PRIORITY]")
            for msg in self.inbox_messages:
                logger.info(f"KERNEL: >> INBOX: {msg['filename']}")

        # Scan backlog for pending agenda tasks (ARCH-045: Agenda System)
        self._scan_backlog()
        if self.agenda_tasks:
            logger.info(f"KERNEL: Agenda has {len(self.agenda_tasks)} pending task(s)")
            for i, task in enumerate(self.agenda_tasks[:3], 1):
                logger.info(f"KERNEL: >> AGENDA[{i}]: {task[:80]}...")

        # Generate and register STEWARD manifests for all agents (ARCH-026)
        logger.debug(f"KERNEL: Generating STEWARD manifests for {len(self.agent_registry)} agents")
        for agent_id, agent in self.agent_registry.items():
            try:
                manifest = generate_manifest_for_agent(agent)
                self.manifest_registry.register(manifest)
                logger.info(
                    f"KERNEL: Registered manifest for {agent_id} "
                    f"(class={manifest.agent_class}, capabilities={manifest.capabilities})"
                )
            except Exception as e:
                logger.error(
                    f"KERNEL: Failed to generate manifest for {agent_id}: {e}",
                    exc_info=True,
                )

    def shutdown(self) -> None:
        """
        Shutdown the kernel and transition to STOPPED state.

        This gracefully stops the kernel. Any pending tasks in the
        scheduler remain queued but will not be processed until
        the kernel is booted again.

        Example:
            >>> kernel = VibeKernel()
            >>> kernel.boot()
            >>> kernel.shutdown()
            >>> print(kernel.status)  # KernelStatus.STOPPED
        """
        self.status = KernelStatus.STOPPED
        logger.info("KERNEL: SHUTDOWN")

    def register_agent(self, agent: VibeAgent) -> None:
        """
        Register an agent with the kernel for task dispatch.

        Agents must be registered before tasks can be dispatched to them.
        The agent's agent_id property is used as the registry key.

        Args:
            agent: The VibeAgent instance to register

        Raises:
            ValueError: If an agent with the same ID is already registered

        Example:
            >>> kernel = VibeKernel()
            >>> agent = MyAgent()  # implements VibeAgent
            >>> kernel.register_agent(agent)
            >>> # Now tasks with agent_id=agent.agent_id can be processed

        Notes:
            - Agents can be registered before or after kernel boot
            - Duplicate registration (same agent_id) raises ValueError
            - To replace an agent, unregister it first (future feature)
        """
        agent_id = agent.agent_id

        if agent_id in self.agent_registry:
            raise ValueError(
                f"Agent '{agent_id}' is already registered. Cannot register duplicate agent IDs."
            )

        self.agent_registry[agent_id] = agent
        logger.info(f"KERNEL: Registered agent '{agent_id}'")

    def _validate_delegation(self, agent_id: str) -> None:
        """
        Validate a delegation request using STEWARD manifest (ARCH-026 Phase 4).

        This implements "Smart Delegation" - before accepting a task for an agent,
        the kernel validates that:
        1. Agent is registered in agent_registry
        2. Agent has a manifest in manifest_registry
        3. Agent's manifest status is "active"

        This prevents delegating to non-existent, inactive, or removed agents.

        Args:
            agent_id: The agent to validate

        Raises:
            ValueError: If validation fails

        Example:
            >>> kernel.boot()  # Generates manifests
            >>> kernel._validate_delegation("specialist-planning")
            >>> # No exception = valid
        """
        # Check 1: Agent registered in agent_registry
        if agent_id not in self.agent_registry:
            raise ValueError(
                f"Agent '{agent_id}' not registered. Available: {list(self.agent_registry.keys())}"
            )

        # Check 2: Agent has manifest (only check after boot)
        if self.status == KernelStatus.RUNNING:
            manifest = self.manifest_registry.lookup(agent_id)
            if manifest is None:
                raise ValueError(
                    f"Agent '{agent_id}' has no STEWARD manifest. "
                    f"Run kernel.boot() to generate manifests."
                )

            # Check 3: Agent status is "active"
            if manifest.to_dict()["agent"]["status"] != "active":
                status = manifest.to_dict()["agent"]["status"]
                raise ValueError(
                    f"Agent '{agent_id}' is not active (status: {status}). "
                    f"Cannot delegate to inactive agents."
                )

        logger.debug(f"KERNEL: Delegation validation passed for {agent_id}")

    def submit(self, task: Task) -> str:
        """
        Submit a task to the kernel's scheduler (ARCH-026 Phase 4).

        This is a convenience proxy to scheduler.submit_task().
        Before queueing, it validates the agent using STEWARD manifest.

        Validation checks (Phase 4):
        1. Agent is registered
        2. Agent has an active manifest
        3. Agent status is "active"

        Args:
            task: The Task to be queued

        Returns:
            str: The task ID for tracking

        Raises:
            ValueError: If agent is not registered or manifest invalid

        Example:
            >>> kernel = VibeKernel()
            >>> task = Task(agent_id="agent-1", payload={"action": "compile"})
            >>> task_id = kernel.submit(task)
        """
        # ARCH-026 Phase 4: Validate delegation using manifest
        self._validate_delegation(task.agent_id)

        task_id = self.scheduler.submit_task(task)
        logger.debug(f"KERNEL: Task {task_id} submitted to {task.agent_id}")
        return task_id

    def tick(self) -> bool:
        """
        Execute one iteration of the kernel loop.

        This is the heartbeat of the system. On each tick:
        1. Retrieve the next task from the scheduler (FIFO)
        2. If a task exists, execute it
        3. If no task exists, return idle status

        Returns:
            bool: True if work was done (busy), False if idle

        Example:
            >>> kernel = VibeKernel()
            >>> kernel.boot()
            >>> task = Task(agent_id="agent-1", payload={})
            >>> kernel.submit(task)
            >>> busy = kernel.tick()  # Returns True, task processed
            >>> idle = kernel.tick()  # Returns False, queue empty

        Notes:
            - This method should be called repeatedly in a loop
            - Non-blocking: returns immediately if no work available
            - Thread-safe with respect to scheduler operations
        """
        if self.status != KernelStatus.RUNNING:
            logger.warning(f"KERNEL: tick() called but status is {self.status}")
            return False

        task = self.scheduler.next_task()

        if task is None:
            # Idle state - no work to do
            return False

        # Execute the task
        self._execute_task(task)
        return True

    def _execute_task(self, task: Task) -> Any:
        """
        Execute a single task by dispatching to the registered agent.

        This method implements the core dispatch mechanism (ARCH-023)
        and ledger recording (ARCH-024). It wraps agent execution in
        try/except to ensure all outcomes are recorded.

        Args:
            task: The Task to execute

        Returns:
            Any: The result returned by the agent's process() method

        Raises:
            AgentNotFoundError: If no agent is registered for task.agent_id
            Exception: Any exception raised by agent.process()

        Notes:
            - This is an internal method, not part of the public API
            - All executions (success/failure) are recorded to the ledger
            - Ledger recording failures are logged but don't stop execution
        """
        agent_id = task.agent_id

        # Look up the agent in the registry
        if agent_id not in self.agent_registry:
            error_msg = (
                f"Agent '{agent_id}' not found. Available: {list(self.agent_registry.keys())}"
            )
            logger.error(f"KERNEL: {error_msg} (task={task.id})")
            # Record the failure before raising
            self.ledger.record_failure(task, error_msg)
            raise AgentNotFoundError(agent_id=agent_id, task_id=task.id)

        agent = self.agent_registry[agent_id]

        # Record task start
        self.ledger.record_start(task)

        # Dispatch to the agent
        logger.info(
            f">> KERNEL EXEC: Dispatching Task {task.id} to Agent '{agent_id}' "
            f"(payload={task.payload})"
        )

        try:
            # Execute the task
            result = agent.process(task)

            # Convert AgentResponse to dict for ledger storage if needed
            from vibe_core.agent_protocol import AgentResponse

            result_for_ledger = result.to_dict() if isinstance(result, AgentResponse) else result

            # Record successful completion
            self.ledger.record_completion(task, result_for_ledger)

            logger.debug(f"KERNEL: Task {task.id} completed (result={result})")

            return result

        except Exception as e:
            # Record failure before re-raising
            error_msg = f"{type(e).__name__}: {e!s}"
            self.ledger.record_failure(task, error_msg)

            logger.error(f"KERNEL: Task {task.id} failed: {error_msg}")

            # Re-raise the exception so caller can handle it
            raise

    def get_status(self) -> dict:
        """
        Get the current kernel status and metrics.

        Returns:
            dict: Status information including kernel state, queue status,
                  and registered agents

        Example:
            >>> kernel = VibeKernel()
            >>> status = kernel.get_status()
            >>> print(status["kernel_status"])  # "STOPPED"
            >>> print(status["pending_tasks"])  # 0
            >>> print(status["registered_agents"])  # 0
        """
        queue_status = self.scheduler.get_queue_status()
        return {
            "kernel_status": self.status.value,
            "pending_tasks": queue_status["pending_tasks"],
            "queue_type": queue_status["queue_type"],
            "registered_agents": len(self.agent_registry),
            "agent_ids": list(self.agent_registry.keys()),
        }

    def get_agent_manifest(self, agent_id: str) -> dict | None:
        """
        Get the STEWARD manifest for an agent (ARCH-026).

        This returns the machine-readable manifest for the agent,
        enabling other agents or external systems to query agent identity,
        capabilities, and constraints.

        Args:
            agent_id: The agent's unique identifier

        Returns:
            dict: The STEWARD manifest (steward.json format), or None if not found

        Example:
            >>> kernel = VibeKernel()
            >>> manifest = kernel.get_agent_manifest("specialist-planning")
            >>> if manifest:
            ...     print(manifest["agent"]["class"])  # "task_executor"
            ...     print(manifest["capabilities"]["operations"])  # List of ops

        Notes:
            - Manifests are generated during kernel.boot()
            - Returns None if agent is not registered
            - Use agent.get_manifest() for direct agent queries
        """
        manifest = self.manifest_registry.lookup(agent_id)
        return manifest.to_dict() if manifest else None

    def find_agents_by_capability(self, capability: str) -> list[dict]:
        """
        Find all agents with a specific capability (ARCH-026).

        This enables capability-based agent discovery: "find all agents
        that can read files" or "find all agents that do planning".

        Args:
            capability: The capability name to search for

        Returns:
            list[dict]: STEWARD manifests for all agents with the capability

        Example:
            >>> kernel = VibeKernel()
            >>> planning_agents = kernel.find_agents_by_capability("planning")
            >>> print(f"Found {len(planning_agents)} planning agents")

        Notes:
            - Searches manifest capabilities
            - Returns empty list if no matches found
            - Useful for intelligent task routing
        """
        manifests = self.manifest_registry.find_by_capability(capability)
        return [manifest.to_dict() for manifest in manifests]

    def get_task_result(self, task_id: str) -> dict | None:
        """
        Retrieve the result of a completed task from the ledger (ARCH-026 Phase 4).

        This is the main entry point for operators to query task results.
        It returns the complete task record from the ledger, including:
        - input_payload: Original task input
        - output_result: Agent's result (AgentResponse dict)
        - status: COMPLETED, FAILED, or STARTED
        - timestamp: When the task was recorded
        - error_message: Error details if status is FAILED

        Args:
            task_id: The task ID to look up

        Returns:
            dict: Task record from ledger, or None if not found

        Example:
            >>> kernel = VibeKernel()
            >>> result = kernel.get_task_result("task-123")
            >>> if result:
            ...     if result["status"] == "COMPLETED":
            ...         print(result["output_result"])  # AgentResponse dict
            ...     else:
            ...         print(result["error_message"])

        Notes:
            - Works with in-memory or on-disk ledger
            - Returns deserialized JSON (input_payload and output_result)
            - Returns None if task_id not found
        """
        record = self.ledger.get_task(task_id)
        if record is None:
            logger.warning(f"KERNEL: Task {task_id} not found in ledger")
            return None

        logger.debug(
            f"KERNEL: Retrieved task {task_id} from ledger (status={record.get('status')})"
        )
        return record

    def get_task_output(self, task_id: str) -> dict | None:
        """
        Convenience method: Get only the output_result from a task (ARCH-026 Phase 4).

        This is a shorter version of get_task_result() that extracts just the
        output_result field. Useful when you only care about the agent's response,
        not the input or metadata.

        Args:
            task_id: The task ID to look up

        Returns:
            dict: The output_result field (AgentResponse dict), or None if not found

        Example:
            >>> kernel = VibeKernel()
            >>> output = kernel.get_task_output("task-123")
            >>> if output and output["success"]:
            ...     print(f"Agent returned: {output['output']}")

        Notes:
            - Equivalent to: kernel.get_task_result(task_id)["output_result"]
            - Returns None if task not found OR if no output_result
            - Always safe to use (no KeyError)
        """
        record = self.get_task_result(task_id)
        if record is None:
            return None
        return record.get("output_result")

    def get_inbox_messages(self) -> list[dict[str, str]]:
        """
        Get all pending messages from the inbox (GAD-006).

        Returns the list of high-priority context messages loaded during boot.
        If the inbox is empty, returns an empty list.

        Returns:
            list[dict]: List of inbox messages with keys: filename, content

        Example:
            >>> kernel = VibeKernel()
            >>> kernel.boot()
            >>> messages = kernel.get_inbox_messages()
            >>> for msg in messages:
            ...     print(f"Message from {msg['filename']}: {msg['content']}")

        Notes:
            - Messages are scanned during boot()
            - Files are loaded in alphabetical order
            - Returns empty list if no messages found
        """
        return self.inbox_messages

    def get_git_status(self) -> str | None:
        """
        Get the current git synchronization status (ARCH-044).

        This returns the git sync status detected during kernel boot.
        The operator can use this to determine if system updates are needed.

        Returns:
            str | None: Git sync status or None if not available

        Possible values:
            - "SYNCED": Repository is up-to-date
            - "BEHIND_BY_N": N commits behind remote (e.g. "BEHIND_BY_5")
            - "DIVERGED": Local and remote have diverged
            - "FETCH_FAILED": Could not fetch (offline or no remote)
            - "NO_REPO": Not a git repository
            - None: Status not checked (pre-ARCH-044 boot)

        Example:
            >>> kernel = VibeKernel()
            >>> kernel.boot()
            >>> status = kernel.get_git_status()
            >>> if status and status.startswith("BEHIND"):
            ...     print("System update available")

        Notes:
            - Status is set during boot() via VIBE_GIT_STATUS env var
            - Operator should check STEWARD.md for update policy
            - Use maintenance specialist to perform updates
        """
        return self.git_status
