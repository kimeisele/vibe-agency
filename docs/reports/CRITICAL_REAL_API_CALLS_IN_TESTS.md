# CRITICAL: Real API Calls in Tests - Systemic Issue

**Date:** 2025-11-16
**Severity:** 🚨 **P0 - CRITICAL**
**Status:** ❌ **FAILING CI/CD**

---

## Executive Summary

**PROBLEM:** Tests are making REAL API calls to Google Search API and external websites, causing:
1. ❌ **CI/CD failures** (429 Rate Limit errors)
2. ❌ **Flaky tests** (network-dependent)
3. ❌ **API quota waste** (costs money)
4. ❌ **Slow tests** (network latency)

**ROOT CAUSE:** No mocking strategy - tests call real services directly

**IMPACT:** Every push to `claude/**` branches triggers CI/CD which hits Google API quota and fails

---

## Evidence

### Failing CI/CD Output
```
TEST 4: Testing Tool Executor
----------------------------------------------------------------------
✅ ToolExecutor initialized
   Testing web_fetch tool...
⚠️  Tool returned error (might be site-specific): None
✅ web_fetch tool is callable
   Testing google_search tool...
❌ google_search failed: Tool execution failed: Google Search API error:
   429 Client Error: Too Many Requests for url:
   https://www.googleapis.com/customsearch/v1?key=***&cx=***&q=test+query&num_results=2
Error: Process completed with exit code 1.
```

### Files Making Real API Calls

#### 1. `scripts/validate_research_tools.py`

**Line 93: Real Google Search API call**
```python
client = GoogleSearchClient()
results = client.search(query, num_results=3)  # ← REAL API CALL
```

**Line 136: Real HTTP request**
```python
client = WebFetchClient()
result = client.fetch("https://httpbin.org/html")  # ← REAL HTTP REQUEST
```

**Line 172: Real HTTP request**
```python
executor = ToolExecutor()
result = executor.execute_tool("web_fetch", {"url": "https://example.com"})  # ← REAL HTTP
```

**Line 183: Real Google Search API call (FAILS HERE)**
```python
result = executor.execute_tool("google_search", {
    "query": "test query",
    "num_results": 2
})  # ← REAL API CALL - HITS RATE LIMIT
```

#### 2. `tests/test_core_orchestrator_tools.py`

**Line 92: Real HTTP request**
```python
client = WebFetchClient()
result = client.fetch("https://news.ycombinator.com/")  # ← REAL HTTP REQUEST
```

#### 3. `.github/workflows/test-google-api.yml`

**Triggers on EVERY push:**
```yaml
on:
  push:
    branches:
      - claude/**      # ← Runs on every Claude Code branch
      - main
      - develop
```

**Runs real API calls:**
```yaml
- name: Run research tools validation
  env:
    GOOGLE_SEARCH_API_KEY: ${{ secrets.GOOGLE_SEARCH_API_KEY }}
    GOOGLE_SEARCH_ENGINE_ID: ${{ secrets.GOOGLE_SEARCH_ENGINE_ID }}
  run: |
    python scripts/validate_research_tools.py  # ← Makes 4+ real API calls
```

---

## Systemic Impact

### What Breaks

1. **CI/CD Pipeline**
   - Every push to `claude/**` triggers workflow
   - Hits Google API rate limit (100 requests/day free tier)
   - Tests fail with 429 errors
   - Blocks merges

2. **Development Velocity**
   - Developers can't push to feature branches
   - False negative test failures
   - Time wasted debugging network issues

3. **Cost**
   - Google API quota consumed
   - Potential overage charges if upgraded plan

4. **Test Reliability**
   - Network outages cause test failures
   - Latency makes tests slow
   - External site changes break tests

### Other Systemic Issues (Likely)

Based on this pattern, **check for**:
- [ ] Other tests making database calls
- [ ] Other tests making external API calls (Anthropic, etc.)
- [ ] Other tests requiring credentials/secrets
- [ ] Integration tests running in unit test suite

---

## Solution: Mocking Strategy

### Principle

**Tests should NEVER make real external calls unless:**
1. Explicitly marked as `@pytest.mark.integration`
2. Only run manually or in dedicated integration test workflow
3. Properly mocked for unit tests

### Fix Plan

#### Phase 1: Immediate Fix (Stop the bleeding)

**Option A: Disable failing workflow (quickest)**
```yaml
# .github/workflows/test-google-api.yml
on:
  workflow_dispatch:  # ← Only run manually
  # Remove: push triggers
```

**Option B: Mock the API calls**
```python
# scripts/validate_research_tools.py
import os
from unittest.mock import Mock, patch

# Mock Google Search API calls in tests
if os.getenv("CI"):  # In CI/CD, use mocks
    @patch('google_search_client.GoogleSearchClient.search')
    def test_with_mock(mock_search):
        mock_search.return_value = [
            {"title": "Test", "url": "http://test.com", "snippet": "Test snippet"}
        ]
        # ... rest of test
```

#### Phase 2: Proper Test Structure (sustainable)

**Create mock fixtures:**

```python
# tests/fixtures/mock_api_responses.py
"""Mock responses for all external API calls"""

MOCK_GOOGLE_SEARCH_RESULTS = [
    {
        "title": "Software Development Best Practices - Example",
        "url": "https://example.com/article",
        "snippet": "Test snippet about software development best practices..."
    }
]

MOCK_WEB_FETCH_RESULT = {
    "title": "Example Domain",
    "content": "<html><body>Example content</body></html>",
    "url": "https://example.com"
}
```

**Update tests to use mocks:**

```python
# tests/test_research_tools_mocked.py
import pytest
from unittest.mock import Mock, patch
from fixtures.mock_api_responses import MOCK_GOOGLE_SEARCH_RESULTS

@pytest.fixture
def mock_google_client():
    """Mock GoogleSearchClient"""
    with patch('google_search_client.GoogleSearchClient') as mock:
        mock.return_value.search.return_value = MOCK_GOOGLE_SEARCH_RESULTS
        yield mock

def test_google_search_with_mock(mock_google_client):
    """Test Google Search with mocked API"""
    from google_search_client import GoogleSearchClient

    client = GoogleSearchClient()
    results = client.search("test query", num_results=3)

    assert len(results) == 1
    assert results[0]['title'] == "Software Development Best Practices - Example"
    # ✅ No real API call made
```

**Separate integration tests:**

```python
# tests/integration/test_research_tools_real.py
import pytest
import os

@pytest.mark.integration  # ← Marked as integration test
@pytest.mark.skipif(
    not os.getenv("GOOGLE_SEARCH_API_KEY"),
    reason="Google API keys not configured"
)
def test_google_search_real_api():
    """Integration test with REAL Google API (manual only)"""
    # This test only runs when:
    # 1. Explicitly requested: pytest -m integration
    # 2. API keys are configured
    # 3. Not in standard test suite
    pass
```

**Update CI/CD workflow:**

```yaml
# .github/workflows/test.yml
- name: Run unit tests (with mocks)
  run: |
    pytest tests/ -v --ignore=tests/integration/

# .github/workflows/test-integration.yml (separate, manual trigger)
on:
  workflow_dispatch:  # Manual only

- name: Run integration tests (real APIs)
  env:
    GOOGLE_SEARCH_API_KEY: ${{ secrets.GOOGLE_SEARCH_API_KEY }}
  run: |
    pytest tests/integration/ -v -m integration
```

---

## Implementation Checklist

### Immediate (Stop CI/CD failures)

- [ ] **Option A:** Disable `test-google-api.yml` workflow (change to `workflow_dispatch`)
- [ ] **Option B:** Add `@pytest.mark.skipif` to skip Google API calls if keys missing
- [ ] Commit and push fix to stop failing builds

### Short-term (Proper mocking)

- [ ] Create `tests/fixtures/mock_api_responses.py`
- [ ] Mock Google Search API calls in `scripts/validate_research_tools.py`
- [ ] Mock HTTP requests in `tests/test_core_orchestrator_tools.py`
- [ ] Add `pytest-mock` to `requirements.txt` (if not present)
- [ ] Update tests to use fixtures

### Long-term (Systemic fix)

- [ ] Audit ALL tests for external calls (`grep -r "http\|API" tests/`)
- [ ] Create testing guidelines document (`docs/testing/MOCKING_STRATEGY.md`)
- [ ] Add pre-commit hook to detect real API calls in tests
- [ ] Separate unit tests from integration tests
- [ ] Create dedicated integration test workflow (manual trigger only)

---

## Success Criteria

**Tests pass when:**
- ✅ No real API calls in unit tests
- ✅ All external dependencies mocked
- ✅ Tests run offline (no network required)
- ✅ Tests run in <10 seconds (no network latency)
- ✅ CI/CD passes consistently (no flaky failures)

**Integration tests exist separately:**
- ✅ Marked with `@pytest.mark.integration`
- ✅ Only run manually or in dedicated workflow
- ✅ Clearly documented when/why to run them

---

## References

- **Failing test:** `scripts/validate_research_tools.py`
- **CI/CD workflow:** `.github/workflows/test-google-api.yml`
- **Related issue:** GAD-003 tool integration (tools exist but tests are broken)

---

## Next Steps

1. **URGENT:** Disable failing workflow or add mocking (today)
2. Create `docs/testing/MOCKING_STRATEGY.md` (this week)
3. Refactor all tests to use mocks (this week)
4. Add to Priority 1 in session handoff

**Estimated effort:** 4-6 hours
**Risk if not fixed:** CI/CD remains broken, blocks all development
