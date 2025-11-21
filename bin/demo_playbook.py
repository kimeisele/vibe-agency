#!/usr/bin/env python3
"""
ARCH-013: Playbook Demo
=======================

This script demonstrates the "Cartridge Slot" functionality:
1. Loads a playbook YAML
2. Validates it
3. Executes it using the PlaybookRunner
4. Outputs results to a file

Proof of concept: Shows that the system can load dynamic workflow presets
and execute them without hardcoded phases.

Usage:
    python bin/demo_playbook.py [playbook_id_or_path]

Examples:
    python bin/demo_playbook.py hello-world
    python bin/demo_playbook.py feature-implement
    python bin/demo_playbook.py playbooks/presets/custom.yaml
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path for imports BEFORE importing vibe_core modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.playbook.runner import (  # noqa: E402
    PlaybookError,
    PlaybookRunner,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Main demo function"""

    # Parse arguments
    if len(sys.argv) < 2:
        playbook_id = "hello-world"  # Default demo playbook
        logger.info(f"No playbook specified, using default: {playbook_id}")
    else:
        playbook_id = sys.argv[1]

    # Create output directory
    output_dir = project_root / ".demo_output"
    output_dir.mkdir(exist_ok=True)

    logger.info("=" * 80)
    logger.info("ARCH-013: Playbook Demo (Cartridge Slot)")
    logger.info("=" * 80)
    logger.info(f"Playbook: {playbook_id}")
    logger.info(f"Output directory: {output_dir}")
    logger.info("=" * 80)

    try:
        # Initialize PlaybookRunner
        logger.info("\n📦 Initializing PlaybookRunner...")
        runner = PlaybookRunner()

        # Load the registry
        logger.info("\n📚 Loading playbook registry...")
        runner.load_registry()

        # Check what playbooks are available
        available = runner.registry.list()
        logger.info(f"Found {len(available)} playbooks in registry:")
        for pb in available:
            logger.info(f"  - {pb.id}: {pb.name}")

        # Try to run the playbook
        logger.info(f"\n🚀 Running playbook: {playbook_id}")

        # Check if it's a registry ID or file path
        playbook_path = Path(playbook_id)
        if playbook_path.exists() and playbook_path.is_file():
            # Load from file
            logger.info(f"Loading from file: {playbook_path}")
            result = runner.run_playbook_file(playbook_path)
        else:
            # Try registry
            result = runner.run_playbook(playbook_id)

        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("EXECUTION RESULTS")
        logger.info("=" * 80)

        print(f"\n✅ Playbook Status: {result['status'].upper()}")
        print(f"   Playbook: {result['playbook_name']}")
        print(f"   Phases executed: {len(result['phases_executed'])}")

        if result.get("phases_executed"):
            print("\n📋 Phase Execution Details:")
            for i, phase in enumerate(result["phases_executed"], 1):
                print(f"  {i}. {phase['phase_name']}")
                print(f"     Status: {phase['status']}")
                print(f"     Agents: {', '.join(phase['agents_activated'])}")
                if phase.get("tools_activated"):
                    print(f"     Tools: {', '.join(phase['tools_activated'])}")

        if result.get("errors"):
            print("\n❌ Errors:")
            for error in result["errors"]:
                print(f"  - {error}")

        # Save results to file
        results_file = output_dir / f"{playbook_id}_results.json"
        with open(results_file, "w") as f:
            json.dump(result, f, indent=2)
        logger.info(f"\n💾 Results saved to: {results_file}")

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Playbook execution: {result['status'].upper()}")
        logger.info(f"📦 Playbook ID: {result['playbook_id']}")
        logger.info(f"📊 Phases: {len(result['phases_executed'])}")
        logger.info(f"💾 Results saved to: {results_file}")

        # Show execution history
        history = runner.get_execution_history()
        logger.info(f"🔄 Total executions in session: {len(history)}")

        logger.info("\n" + "=" * 80)
        logger.info("✨ Demo complete! The Cartridge Slot mechanism works!")
        logger.info("=" * 80)

        return 0 if result["status"] == "success" else 1

    except PlaybookError as e:
        logger.error(f"\n❌ Playbook Error: {e}")
        logger.info("\n" + "=" * 80)
        logger.info("Available playbooks:")
        runner = PlaybookRunner()
        runner.load_registry()
        for pb in runner.registry.list():
            logger.info(f"  - {pb.id}: {pb.name}")
        logger.info("=" * 80)
        return 1

    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
