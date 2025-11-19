#!/usr/bin/env python3
"""
Quick test: Can we compose VIBE_ALIGNER prompt?
"""

import os
import sys
from pathlib import Path

# Add current dir to path

# Debug: Print working directory
print(f"Working directory: {os.getcwd()}")

# Check if prompt_runtime file exists
runtime_path = Path("agency_os/00_system/runtime/prompt_runtime.py")
if not runtime_path.exists():
    print(f"❌ ERROR: prompt_runtime.py not found at {runtime_path.absolute()}")
    print(f"   Current dir contents: {list(Path('.').iterdir())[:10]}")
    sys.exit(1)

print(f"✓ Found prompt_runtime at {runtime_path.absolute()}")

# Import prompt runtime (can't use normal import due to 00_ directory name)
import importlib.util

try:
    spec = importlib.util.spec_from_file_location("prompt_runtime", str(runtime_path))
    prompt_runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prompt_runtime)
    PromptRuntime = prompt_runtime.PromptRuntime
    print("✓ Successfully loaded PromptRuntime")
except Exception as e:
    print(f"❌ ERROR loading prompt_runtime: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


def test_vibe_aligner():
    print("=" * 60)
    print("Testing VIBE_ALIGNER prompt composition")
    print("=" * 60)

    runtime = PromptRuntime()

    try:
        prompt = runtime.execute_task(
            agent_id="VIBE_ALIGNER",
            task_id="02_feature_extraction",
            context={
                "project_id": "test_project_001",
                "workspace": "test",
                "user_requirements": "I want a booking system for my yoga studio",
            },
        )

        print("\n✅ SUCCESS!")
        print(f"   Prompt length: {len(prompt)} chars")
        print(f"   Preview: {prompt[:200]}...")

        # Save to file
        output_file = Path("VIBE_ALIGNER_TEST.md")
        with open(output_file, "w") as f:
            f.write(prompt)
        print(f"\n   Saved to: {output_file}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_vibe_aligner()
    sys.exit(0 if success else 1)
