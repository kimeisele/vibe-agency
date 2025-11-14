"""Tool executor for dispatching tool calls from Claude Code."""

import json
from typing import Dict, Any
from .google_search_client import GoogleSearchClient
from .web_fetch_client import WebFetchClient


class ToolExecutor:
    """Executes tool calls from Claude Code"""

    def __init__(self):
        self.tools = {
            'google_search': GoogleSearchClient(),
            'web_fetch': WebFetchClient()
        }

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict:
        """
        Execute a tool call

        Args:
            tool_name: Name of tool (e.g., 'google_search')
            parameters: Tool parameters dict

        Returns:
            Tool result dict (serializable to JSON)
        """
        if tool_name not in self.tools:
            return {'error': f"Unknown tool: {tool_name}"}

        try:
            if tool_name == 'google_search':
                query = parameters.get('query')
                num_results = parameters.get('num_results', 10)
                return {'results': self.tools['google_search'].search(query, num_results)}

            elif tool_name == 'web_fetch':
                url = parameters.get('url')
                return self.tools['web_fetch'].fetch(url)

        except Exception as e:
            return {'error': f"Tool execution failed: {e}"}
