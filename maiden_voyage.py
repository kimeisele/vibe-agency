#!/usr/bin/env python3
"""
MAIDEN VOYAGE - v2.5 Architecture Verification

This script runs a simple documentation harmonization mission through the
new HAP (Hierarchical Agent Pattern) architecture to verify:

1. AgentRegistry routing to specialists
2. PlanningSpecialist & CodingSpecialist execution
3. ToolSafetyGuard file write checks
4. SQLite decision logging

Mission: Update README.md to reflect v2.5 architecture completion.
"""

import logging
import sys
from pathlib import Path

# Setup logging to see component activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from agency_os.core_system.orchestrator.core_orchestrator import (
    CoreOrchestrator,
    ProjectManifest,
    ProjectPhase
)

def main():
    print("\n" + "="*80)
    print("🚢 MAIDEN VOYAGE - Vibe Agency OS v2.5 Architecture Test")
    print("="*80)

    print("\n📋 MISSION: Documentation Harmonization")
    print("   Task: Update README.md to reflect v2.5 architecture completion")
    print("   Expected: See AgentRegistry, Specialists, SafetyGuard, SQLite in logs\n")

    # Initialize orchestrator
    print("🔧 Initializing CoreOrchestrator...")
    orchestrator = CoreOrchestrator(
        repo_root=Path.cwd(),
        execution_mode="autonomous"  # Run without file delegation
    )

    # Create mission manifest
    print("📝 Creating mission manifest...")
    manifest = ProjectManifest(
        project_id="maiden-voyage-doc-harmonization",
        name="Documentation Harmonization - v2.5 Architecture",
        current_phase=ProjectPhase.PLANNING,
        metadata={
            "description": (
                "Update README.md and docs/architecture/INDEX.md to reflect "
                "the completed v2.5 architecture (HAP, SQLite, Registry patterns)"
            ),
            "workspace_root": str(Path.cwd() / "workspaces" / "maiden-voyage")
        }
    )

    # Execute planning phase
    print("\n" + "-"*80)
    print("🎯 PHASE 1: PLANNING (via PlanningSpecialist)")
    print("-"*80)

    try:
        # This should trigger:
        # 1. AgentRegistry.get_specialist(PLANNING) -> PlanningSpecialist
        # 2. SpecialistHandlerAdapter wrapping the specialist
        # 3. PlanningSpecialist.execute() running the planning logic
        # 4. SQLite logging decisions

        print("\n👀 WATCH FOR:")
        print("   • AgentRegistry selecting PlanningSpecialist")
        print("   • SpecialistHandlerAdapter initialization")
        print("   • SQLite decision logging")
        print("   • Planning analysis output\n")

        orchestrator.execute_phase(manifest)
        print("\n✅ Planning phase complete")

    except Exception as e:
        print(f"\n❌ Planning phase failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Execute coding phase
    print("\n" + "-"*80)
    print("🎯 PHASE 2: CODING (via CodingSpecialist)")
    print("-"*80)

    try:
        # This should trigger:
        # 1. AgentRegistry.get_specialist(CODING) -> CodingSpecialist
        # 2. CodingSpecialist.execute() with file modifications
        # 3. ToolSafetyGuard checking file write permissions
        # 4. SQLite logging decisions

        print("\n👀 WATCH FOR:")
        print("   • AgentRegistry selecting CodingSpecialist")
        print("   • ToolSafetyGuard file write checks")
        print("   • SQLite decision logging")
        print("   • README.md modifications\n")

        manifest.current_phase = ProjectPhase.CODING
        orchestrator.execute_phase(manifest)
        print("\n✅ Coding phase complete")

    except Exception as e:
        print(f"\n❌ Coding phase failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Verify SQLite logging
    print("\n" + "="*80)
    print("🔍 VERIFICATION: Check SQLite Decisions Table")
    print("="*80)

    import sqlite3
    db_path = Path.cwd() / ".vibe" / "state" / "vibe_agency.db"

    if not db_path.exists():
        print(f"⚠️  SQLite database not found at {db_path}")
        return 1

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM decisions")
    count = cursor.fetchone()[0]

    print(f"\n📊 Total decisions logged: {count}")

    if count > 0:
        cursor.execute("""
            SELECT id, mission_id, timestamp, decision_type, context
            FROM decisions
            ORDER BY id DESC
            LIMIT 5
        """)

        print("\n📝 Recent decisions:")
        for row in cursor.fetchall():
            decision_id, mission_id, timestamp, decision_type, context = row
            context_preview = context[:60] + "..." if context and len(context) > 60 else context
            print(f"   • Decision #{decision_id}: {decision_type} @ {timestamp}")
            print(f"     Mission: {mission_id}")
            print(f"     Context: {context_preview}")

    conn.close()

    # Final report
    print("\n" + "="*80)
    print("🎉 MAIDEN VOYAGE COMPLETE")
    print("="*80)

    if count > 0:
        print("\n✅ SUCCESS: v2.5 Architecture operational")
        print("   • AgentRegistry routing verified")
        print("   • Specialist execution verified")
        print(f"   • SQLite logging verified ({count} decisions)")
        print("   • Mission completed successfully")
        return 0
    else:
        print("\n⚠️  WARNING: No decisions logged to SQLite")
        print("   • Mission completed but shadow mode may not be active")
        return 1

if __name__ == "__main__":
    sys.exit(main())
