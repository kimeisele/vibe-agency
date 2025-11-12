# Task: Deployment Execution

## Objective
Execute deployment to target environment.

## Input Artifacts
- `artifact_bundle` (via qa_report.json reference)
- `DEPLOY_quality_rules.yaml`

## Process
1. Retrieve artifact_bundle
2. Execute deployment strategy (blue/green, canary, rolling)
3. Apply environment-specific configurations
4. Execute database migrations (with rollback capability)

## Output
Deployment execution result

## Success Criteria
- ✅ Deployment completed
- ✅ Configurations applied
- ✅ Migrations executed
