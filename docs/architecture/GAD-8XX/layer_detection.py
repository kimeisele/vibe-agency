"""
GAD-800 Layer Detection Implementation

Concrete implementation for detecting which execution layer the system is running in.

LAYERS:
- Layer 1: Prompt-only (browser, no tools, manual operations)
- Layer 2: Tool-based (Claude Code, file access, automated tools)
- Layer 3: Runtime (full APIs, services, external integrations)

This module provides runtime layer detection with graceful degradation support.
"""

import sys
from pathlib import Path
from typing import Literal, Dict, List, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


LayerType = Literal[1, 2, 3]


class LayerDetector:
    """
    Concrete layer detection implementation.

    Detects which execution layer is currently available and provides
    capability checks for graceful degradation.
    """

    def __init__(
        self,
        runtime_health_url: str = "http://localhost:8000/health",
        timeout: float = 1.0
    ):
        """
        Initialize layer detector.

        Args:
            runtime_health_url: URL to check for runtime services (Layer 3)
            timeout: Timeout in seconds for service checks
        """
        self.runtime_health_url = runtime_health_url
        self.timeout = timeout
        self._cached_layer: Optional[LayerType] = None

    def detect_layer(self, use_cache: bool = True) -> LayerType:
        """
        Detect current execution layer.

        Detection logic (checked in order):
        1. Check Layer 3: Runtime services available?
        2. Check Layer 2: Tool execution capability?
        3. Default: Layer 1 (prompt-only)

        Args:
            use_cache: Whether to use cached layer detection result

        Returns:
            1: Browser/prompt-only
            2: Claude Code/tools
            3: Full runtime/APIs
        """
        if use_cache and self._cached_layer is not None:
            return self._cached_layer

        # Check Layer 3: Runtime services
        if self._check_runtime_services():
            self._cached_layer = 3
            return 3

        # Check Layer 2: Tool execution capability
        if self._check_tool_capability():
            self._cached_layer = 2
            return 2

        # Default: Layer 1
        self._cached_layer = 1
        return 1

    def _check_runtime_services(self) -> bool:
        """
        Check if runtime services are available (Layer 3).

        Attempts to connect to the health endpoint of runtime services.

        Returns:
            True if runtime services are available, False otherwise
        """
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(
                self.runtime_health_url,
                timeout=self.timeout
            )
            return response.status_code == 200
        except (requests.RequestException, ConnectionError, OSError):
            return False

    def _check_tool_capability(self) -> bool:
        """
        Check if tools can be executed (Layer 2).

        Detection strategies:
        1. Check for .claude/settings.local.json (Claude Code environment)
        2. Check for Claude Code markers in environment
        3. Check for workspace indicators

        Returns:
            True if tool execution is available, False otherwise
        """
        # Strategy 1: Check for Claude Code config
        config_file = Path('.claude/settings.local.json')
        if config_file.exists():
            return True

        # Strategy 2: Check for Claude Code environment markers
        claude_markers = [
            '/tmp/.claude_code',
            Path.home() / '.config' / 'claude-code'
        ]
        for marker in claude_markers:
            if Path(marker).exists():
                return True

        # Strategy 3: Check Python environment for tool execution capability
        # In Claude Code, sys.modules will contain specific packages
        if 'anthropic' in sys.modules or 'claude_code' in sys.modules:
            return True

        # Strategy 4: Check for workspace directory structure
        # Vibe-agency workspace indicates tool capability
        workspace_indicators = [
            Path('agency_os'),
            Path('knowledge_department'),
            Path('steward'),
            Path('.session_handoff.json')
        ]

        # If at least 2 indicators present, likely in tool environment
        present_count = sum(1 for indicator in workspace_indicators if indicator.exists())
        if present_count >= 2:
            return True

        return False

    def get_capabilities(self, layer: Optional[LayerType] = None) -> List[str]:
        """
        Get list of capabilities available at a specific layer.

        Args:
            layer: Layer to query (if None, uses detected layer)

        Returns:
            List of capability names available at this layer
        """
        if layer is None:
            layer = self.detect_layer()

        capabilities_map: Dict[LayerType, List[str]] = {
            1: [
                "guidance",
                "manual_operations",
                "prompt_based_interaction",
                "user_file_access",
                "manual_validation"
            ],
            2: [
                "automated_queries",
                "tool_execution",
                "file_system_access",
                "validation_tools",
                "knowledge_query",
                "steward_validate",
                "receipt_generation",
                "integrity_checks"
            ],
            3: [
                "api_calls",
                "runtime_services",
                "policy_enforcement",
                "research_engine",
                "governance_engine",
                "vector_search",
                "semantic_expansion",
                "audit_logging",
                "client_research_apis",
                "federated_query"
            ]
        }

        # Return cumulative capabilities (Layer 3 includes Layer 2 and 1)
        all_capabilities = []
        for l in range(1, layer + 1):
            all_capabilities.extend(capabilities_map[l])

        return all_capabilities

    def has_capability(self, capability: str, layer: Optional[LayerType] = None) -> bool:
        """
        Check if a specific capability is available.

        Args:
            capability: Capability name to check
            layer: Layer to query (if None, uses detected layer)

        Returns:
            True if capability is available, False otherwise
        """
        if layer is None:
            layer = self.detect_layer()

        return capability in self.get_capabilities(layer)

    def clear_cache(self):
        """Clear cached layer detection result."""
        self._cached_layer = None


class LayerAdapter:
    """
    Adapter class that activates components based on detected layer.

    Use this as a base class for components that need layer-aware behavior.
    """

    def __init__(self, detector: Optional[LayerDetector] = None):
        """
        Initialize layer adapter.

        Args:
            detector: LayerDetector instance (creates new one if None)
        """
        self.detector = detector or LayerDetector()
        self.layer = self.detector.detect_layer()
        self.activate_for_layer(self.layer)

    def activate_for_layer(self, layer: LayerType):
        """
        Activate component for specific layer.

        Override this method in subclasses to implement layer-specific behavior.

        Args:
            layer: Layer to activate for (1, 2, or 3)
        """
        if layer == 1:
            self.mode = "prompt"
            self.capabilities = self.detector.get_capabilities(1)
        elif layer == 2:
            self.mode = "tool"
            self.capabilities = self.detector.get_capabilities(2)
        elif layer == 3:
            self.mode = "runtime"
            self.capabilities = self.detector.get_capabilities(3)

    def degrade_to(self, target_layer: LayerType):
        """
        Gracefully degrade to a lower layer.

        Args:
            target_layer: Layer to degrade to (must be lower than current)
        """
        if target_layer >= self.layer:
            raise ValueError(
                f"Cannot degrade from Layer {self.layer} to Layer {target_layer}. "
                f"Target layer must be lower than current layer."
            )

        self.layer = target_layer
        self.activate_for_layer(target_layer)


# Convenience function for quick layer detection
def get_current_layer() -> LayerType:
    """
    Quick function to get current layer without creating detector instance.

    Returns:
        Current execution layer (1, 2, or 3)
    """
    detector = LayerDetector()
    return detector.detect_layer()


# Usage example
if __name__ == "__main__":
    detector = LayerDetector()
    current_layer = detector.detect_layer()

    print(f"🔍 Running in Layer {current_layer}")
    print(f"📋 Available capabilities: {detector.get_capabilities(current_layer)}")

    # Check specific capabilities
    if detector.has_capability("knowledge_query"):
        print("✅ Knowledge query available")
    else:
        print("❌ Knowledge query not available (Layer 1 mode)")

    if detector.has_capability("research_engine"):
        print("✅ Research engine available")
    else:
        print("⚠️  Research engine not available (degraded from Layer 3)")
