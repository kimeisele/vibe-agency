"""Tool executor for dispatching tool calls from Claude Code."""

from typing import Any

# Support both relative and absolute imports
try:
    from .google_search_client import GoogleSearchClient
    from .web_fetch_client import WebFetchClient
except ImportError:
    from google_search_client import GoogleSearchClient
    from web_fetch_client import WebFetchClient


class ToolExecutor:
    """Executes tool calls from Claude Code"""

    def __init__(self):
        # Lazy-load tools to avoid errors if keys aren't set
        self.tools = {}
        self._initialized = False

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
        Execute a tool call

        Args:
            tool_name: Name of tool (e.g., 'google_search')
            parameters: Tool parameters dict

        Returns:
            Tool result dict (serializable to JSON)
        """
        self._ensure_tools_initialized()

        if tool_name not in self.tools:
            return {"error": f"Tool not available: {tool_name} (check API keys)"}

        try:
            if tool_name == "google_search":
                query = parameters.get("query")
                num_results = parameters.get("num_results", 10)
                return {"results": self.tools["google_search"].search(query, num_results)}

            elif tool_name == "web_fetch":
                url = parameters.get("url")
                return self.tools["web_fetch"].fetch(url)

        except Exception as e:
            return {"error": f"Tool execution failed: {e}"}
