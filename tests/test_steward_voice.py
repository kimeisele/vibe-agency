"""
Test: Steward Voice & Identity Injection (ARCH-051.5)

Verifies that the Steward's identity is properly injected into the system prompt
and that the Steward understands its core directives.
"""

import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_steward_identity_in_system_prompt():
    """
    ARCH-051.5: Verify that the system prompt contains Steward identity directives.

    The system prompt should:
    1. Identify the Steward by name and ID
    2. State the three CORE DIRECTIVES
    3. Reference steward_cartridge tools
    4. Emphasize system integrity
    """
    import logging

    from apps.agency.cli import boot_kernel

    # Suppress logging for test
    logging.getLogger().setLevel(logging.CRITICAL)

    # Boot the kernel (which initializes the operator agent with the system prompt)
    kernel = boot_kernel()

    # Get the operator agent
    operator = kernel.agent_registry.get("vibe-operator")
    assert operator is not None, "Operator agent not found in registry"

    # Get the system prompt
    system_prompt = operator._system_prompt

    # Assertions: Check for Steward identity
    assert "STEWARD" in system_prompt, "System prompt should identify as STEWARD"
    assert "vibe-agency-orchestrator" in system_prompt, "System prompt should reference agent ID"

    # Check for CORE DIRECTIVES
    assert "CORE DIRECTIVES (MANDATORY)" in system_prompt, (
        "System prompt should list core directives"
    )
    assert "YOU ARE THE STEWARD" in system_prompt, "System prompt should emphasize Steward role"
    assert "KNOW YOUR USER" in system_prompt, "System prompt should mention user personalization"
    assert "CONFIGURATION IS SACRED" in system_prompt, (
        "System prompt should emphasize config safety"
    )

    # Check for steward_cartridge references
    assert "steward_cartridge" in system_prompt, (
        "System prompt should reference steward_cartridge tools"
    )
    assert "manage_api_keys()" in system_prompt, "System prompt should mention manage_api_keys tool"
    assert "update_user_preferences()" in system_prompt, (
        "System prompt should mention update_user_preferences tool"
    )
    assert "change_persona()" in system_prompt, "System prompt should mention change_persona tool"

    # Check for safety enforcement
    assert "NEVER edit .env or STEWARD.md by hand" in system_prompt, (
        "System prompt should forbid manual edits"
    )
    assert "Use the tools. They have safety guards. You don't." in system_prompt, (
        "System prompt should explain why to use tools"
    )

    print("✅ ARCH-051.5 VERIFIED: Steward Voice & Identity properly injected")
    print("   - Steward Identity: CONFIRMED")
    print("   - Core Directives: CONFIRMED")
    print("   - Tool References: CONFIRMED")
    print("   - Safety Enforcement: CONFIRMED")

    return True


def test_steward_config_available():
    """
    Verify that steward.json exists and contains the required agent identity.
    """
    import json

    steward_json_path = PROJECT_ROOT / "steward.json"
    assert steward_json_path.exists(), f"steward.json not found at {steward_json_path}"

    with open(steward_json_path) as f:
        config = json.load(f)

    # Check for agent identity
    assert "agent" in config, "steward.json should have 'agent' section"
    agent = config["agent"]

    assert agent["id"] == "vibe-agency-orchestrator", "Agent ID should match"
    assert agent["name"] == "STEWARD", "Agent name should be STEWARD"
    assert agent["status"] == "active", "Agent status should be active"

    print("✅ STEWARD CONFIGURATION VERIFIED")
    print(f"   - Agent ID: {agent['id']}")
    print(f"   - Agent Name: {agent['name']}")
    print(f"   - Status: {agent['status']}")

    return True


if __name__ == "__main__":
    try:
        test_steward_config_available()
        test_steward_identity_in_system_prompt()
        print("\n✅ ALL TESTS PASSED - ARCH-051.5 IMPLEMENTATION VERIFIED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
