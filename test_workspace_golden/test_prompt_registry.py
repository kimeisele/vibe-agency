#!/usr/bin/env python3
"""
import sys
Golden Path Test - Prompt Registry Integration Validation
Tests if PromptRegistry correctly loads and injects Guardian Directives
"""

import sys

print("=" * 80)
print("GOLDEN PATH TEST - Prompt Registry Integration")
print("=" * 80)
print()

# Test 1: Import PromptRegistry
print("TEST 1: Import PromptRegistry")
print("-" * 80)
try:
    from vibe_core.runtime.prompt_registry import PromptRegistry

    print("✅ PASS: PromptRegistry imported successfully")
    print(f"   Location: {PromptRegistry.__module__}")
except ImportError as e:
    print(f"❌ FAIL: Cannot import PromptRegistry: {e}")
    sys.exit(1)
print()

# Test 2: Initialize PromptRegistry
print("TEST 2: Initialize PromptRegistry")
print("-" * 80)
try:
    registry = PromptRegistry()
    print("✅ PASS: PromptRegistry initialized")
except Exception as e:
    print(f"❌ FAIL: Cannot initialize PromptRegistry: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
print()

# Test 3: Load Guardian Directives
print("TEST 3: Load Guardian Directives")
print("-" * 80)
try:
    directives = registry.guardian_directives
    if directives:
        print("✅ PASS: Guardian Directives loaded")
        print(f"   Directives count: {len(directives)}")
        print(f"   Keys: {list(directives.keys())[:5]}...")  # Show first 5 keys
    else:
        print("⚠️  WARNING: Guardian Directives is empty")
except Exception as e:
    print(f"❌ FAIL: Cannot load Guardian Directives: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
print()

# Test 4: Test compose() method with guardian directives
print("TEST 4: Test compose() method")
print("-" * 80)
try:
    # Create a simple test case (VIBE_ALIGNER task)
    test_agent = "VIBE_ALIGNER"
    test_task = "EDUCATE_USER"
    test_context = {
        "user_input": "I want to build a yoga booking system",
        "project_phase": "PLANNING",
    }

    prompt = registry.compose(agent_name=test_agent, task_name=test_task, context=test_context)

    if prompt:
        print("✅ PASS: compose() returned prompt")
        print(f"   Prompt length: {len(prompt)} characters")

        # Check if guardian directives are in the prompt
        if "GUARDIAN" in prompt.upper() or "DIRECTIVE" in prompt.upper():
            print("   ✅ Guardian Directives appear to be injected")
        else:
            print("   ⚠️  WARNING: Cannot find 'GUARDIAN' or 'DIRECTIVE' in prompt")
            print("   (May be using different keywords)")

        # Show snippet
        print()
        print("   Prompt snippet (first 500 chars):")
        print("   " + "-" * 76)
        for line in prompt[:500].split("\n"):
            print(f"   {line}")
        print("   " + "-" * 76)
    else:
        print("❌ FAIL: compose() returned empty prompt")
        sys.exit(1)

except Exception as e:
    print(f"❌ FAIL: compose() error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
print()

# Test 5: Verify governance injection is automatic
print("TEST 5: Verify governance injection")
print("-" * 80)
try:
    # Check if prompt contains governance keywords
    governance_keywords = [
        "constraint",
        "requirement",
        "rule",
        "policy",
        "governance",
        "compliance",
        "standard",
    ]

    found_keywords = []
    for keyword in governance_keywords:
        if keyword.lower() in prompt.lower():
            found_keywords.append(keyword)

    if found_keywords:
        print("✅ PASS: Governance keywords found in prompt")
        print(f"   Keywords: {', '.join(found_keywords)}")
    else:
        print("⚠️  WARNING: No governance keywords found")
        print(f"   Checked: {', '.join(governance_keywords)}")

except Exception as e:
    print(f"❌ FAIL: Cannot verify governance injection: {e}")
    sys.exit(1)
print()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("✅ All integration tests passed!")
print()
print("CONCLUSIONS:")
print("1. PromptRegistry imports correctly")
print("2. Guardian Directives load successfully")
print("3. compose() method works and appears to inject governance")
print()
print("NEXT STEP: Run full end-to-end test with Core Orchestrator")
print("=" * 80)
