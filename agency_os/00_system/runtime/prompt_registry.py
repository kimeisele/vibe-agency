#!/usr/bin/env python3
"""
Prompt Registry - High-level interface for governed prompt composition

This is the "heart" of the system - provides automatic governance injection,
context enrichment, and tool/SOP composition.

Usage:
    from agency_os.runtime import PromptRegistry

    # Compose prompt with full governance
    prompt = PromptRegistry.compose(
        agent="VIBE_ALIGNER",
        task="02_feature_extraction",
        workspace="my-project",
        inject_governance=True,
        inject_tools=["google_search"],
        inject_sops=["SOP_001"]
    )

Architecture:
    Wraps PromptRuntime (low-level composition) and adds:
    - Guardian Directives injection (from SSF)
    - Context enrichment (manifest, workspace paths)
    - Tool definitions injection
    - SOP injection
    - Composition order: Governance → Context → Tools → SOPs → Agent

Created: 2025-11-15
Version: 1.0 (MVP)
"""

import yaml
import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import PromptRuntime (same directory)
# Use try/except to handle both direct execution and module import
try:
    from .prompt_runtime import PromptRuntime, PromptRuntimeError
except ImportError:
    # Direct execution - import without relative path
    from prompt_runtime import PromptRuntime, PromptRuntimeError

# Import workspace utilities
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / 'scripts'))

try:
    from workspace_utils import (
        resolve_manifest_path,
        load_workspace_manifest,
        get_active_workspace
    )
    WORKSPACE_UTILS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"workspace_utils not available: {e}")
    WORKSPACE_UTILS_AVAILABLE = False


logger = logging.getLogger(__name__)


class PromptRegistryError(Exception):
    """Base exception for PromptRegistry errors"""
    pass


class GovernanceLoadError(PromptRegistryError):
    """Raised when Guardian Directives can't be loaded"""
    pass


class ContextEnrichmentError(PromptRegistryError):
    """Raised when workspace context enrichment fails"""
    pass


class PromptRegistry:
    """
    High-level interface for prompt composition with automatic injections.

    This is a thin wrapper around PromptRuntime that adds governance and
    context enrichment capabilities.
    """

    # Class-level cache for Guardian Directives (loaded once)
    _guardian_directives_cache: Optional[str] = None

    @classmethod
    def compose(
        cls,
        agent: str,
        task: Optional[str] = None,  # Optional for meta-agents like SSF_ROUTER
        workspace: Optional[str] = None,
        inject_governance: bool = True,
        inject_tools: Optional[List[str]] = None,
        inject_sops: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Compose a governed prompt with all injections.

        Args:
            agent: Agent ID (e.g., "VIBE_ALIGNER")
            task: Task ID (e.g., "02_feature_extraction"). Optional for meta-agents.
            workspace: Workspace name or path. Defaults to active workspace.
            inject_governance: Whether to inject Guardian Directives (default: True)
            inject_tools: List of tool names to inject (e.g., ["google_search"])
            inject_sops: List of SOP IDs to inject (e.g., ["SOP_001"])
            context: Additional runtime context

        Returns:
            Fully composed prompt string ready for LLM execution

        Raises:
            PromptRuntimeError: If base prompt composition fails
            GovernanceLoadError: If Guardian Directives can't be loaded
            ContextEnrichmentError: If workspace context enrichment fails
        """
        logger.info(f"Composing prompt: agent={agent}, task={task}, workspace={workspace}")

        # Initialize context if not provided
        if context is None:
            context = {}

        # Resolve workspace
        if workspace is None and WORKSPACE_UTILS_AVAILABLE:
            workspace = get_active_workspace()
        elif workspace is None:
            workspace = "ROOT"  # Fallback

        context["_registry_workspace"] = workspace

        # 1. Get base prompt from PromptRuntime
        runtime = PromptRuntime()

        # If task is None, create a minimal context-only prompt
        if task is None:
            logger.warning(f"No task specified for agent {agent} - creating meta-agent prompt")
            base_prompt = cls._create_meta_agent_prompt(agent)
        else:
            base_prompt = runtime.execute_task(agent, task, context)

        # 2. Build injection layers (in order)
        layers = []

        # Layer 1: Governance (if requested)
        if inject_governance:
            try:
                governance_section = cls._load_guardian_directives()
                layers.append(governance_section)
                logger.debug("Guardian Directives injected")
            except Exception as e:
                logger.error(f"Failed to load Guardian Directives: {e}")
                raise GovernanceLoadError(f"Failed to inject governance: {e}") from e

        # Layer 2: Context (automatic)
        try:
            context_section = cls._enrich_context(workspace, context)
            layers.append(context_section)
            logger.debug("Context enrichment completed")
        except Exception as e:
            logger.error(f"Failed to enrich context: {e}")
            raise ContextEnrichmentError(f"Failed to enrich context: {e}") from e

        # Layer 3: Tools (if requested)
        if inject_tools:
            tools_section = cls._inject_tools(inject_tools)
            layers.append(tools_section)
            logger.debug(f"Tools injected: {inject_tools}")

        # Layer 4: SOPs (if requested)
        if inject_sops:
            sops_section = cls._inject_sops(inject_sops)
            layers.append(sops_section)
            logger.debug(f"SOPs injected: {inject_sops}")

        # 3. Combine layers + base prompt
        # Order: Governance → Context → Tools → SOPs → Agent
        final_prompt = "\n\n".join(layers + [base_prompt])

        prompt_size = len(final_prompt)
        logger.info(f"Prompt composed successfully: {prompt_size:,} chars")

        return final_prompt

    @classmethod
    def _load_guardian_directives(cls) -> str:
        """
        Load Guardian Directives from SSF knowledge base (with caching).

        Returns:
            Formatted markdown section with Guardian Directives
        """
        # Return cached version if available
        if cls._guardian_directives_cache is not None:
            return cls._guardian_directives_cache

        # Load from file
        directives_path = (
            _REPO_ROOT /
            "system_steward_framework" /
            "knowledge" /
            "guardian_directives.yaml"
        )

        if not directives_path.exists():
            raise GovernanceLoadError(
                f"Guardian Directives not found: {directives_path}\n"
                f"Expected location: system_steward_framework/knowledge/guardian_directives.yaml\n"
                f"Fix: Create Guardian Directives file or disable governance injection"
            )

        try:
            with open(directives_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise GovernanceLoadError(
                f"Invalid YAML in Guardian Directives: {e}"
            ) from e

        # Use injection template from YAML
        template = data.get("injection_template", "")
        if not template:
            raise GovernanceLoadError(
                "Guardian Directives YAML missing 'injection_template' field"
            )

        # Cache for future calls
        cls._guardian_directives_cache = template.strip()

        return cls._guardian_directives_cache

    @classmethod
    def _enrich_context(cls, workspace: str, context: Dict[str, Any]) -> str:
        """
        Enrich context with workspace manifest and runtime state.

        Args:
            workspace: Workspace name
            context: Runtime context dict

        Returns:
            Formatted markdown section with enriched context
        """
        lines = ["# === RUNTIME CONTEXT ===\n"]

        # Add workspace info
        lines.append(f"**Active Workspace:** `{workspace}`\n")

        # Load manifest if workspace utils available
        manifest_data = None
        if WORKSPACE_UTILS_AVAILABLE:
            try:
                manifest_path = resolve_manifest_path(workspace)
                if manifest_path.exists():
                    manifest_data = load_workspace_manifest(workspace)
                    lines.append(f"**Manifest Path:** `{manifest_path}`\n")
            except Exception as e:
                logger.warning(f"Could not load manifest for workspace {workspace}: {e}")
                lines.append(f"**Manifest:** *(not available - {e})*\n")
        else:
            lines.append(f"**Manifest:** *(workspace_utils not available)*\n")

        # Add manifest state (if loaded)
        if manifest_data:
            lines.append("\n**Project State:**")
            lines.append(f"- Project ID: `{manifest_data.get('project_id', 'unknown')}`")
            lines.append(f"- Current Phase: `{manifest_data.get('current_phase', 'unknown')}`")

            # Artifacts summary
            artifacts = manifest_data.get('artifacts', {})
            if artifacts:
                lines.append(f"- Artifacts: {len(artifacts)} available")
                for key in list(artifacts.keys())[:5]:  # Show first 5
                    lines.append(f"  - `{key}`")
                if len(artifacts) > 5:
                    lines.append(f"  - ... and {len(artifacts) - 5} more")

            # Budget tracking
            budget_used = manifest_data.get('budget_tracking', {}).get('total_tokens_used', 0)
            if budget_used:
                lines.append(f"- Budget Used: {budget_used:,} tokens")

        # Add additional context (from caller)
        if context and len(context) > 1:  # More than just _registry_workspace
            lines.append("\n**Additional Context:**")
            for key, value in context.items():
                if not key.startswith("_"):  # Skip internal keys
                    if isinstance(value, dict):
                        lines.append(f"- **{key}:**")
                        for k, v in list(value.items())[:3]:  # Limit nested items
                            lines.append(f"  - {k}: `{v}`")
                    else:
                        lines.append(f"- **{key}:** `{value}`")

        return "\n".join(lines)

    @classmethod
    def _inject_tools(cls, tool_names: List[str]) -> str:
        """
        Inject tool definitions.

        Args:
            tool_names: List of tool names to inject

        Returns:
            Formatted markdown section with tool definitions
        """
        # Load tool definitions
        tool_defs_path = (
            _REPO_ROOT /
            "agency_os" /
            "00_system" /
            "orchestrator" /
            "tools" /
            "tool_definitions.yaml"
        )

        if not tool_defs_path.exists():
            logger.warning(f"Tool definitions not found: {tool_defs_path}")
            return "# === TOOLS ===\n\n*(Tool definitions file not found)*"

        try:
            with open(tool_defs_path) as f:
                all_tools = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in tool definitions: {e}")
            return "# === TOOLS ===\n\n*(Invalid tool definitions YAML)*"

        # Filter to requested tools
        tools_dict = all_tools.get("tools", {})
        filtered_tools = {name: tool for name, tool in tools_dict.items() if name in tool_names}

        if not filtered_tools:
            return "# === TOOLS ===\n\n*(No matching tools found)*"

        # Format as markdown (reuse PromptRuntime's formatting logic)
        lines = ["# === TOOLS ===\n"]
        lines.append("You have access to the following tools:\n")

        for tool_name, tool_def in filtered_tools.items():
            lines.append(f"## Tool: `{tool_name}`\n")
            lines.append(f"**Description:** {tool_def.get('description', 'No description')}\n")

            # Parameters
            params = tool_def.get('parameters', {})
            if params:
                lines.append("\n**Parameters:**")
                for param_name, param_spec in params.items():
                    required = " (required)" if param_spec.get('required', False) else " (optional)"
                    param_type = param_spec.get('type', 'any')
                    param_desc = param_spec.get('description', '')
                    default = f", default: `{param_spec['default']}`" if 'default' in param_spec else ""
                    lines.append(f"- `{param_name}` ({param_type}){required}: {param_desc}{default}")

            lines.append("\n---\n")

        return "\n".join(lines)

    @classmethod
    def _inject_sops(cls, sop_ids: List[str]) -> str:
        """
        Inject Standard Operating Procedures.

        Args:
            sop_ids: List of SOP IDs (e.g., ["SOP_001", "SOP_005"])

        Returns:
            Formatted markdown section with SOP content
        """
        sops_dir = _REPO_ROOT / "system_steward_framework" / "knowledge" / "sops"

        if not sops_dir.exists():
            logger.warning(f"SOPs directory not found: {sops_dir}")
            return "# === STANDARD OPERATING PROCEDURES ===\n\n*(SOPs directory not found)*"

        lines = ["# === STANDARD OPERATING PROCEDURES ===\n"]

        for sop_id in sop_ids:
            # Try to find SOP file with pattern SOP_XXX_*.md
            sop_files = list(sops_dir.glob(f"{sop_id}_*.md"))

            if not sop_files:
                # Fall back to exact match
                sop_file = sops_dir / f"{sop_id}.md"
                if sop_file.exists():
                    sop_files = [sop_file]

            if sop_files:
                sop_file = sop_files[0]  # Use first match
                try:
                    with open(sop_file) as f:
                        sop_content = f.read()
                    lines.append(f"\n## {sop_id}\n")
                    lines.append(sop_content)
                    lines.append("\n---\n")
                except Exception as e:
                    logger.error(f"Failed to load SOP {sop_id}: {e}")
                    lines.append(f"\n## {sop_id}\n")
                    lines.append(f"*(Error loading SOP: {e})*\n")
            else:
                logger.warning(f"SOP file not found for ID: {sop_id}")
                lines.append(f"\n## {sop_id}\n")
                lines.append(f"*(SOP file not found in {sops_dir})*\n")

        return "\n".join(lines)

    @classmethod
    def _create_meta_agent_prompt(cls, agent: str) -> str:
        """
        Create a minimal prompt for meta-agents (agents with no tasks).

        Args:
            agent: Agent ID

        Returns:
            Minimal base prompt
        """
        return f"""# === AGENT: {agent} ===

This is a meta-agent session (no specific task).
Context and governance will be injected via Prompt Registry.

Await further instructions.
"""


# =================================================================
# CLI Interface (for testing)
# =================================================================

if __name__ == "__main__":
    import sys

    # Example usage
    context = {
        "test_mode": True,
        "example_key": "example_value"
    }

    # Test composition with all injections
    composed_prompt = PromptRegistry.compose(
        agent="VIBE_ALIGNER",
        task="02_feature_extraction",
        workspace="ROOT",
        inject_governance=True,
        inject_tools=["google_search"],
        inject_sops=["SOP_001"],
        context=context
    )

    # Output to file for inspection
    output_file = Path("/home/user/vibe-agency/COMPOSED_PROMPT_REGISTRY_TEST.md")
    with open(output_file, "w") as f:
        f.write(composed_prompt)

    print(f"✓ Composed prompt written to: {output_file}")
    print(f"\nPrompt size: {len(composed_prompt):,} chars")
    print(f"\nFirst 1000 chars:")
    print("-" * 60)
    print(composed_prompt[:1000] + "...")
