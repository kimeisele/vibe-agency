"""
Tool Registry for Vibe Agency (ARCH-027 + ARCH-029).

The ToolRegistry is the central gatekeeper for all tool execution. It:
1. Registers available tools
2. Validates tool calls against Soul governance (ARCH-029)
3. Executes tools and returns structured results
4. Logs all tool calls for audit trail

Security Architecture (Defense in Depth):
    User/Agent Request
         ↓
    🛡️ Layer 1: Soul Governance (InvariantChecker)
         → "Is this EVER allowed?" (Global rules from config/soul.yaml)
         ↓
    🛡️ Layer 2: Tool Execution
         → Actual tool logic (read file, write file, etc.)
         ↓
    Result (success/error)

This is "Security by Design" - governance is not bolted on afterward,
it's baked into the execution path from day 1.

Example:
    >>> from vibe_core.governance import InvariantChecker
    >>> from vibe_core.tools.file_tools import WriteFileTool
    >>>
    >>> checker = InvariantChecker("config/soul.yaml")
    >>> registry = ToolRegistry(invariant_checker=checker)
    >>> registry.register("write_file", WriteFileTool())
    >>>
    >>> # Safe operation - allowed
    >>> result = registry.execute("write_file", path="docs/readme.md", content="...")
    >>> print(result["success"])  # True
    >>>
    >>> # Dangerous operation - blocked by Soul
    >>> result = registry.execute("write_file", path=".git/config", content="...")
    >>> print(result["blocked"])  # True
    >>> print(result["error"])    # "Governance Violation: ..."
"""

import logging
from typing import Any, Optional

from vibe_core.governance.invariants import InvariantChecker, SoulResult
from vibe_core.tools.tool_protocol import ToolCall

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry and gatekeeper for tool execution.

    The ToolRegistry enforces governance rules before executing any tool.
    This ensures that dangerous operations (e.g., modifying .git, escaping
    sandbox) are blocked BEFORE they can cause damage.

    Architecture:
    - Tools register themselves by name
    - execute() validates against InvariantChecker (Soul governance)
    - Blocked operations return {"blocked": True, "error": "..."}
    - Successful operations return {"success": True, "result": ...}
    """

    def __init__(self, invariant_checker: Optional[InvariantChecker] = None):
        """
        Initialize the ToolRegistry.

        Args:
            invariant_checker: Optional InvariantChecker for Soul governance.
                              If None, ALL tools execute without governance checks.
                              (Use None only for testing - production MUST have checker)

        Example:
            >>> # Production (with governance)
            >>> checker = InvariantChecker("config/soul.yaml")
            >>> registry = ToolRegistry(invariant_checker=checker)
            >>>
            >>> # Testing (no governance - use carefully!)
            >>> registry = ToolRegistry(invariant_checker=None)
        """
        self._tools: dict[str, ToolCall] = {}
        self._invariant_checker = invariant_checker

        if invariant_checker:
            logger.info(
                f"🛡️ ToolRegistry initialized with Soul governance "
                f"({invariant_checker.rule_count} rules loaded)"
            )
        else:
            logger.warning(
                "⚠️ ToolRegistry initialized WITHOUT governance checks. "
                "This should only be used in testing!"
            )

    def register(self, name: str, tool: ToolCall) -> None:
        """
        Register a tool with the registry.

        Args:
            name: Tool name (e.g., "write_file", "read_file")
            tool: Tool instance implementing ToolCall protocol

        Example:
            >>> from vibe_core.tools.file_tools import WriteFileTool
            >>> registry.register("write_file", WriteFileTool())
        """
        self._tools[name] = tool
        logger.debug(f"📝 Registered tool: {name}")

    def execute(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Execute a tool with governance validation.

        Execution flow:
        1. Check if tool exists
        2. 🛡️ Validate against Soul governance (if checker configured)
        3. Execute tool
        4. Return structured result

        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool-specific parameters

        Returns:
            dict: Structured result with keys:
                - success (bool): Whether execution succeeded
                - result (Any): Tool result (if success=True)
                - error (str): Error message (if success=False)
                - blocked (bool): Whether blocked by governance (if success=False)

        Example:
            >>> # Successful execution
            >>> result = registry.execute("write_file", path="test.txt", content="hi")
            >>> print(result)
            {"success": True, "result": "File written: test.txt"}
            >>>
            >>> # Blocked by governance
            >>> result = registry.execute("write_file", path=".git/config", content="x")
            >>> print(result)
            {"success": False, "blocked": True, "error": "Governance Violation: ..."}
            >>>
            >>> # Tool not found
            >>> result = registry.execute("unknown_tool", param="value")
            >>> print(result)
            {"success": False, "error": "Tool not found: unknown_tool"}
        """
        # 1. Existence check
        if tool_name not in self._tools:
            logger.error(f"❌ Tool not found: {tool_name}")
            return {"success": False, "error": f"Tool not found: {tool_name}"}

        # 2. 🛡️ SOUL GOVERNANCE CHECK (Layer 1 - ARCH-029)
        if self._invariant_checker:
            check: SoulResult = self._invariant_checker.check_tool_call(
                tool_name, kwargs
            )
            if not check.allowed:
                logger.warning(f"⛔ SOUL BLOCKED {tool_name}: {check.reason}")
                return {
                    "success": False,
                    "error": f"Governance Violation: {check.reason}",
                    "blocked": True,
                }

        # 3. Tool execution
        try:
            logger.debug(f"🔧 Executing tool: {tool_name} with params: {kwargs}")
            tool = self._tools[tool_name]
            result = tool.execute(**kwargs)

            logger.info(f"✅ Tool {tool_name} executed successfully")
            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"❌ Tool {tool_name} execution failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def list_tools(self) -> list[str]:
        """
        Get list of registered tool names.

        Returns:
            List of tool names

        Example:
            >>> registry.list_tools()
            ['write_file', 'read_file']
        """
        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            name: Tool name

        Returns:
            True if tool is registered

        Example:
            >>> registry.has_tool("write_file")
            True
            >>> registry.has_tool("unknown")
            False
        """
        return name in self._tools

    @property
    def tool_count(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    @property
    def has_governance(self) -> bool:
        """Return True if governance checker is configured."""
        return self._invariant_checker is not None
