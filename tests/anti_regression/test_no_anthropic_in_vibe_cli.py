#!/usr/bin/env python3
"""
Anti-Regression Test: No Anthropic SDK in vibe-cli (MVP)
========================================================

RULE: vibe-cli MUST NOT import or use Anthropic SDK in MVP.

WHY: MVP = DELEGATION ONLY
     - Claude Code is the ONLY operator
     - vibe-cli is a BRIDGE, not an executor
     - Nested API calls = architecture violation

ENFORCEMENT: This test FAILS if vibe-cli contains Anthropic SDK usage.

Related: docs/architecture/EXECUTION_MODE_STRATEGY.md
"""

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_vibe_cli_no_anthropic_imports():
    """
    ANTI-REGRESSION: vibe-cli MUST NOT import anthropic SDK

    Prevents recurring bug where developers add:
        import anthropic

    This violates MVP architecture (delegation only).
    """
    vibe_cli_path = REPO_ROOT / "vibe-cli"

    with open(vibe_cli_path) as f:
        content = f.read()

    # Check for anthropic imports
    forbidden_imports = [
        "import anthropic",
        "from anthropic import",
    ]

    violations = []
    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern in forbidden_imports:
            if pattern in line:
                violations.append(f"Line {line_num}: {line.strip()}")

    assert len(violations) == 0, (
        f"\n{'=' * 70}\n"
        f"REGRESSION DETECTED: vibe-cli imports anthropic SDK\n"
        f"{'=' * 70}\n\n"
        f"VIOLATIONS:\n" + "\n".join(f"  {v}" for v in violations) + "\n\n"
        f"WHY THIS IS FORBIDDEN:\n"
        f"  - MVP = DELEGATION ONLY (no API calls)\n"
        f"  - Claude Code is the operator (intelligence layer)\n"
        f"  - vibe-cli is a BRIDGE (STDOUT/STDIN only)\n"
        f"  - Anthropic SDK = nested API calls = violation\n\n"
        f"FIX:\n"
        f"  1. Remove 'import anthropic' from vibe-cli\n"
        f"  2. Remove Anthropic API client initialization\n"
        f"  3. Replace with delegation to Claude Code operator\n\n"
        f"See: docs/architecture/EXECUTION_MODE_STRATEGY.md\n"
        f"{'=' * 70}\n"
    )


def test_vibe_cli_no_anthropic_client():
    """
    ANTI-REGRESSION: vibe-cli MUST NOT use Anthropic API client

    Prevents:
        self.client = anthropic.Anthropic(api_key=...)
        response = self.client.messages.create(...)
    """
    vibe_cli_path = REPO_ROOT / "vibe-cli"

    with open(vibe_cli_path) as f:
        content = f.read()

    # Check for Anthropic client usage
    forbidden_patterns = [
        "anthropic.Anthropic(",
        "Anthropic(",
        ".messages.create(",
        "client.messages",
    ]

    violations = []
    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern in forbidden_patterns:
            if pattern in line:
                violations.append(f"Line {line_num}: {line.strip()}")

    assert len(violations) == 0, (
        f"\n{'=' * 70}\n"
        f"REGRESSION DETECTED: vibe-cli uses Anthropic API client\n"
        f"{'=' * 70}\n\n"
        f"VIOLATIONS:\n" + "\n".join(f"  {v}" for v in violations) + "\n\n"
        f"WHY THIS IS FORBIDDEN:\n"
        f"  - vibe-cli should NOT make API calls in MVP\n"
        f"  - Intelligence requests should be delegated to Claude Code\n"
        f"  - API calls = nested execution = architecture violation\n\n"
        f"CORRECT ARCHITECTURE:\n"
        f"  Claude Code → vibe-cli (bridge) → Orchestrator\n"
        f"  Orchestrator prints prompt → vibe-cli → Claude Code responds\n\n"
        f"See: docs/architecture/EXECUTION_MODE_STRATEGY.md\n"
        f"{'=' * 70}\n"
    )


def test_vibe_cli_no_api_key_usage():
    """
    ANTI-REGRESSION: vibe-cli MUST NOT use ANTHROPIC_API_KEY in MVP

    Prevents:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.anthropic_api_key = ...
    """
    vibe_cli_path = REPO_ROOT / "vibe-cli"

    with open(vibe_cli_path) as f:
        content = f.read()

    # Check for API key usage
    forbidden_patterns = [
        "ANTHROPIC_API_KEY",
        "anthropic_api_key",
    ]

    violations = []
    for line_num, line in enumerate(content.split("\n"), 1):
        # Skip comments
        if line.strip().startswith("#"):
            continue

        for pattern in forbidden_patterns:
            if pattern in line:
                violations.append(f"Line {line_num}: {line.strip()}")

    assert len(violations) == 0, (
        f"\n{'=' * 70}\n"
        f"REGRESSION DETECTED: vibe-cli references ANTHROPIC_API_KEY\n"
        f"{'=' * 70}\n\n"
        f"VIOLATIONS:\n" + "\n".join(f"  {v}" for v in violations) + "\n\n"
        f"WHY THIS IS FORBIDDEN:\n"
        f"  - vibe-cli doesn't need API keys in delegation mode\n"
        f"  - Claude Code operator provides intelligence\n"
        f"  - API keys would enable nested API calls\n\n"
        f"MVP RULE:\n"
        f"  No ANTHROPIC_API_KEY in vibe-cli\n"
        f"  (Standalone mode deferred to v1.1)\n\n"
        f"See: docs/architecture/EXECUTION_MODE_STRATEGY.md\n"
        f"{'=' * 70}\n"
    )


def test_execution_mode_strategy_exists():
    """
    Verify EXECUTION_MODE_STRATEGY.md exists

    This document defines the rules these tests enforce.
    """
    strategy_doc = REPO_ROOT / "docs" / "architecture" / "EXECUTION_MODE_STRATEGY.md"

    assert strategy_doc.exists(), (
        f"Missing: {strategy_doc}\n"
        f"This document defines execution mode rules.\n"
        f"Create it with clear MVP guidelines."
    )

    # Verify it contains key terms
    with open(strategy_doc) as f:
        content = f.read()

    required_terms = [
        "DELEGATION ONLY",
        "MVP",
        "FORBIDDEN",
        "Claude Code",
    ]

    for term in required_terms:
        assert term in content, (
            f"EXECUTION_MODE_STRATEGY.md missing key term: '{term}'\n"
            f"Document should clearly define MVP execution rules."
        )


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
