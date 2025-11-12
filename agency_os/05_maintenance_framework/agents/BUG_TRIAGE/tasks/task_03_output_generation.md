# Task: Output Generation

## Objective
Generate code_gen_spec.json (hotfix) OR signal to backlog (regular fix).

## Input Artifacts
- `remediation_decision` (from Task 02)
- `bug_report.json`

## Process
1. If hotfix:
   - Generate minimal code_gen_spec.json
   - Outline specific code changes
   - Signal orchestrator for high-priority CODING phase
2. If regular fix:
   - Signal orchestrator to add to PLANNING backlog

## Output
`code_gen_spec.json` (hotfix) OR backlog signal

## Success Criteria
- ✅ Output matches remediation decision
- ✅ Hotfix specs are minimal and targeted
- ✅ Clear signal for orchestrator
