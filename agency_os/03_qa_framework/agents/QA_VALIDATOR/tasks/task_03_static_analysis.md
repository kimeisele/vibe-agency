# Task: Static Analysis & Quality Gates

## Objective
Perform SAST, SCA, and code quality checks.

## Input Artifacts
- `artifact_bundle`
- `QA_quality_rules.yaml`
- `QA_constraints.yaml`

## Process
1. Run SAST (e.g., Bandit)
2. Run SCA (dependency vulnerabilities)
3. Run linters/formatters
4. Validate against QA_constraints.yaml

## Output
Static analysis results

## Success Criteria
- ✅ SAST completed
- ✅ SCA completed
- ✅ No critical vulnerabilities
- ✅ Constraints validated
