# Validation Gate: QA Approved

## Rule
qa_report.json must have status APPROVED before deployment.

## Pass Criteria
- ✅ qa_report.json status = APPROVED
- ✅ approval.isApproved = true

## Failure Conditions
- ❌ qa_report.json status ≠ APPROVED
- ❌ Missing approval
