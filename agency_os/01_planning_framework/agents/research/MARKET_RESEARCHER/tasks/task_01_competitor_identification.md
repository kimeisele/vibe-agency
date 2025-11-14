# Task 01: Competitor Identification

**Task ID:** task_01_competitor_identification
**Dependencies:** None (first task)
**Output:** competitor_list.json

---

## Objective

Identify and research 3-5 major competitors in the target market. Include both **direct competitors** (same solution approach) and **indirect competitors** (alternative solutions to the same problem).

---

## Instructions

### Step 1: Analyze User Vision
Review the user's project vision to understand:
- What problem are they solving?
- Who is the target audience?
- What type of solution are they building? (web app, mobile app, SaaS, etc.)

### Step 2: Search for Competitors (2-Level Fallback Strategy)

Implement **multi-level search with fallbacks** to prevent quota failures:

#### 🟢 PRIMARY: Google Custom Search API
```python
# Try this first (best quality, full coverage)
def search_competitors_google(query, api_key, search_engine_id):
    """
    Primary search method using Google Custom Search.

    Rate limit: 100 searches/day (free tier)

    Returns:
    [
        {
            "title": "Asana - Work Management Platform",
            "link": "https://asana.com",
            "snippet": "Organize and execute work with your team...",
            "source": "google_custom_search"
        }
    ]

    Raises:
    - QuotaExceededError: When daily quota exceeded (100/day)
    - AuthenticationError: Invalid API key
    - NetworkError: Connection issues
    """
```

**When to use:** Standard competitor research
**Rate limit:** 100 searches/day (free tier)
**Cost:** Free ($25 per 1000 queries after free tier)
**When it fails:** Log warning and proceed to FALLBACK 1

#### 🟡 FALLBACK 1: DuckDuckGo (Free, Unlimited)
```python
def search_competitors_duckduckgo(query):
    """
    Fallback to DuckDuckGo when Google quota exceeded.

    Requires: pip install duckduckgo-search

    Returns (same format as Google):
    [
        {
            "title": "Asana - Work Management Platform",
            "link": "https://asana.com",
            "snippet": "Organize and execute work with your team...",
            "source": "duckduckgo"
        }
    ]

    Advantages:
    - FREE and UNLIMITED requests
    - No API key required
    - No quota limits
    - Good coverage of web results

    Disadvantages:
    - Slightly different ranking than Google
    - May include some less relevant results

    When to use:
    - After Google Custom Search quota exceeded
    - As primary method if no API key available
    """
```

**When to use:** After Google Search quota exceeded (100/day)
**Rate limit:** Unlimited (free service, respect robots.txt)
**Cost:** Free
**When it fails:** Log warning and proceed to FALLBACK 2

#### 🔴 FALLBACK 2: Manual Search Guidance
```python
def search_competitors_manual(query):
    """
    Final fallback when both APIs fail.
    Provide actionable guidance for manual search.

    Returns:
    {
        "competitors": [],
        "search_status": "MANUAL_SEARCH_REQUIRED",
        "manual_search_instructions": [
            "Search on Google: '" + query + "'",
            "Search on DuckDuckGo: '" + query + "'",
            "Visit competitor websites directly",
            "Record findings in the competitor_list.json file"
        ],
        "suggested_keywords": [
            query,
            query + " alternative",
            query + " competitor",
            query + " similar tools"
        ]
    }

    When to use:
    - Both Google Custom Search AND DuckDuckGo have failed
    - Network connectivity issues
    - As absolute last resort only
    """
```

**When to use:** When both primary and fallback 1 fail
**Rate limit:** N/A (no API call)
**Result:** Non-blocking - returns with "manual search required" flag

### Step 3: Implement Multi-Level Search with Fallback

```python
def search_with_fallback(query, google_api_key=None, search_engine_id=None, cache=None):
    """
    Multi-level search with automatic fallback strategy.

    Returns consistent format regardless of source.
    """

    try:
        # PRIMARY: Google Custom Search
        if google_api_key and search_engine_id:
            log("🟢 Attempting Google Custom Search...")
            results = search_competitors_google(query, google_api_key, search_engine_id)
            log(f"✅ Google search succeeded. Found {len(results)} results.")
            return {
                "results": results,
                "source": "google_custom_search",
                "reliability": "high",
                "cached": False
            }
        else:
            log("ℹ️  Google API credentials not configured. Using DuckDuckGo...")
            raise ValueError("No Google credentials")

    except QuotaExceededError:
        log("⚠️  Google Custom Search quota exceeded (100/day limit reached)")
        log("🟡 Attempting DuckDuckGo fallback...")
        try:
            results = search_competitors_duckduckgo(query)
            log(f"✅ DuckDuckGo search succeeded. Found {len(results)} results.")
            return {
                "results": results,
                "source": "duckduckgo",
                "reliability": "medium",
                "fallback_reason": "Google quota exceeded",
                "cached": False
            }
        except Exception as e:
            log(f"⚠️  DuckDuckGo search failed: {str(e)}")
            log("🔴 Using manual search guidance as final fallback...")
            return {
                "results": [],
                "source": "manual_search_required",
                "reliability": "low",
                "fallback_reason": f"Both APIs failed: {str(e)}",
                "manual_instructions": search_competitors_manual(query),
                "cached": False
            }

    except Exception as e:
        log(f"⚠️  Primary search failed: {str(e)}")
        log("🟡 Attempting DuckDuckGo fallback...")
        try:
            results = search_competitors_duckduckgo(query)
            log(f"✅ DuckDuckGo search succeeded. Found {len(results)} results.")
            return {
                "results": results,
                "source": "duckduckgo",
                "reliability": "medium",
                "fallback_reason": str(e),
                "cached": False
            }
        except Exception as e:
            log(f"⚠️  DuckDuckGo search also failed: {str(e)}")
            log("🔴 Using manual search guidance as final fallback...")
            return {
                "results": [],
                "source": "manual_search_required",
                "reliability": "low",
                "fallback_reason": f"Both APIs failed: {str(e)}",
                "manual_instructions": search_competitors_manual(query),
                "cached": False
            }

# CACHE RESULTS TO REDUCE API CALLS
# Store successful search results for 7 days to minimize API usage
def get_competitors_with_cache(query, google_api_key=None, search_engine_id=None):
    cache_key = hash(query)
    cached = check_cache(cache_key)

    if cached and not cache_expired(cached):
        log(f"✅ Using cached results for: {query}")
        return {**cached["data"], "cached": True}

    # Cache miss or expired
    results = search_with_fallback(query, google_api_key, search_engine_id)

    # Store in cache
    save_to_cache(cache_key, results)

    return results
```

### Step 4: Identify Competitor Categories

Research competitors in these categories:

1. **Direct Competitors:** Companies offering very similar solutions
   - Example: If building a project management tool, look for other project management SaaS

2. **Indirect Competitors:** Companies solving the same problem differently
   - Example: For project management, might include spreadsheets, email-based workflows, or all-in-one productivity suites

3. **Aspirational Competitors:** Larger players the product might compete with eventually
   - Example: Microsoft Project, Jira, Monday.com

### Step 5: Research Each Competitor

For each competitor, gather:
- **Name:** Official company name
- **Positioning:** How do they describe themselves? (from their homepage or About page)
- **Pricing:** Pricing model overview (detailed pricing comes in Task 2)
- **Source:** URL to their main website or product page

### Step 6: Verify Sources

Every competitor must have:
- A working URL (test the link)
- An official source (company website, not blog posts or reviews)
- Recent information (check if company is still active)

---

## Output Format

Generate `competitor_list.json`:

```json
{
  "search_metadata": {
    "query": "project management software alternatives",
    "search_source": "google_custom_search",
    "reliability": "high",
    "fallback_reason": null,
    "cached": false,
    "search_date": "2025-11-14T15:30:00Z"
  },
  "competitors": [
    {
      "name": "Asana",
      "category": "direct",
      "positioning": "Work management platform for teams to organize and execute work",
      "pricing_model": "freemium",
      "target_market": "smb",
      "source": "https://asana.com",
      "verified": true,
      "last_verified": "2025-11-14"
    },
    {
      "name": "Monday.com",
      "category": "direct",
      "positioning": "Work OS that powers teams to run projects and workflows",
      "pricing_model": "subscription",
      "target_market": "all",
      "source": "https://monday.com",
      "verified": true,
      "last_verified": "2025-11-14"
    },
    {
      "name": "Notion",
      "category": "indirect",
      "positioning": "All-in-one workspace for notes, docs, wikis, and project management",
      "pricing_model": "freemium",
      "target_market": "all",
      "source": "https://notion.so",
      "verified": true,
      "last_verified": "2025-11-14"
    }
  ],
  "research_notes": {
    "market_category": "Project Management & Collaboration Software",
    "search_keywords_used": ["project management software", "team collaboration tools", "work management platform"],
    "competitors_found": 3,
    "search_method": "Google Custom Search",
    "research_date": "2025-11-14"
  }
}
```

**If fallback is used, output would include:**
```json
{
  "search_metadata": {
    "query": "project management software alternatives",
    "search_source": "duckduckgo",
    "reliability": "medium",
    "fallback_reason": "Google quota exceeded (100/day limit)",
    "cached": false,
    "search_date": "2025-11-14T15:30:00Z"
  },
  "competitors": [
    // ... competitors found via DuckDuckGo
  ]
}
```

**If all APIs fail, output would be:**
```json
{
  "search_metadata": {
    "query": "project management software alternatives",
    "search_source": "manual_search_required",
    "reliability": "low",
    "fallback_reason": "Both Google Custom Search and DuckDuckGo APIs failed",
    "cached": false,
    "search_date": "2025-11-14T15:30:00Z",
    "manual_search_instructions": [
      "Search on Google: 'project management software alternatives'",
      "Search on DuckDuckGo: 'project management software alternatives'",
      "Visit competitor websites directly",
      "Record findings in the competitor_list.json file"
    ]
  },
  "competitors": [],
  "note": "Manual competitor research required - please complete search and add findings"
}
```

---

## Quality Checklist

Before completing this task, verify:
- [ ] At least 3 competitors identified (5+ preferred)
- [ ] Mix of direct and indirect competitors included
- [ ] Every competitor has a valid source URL
- [ ] Positioning descriptions are based on official sources, not assumptions
- [ ] All URLs are tested and working
- [ ] No generic competitors listed without specific product names
- [ ] **NEW:** Search completed without crashing (even if API fails)
- [ ] **NEW:** Fallback mechanism logged (Google → DuckDuckGo → Manual)
- [ ] **NEW:** Search reliability and source documented in metadata
- [ ] **NEW:** If manual search required, actionable instructions provided

---

## Success Criteria

✅ Task completes even if Google Custom Search quota is exceeded
✅ DuckDuckGo search is used as fallback for unlimited searches
✅ Manual search guidance provided when both APIs fail
✅ At least 3-5 competitors identified from first attempt
✅ All search attempts logged with clear source attribution
✅ Output metadata shows which search method was used and why
✅ No crashes or unhandled errors
✅ Task is non-blocking (framework continues even if search fails)

---

## Common Pitfalls

❌ **Too narrow:** "There are no competitors" → There are ALWAYS alternatives
✅ **Solution:** Use fallback search (DuckDuckGo) if Google quota exceeded

❌ **Too broad:** Listing every project management tool ever created
✅ **Solution:** Focus on 3-5 most relevant competitors

❌ **No sources:** Competitor names without URLs
✅ **Solution:** Verify every URL before adding to list

❌ **Outdated info:** Listing defunct companies or abandoned products
✅ **Solution:** Check last updated date and verify company is still active

❌ **Generic descriptions:** "They make software" instead of specific positioning
✅ **Solution:** Copy positioning from official website/about page

❌ **Crashing on API failure:** Task fails when Google Custom Search quota exceeded
✅ **Solution:** Implement fallback to DuckDuckGo → Manual search guidance

❌ **No error logging:** Silent failures make debugging impossible
✅ **Solution:** Log every search attempt (source, result, fallback reason)

---

## Next Task

Once complete, proceed to **Task 02: Pricing Analysis** to gather detailed pricing data for these competitors.
