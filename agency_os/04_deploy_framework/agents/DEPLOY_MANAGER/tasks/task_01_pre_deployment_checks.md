# Task: Pre-Deployment Checks

## Objective
Validate qa_report.json is APPROVED and environment is ready.

## Input Artifacts
- `qa_report.json` (must be APPROVED)
- `DEPLOY_constraints.yaml`
- `DEPLOY_dependencies.yaml`

## Process
1. Validate qa_report.json status = APPROVED
2. Check target environment readiness
3. Verify deployment dependencies available

## Output
Pre-deployment validation result

## Success Criteria
- ✅ qa_report.json is APPROVED
- ✅ Environment ready
- ✅ Dependencies available
