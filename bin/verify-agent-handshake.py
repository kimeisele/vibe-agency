#!/usr/bin/env python3
"""
verify-agent-handshake.py - Verify Agent Can Use GAD-000 JSON Interface

ARCH-018: The Semantic Handshake
Purpose: Verify that agents can successfully use the --json flag with vibe CLI
         and parse the structured output.

This script simulates an agent's thought process:
1. Agent decides to check system status
2. Agent executes: ./bin/vibe status --json
3. Agent parses JSON output
4. Agent uses the parsed data

Success: Agent successfully parses and uses JSON output
Failure: Agent crashes on JSON parsing or receives unparseable output
"""

import json
import subprocess
import sys
from pathlib import Path


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def simulate_agent_decision():
    """Simulate an agent deciding to check system status"""
    print_section("STEP 1: Agent Decision")
    print("🤖 AGENT THOUGHT PROCESS:")
    print("   → User asked: 'What is the system status?'")
    print("   → I need to check the vibe system status")
    print("   → According to GAD-000, I must use --json flag")
    print("   → Decision: Execute './bin/vibe status --json'")
    return True


def execute_vibe_command():
    """Execute vibe status --json command"""
    print_section("STEP 2: Execute Command")

    # Get the project root (assuming script is in bin/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    vibe_path = project_root / "bin" / "vibe"

    print(f"📍 Working directory: {project_root}")
    print(f"🔧 Command: {vibe_path} status --json")

    try:
        result = subprocess.run(
            [str(vibe_path), "status", "--json"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=10,
        )

        print(f"✅ Exit code: {result.returncode}")

        if result.returncode != 0:
            print(f"⚠️  stderr: {result.stderr}")
            return None, result.stderr

        return result.stdout, None

    except subprocess.TimeoutExpired:
        error = "Command timed out after 10 seconds"
        print(f"❌ {error}")
        return None, error
    except FileNotFoundError:
        error = f"Command not found: {vibe_path}"
        print(f"❌ {error}")
        return None, error
    except Exception as e:
        error = f"Unexpected error: {e}"
        print(f"❌ {error}")
        return None, error


def parse_json_output(output: str):
    """Parse JSON output from vibe command"""
    print_section("STEP 3: Parse JSON Output")

    print("🔍 Raw output (first 500 chars):")
    print("-" * 70)
    print(output[:500])
    if len(output) > 500:
        print(f"... (truncated, total length: {len(output)} chars)")
    print("-" * 70)

    try:
        data = json.loads(output)
        print("\n✅ JSON parsing: SUCCESS")
        return data, None
    except json.JSONDecodeError as e:
        error = f"JSON parsing failed: {e}"
        print(f"\n❌ {error}")
        print(f"   → Error at line {e.lineno}, column {e.colno}")
        print(f"   → Message: {e.msg}")
        return None, error


def use_parsed_data(data: dict):
    """Simulate agent using the parsed data"""
    print_section("STEP 4: Agent Uses Data")

    print("🤖 AGENT PROCESSING:")

    # Extract key information
    health = data.get("health", "unknown")
    version = data.get("version", "unknown")
    timestamp = data.get("timestamp", "unknown")

    print(f"   → Parsed health status: {health}")
    print(f"   → System version: {version}")
    print(f"   → Timestamp: {timestamp}")

    # Check if we got meaningful data
    if health == "unknown" and version == "unknown":
        print("\n⚠️  WARNING: Could not extract meaningful data from JSON")
        return False

    # Simulate agent formulating response
    print("\n🤖 AGENT RESPONSE TO USER:")
    print(f"   'The system health is: {health}'")
    print(f"   'Running version: {version}'")

    return True


def verify_handshake():
    """Main verification flow"""
    print_section("ARCH-018: Agent Handshake Verification")
    print("Testing GAD-000 compliance: Can agents use --json interface?")

    # Step 1: Simulate agent decision
    if not simulate_agent_decision():
        print("❌ Agent decision simulation failed")
        return False

    # Step 2: Execute command
    output, error = execute_vibe_command()
    if error:
        print("\n❌ FAILURE: Command execution failed")
        print(f"   Error: {error}")
        return False

    # Step 3: Parse JSON
    data, error = parse_json_output(output)
    if error:
        print("\n❌ FAILURE: JSON parsing failed")
        print(f"   Error: {error}")
        print("\n🔍 DIAGNOSIS:")
        print("   → The command did not return valid JSON")
        print("   → This violates GAD-000 (Operator Inversion Principle)")
        print("   → Agents cannot reliably parse this output")
        return False

    # Step 4: Use data
    if not use_parsed_data(data):
        print("\n⚠️  WARNING: JSON parsed but contains no useful data")
        return False

    # Success!
    print_section("VERIFICATION RESULT")
    print("✅ SUCCESS: Agent successfully completed the handshake!")
    print("\n📊 Summary:")
    print("   ✅ Agent executed command with --json flag")
    print("   ✅ Command returned valid JSON")
    print("   ✅ Agent parsed JSON successfully")
    print("   ✅ Agent extracted and used data")
    print("\n🎯 CONCLUSION: Zero Semantic Debt")
    print("   The code (tool) and mind (agent) are synchronized.")
    return True


def main():
    """Entry point"""
    try:
        success = verify_handshake()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
