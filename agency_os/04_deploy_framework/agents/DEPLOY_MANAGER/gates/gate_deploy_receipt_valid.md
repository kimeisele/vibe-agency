# Validation Gate: Deploy Receipt Valid

## Rule
deploy_receipt.json must be well-formed and complete.

## Pass Criteria
- ✅ JSON is valid
- ✅ Status is SUCCESS or ROLLED_BACK
- ✅ All details included

## Failure Conditions
- ❌ Malformed JSON
- ❌ Missing required fields
