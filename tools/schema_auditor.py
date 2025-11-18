#!/usr/bin/env python3
"""Schema Auditor - Find structural inconsistencies in state files.

This tool audits all state files (manifests, handoffs, configs) to find:
- Structural variations (missing/extra fields)
- Type inconsistencies (string vs number, etc.)
- Naming inconsistencies (camelCase vs snake_case, etc.)

CRITICAL: This tool does NOT auto-generate schemas. It FINDS inconsistencies
for human review. The human then defines canonical schemas based on the audit.
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class FieldInfo:
    """Information about a field found in files."""

    name: str
    types: set[str] = field(default_factory=set)
    present_in: list[str] = field(default_factory=list)
    sample_values: list[Any] = field(default_factory=list)


@dataclass
class StructureVariation:
    """A unique structure variation found in files."""

    fields: frozenset[str]
    files: list[str] = field(default_factory=list)
    sample_file: str | None = None


@dataclass
class AuditResult:
    """Results from auditing a file type."""

    file_type: str
    files_scanned: list[str]
    variations: list[StructureVariation]
    field_analysis: dict[str, FieldInfo]
    type_mismatches: list[tuple[str, str, str]]  # (field, file, type)
    missing_in_files: dict[str, list[str]]  # field -> files missing it


class SchemaAuditor:
    """Audits state files for structural inconsistencies."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: dict[str, AuditResult] = {}

    def audit_all(self) -> dict[str, AuditResult]:
        """Run audit on all state file types."""
        print("🔍 Starting Schema Audit...")
        print()

        # Audit each file type
        self.audit_project_manifests()
        self.audit_session_handoffs()
        self.audit_knowledge_bases()

        return self.results

    def audit_project_manifests(self) -> None:
        """Audit workspaces/*/project_manifest.json files."""
        print("📋 Auditing project_manifest.json files...")

        files = list(self.repo_root.glob("workspaces/*/project_manifest.json"))
        if not files:
            print("  ⚠️  No project manifest files found")
            return

        structures = self._analyze_json_files(files)
        field_info = self._analyze_fields(files, "json")

        self.results["project_manifest"] = AuditResult(
            file_type="project_manifest.json",
            files_scanned=[str(f.relative_to(self.repo_root)) for f in files],
            variations=structures,
            field_analysis=field_info,
            type_mismatches=self._find_type_mismatches(field_info),
            missing_in_files=self._find_missing_fields(field_info, len(files)),
        )

        print(f"  ✅ Scanned {len(files)} files")
        print(f"  📊 Found {len(structures)} unique structures")
        print()

    def audit_session_handoffs(self) -> None:
        """Audit .session_handoff.json and .system_status.json files."""
        print("🤝 Auditing session handoff files...")

        files = []
        for pattern in [".session_handoff.json", ".system_status.json"]:
            found = list(self.repo_root.glob(pattern))
            files.extend(found)

        if not files:
            print("  ⚠️  No session handoff files found")
            return

        structures = self._analyze_json_files(files)
        field_info = self._analyze_fields(files, "json")

        self.results["session_handoff"] = AuditResult(
            file_type="session_handoff.json",
            files_scanned=[str(f.relative_to(self.repo_root)) for f in files],
            variations=structures,
            field_analysis=field_info,
            type_mismatches=self._find_type_mismatches(field_info),
            missing_in_files=self._find_missing_fields(field_info, len(files)),
        )

        print(f"  ✅ Scanned {len(files)} files")
        print(f"  📊 Found {len(structures)} unique structures")
        print()

    def audit_knowledge_bases(self) -> None:
        """Audit agency_os/*/knowledge/*.yaml files."""
        print("📚 Auditing knowledge base YAML files...")

        files = []
        for pattern in [
            "agency_os/*/knowledge/*.yaml",
            "agency_os/*/agents/**/_knowledge_deps.yaml",
        ]:
            found = list(self.repo_root.glob(pattern))
            files.extend(found)

        if not files:
            print("  ⚠️  No knowledge base files found")
            return

        # Sample first 10 files (knowledge bases can be large)
        sample_files = files[:10]
        structures = self._analyze_yaml_files(sample_files)
        field_info = self._analyze_fields(sample_files, "yaml")

        self.results["knowledge_base"] = AuditResult(
            file_type="knowledge_base.yaml",
            files_scanned=[str(f.relative_to(self.repo_root)) for f in sample_files],
            variations=structures,
            field_analysis=field_info,
            type_mismatches=self._find_type_mismatches(field_info),
            missing_in_files=self._find_missing_fields(field_info, len(sample_files)),
        )

        print(f"  ✅ Scanned {len(sample_files)} files (sampled from {len(files)} total)")
        print(f"  📊 Found {len(structures)} unique structures")
        print()

    def _analyze_json_files(self, files: list[Path]) -> list[StructureVariation]:
        """Analyze structural variations in JSON files."""
        structures: dict[frozenset, StructureVariation] = {}

        for file_path in files:
            try:
                with file_path.open() as f:
                    data = json.load(f)
                    fields = self._get_all_field_paths(data)
                    field_set = frozenset(fields)

                    if field_set not in structures:
                        structures[field_set] = StructureVariation(
                            fields=field_set,
                            sample_file=str(file_path.relative_to(self.repo_root)),
                        )
                    structures[field_set].files.append(str(file_path.relative_to(self.repo_root)))
            except (json.JSONDecodeError, OSError) as e:
                print(f"  ⚠️  Error reading {file_path}: {e}")

        return list(structures.values())

    def _analyze_yaml_files(self, files: list[Path]) -> list[StructureVariation]:
        """Analyze structural variations in YAML files."""
        structures: dict[frozenset, StructureVariation] = {}

        for file_path in files:
            try:
                with file_path.open() as f:
                    data = yaml.safe_load(f)
                    if not isinstance(data, dict):
                        continue
                    fields = self._get_all_field_paths(data)
                    field_set = frozenset(fields)

                    if field_set not in structures:
                        structures[field_set] = StructureVariation(
                            fields=field_set,
                            sample_file=str(file_path.relative_to(self.repo_root)),
                        )
                    structures[field_set].files.append(str(file_path.relative_to(self.repo_root)))
            except (yaml.YAMLError, OSError) as e:
                print(f"  ⚠️  Error reading {file_path}: {e}")

        return list(structures.values())

    def _get_all_field_paths(self, data: dict[str, Any], prefix: str = "") -> list[str]:
        """Get all nested field paths from a dict (e.g., 'metadata.name')."""
        fields = []
        for key, value in data.items():
            field_path = f"{prefix}.{key}" if prefix else key
            fields.append(field_path)
            if isinstance(value, dict):
                fields.extend(self._get_all_field_paths(value, field_path))
        return fields

    def _analyze_fields(self, files: list[Path], file_type: str) -> dict[str, FieldInfo]:
        """Analyze field presence and types across files."""
        field_info: dict[str, FieldInfo] = {}

        for file_path in files:
            try:
                if file_type == "json":
                    with file_path.open() as f:
                        data = json.load(f)
                else:  # yaml
                    with file_path.open() as f:
                        data = yaml.safe_load(f)
                        if not isinstance(data, dict):
                            continue

                for field_path, value in self._get_field_values(data):
                    if field_path not in field_info:
                        field_info[field_path] = FieldInfo(name=field_path)

                    field_info[field_path].types.add(type(value).__name__)
                    field_info[field_path].present_in.append(
                        str(file_path.relative_to(self.repo_root))
                    )
                    if len(field_info[field_path].sample_values) < 3:
                        field_info[field_path].sample_values.append(value)

            except (json.JSONDecodeError, yaml.YAMLError, OSError):
                continue

        return field_info

    def _get_field_values(self, data: dict[str, Any], prefix: str = "") -> list[tuple[str, Any]]:
        """Get all field paths and their values."""
        items = []
        for key, value in data.items():
            field_path = f"{prefix}.{key}" if prefix else key
            items.append((field_path, value))
            if isinstance(value, dict):
                items.extend(self._get_field_values(value, field_path))
        return items

    def _find_type_mismatches(self, field_info: dict[str, FieldInfo]) -> list[tuple[str, str, str]]:
        """Find fields with multiple types across files."""
        mismatches = []
        for field_name, info in field_info.items():
            if len(info.types) > 1:
                for file_path in info.present_in:
                    # Find which type this file has
                    types_str = ", ".join(sorted(info.types))
                    mismatches.append((field_name, file_path, types_str))
        return mismatches

    def _find_missing_fields(
        self, field_info: dict[str, FieldInfo], total_files: int
    ) -> dict[str, list[str]]:
        """Find fields that are missing in some files."""
        missing = {}
        for field_name, info in field_info.items():
            if len(info.present_in) < total_files:
                missing[field_name] = info.present_in
        return missing


def generate_report(results: dict[str, AuditResult], output_path: Path) -> None:
    """Generate markdown audit report."""
    print("📝 Generating audit report...")

    with output_path.open("w") as f:
        f.write("# SCHEMA AUDIT REPORT\n\n")
        f.write("**Generated by:** tools/schema_auditor.py\n")
        f.write("**Purpose:** Find structural inconsistencies in state files\n")
        f.write(
            "**Next Step:** Human review → Define canonical schemas → Create .schema.json files\n\n"
        )

        # Summary
        total_files = sum(len(r.files_scanned) for r in results.values())
        total_variations = sum(len(r.variations) for r in results.values())
        total_mismatches = sum(len(r.type_mismatches) for r in results.values())

        f.write("## 📊 Summary\n\n")
        f.write(f"- **File types scanned:** {len(results)}\n")
        f.write(f"- **Total files:** {total_files}\n")
        f.write(f"- **Unique structures:** {total_variations}\n")
        f.write(f"- **Type mismatches:** {total_mismatches}\n\n")

        # Detailed findings per file type
        for file_type, result in results.items():
            f.write(f"## 📁 {result.file_type}\n\n")
            f.write(f"**Files scanned:** {len(result.files_scanned)}\n\n")

            # Structure variations
            f.write(f"### Structural Variations ({len(result.variations)})\n\n")
            for i, variation in enumerate(result.variations, 1):
                f.write(f"#### Structure {chr(64 + i)}\n\n")
                f.write(f"**Files:** {len(variation.files)}\n\n")
                f.write("**Fields:**\n")
                for field in sorted(variation.fields):
                    f.write(f"- `{field}`\n")
                f.write("\n")
                f.write("**Sample file:**\n")
                f.write(f"```\n{variation.sample_file}\n```\n\n")

            # Missing fields
            if result.missing_in_files:
                f.write("### Missing Fields\n\n")
                f.write("Fields that appear in SOME files but not ALL files:\n\n")
                for field, present_files in sorted(result.missing_in_files.items()):
                    missing_count = len(result.files_scanned) - len(present_files)
                    f.write(
                        f"- `{field}`: Missing in {missing_count}/{len(result.files_scanned)} files\n"
                    )
                f.write("\n")

            # Type mismatches
            if result.type_mismatches:
                f.write("### Type Inconsistencies\n\n")
                f.write("Fields with different types across files:\n\n")
                seen = set()
                for field, file_path, types in result.type_mismatches:
                    if field not in seen:
                        f.write(f"- `{field}`: {types}\n")
                        seen.add(field)
                f.write("\n")

            # Field analysis
            f.write("### Field Analysis\n\n")
            f.write("| Field | Types | Present In |\n")
            f.write("|-------|-------|------------|\n")
            for field_name in sorted(result.field_analysis.keys()):
                info = result.field_analysis[field_name]
                types_str = ", ".join(sorted(info.types))
                present_count = len(info.present_in)
                total_count = len(result.files_scanned)
                f.write(f"| `{field_name}` | {types_str} | {present_count}/{total_count} |\n")
            f.write("\n")

        # Recommendations
        f.write("## 🎯 Recommendations\n\n")
        f.write("Based on this audit, the following canonical schemas should be defined:\n\n")

        for file_type, result in results.items():
            if result.variations:
                f.write(f"### {result.file_type}\n\n")
                most_common = max(result.variations, key=lambda v: len(v.files))
                f.write(
                    f"**Recommended base structure:** Structure with {len(most_common.files)} files\n\n"
                )
                f.write("**Required fields:**\n")
                # Fields present in ALL files
                all_fields = set.intersection(*[set(v.fields) for v in result.variations])
                for field in sorted(all_fields):
                    f.write(f"- `{field}` (present in all files)\n")
                f.write("\n")
                f.write("**Optional fields:**\n")
                # Fields present in SOME files
                some_fields = set.union(*[set(v.fields) for v in result.variations]) - all_fields
                for field in sorted(some_fields):
                    present_count = sum(1 for v in result.variations if field in v.fields)
                    f.write(
                        f"- `{field}` (present in {present_count}/{len(result.variations)} structures)\n"
                    )
                f.write("\n")

        # Next steps
        f.write("## 🚀 Next Steps\n\n")
        f.write("1. **Human Review** - Review this report and decide:\n")
        f.write("   - Which structure should be canonical?\n")
        f.write("   - Which fields are required vs optional?\n")
        f.write("   - Which inconsistencies are bugs vs intentional?\n\n")
        f.write("2. **Define Schemas** - Create JSON Schema files in `config/schemas/`:\n")
        for file_type in results:
            schema_name = file_type.replace("_", "_")
            f.write(f"   - `config/schemas/{schema_name}.schema.json`\n")
        f.write("\n")
        f.write("3. **Implement Validation** - Wire up schemas to config loader\n")
        f.write("4. **Fix Inconsistencies** - Update files to match canonical schema\n\n")

    print(f"  ✅ Report written to {output_path}")


def main() -> int:
    """Run schema audit and generate report."""
    repo_root = Path(__file__).parent.parent
    auditor = SchemaAuditor(repo_root)

    try:
        results = auditor.audit_all()

        if not results:
            print("❌ No files found to audit")
            return 1

        # Generate report
        report_path = repo_root / "reports" / "SCHEMA_AUDIT_REPORT.md"
        report_path.parent.mkdir(exist_ok=True)
        generate_report(results, report_path)

        print()
        print("✅ Schema audit complete!")
        print(f"📄 Report: {report_path.relative_to(repo_root)}")
        print()
        print("🎯 Next: Review report and define canonical schemas")

        return 0

    except Exception as e:
        print(f"❌ Audit failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
