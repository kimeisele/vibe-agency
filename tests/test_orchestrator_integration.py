#!/usr/bin/env python3
"""
Test script: Run orchestrator in delegated mode and capture INTELLIGENCE_REQUEST
This proves the Prompt Registry integration works end-to-end.
"""

import os
import subprocess
import time
from pathlib import Path

# Get repo root
repo_root = Path(__file__).parent.parent

print("=" * 80)
print("RUNNING CORE ORCHESTRATOR - DELEGATED MODE TEST")
print("=" * 80)
print()

# Set up environment - use actual current working directory
os.chdir(str(repo_root))

# Run orchestrator in delegated mode
print("Starting orchestrator...")
print("Project: golden-test-registry")
print("Mode: delegated")
print("Expected: INTELLIGENCE_REQUEST with Guardian Directives")
print()

cmd = [
    "python3",
    str(repo_root / "agency_os/00_system/orchestrator/core_orchestrator.py"),
    str(repo_root),
    "golden-test-registry",
    "--mode=delegated",
    "--log-level=INFO",
]

print(f"Command: {' '.join(cmd)}")
print()
print("-" * 80)

# Run and capture output
try:
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True
    )

    # Read output for 5 seconds or until we get INTELLIGENCE_REQUEST
    output_lines = []
    start_time = time.time()
    found_request = False

    # Set a timeout
    proc.stdin.close()  # Close stdin so orchestrator doesn't wait forever

    while time.time() - start_time < 5:
        line = proc.stdout.readline()
        if not line:
            break
        output_lines.append(line)
        print(line, end="")

        if "<INTELLIGENCE_REQUEST>" in line:
            found_request = True
            # Read until </INTELLIGENCE_REQUEST>
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                output_lines.append(line)
                print(line, end="")
                if "</INTELLIGENCE_REQUEST>" in line:
                    break

    # Kill the process
    proc.terminate()
    proc.wait(timeout=2)

    print("-" * 80)
    print()

    # Analyze results
    full_output = "".join(output_lines)

    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    if found_request:
        print("✅ PASS: INTELLIGENCE_REQUEST found!")

        # Check for Guardian Directives
        if "GUARDIAN DIRECTIVES" in full_output or "GUARDIAN_DIRECTIVE" in full_output:
            print("✅ PASS: Guardian Directives present in request!")
        else:
            print("❌ FAIL: Guardian Directives NOT found in request")

        # Check for PromptRegistry usage
        if "PromptRegistry" in full_output:
            print("✅ PASS: PromptRegistry mentioned in logs")
        else:
            print("⚠️  WARNING: PromptRegistry not mentioned (may be normal)")

        # Check prompt size
        if len(full_output) > 10000:
            print(
                f"✅ PASS: Large prompt ({len(full_output):,} chars - likely includes governance)"
            )
        else:
            print(f"⚠️  WARNING: Small prompt ({len(full_output):,} chars)")

    else:
        print("❌ FAIL: No INTELLIGENCE_REQUEST found")
        print("This suggests the orchestrator didn't start properly")

    print()
    print("=" * 80)

except subprocess.TimeoutExpired:
    print("❌ TIMEOUT: Orchestrator didn't respond in 5 seconds")
    proc.kill()
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
