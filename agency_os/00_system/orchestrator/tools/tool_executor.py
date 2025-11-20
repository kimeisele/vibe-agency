"""Tool executor for dispatching tool calls from Claude Code."""

import importlib
from typing import Any

# Support both relative and absolute imports
try:
    from .google_search_client import GoogleSearchClient
    from .web_fetch_client import WebFetchClient
except ImportError:
    from google_search_client import GoogleSearchClient
    from web_fetch_client import WebFetchClient

# Import Iron Dome protection (directory name starts with digit, use importlib)
tool_safety_guard = importlib.import_module("agency_os.00_system.runtime.tool_safety_guard")
ToolSafetyGuard = tool_safety_guard.ToolSafetyGuard
ToolSafetyGuardError = tool_safety_guard.ToolSafetyGuardError


class ToolExecutor:
    """Executes tool calls from Claude Code"""

    def __init__(self, enable_iron_dome: bool = True):
        # Lazy-load tools to avoid errors if keys aren't set
        self.tools = {}
        self._initialized = False

        # Initialize Iron Dome protection layer
        self.iron_dome = ToolSafetyGuard(enable_strict_mode=enable_iron_dome)
        self.enable_iron_dome = enable_iron_dome

    def _ensure_tools_initialized(self):
        """Initialize tools on first use"""
        if self._initialized:
            return

        # Always available
        self.tools["web_fetch"] = WebFetchClient()

        # Only if API keys are set
        import os

        if os.getenv("GOOGLE_SEARCH_API_KEY") and os.getenv("GOOGLE_SEARCH_ENGINE_ID"):
            self.tools["google_search"] = GoogleSearchClient()

        self._initialized = True

    def execute_tool(self, tool_name: str, parameters: dict[str, Any]) -> dict:
        """
        Execute a tool call with Iron Dome protection.

        Args:
            tool_name: Name of tool (e.g., 'google_search')
            parameters: Tool parameters dict

        Returns:
            Tool result dict (serializable to JSON)
        """
        # 🛡️ IRON DOME: Pre-execution safety check
        if self.enable_iron_dome:
            allowed, violation = self.iron_dome.check_action(tool_name, parameters)
            if not allowed:
                return {
                    "error": violation.message,
                    "blocked_by": "iron_dome",
                    "rule": violation.rule,
                    "severity": violation.severity.value,
                }

        self._ensure_tools_initialized()

        if tool_name not in self.tools:
            return {"error": f"Tool not available: {tool_name} (check API keys)"}

        try:
            result = None

            if tool_name == "google_search":
                query = parameters.get("query")
                num_results = parameters.get("num_results", 10)
                result = {"results": self.tools["google_search"].search(query, num_results)}

            elif tool_name == "web_fetch":
                url = parameters.get("url")
                result = self.tools["web_fetch"].fetch(url)

            # 🛡️ IRON DOME: Post-execution tracking
            if self.enable_iron_dome and result:
                self._track_tool_execution(tool_name, parameters)

            return result

        except Exception as e:
            return {"error": f"Tool execution failed: {e}"}

    def _track_tool_execution(self, tool_name: str, parameters: dict[str, Any]):
        """
        Track tool execution for Iron Dome session context.

        Args:
            tool_name: Name of tool that was executed
            parameters: Tool parameters
        """
        # Track file reads
        if tool_name in ["read_file", "cat", "view_file"]:
            file_path = parameters.get("path") or parameters.get("file")
            if file_path:
                self.iron_dome.record_file_read(file_path)

        # Track file writes
        elif tool_name in ["edit_file", "write_file", "modify_file", "save_file"]:
            file_path = parameters.get("path") or parameters.get("file")
            if file_path:
                self.iron_dome.record_file_write(file_path)
