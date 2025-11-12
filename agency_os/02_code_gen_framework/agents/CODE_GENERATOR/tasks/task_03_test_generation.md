# Task: Test Generation

## Objective
Generate comprehensive unit and integration tests for all generated code.

---

## Goal
Ensure all generated code has adequate test coverage to catch bugs early.

---

## Input Artifacts
- `generated_code.json` (from Task 02)
- `CODE_GEN_quality_rules.yaml` (coverage targets)

---

## Process

### Step 1: Unit Tests
For **every** generated code module and function:
- Generate unit tests covering normal cases
- Generate edge case tests
- Generate error/exception tests
- Mock external dependencies

**Coverage Targets:**
- Core modules: **100%** coverage
- Extension modules: **90%** coverage

### Step 2: Integration Tests
Generate basic integration tests for:
- API endpoints (request → response)
- Module interactions (Extension → Core)
- Database operations (if applicable)

---

## Test Structure

```python
# tests/test_auth.py
import pytest
from src.core.auth import hash_password, verify_password

def test_hash_password_creates_valid_hash():
    """Test that password hashing produces valid output"""
    password = "test_password_123"
    hashed = hash_password(password)

    assert hashed is not None
    assert len(hashed) > 0
    assert hashed != password  # Should be hashed, not plaintext

def test_verify_password_correct():
    """Test password verification with correct password"""
    password = "test_password_123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    """Test password verification with incorrect password"""
    hashed = hash_password("correct_password")

    assert verify_password("wrong_password", hashed) is False
```

---

## Output

Generated tests structure:

```json
{
  "test_files": [
    {
      "file_path": "tests/test_auth.py",
      "content": "...",
      "tested_module": "src/core/auth.py",
      "test_count": 12,
      "estimated_coverage": 100
    },
    {
      "file_path": "tests/test_user_service.py",
      "content": "...",
      "tested_module": "src/extensions/user_management/user_service.py",
      "test_count": 8,
      "estimated_coverage": 90
    }
  ],
  "integration_tests": [
    {
      "file_path": "tests/integration/test_auth_api.py",
      "content": "...",
      "endpoints_tested": ["/auth/login", "/auth/register"]
    }
  ]
}
```

---

## Success Criteria

- ✅ Every code module has corresponding tests
- ✅ Core modules have 100% coverage target
- ✅ Extension modules have 90% coverage target
- ✅ Integration tests cover all API endpoints
- ✅ Tests are runnable with pytest

---

## Validation Gates

- `gate_test_coverage_adequate.md` - Ensures coverage meets targets
