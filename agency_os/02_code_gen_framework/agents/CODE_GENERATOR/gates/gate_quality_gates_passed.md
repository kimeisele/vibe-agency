# Validation Gate: Quality Gates Passed

## Rule
All quality checks (linting, formatting, security) must pass before packaging.

---

## Quality Checks

### 1. Linting
- No critical linting errors
- Code follows style guide
- No code smells or anti-patterns

### 2. Formatting
- Consistent code formatting
- Imports sorted correctly
- Line length within limits

### 3. Security Scan
- No hardcoded secrets
- No SQL injection patterns
- No XSS vulnerabilities
- Secure crypto usage

---

## Pass Criteria

- ✅ Linting: 0 critical errors
- ✅ Formatting: All files formatted
- ✅ Security: 0 critical vulnerabilities
- ✅ All auto-fixable issues corrected

---

## Failure Conditions

- ❌ Critical linting errors remain
- ❌ Code not formatted
- ❌ Critical security vulnerability found

---

## Error Message Template

```
GATE FAILED: Quality checks not passed

Linting:
  - Errors: {error_count}
  - Warnings: {warning_count}

Security:
  - Critical vulnerabilities: {critical_count}
  - Warnings: {warning_count}

Issues:
{list_issues}

Action: Fix quality issues before packaging
```
