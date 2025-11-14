# Task 03: Library GitHub Metrics Collection (With Fallbacks)

**Task ID:** task_03_library_comparison
**Dependencies:** task_02_library_comparison
**Output:** library_github_metrics.json

---

## Objective

Enrich library comparison data with GitHub metrics (stars, last update, contributors). Implement **multi-level API fallbacks** to prevent rate-limiting failures.

---

## Context

This task MUST NOT crash when:
- GitHub API rate limit is hit (60 requests/hour unauthenticated)
- Network issues occur
- A repository has been deleted or moved

---

## Instructions

### Step 1: Prepare Library List
From task_02 output, extract all libraries with GitHub URLs.

### Step 2: Collect GitHub Metrics (3-level fallback strategy)

For **EACH library**, attempt to fetch GitHub metrics in this order:

#### 🟢 PRIMARY: GitHub REST API v3
```python
# Try this first (fastest, most detailed)
def get_github_metrics_api(github_url, github_token=None):
    """
    Fetch from: https://api.github.com/repos/{owner}/{repo}

    Returns:
    {
        "source": "github_api",
        "stars": 15000,
        "watchers": 500,
        "forks": 2000,
        "open_issues": 45,
        "last_updated": "2025-11-14T10:30:00Z",
        "language": "Python",
        "topics": ["testing", "framework"],
        "created_at": "2015-06-29T00:00:00Z"
    }

    Raises:
    - RateLimitError: If GitHub rate limit exceeded (HTTP 403)
    - RepositoryNotFoundError: If repo deleted (HTTP 404)
    - NetworkError: If connection fails
    """
```

**When to use:** Standard library research
**Rate limit:** 60/hour unauthenticated, 5000/hour with auth token
**When it fails:** Log warning and proceed to FALLBACK 1

---

#### 🟡 FALLBACK 1: npm Registry (for JavaScript libraries)
```python
def get_library_info_npm(package_name):
    """
    Fallback to npm registry when GitHub API fails.
    Fetch from: https://registry.npmjs.org/{package}

    Returns (subset of GitHub metrics):
    {
        "source": "npm_registry",
        "package_name": package_name,
        "downloads_weekly": 500000,
        "last_published": "2025-11-10T15:22:30Z",
        "maintainers": ["user1", "user2"],
        "keywords": ["react", "ui-framework"],
        "note": "GitHub metrics unavailable - using npm data as proxy"
    }

    Advantages:
    - FREE and unlimited requests
    - No authentication needed
    - Reliable uptime

    When to use:
    - After GitHub API rate limit failure
    - For any JavaScript/TypeScript library
    """
```

**When to use:** After GitHub API fails
**Rate limit:** Unlimited (free service)
**When it fails:** Log warning and proceed to FALLBACK 2

---

#### 🔴 FALLBACK 2: Manual Check Placeholder
```python
def get_library_info_manual(library_name, github_url):
    """
    Final fallback when all APIs fail.
    Returns a placeholder requiring manual verification.

    Returns:
    {
        "source": "manual_check_required",
        "library_name": library_name,
        "github_url": github_url,
        "stars": "UNKNOWN",
        "last_updated": "UNKNOWN",
        "status": "API_UNAVAILABLE",
        "action_required": "Manual verification needed - API unavailable",
        "how_to_verify": [
            "Visit: " + github_url,
            "Check: Repository active? (commits in last 90 days)",
            "Check: Maintenance status (releases, issue resolution)",
            "Record findings in library_github_metrics.json"
        ]
    }

    When to use:
    - Both GitHub API AND npm registry have failed
    - Network connectivity issues
    - As last resort only
    """
```

**When to use:** When both primary and fallback 1 fail
**Rate limit:** N/A (no API call)
**Result:** Non-blocking - returns with "manual verification required" flag

---

### Step 3: Error Handling & Logging

For EACH attempt, log at appropriate level:

```
✅ SUCCESS: Fetched metrics for react (GitHub API) - 220K stars
⚠️  WARNING: GitHub rate limit reached. Switching to npm registry for axios
❌ ERROR: Both GitHub API and npm registry failed for lodash. Manual check required.
```

**Never crash or fail the entire task.** Always provide SOME data, even if incomplete.

---

### Step 4: Implement Retry Logic

```python
def get_library_info_with_fallback(library_name, github_url, github_token=None):
    """
    Multi-level fallback with exponential backoff for transient errors.
    """

    try:
        # PRIMARY: GitHub API
        result = get_github_metrics_api(github_url, github_token)
        log(f"✅ GitHub API succeeded for {library_name}")
        return {**result, "reliability": "high", "source": "github_api"}

    except RateLimitError as e:
        log.warning(f"⚠️  GitHub rate limit hit. Using npm registry for {library_name}")
        try:
            # FALLBACK 1: npm
            result = get_library_info_npm(library_name)
            return {**result, "reliability": "medium", "source": "npm_registry"}

        except Exception as e:
            log.warning(f"⚠️  npm registry failed for {library_name}. Using manual placeholder.")
            # FALLBACK 2: Manual
            return {
                **get_library_info_manual(library_name, github_url),
                "reliability": "low",
                "fallback_reason": str(e)
            }

    except RepositoryNotFoundError:
        log.error(f"❌ Repository not found: {github_url}. Manual check required.")
        return {
            **get_library_info_manual(library_name, github_url),
            "reliability": "low",
            "error": "repository_not_found"
        }

    except NetworkError as e:
        log.warning(f"⚠️  Network error for {library_name}. Retrying with exponential backoff...")
        # Implement retry with 2s, 4s, 8s delays
        for attempt in [2, 4, 8]:
            time.sleep(attempt)
            try:
                return get_library_info_with_fallback(library_name, github_url, github_token)
            except Exception:
                continue

        # All retries failed
        return {
            **get_library_info_manual(library_name, github_url),
            "reliability": "low",
            "error": "network_unavailable_after_retries"
        }
```

---

## Output Format

Generate `library_github_metrics.json`:

```json
{
  "metadata": {
    "generated_at": "2025-11-14T15:30:00Z",
    "total_libraries": 15,
    "successful_api_calls": 12,
    "fallback_1_used": 2,
    "fallback_2_used": 1,
    "failure_rate": "6.7%"
  },
  "libraries": [
    {
      "name": "React",
      "github_url": "https://github.com/facebook/react",
      "metrics": {
        "source": "github_api",
        "reliability": "high",
        "stars": 220000,
        "watchers": 8000,
        "forks": 45000,
        "open_issues": 250,
        "last_updated": "2025-11-14T10:30:00Z",
        "language": "JavaScript",
        "topics": ["react", "javascript", "ui-framework"],
        "created_at": "2013-05-29T00:00:00Z",
        "is_archived": false,
        "contributors_count": 1500
      }
    },
    {
      "name": "axios",
      "github_url": "https://github.com/axios/axios",
      "metrics": {
        "source": "npm_registry",
        "reliability": "medium",
        "fallback_reason": "GitHub rate limit exceeded",
        "package_name": "axios",
        "downloads_weekly": 50000000,
        "last_published": "2025-11-10T15:22:30Z",
        "maintainers": ["jasonslyvia", "jakeonrails"],
        "note": "GitHub metrics from npm registry (used as fallback)"
      }
    },
    {
      "name": "lodash",
      "github_url": "https://github.com/lodash/lodash",
      "metrics": {
        "source": "manual_check_required",
        "reliability": "low",
        "error": "both_apis_failed",
        "fallback_reason": "Both GitHub API and npm registry unavailable",
        "status": "MANUAL_VERIFICATION_REQUIRED",
        "action_required": "Manual verification needed",
        "how_to_verify": [
          "Visit: https://github.com/lodash/lodash",
          "Check recent commits and releases",
          "Verify maintenance status",
          "Record findings manually"
        ]
      }
    }
  ]
}
```

---

## Quality Checklist

Before completing this task, verify:
- [ ] All libraries from task_02 have been processed
- [ ] No task crashes occurred (even with API failures)
- [ ] At least 80% success rate on GitHub API calls
- [ ] All failures logged with clear reasons
- [ ] Fallback metrics are present for failed requests
- [ ] Output JSON is valid and complete
- [ ] Manual check placeholders are actionable (include GitHub URL)

---

## Success Criteria

✅ Task completes even if GitHub API rate limit is hit
✅ npm registry data is used as fallback for JavaScript libraries
✅ Manual check placeholders guide users when APIs fail
✅ All libraries have SOME data in output (no empty entries)
✅ Warnings are logged, no crashes
✅ Metadata shows fallback usage rate

---

## Common Pitfalls

❌ **Crash on rate limit:** Task fails entirely when GitHub API hits limit
✅ **Solution:** Use fallback strategy above

❌ **Ignore deleted repositories:** Crash when repo returns 404
✅ **Solution:** Return manual check placeholder instead

❌ **No logging:** Silent failures make debugging impossible
✅ **Solution:** Log every API attempt (success, failure, fallback trigger)

❌ **Dead fallback data:** Return npm metrics that don't match GitHub metrics
✅ **Solution:** Clearly label source and reliability for each metric

---

## Next Task

Once complete, proceed to **Task 04: Stack Recommendation** with enriched library data.
