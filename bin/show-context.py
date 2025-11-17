#!/usr/bin/env python3
"""
show-context.py - Display session context in one command

BURN THE GHEE Phase 3: Enhanced with full system visibility
- Session handoff (Layer 0-2)
- System status (git, linting, tests)
- Test results (quick smoke check)
- TODO summary (code + docs)
- Architecture completion (GAD/VAD/LAD status)
- Recent activity (last 3 commits)

Usage: ./bin/show-context.py
"""

import json
import subprocess
from pathlib import Path


def get_test_status():
    """Run quick smoke test and return status."""
    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "tests/test_layer0_integrity.py", "-v", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout + result.stderr

        # Parse pytest output
        if "passed" in output:
            # Extract counts (e.g., "14 passed in 0.5s")
            for line in output.split("\n"):
                if "passed" in line and ("failed" in line or "error" in line or "in" in line):
                    return "✅", line.strip()
            return "✅", "Tests passing"
        elif "FAILED" in output or "failed" in output:
            return "❌", "Tests failing"
        elif "ERROR" in output or "error" in output:
            return "⚠️", "Test errors"
        else:
            return "⚠️", "Unknown status"
    except Exception as e:
        return "⚠️", f"Could not run tests: {str(e)[:50]}"


def get_todo_summary():
    """Scan for TODOs in code and docs."""
    try:
        # Search in code
        code_result = subprocess.run(
            ["grep", "-r", "-i", "TODO\\|FIXME\\|XXX\\|HACK", "agency_os/", "--include=*.py"],
            capture_output=True,
            text=True,
        )
        code_count = (
            len(code_result.stdout.strip().split("\n")) if code_result.stdout.strip() else 0
        )

        # Search in docs
        docs_result = subprocess.run(
            ["grep", "-r", "-i", "TODO\\|FIXME", "docs/", "--include=*.md"],
            capture_output=True,
            text=True,
        )
        docs_count = (
            len(docs_result.stdout.strip().split("\n")) if docs_result.stdout.strip() else 0
        )

        return code_count, docs_count
    except Exception:
        return 0, 0


def get_architecture_status():
    """Check GAD/VAD/LAD completion status."""
    gad_status = {}

    # Check GAD pillars
    pillars = {
        "GAD-1XX": "docs/architecture/GAD-1XX/GAD-100.md",
        "GAD-2XX": "docs/architecture/GAD-2XX/GAD-200.md",
        "GAD-3XX": "docs/architecture/GAD-3XX/GAD-300.md",
        "GAD-4XX": "docs/architecture/GAD-4XX/GAD-400.md",
        "GAD-5XX": "docs/architecture/GAD-5XX/GAD-500.md",
        "GAD-6XX": "docs/architecture/GAD-6XX/GAD-600.md",
        "GAD-7XX": "docs/architecture/GAD-7XX/GAD-700.md",
        "GAD-8XX": "docs/architecture/GAD-8XX/GAD-800.md",
    }

    for pillar, path in pillars.items():
        gad_status[pillar] = "✅" if Path(path).exists() else "❌"

    # Check LAD
    lad_complete = all(Path(f"docs/architecture/LAD/LAD-{i}.md").exists() for i in [1, 2, 3])

    # Check VAD
    vad_files = list(Path("docs/architecture/VAD").glob("VAD-00*.md"))
    vad_complete = len(vad_files) >= 3

    return gad_status, lad_complete, vad_complete


def get_recent_commits():
    """Get last 3 commits."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        return []


def main():
    """Display session context from .session_handoff.json and .system_status.json"""

    # Load data
    handoff_file = Path(".session_handoff.json")
    status_file = Path(".system_status.json")

    handoff = json.load(open(handoff_file)) if handoff_file.exists() else None
    status = json.load(open(status_file)) if status_file.exists() else {}

    print("=" * 70)
    print("📋 SESSION CONTEXT")
    print("=" * 70)
    print()

    # Session handoff (Layer 0 + Layer 1 + Layer 2)
    if handoff:
        print("━━━ SESSION HANDOFF ━━━")
        print()

        # Layer 0: Bedrock (always show)
        layer0 = handoff.get("layer0_bedrock", {})
        if layer0:
            print(f"From: {layer0.get('from', 'Unknown')}")
            print(f"Date: {layer0.get('date', 'Unknown')}")
            print(f"State: {layer0.get('state', 'Unknown')}")

            if layer0.get("blocker"):
                print(f"⚠️  Blocker: {layer0['blocker']}")
            print()

        # Layer 1: Runtime (session start)
        layer1 = handoff.get("layer1_runtime", {})
        if layer1:
            summary = layer1.get("completed_summary", "")
            if summary:
                print(f"Summary: {summary}")
                print()

            todos = layer1.get("todos", [])
            if todos:
                print("Your TODOs:")
                for todo in todos[:5]:
                    print(f"  → {todo}")
                if len(todos) > 5:
                    print(f"  ... and {len(todos) - 5} more")
                print()

            files = layer1.get("critical_files", [])
            if files:
                print("Critical files:")
                for file in files[:5]:
                    print(f"  📄 {file}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")
                print()

        # Layer 2: Detail (show available, prompt to read file)
        layer2 = handoff.get("layer2_detail", {})
        if layer2:
            print("💡 More detail available:")
            print("   cat .session_handoff.json | jq .layer2_detail")
            print()
    else:
        print("⚠️  No session handoff found (.session_handoff.json)")
        print()

    # System status
    if status:
        print("━━━ SYSTEM STATUS (auto-updated) ━━━")
        print()

        git = status.get("git", {})
        linting = status.get("linting", {})
        tests = status.get("tests", {})

        print(f"Branch: {git.get('branch', 'Unknown')}")

        clean = "✅ Clean" if git.get("working_directory_clean") else "⚠️  Modified"
        print(f"Working directory: {clean}")

        linting_status = linting.get("status", "unknown")
        linting_icon = "✅" if linting_status == "passing" else "❌"
        linting_errors = linting.get("errors_count", 0)
        print(f"Linting: {linting_icon} {linting_status.title()} ({linting_errors} errors)")

        test_status = tests.get("planning_workflow", "unknown")
        test_icon = "✅" if test_status == "passing" else "❌"
        print(f"Tests (planning): {test_icon} {test_status.title()}")

        timestamp = status.get("timestamp", "Unknown")
        print(f"\nLast updated: {timestamp}")
        print()
    else:
        print("⚠️  No system status found (.system_status.json)")
        print("   Run: ./bin/update-system-status.sh")
        print()

    # Test status (quick smoke check)
    print("━━━ TEST STATUS (live check) ━━━")
    print()
    test_icon, test_msg = get_test_status()
    print(f"{test_icon} {test_msg}")
    print()

    # TODO summary
    print("━━━ TODO SUMMARY ━━━")
    print()
    code_todos, docs_todos = get_todo_summary()
    total_todos = code_todos + docs_todos
    if total_todos > 0:
        print(f"⚠️  {total_todos} TODOs found ({code_todos} in code, {docs_todos} in docs)")
    else:
        print("✅ No TODOs found")
    print()

    # Architecture status
    print("━━━ ARCHITECTURE STATUS ━━━")
    print()
    gad_status, lad_complete, vad_complete = get_architecture_status()

    print("GAD Pillars:")
    for pillar, status_icon in gad_status.items():
        print(f"  {status_icon} {pillar}")

    lad_icon = "✅" if lad_complete else "❌"
    vad_icon = "✅" if vad_complete else "❌"
    print(f"\n{lad_icon} LAD (Layers): {'Complete' if lad_complete else 'Incomplete'}")
    print(f"{vad_icon} VAD (Verification): {'Complete' if vad_complete else 'Incomplete'}")
    print()

    # Recent activity
    print("━━━ RECENT ACTIVITY ━━━")
    print()
    commits = get_recent_commits()
    if commits:
        for commit in commits:
            print(f"  {commit}")
    else:
        print("  (No commits found)")
    print()

    print("=" * 70)
    print()
    print("💡 Quick commands:")
    print("   Update system status:       ./bin/update-system-status.sh")
    print("   Pre-push checks:            ./bin/pre-push-check.sh")
    print("   Full verification suite:    ./bin/verify-all.sh")
    print("   Verify CLAUDE.md claims:    grep 'Verify Command' CLAUDE.md")
    print()


if __name__ == "__main__":
    main()
