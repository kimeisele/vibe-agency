#!/usr/bin/env python3
"""
GAD Watchdog: Audit all code for GAD references and verify documentation exists

Law: "If it is not documented, it does not exist"

This script:
1. Scans all .py files for GAD-XXX references in comments
2. Checks if corresponding documentation exists in docs/architecture/GAD-XXX/
3. Fails if code references a GAD without documentation
4. Can be integrated into CI/CD pipeline

Usage:
    python scripts/audit_gads.py [--fix-suggestions] [--verbose]

Exit codes:
    0 = All GADs documented (pass)
    1 = Undocumented GADs found (fail)
    2 = Script error
"""

import re
import sys
from pathlib import Path


class GADWatchdog:
    """Audit GAD references in code and verify documentation exists"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.code_dir = repo_root / "agency_os"
        self.scripts_dir = repo_root / "scripts"
        self.tests_dir = repo_root / "tests"
        self.docs_dir = repo_root / "docs" / "architecture"

        # Patterns for finding GAD references
        self.gad_pattern = re.compile(r"#\s*(GAD-\d{3,4})")
        self.import_pattern = re.compile(r"from.*GAD.*import|import.*GAD")

        # Tracked results
        self.gad_references: dict[str, list[tuple[str, int]]] = {}  # GAD -> [(file, line)]
        self.documented_gads: set[str] = set()
        self.undocumented_gads: set[str] = set()
        self.errors: list[str] = []

    def scan_python_files(self) -> None:
        """Scan all Python files for GAD references"""
        print("🔍 Scanning Python files for GAD references...")

        search_dirs = [self.code_dir, self.scripts_dir, self.tests_dir]
        python_files = []

        for search_dir in search_dirs:
            if search_dir.exists():
                python_files.extend(search_dir.rglob("*.py"))

        print(f"   Found {len(python_files)} Python files to scan\n")

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        # Look for GAD comments
                        matches = self.gad_pattern.findall(line)
                        for gad_id in matches:
                            if gad_id not in self.gad_references:
                                self.gad_references[gad_id] = []
                            rel_path = py_file.relative_to(self.repo_root)
                            self.gad_references[gad_id].append((str(rel_path), line_num))
            except Exception as e:
                self.errors.append(f"Error reading {py_file}: {e}")

    def check_documentation(self) -> None:
        """Check if documentation exists for each GAD"""
        print("📚 Checking documentation for discovered GADs...")

        if not self.gad_references:
            print("   No GAD references found in code\n")
            return

        print(f"   Found {len(self.gad_references)} unique GAD references\n")

        for gad_id in sorted(self.gad_references.keys()):
            # Extract the numeric part (e.g., "509" from "GAD-509")
            gad_num = gad_id.replace("GAD-", "")

            # Determine the directory (e.g., "GAD-5XX" for "GAD-509")
            if len(gad_num) == 3:
                gad_dir = f"GAD-{gad_num[0]}XX"
            elif len(gad_num) == 4:
                gad_dir = f"GAD-{gad_num[0:2]}XX"
            else:
                gad_dir = None

            if not gad_dir:
                self.errors.append(f"Invalid GAD format: {gad_id}")
                continue

            # Check if docs directory exists
            docs_dir = self.docs_dir / gad_dir
            doc_file = docs_dir / f"{gad_id}.md"

            if doc_file.exists():
                self.documented_gads.add(gad_id)
                status = "✅"
            else:
                self.undocumented_gads.add(gad_id)
                status = "❌"

            locations = self.gad_references[gad_id]
            print(f"   {status} {gad_id}: Found in {len(locations)} location(s)")

            if status == "❌":
                print(f"      Expected: {doc_file}")
                for file_path, line_num in locations[:3]:  # Show first 3 locations
                    print(f"      Referenced: {file_path}:{line_num}")
                if len(locations) > 3:
                    print(f"      ... and {len(locations) - 3} more locations")

        print()

    def generate_report(self) -> None:
        """Generate and display audit report"""
        print("=" * 80)
        print("📊 GAD AUDIT REPORT")
        print("=" * 80)
        print()

        total_gads = len(self.gad_references)
        documented = len(self.documented_gads)
        undocumented = len(self.undocumented_gads)

        print(f"Total GAD References: {total_gads}")
        print(f"  ✅ Documented: {documented}")
        print(f"  ❌ Undocumented: {undocumented}")
        print()

        if self.undocumented_gads:
            print("🚨 UNDOCUMENTED GADs (Code without Documentation):")
            print("-" * 80)
            for gad_id in sorted(self.undocumented_gads):
                locations = self.gad_references[gad_id]
                print(f"\n{gad_id}:")
                print(f"  References ({len(locations)} total):")
                for file_path, line_num in locations[:5]:  # Show first 5
                    print(f"    - {file_path}:{line_num}")
                if len(locations) > 5:
                    print(f"    - ... and {len(locations) - 5} more")
                print("\n  Action Required:")
                gad_num = gad_id.replace("GAD-", "")
                gad_dir = f"GAD-{gad_num[0]}XX" if len(gad_num) == 3 else f"GAD-{gad_num[0:2]}XX"
                print(f"    Create: docs/architecture/{gad_dir}/{gad_id}.md")
            print()
        else:
            print("✅ ALL GADs ARE DOCUMENTED")
            print()

        if self.errors:
            print(f"⚠️  {len(self.errors)} Errors encountered:")
            for error in self.errors:
                print(f"   - {error}")
            print()

        print("=" * 80)

    def run(self, verbose: bool = False) -> int:
        """Run complete audit"""
        print()
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  🔍 GAD WATCHDOG - CODE DOCUMENTATION AUDIT".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "=" * 78 + "╝")
        print()

        try:
            self.scan_python_files()
            self.check_documentation()
            self.generate_report()

            if self.undocumented_gads:
                print(
                    "❌ AUDIT FAILED: Undocumented GADs found\n"
                    "   Law: 'If it is not documented, it does not exist'\n"
                    "   Please document all GAD references before pushing.\n"
                )
                return 1
            else:
                print(
                    "✅ AUDIT PASSED: All GAD references have documentation\n"
                    "   System is in compliance.\n"
                )
                return 0

        except Exception as e:
            print(f"❌ AUDIT ERROR: {e}")
            return 2


def main():
    """Entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="GAD Watchdog: Audit code for undocumented GAD references"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Show suggestions for creating missing docs",
    )

    args = parser.parse_args()

    # Find repo root
    repo_root = Path(__file__).parent.parent
    if not repo_root.is_dir():
        print(f"❌ Error: Could not find repository root from {__file__}")
        return 2

    # Run audit
    watchdog = GADWatchdog(repo_root)
    return watchdog.run(verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
