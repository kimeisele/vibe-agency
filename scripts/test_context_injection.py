#!/usr/bin/env python3
"""Verification script for GAD-502: Context Projection

This script proves that context injection works by:
1. Loading a real task file (task_02_handle_coding.md)
2. Injecting live context
3. Printing the result
"""

from pathlib import Path

from agency_os.core_system.runtime.context_loader import ContextLoader


def main():
    print("=" * 60)
    print("GAD-502 CONTEXT INJECTION VERIFICATION")
    print("=" * 60)
    print()

    # Load task file
    task_file = Path(
        "agency_os/core_system/agents/AGENCY_OS_ORCHESTRATOR/tasks/task_02_handle_coding.md"
    )

    if not task_file.exists():
        print(f"❌ Task file not found: {task_file}")
        return 1

    print(f"📄 Reading task file: {task_file.name}")
    template = task_file.read_text()
    print()

    # Initialize context loader
    print("🔄 Loading system context...")
    loader = ContextLoader()

    # Show what context was loaded
    context = loader.load()
    print("\n📊 Loaded Context:")
    print(f"  Session Phase: {context['session']['phase']}")
    print(f"  Git Branch: {context['git']['branch']}")
    uncommitted_count = context["git"]["uncommitted"]
    git_status = "Clean" if uncommitted_count == 0 else f"{uncommitted_count} uncommitted"
    print(f"  Git Status: {git_status}")
    print(f"  Test Status: {context['tests']['status']}")
    print(f"  Failing Tests: {context['tests']['failing_count']}")
    print(f"  Last Task: {context['session']['last_task']}")
    print()

    # Inject context
    print("💉 Injecting context into template...")
    injected = loader.inject_context(template)

    # Display result
    print("\n" + "=" * 60)
    print("INJECTED TEMPLATE (First 50 lines)")
    print("=" * 60)
    lines = injected.split("\n")
    for i, line in enumerate(lines[:50], 1):
        print(f"{i:3d} | {line}")

    if len(lines) > 50:
        print(f"... ({len(lines) - 50} more lines)")

    # Verify injection worked
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    # Check that placeholders were replaced
    remaining_placeholders = [
        line for line in lines if "{{" in line and "}}" in line and "GAD-502" not in line
    ]

    if remaining_placeholders:
        print(f"\n⚠️  Warning: {len(remaining_placeholders)} placeholders still present:")
        for placeholder_line in remaining_placeholders[:5]:
            print(f"  - {placeholder_line.strip()}")
    else:
        print("\n✅ All placeholders successfully replaced!")

    # Check specific injections
    checks = [
        ("session.phase", context["session"]["phase"]),
        ("git.branch", context["git"]["branch"]),
        ("tests.status", context["tests"]["status"]),
    ]

    print("\n🔍 Spot Checks:")
    for placeholder, expected in checks:
        if str(expected) in injected:
            print(f"  ✅ {{ {placeholder} }} → {expected}")
        else:
            print(f"  ❌ {{ {placeholder} }} not found (expected: {expected})")

    print()
    print("=" * 60)
    print("✅ CONTEXT INJECTION VERIFICATION COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
