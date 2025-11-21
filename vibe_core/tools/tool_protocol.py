"""
Tool Protocol for Vibe Agency (ARCH-027).

This module defines the interface for all tools that can be called by agents.
Tools provide "hands" to LLM agents - the ability to perform actions on the
system (read files, write files, execute commands, etc.).

Architecture:
- ToolCall: Protocol defining the tool interface
- All tools implement execute(**kwargs) method
- Return structured results (success/error format)

Security:
- Tools are executed through ToolRegistry (gatekeeper)
- InvariantChecker validates calls before execution (ARCH-029)
- Defense in depth: Soul → Iron Dome → Tool execution

Design Principles:
- Simple interface (just execute method)
- Structured results (dict with success/error)
- Type-safe (runtime_checkable Protocol)
- Extensible (easy to add new tools)
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ToolCall(Protocol):
    """
    Protocol defining the interface for all tools.

    Any class implementing this protocol can be registered as a tool
    and called by agents.

    Example:
        >>> class MyTool:
        ...     def execute(self, **kwargs) -> dict:
        ...         return {"result": "success"}
        >>>
        >>> tool = MyTool()
        >>> isinstance(tool, ToolCall)  # True
        >>> result = tool.execute(param1="value")
    """

    def execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result (typically a dict with success/error info)

        Example:
            >>> tool.execute(path="file.txt", content="Hello")
            {"success": True, "result": "File written"}
        """
        ...
