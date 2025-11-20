#!/usr/bin/env python3
"""
ARCH-004: Shadow Mode Validation Tool

Purpose: Verify that SQLite shadow copy matches JSON source of truth (ARCH-003).

This tool provides empirical validation during the "baking period" between
ARCH-003 (Shadow Mode Dual Write) and Phase 2 (Cutover to SQLite Primary).

Usage:
    ./bin/verify-shadow-mode.py [--verbose] [--project-root PATH]

Exit Codes:
    0 = GREEN (100% match)
    1 = RED (mismatches found)
    2 = ERROR (validation failed to run)
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class ShadowModeValidator:
    """Validates SQLite shadow copy against JSON source of truth"""

    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.errors = []
        self.warnings = []

        # File paths
        self.manifest_file = project_root / "project_manifest.json"
        self.memory_file = project_root / ".vibe" / "project_memory.json"
        self.db_file = project_root / ".vibe" / "state" / "vibe_agency.db"

    def log(self, msg: str, level: str = "INFO"):
        """Log message if verbose"""
        if self.verbose or level in ["ERROR", "WARNING"]:
            prefix = {"INFO": "ℹ️ ", "ERROR": "❌", "WARNING": "⚠️ "}
            print(f"{prefix.get(level, '')} {msg}", file=sys.stderr)

    def error(self, msg: str):
        """Record error"""
        self.errors.append(msg)
        self.log(msg, "ERROR")

    def warn(self, msg: str):
        """Record warning"""
        self.warnings.append(msg)
        self.log(msg, "WARNING")

    def validate(self) -> dict[str, Any]:
        """
        Run full validation.

        Returns:
            Report dict with validation results
        """
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "project_root": str(self.project_root),
            "status": "UNKNOWN",
            "checks": {},
            "errors": [],
            "warnings": [],
        }

        # Pre-flight checks
        self.log("🔍 Starting Shadow Mode validation...")

        if not self._check_files_exist():
            report["status"] = "INCOMPLETE"
            report["errors"] = self.errors
            report["warnings"] = self.warnings
            return report

        # Load data
        manifest = self._load_json(self.manifest_file)
        memory = self._load_json(self.memory_file)
        db_mission = self._load_db_mission()

        if not manifest or not db_mission:
            report["status"] = "ERROR"
            report["errors"] = self.errors
            report["warnings"] = self.warnings
            return report

        # Run validation checks
        self.log("📊 Comparing Manifest → SQLite (missions table)...")
        report["checks"]["mission"] = self._validate_mission(manifest, db_mission)

        if memory:
            self.log("🧠 Comparing Memory → SQLite (v2 tables)...")
            report["checks"]["memory"] = self._validate_memory(memory, db_mission)
        else:
            self.warn("No project_memory.json found - skipping memory validation")

        # Determine final status
        if self.errors:
            report["status"] = "RED"
        elif self.warnings:
            report["status"] = "YELLOW"
        else:
            report["status"] = "GREEN"

        report["errors"] = self.errors
        report["warnings"] = self.warnings

        return report

    def _check_files_exist(self) -> bool:
        """Check if required files exist"""
        if not self.manifest_file.exists():
            self.warn(f"Manifest not found: {self.manifest_file}")
            return False

        if not self.db_file.exists():
            self.warn(f"Database not found: {self.db_file}")
            self.warn("Shadow mode not yet initialized (database doesn't exist)")
            return False

        return True

    def _load_json(self, path: Path) -> dict[str, Any] | None:
        """Load JSON file"""
        if not path.exists():
            return None

        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            self.error(f"Failed to load {path}: {e}")
            return None

    def _load_db_mission(self) -> dict[str, Any] | None:
        """Load mission from SQLite database"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row

            # Get the most recent mission (should be current project)
            cursor = conn.execute("SELECT * FROM missions ORDER BY created_at DESC LIMIT 1")
            row = cursor.fetchone()

            if not row:
                self.error("No missions found in database")
                conn.close()
                return None

            mission = dict(row)

            # Parse JSON fields
            if mission.get("metadata"):
                mission["metadata"] = json.loads(mission["metadata"])
            if mission.get("cost_breakdown"):
                mission["cost_breakdown"] = json.loads(mission["cost_breakdown"])

            conn.close()
            return mission

        except sqlite3.Error as e:
            self.error(f"Database error: {e}")
            return None

    def _validate_mission(self, manifest: dict, db_mission: dict) -> dict[str, Any]:
        """Validate mission data (manifest → missions table)"""
        checks = {"passed": 0, "failed": 0, "mismatches": []}

        # Extract expected values from manifest
        metadata = manifest.get("metadata", {})
        status = manifest.get("status", {})
        budget = manifest.get("budget", {})

        # Check mission_uuid (metadata.projectId)
        expected_uuid = metadata.get("projectId", "unknown")
        if db_mission["mission_uuid"] != expected_uuid:
            checks["failed"] += 1
            checks["mismatches"].append(
                {
                    "field": "mission_uuid",
                    "expected": expected_uuid,
                    "actual": db_mission["mission_uuid"],
                }
            )
            self.error(f"mission_uuid mismatch: expected={expected_uuid}, actual={db_mission['mission_uuid']}")
        else:
            checks["passed"] += 1
            self.log(f"✅ mission_uuid matches: {expected_uuid}")

        # Check phase (status.projectPhase)
        expected_phase = status.get("projectPhase", "PLANNING")
        if db_mission["phase"] != expected_phase:
            checks["failed"] += 1
            checks["mismatches"].append(
                {"field": "phase", "expected": expected_phase, "actual": db_mission["phase"]}
            )
            self.error(f"phase mismatch: expected={expected_phase}, actual={db_mission['phase']}")
        else:
            checks["passed"] += 1
            self.log(f"✅ phase matches: {expected_phase}")

        # Check owner (metadata.owner)
        expected_owner = metadata.get("owner")
        if db_mission["owner"] != expected_owner:
            checks["failed"] += 1
            checks["mismatches"].append(
                {"field": "owner", "expected": expected_owner, "actual": db_mission["owner"]}
            )
            self.error(f"owner mismatch: expected={expected_owner}, actual={db_mission['owner']}")
        else:
            checks["passed"] += 1
            self.log(f"✅ owner matches: {expected_owner}")

        # Check description
        expected_desc = metadata.get("description")
        if db_mission["description"] != expected_desc:
            checks["failed"] += 1
            checks["mismatches"].append(
                {"field": "description", "expected": expected_desc, "actual": db_mission["description"]}
            )
            self.error(f"description mismatch")
        else:
            checks["passed"] += 1
            self.log(f"✅ description matches")

        # Check budget fields (if present in manifest)
        if budget:
            expected_max = budget.get("max_cost_usd")
            expected_current = budget.get("current_cost_usd", 0.0)

            if db_mission["max_cost_usd"] != expected_max:
                checks["failed"] += 1
                checks["mismatches"].append(
                    {
                        "field": "max_cost_usd",
                        "expected": expected_max,
                        "actual": db_mission["max_cost_usd"],
                    }
                )
                self.error(f"max_cost_usd mismatch: expected={expected_max}, actual={db_mission['max_cost_usd']}")
            else:
                checks["passed"] += 1
                self.log(f"✅ max_cost_usd matches: {expected_max}")

            if db_mission["current_cost_usd"] != expected_current:
                checks["failed"] += 1
                checks["mismatches"].append(
                    {
                        "field": "current_cost_usd",
                        "expected": expected_current,
                        "actual": db_mission["current_cost_usd"],
                    }
                )
                self.error(
                    f"current_cost_usd mismatch: expected={expected_current}, actual={db_mission['current_cost_usd']}"
                )
            else:
                checks["passed"] += 1
                self.log(f"✅ current_cost_usd matches: {expected_current}")

        return checks

    def _validate_memory(self, memory: dict, db_mission: dict) -> dict[str, Any]:
        """Validate project memory (memory → v2 tables)"""
        checks = {"passed": 0, "failed": 0, "mismatches": []}

        mission_id = db_mission["id"]

        try:
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row

            # Check session_narrative count
            narrative = memory.get("narrative", [])
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM session_narrative WHERE mission_id = ?", (mission_id,)
            )
            db_count = cursor.fetchone()[0]

            if db_count != len(narrative):
                checks["failed"] += 1
                checks["mismatches"].append(
                    {
                        "field": "session_narrative.count",
                        "expected": len(narrative),
                        "actual": db_count,
                    }
                )
                self.error(f"session_narrative count mismatch: expected={len(narrative)}, actual={db_count}")
            else:
                checks["passed"] += 1
                self.log(f"✅ session_narrative count matches: {len(narrative)}")

            # Check domain_concepts count
            domain = memory.get("domain", {})
            concepts = domain.get("concepts", [])
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM domain_concepts WHERE mission_id = ?", (mission_id,)
            )
            db_count = cursor.fetchone()[0]

            if db_count != len(concepts):
                checks["failed"] += 1
                checks["mismatches"].append(
                    {
                        "field": "domain_concepts.count",
                        "expected": len(concepts),
                        "actual": db_count,
                    }
                )
                self.error(f"domain_concepts count mismatch: expected={len(concepts)}, actual={db_count}")
            else:
                checks["passed"] += 1
                self.log(f"✅ domain_concepts count matches: {len(concepts)}")

            # Check domain_concerns count
            concerns = domain.get("concerns", [])
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM domain_concerns WHERE mission_id = ?", (mission_id,)
            )
            db_count = cursor.fetchone()[0]

            if db_count != len(concerns):
                checks["failed"] += 1
                checks["mismatches"].append(
                    {
                        "field": "domain_concerns.count",
                        "expected": len(concerns),
                        "actual": db_count,
                    }
                )
                self.error(f"domain_concerns count mismatch: expected={len(concerns)}, actual={db_count}")
            else:
                checks["passed"] += 1
                self.log(f"✅ domain_concerns count matches: {len(concerns)}")

            # Check trajectory
            trajectory = memory.get("trajectory", {})
            cursor = conn.execute("SELECT * FROM trajectory WHERE mission_id = ?", (mission_id,))
            row = cursor.fetchone()

            if row:
                db_trajectory = dict(row)
                expected_phase = trajectory.get("phase", "UNKNOWN")

                if db_trajectory["current_phase"] != expected_phase:
                    checks["failed"] += 1
                    checks["mismatches"].append(
                        {
                            "field": "trajectory.current_phase",
                            "expected": expected_phase,
                            "actual": db_trajectory["current_phase"],
                        }
                    )
                    self.error(
                        f"trajectory.current_phase mismatch: expected={expected_phase}, actual={db_trajectory['current_phase']}"
                    )
                else:
                    checks["passed"] += 1
                    self.log(f"✅ trajectory.current_phase matches: {expected_phase}")
            else:
                if trajectory:
                    checks["failed"] += 1
                    self.error("trajectory missing in database but present in memory.json")

            conn.close()

        except sqlite3.Error as e:
            checks["failed"] += 1
            self.error(f"Database error during memory validation: {e}")

        return checks

    def print_report(self, report: dict):
        """Print human-readable report"""
        print("\n" + "=" * 80)
        print("ARCH-004: SHADOW MODE VALIDATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Project:   {report['project_root']}")
        print(f"\nStatus:    {self._status_badge(report['status'])}")
        print("=" * 80)

        if report.get("checks"):
            print("\n📊 VALIDATION CHECKS:")
            for check_name, check_data in report["checks"].items():
                passed = check_data.get("passed", 0)
                failed = check_data.get("failed", 0)
                total = passed + failed
                print(f"\n  {check_name.upper()}:")
                print(f"    Passed: {passed}/{total}")
                print(f"    Failed: {failed}/{total}")

                if check_data.get("mismatches"):
                    print(f"\n    Mismatches:")
                    for mismatch in check_data["mismatches"]:
                        print(f"      • {mismatch['field']}")
                        print(f"        Expected: {mismatch['expected']}")
                        print(f"        Actual:   {mismatch['actual']}")

        if report.get("warnings"):
            print(f"\n⚠️  WARNINGS ({len(report['warnings'])}):")
            for warning in report["warnings"]:
                print(f"  • {warning}")

        if report.get("errors"):
            print(f"\n❌ ERRORS ({len(report['errors'])}):")
            for error in report["errors"]:
                print(f"  • {error}")

        print("\n" + "=" * 80)

        if report["status"] == "GREEN":
            print("✅ VALIDATION PASSED - SQLite shadow copy is 100% consistent with JSON")
        elif report["status"] == "YELLOW":
            print("⚠️  VALIDATION PASSED WITH WARNINGS - Minor issues detected")
        elif report["status"] == "RED":
            print("❌ VALIDATION FAILED - Mismatches detected between JSON and SQLite")
        elif report["status"] == "INCOMPLETE":
            print("⚠️  VALIDATION INCOMPLETE - Required files missing (shadow mode not initialized)")
        else:
            print("❌ VALIDATION ERROR - Could not complete validation")

        print("=" * 80 + "\n")

    def _status_badge(self, status: str) -> str:
        """Return colored status badge"""
        badges = {
            "GREEN": "🟢 GREEN (100% MATCH)",
            "YELLOW": "🟡 YELLOW (WARNINGS)",
            "RED": "🔴 RED (MISMATCHES)",
            "INCOMPLETE": "⚪ INCOMPLETE",
            "ERROR": "⚫ ERROR",
        }
        return badges.get(status, status)


def main():
    parser = argparse.ArgumentParser(
        description="ARCH-004: Validate SQLite shadow copy against JSON source of truth"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--json-output", type=Path, help="Write report to JSON file (optional)"
    )

    args = parser.parse_args()

    # Run validation
    validator = ShadowModeValidator(args.project_root, verbose=args.verbose)
    report = validator.validate()

    # Print report
    validator.print_report(report)

    # Save JSON report if requested
    if args.json_output:
        with open(args.json_output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {args.json_output}", file=sys.stderr)

    # Exit with appropriate code
    if report["status"] == "GREEN":
        sys.exit(0)
    elif report["status"] in ["YELLOW", "INCOMPLETE"]:
        sys.exit(0)  # Non-fatal
    else:
        sys.exit(1)  # Fatal


if __name__ == "__main__":
    main()
