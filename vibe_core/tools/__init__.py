"""
Tool System for Vibe Agency (ARCH-027).

This module provides the tool execution infrastructure for agents:
- ToolCall protocol: Interface all tools must implement
- ToolRegistry: Central gatekeeper with governance integration
- File tools: Basic file system operations

Security Architecture:
The tool system integrates with ARCH-029 (Soul Governance) to ensure
all tool calls are validated against invariant rules before execution.

Example:
    >>> from vibe_core.tools import ToolRegistry, WriteFileTool
    >>> from vibe_core.governance import InvariantChecker
    >>>
    >>> # Setup with governance
    >>> checker = InvariantChecker("config/soul.yaml")
    >>> registry = ToolRegistry(invariant_checker=checker)
    >>> registry.register("write_file", WriteFileTool())
    >>>
    >>> # Safe operation
    >>> result = registry.execute("write_file", path="test.txt", content="ok")
    >>> print(result["success"])  # True
    >>>
    >>> # Blocked operation
    >>> result = registry.execute("write_file", path=".git/config", content="bad")
    >>> print(result["blocked"])  # True
"""

from vibe_core.tools.file_tools import ReadFileTool, WriteFileTool
from vibe_core.tools.tool_protocol import ToolCall
from vibe_core.tools.tool_registry import ToolRegistry

__all__ = ["ToolCall", "ToolRegistry", "ReadFileTool", "WriteFileTool"]
