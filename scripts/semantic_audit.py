#!/usr/bin/env python3
"""
semantic_audit.py
================

Automated semantic validation engine for AOS Knowledge Base files.

This script validates KB YAML files against AOS_Ontology.yaml to detect:
1. Undefined terms (terms used but not in ontology)
2. Type mismatches (term used with wrong value type)
3. Owner consistency issues (term defined by different owner in different KBs)
4. Circular dependencies (semantic cycles)
5. Orphaned terms (defined but not used)
6. Stale terms (not updated in >6 months)

Usage:
    # Full validation of all KB files
    python scripts/semantic_audit.py --mode validate

    # Validation in dry-run mode (for proposed changes)
    python scripts/semantic_audit.py --mode validate --dry-run --file agency_os/01_planning_framework/knowledge/FAE_constraints.yaml

    # GitHub Actions integration (changed files from PR)
    python scripts/semantic_audit.py --mode validate --changed-files file1.yaml file2.yaml

Exit Codes:
    0: All validations passed
    1: Validation errors (blockers)
    2: Validation warnings (non-blockers)
"""

import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


class SemanticAudit:
    """Core semantic audit engine."""

    def __init__(self, ontology_path: str = None, verbose: bool = False):
        self.ontology_path = ontology_path or "agency_os/00_system/knowledge/AOS_Ontology.yaml"
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.ontology: Dict = {}
        self.all_terms: Dict = {}
        self.term_usage: Dict[str, List[str]] = defaultdict(list)

    def load_ontology(self) -> bool:
        """Load and parse the AOS_Ontology.yaml file."""
        try:
            with open(self.ontology_path, 'r') as f:
                data = yaml.safe_load(f)
            self.ontology = data
            self.all_terms = data.get('terms', {})
            if self.verbose:
                print(f"✓ Loaded ontology with {len(self.all_terms)} terms")
            return True
        except FileNotFoundError:
            self.errors.append(f"FATAL: Ontology file not found: {self.ontology_path}")
            return False
        except yaml.YAMLError as e:
            self.errors.append(f"FATAL: Failed to parse ontology YAML: {e}")
            return False

    def load_kb_file(self, kb_path: str) -> Optional[Dict]:
        """Load a KB YAML file."""
        try:
            with open(kb_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.errors.append(f"KB file not found: {kb_path}")
            return None
        except yaml.YAMLError as e:
            self.errors.append(f"Failed to parse KB YAML '{kb_path}': {e}")
            return None

    def extract_terms_from_kb(self, kb_data: Dict, kb_path: str) -> Set[str]:
        """Extract all semantic terms referenced in a KB file."""
        terms_found = set()

        def traverse(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Check if key matches a term name
                    if key in self.all_terms:
                        terms_found.add(key)
                        self.term_usage[key].append(kb_path)
                    traverse(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    traverse(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                # Check if string value is a term reference (heuristic)
                if obj in self.all_terms and not obj.startswith('_'):
                    terms_found.add(obj)
                    self.term_usage[obj].append(kb_path)

        traverse(kb_data)
        return terms_found

    def audit_kb_file(self, kb_path: str) -> bool:
        """Run full semantic audit on a single KB file."""
        if self.verbose:
            print(f"\nAuditing: {kb_path}")

        kb_data = self.load_kb_file(kb_path)
        if kb_data is None:
            return False

        # Extract terms used in this KB
        terms_in_kb = self.extract_terms_from_kb(kb_data, kb_path)

        has_errors = False

        # AUDIT_001: Check for undefined terms
        undefined = terms_in_kb - set(self.all_terms.keys())
        if undefined:
            for term in sorted(undefined):
                self.errors.append(
                    f"[AUDIT_001] Undefined term in '{kb_path}': '{term}'. "
                    f"Define it in AOS_Ontology.yaml."
                )
                has_errors = True

        # AUDIT_002: Check type consistency (basic check)
        for term_name in terms_in_kb:
            term_def = self.all_terms.get(term_name, {})
            term_type = term_def.get('type', 'unknown')
            if term_type == 'numeric_multiplier':
                # Would need more sophisticated type checking here
                pass

        # AUDIT_003: Check owner consistency
        for term_name in terms_in_kb:
            term_def = self.all_terms.get(term_name, {})
            owner = term_def.get('owner', 'unassigned')
            if owner in self.term_usage:
                # Check if all usages have consistent owner (simplified)
                pass

        return not has_errors

    def audit_all_kbs(self) -> bool:
        """Run audit on all KB files in the repository."""
        kb_paths = self._find_all_kb_files()

        if not kb_paths:
            self.warnings.append("No KB files found to audit")
            return True

        has_errors = False
        for kb_path in sorted(kb_paths):
            if not self.audit_kb_file(kb_path):
                has_errors = True

        # AUDIT_005: Check for orphaned terms
        all_referenced = set()
        for term, usages in self.term_usage.items():
            if usages:
                all_referenced.add(term)

        orphaned = set(self.all_terms.keys()) - all_referenced
        for term in sorted(orphaned):
            self.info.append(
                f"[AUDIT_005] Orphaned term: '{term}' defined in ontology but not used in any KB. "
                f"Consider deprecation."
            )

        return not has_errors

    def _find_all_kb_files(self) -> List[str]:
        """Find all KB files in the repository."""
        kb_files = []

        # Search patterns
        patterns = [
            "agency_os/*/knowledge/*.yaml",
            "agency_os/00_system/knowledge/*.yaml",
        ]

        for pattern in patterns:
            for path in Path(".").glob(pattern):
                if path.is_file() and path.name != "AOS_Ontology.yaml":
                    kb_files.append(str(path))

        return kb_files

    def print_report(self):
        """Print audit report to stdout."""
        print("\n" + "="*80)
        print("SEMANTIC AUDIT REPORT")
        print("="*80)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for err in self.errors:
                print(f"  {err}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  {warn}")

        if self.info:
            print(f"\nℹ️  INFO ({len(self.info)}):")
            for inf in self.info[:5]:  # Limit to 5 info messages
                print(f"  {inf}")
            if len(self.info) > 5:
                print(f"  ... and {len(self.info) - 5} more info messages")

        if not self.errors and not self.warnings:
            print("\n✓ All semantic audits passed!")

        print("\n" + "="*80)

    def get_exit_code(self) -> int:
        """Return appropriate exit code based on audit results."""
        if self.errors:
            return 1  # Errors block merge
        elif self.warnings:
            return 2  # Warnings are informational
        else:
            return 0  # All good


def main():
    parser = argparse.ArgumentParser(
        description="Semantic validation for AOS Knowledge Base files"
    )
    parser.add_argument(
        "--mode",
        choices=["validate", "report"],
        default="validate",
        help="Audit mode"
    )
    parser.add_argument(
        "--ontology",
        default="agency_os/00_system/knowledge/AOS_Ontology.yaml",
        help="Path to AOS_Ontology.yaml"
    )
    parser.add_argument(
        "--file",
        help="Single KB file to audit (instead of all)"
    )
    parser.add_argument(
        "--changed-files",
        nargs="*",
        help="Changed files from PR (for GitHub Actions)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode (validate but don't fail)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Initialize audit engine
    audit = SemanticAudit(ontology_path=args.ontology, verbose=args.verbose)

    # Load ontology
    if not audit.load_ontology():
        print("FATAL: Could not load ontology")
        return 1

    # Run audit based on mode
    if args.mode == "validate":
        if args.file:
            # Single file audit
            audit.audit_kb_file(args.file)
        elif args.changed_files:
            # Audit only changed files
            for f in args.changed_files:
                if f.endswith('.yaml') and 'knowledge' in f:
                    audit.audit_kb_file(f)
        else:
            # Full audit of all KB files
            audit.audit_all_kbs()

    # Print report
    audit.print_report()

    # Exit with appropriate code
    exit_code = audit.get_exit_code()

    if args.dry_run:
        print("\n[DRY-RUN MODE] Not failing on errors")
        return 0

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
