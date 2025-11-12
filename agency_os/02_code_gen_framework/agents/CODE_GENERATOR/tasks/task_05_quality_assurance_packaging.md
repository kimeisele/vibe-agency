# Task: Quality Assurance & Packaging

## Objective
Perform final quality checks, self-correct violations, and package all artifacts into final artifact_bundle.

---

## Goal
Ensure generated code meets all quality standards before handoff to TESTING phase.

---

## Input Artifacts
- `generated_code.json` (from Task 02)
- `generated_tests.json` (from Task 03)
- `generated_documentation.json` (from Task 04)
- `CODE_GEN_quality_rules.yaml` (from knowledge base)

---

## Process

### Step 1: Self-Correction (Linting/Formatting)
Apply quality rules from `CODE_GEN_quality_rules.yaml`:
- **Linting:** Check for code smells, anti-patterns
- **Formatting:** Apply consistent code style (e.g., Black, Ruff)
- **Import Sorting:** Organize imports (e.g., isort)
- **Self-Correct:** Fix all auto-fixable violations

### Step 2: Security Scan (Basic)
Perform basic static analysis for common vulnerabilities:
- SQL injection patterns
- XSS vulnerabilities
- Hardcoded secrets
- Insecure crypto usage
- Path traversal risks

**If critical issues found:** Flag for manual review (but do not block packaging)

### Step 3: Package Output
Assemble all artifacts into structured `artifact_bundle`:
- Source code files
- Test files
- Documentation files
- Metadata (timestamps, versions, quality gates passed)

---

## Quality Gates Checklist

Before packaging, verify:
- ✅ All linting violations fixed
- ✅ Code is formatted consistently
- ✅ No hardcoded secrets
- ✅ All tests are runnable
- ✅ Documentation is complete
- ✅ Genesis Core Pattern enforced

---

## Output

Final `artifact_bundle`:

```json
{
  "bundleId": "ab-001",
  "projectId": "uuid-...",
  "codeGenSpecRef": {
    "ref": "commit-sha-...",
    "path": "/artifacts/code_gen_spec.v1.json"
  },
  "sourceCode": [
    {
      "filePath": "src/core/auth.py",
      "content": "..."
    },
    {
      "filePath": "src/extensions/user_management/user_service.py",
      "content": "..."
    }
  ],
  "tests": [
    {
      "filePath": "tests/test_auth.py",
      "content": "..."
    }
  ],
  "documentation": [
    {
      "filePath": "docs/api.md",
      "content": "..."
    },
    {
      "filePath": "README.md",
      "content": "..."
    }
  ],
  "metadata": {
    "generatedAt": "2025-01-15T10:30:00Z",
    "codeGenVersion": "1.0",
    "qualityGatesPassed": true,
    "lintingResults": {
      "violations_found": 12,
      "violations_fixed": 12,
      "critical_issues": 0
    },
    "securityScanResults": {
      "vulnerabilities_found": 0,
      "warnings": 2
    }
  }
}
```

---

## Success Criteria

- ✅ All quality gates passed
- ✅ Code is linted and formatted
- ✅ No critical security issues
- ✅ artifact_bundle is well-formed
- ✅ Ready for TESTING phase

---

## Validation Gates

- `gate_quality_gates_passed.md` - Ensures all quality checks passed
- `gate_artifact_bundle_valid.md` - Ensures bundle is well-formed
