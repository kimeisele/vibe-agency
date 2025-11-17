# LAD-2: Claude Code Layer (Tool-Based)

## Overview
Enhanced with Claude Code - automated tools, no external APIs.

## What Works

| Pillar | Feature | Tool | Status |
|--------|---------|------|--------|
| GAD-5 (Runtime) | Receipts | receipt_create | ✅ |
| GAD-5 (Runtime) | Integrity | verify_integrity | ✅ |
| GAD-6 (Knowledge) | Query | knowledge_query | ✅ |
| GAD-7 (STEWARD) | Validation | steward_validate | ✅ |
| GAD-8 (Integration) | Layer Detection | layer_detect | ✅ |

## Setup
1. Install Claude Code
2. Clone repo
3. Run `./scripts/setup-layer2.sh` (if exists)
4. Tools available in Claude Code environment

## Limitations
- ❌ No external APIs
- ❌ No federated research
- ✅ Local tools only
- ✅ File system access

## Use Cases
- Individual developer
- Small teams
- Most projects

## Cost
$20/month (Claude subscription)
