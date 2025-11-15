# Research Validation - Yoga Studio MVP Portfolio Test

This document provides comprehensive validation checklists and expected behavior for the research integration components of the portfolio test.

---

## Pre-Test Validation

### Dependency Check

Run these commands to verify all research dependencies are installed:

```bash
# Check beautifulsoup4 (web scraping)
python -c "import bs4; print('✅ beautifulsoup4 installed')" || echo "❌ Missing: pip install beautifulsoup4"

# Check google-api-python-client (Google Search API)
python -c "import googleapiclient; print('✅ google-api-python-client installed')" || echo "❌ Missing: pip install google-api-python-client"

# Check requests (HTTP client)
python -c "import requests; print('✅ requests installed')" || echo "❌ Missing: pip install requests"
```

**Expected output:**
```
✅ beautifulsoup4 installed
✅ google-api-python-client installed
✅ requests installed
```

### Google API Keys (Optional)

Check if Google API keys are configured:

```bash
# Check environment variables
echo "GOOGLE_SEARCH_API_KEY: ${GOOGLE_SEARCH_API_KEY:0:8}...${GOOGLE_SEARCH_API_KEY: -4}"
echo "GOOGLE_SEARCH_ENGINE_ID: $GOOGLE_SEARCH_ENGINE_ID"
```

**If NOT configured:**
- ✅ Test will use Claude Code WebSearch (fallback)
- ⚠️ Research phase may take longer (manual delegation)
- ✅ Test will still pass and complete successfully

**If configured:**
- ✅ Faster research (automated Google API calls)
- ✅ More comprehensive results
- ✅ Reduced Claude Code delegations

### Validation Script

Run the official validation script:

```bash
python scripts/validate_research_tools.py
```

**Expected checklist:**
- [ ] WebFetchClient initializes successfully
- [ ] ToolExecutor initializes successfully
- [ ] `web_fetch` tool is callable
- [ ] Google Search API works (if keys configured) OR fallback message shown
- [ ] Script exits with success code 0

---

## During-Test Validation

Monitor these behaviors while the test is running.

### PLANNING Phase → RESEARCH Transition

**When to observe:** After PLANNING phase completes (~30-45 minutes in)

**Expected log entries:**
```json
{
  "phase": "PLANNING",
  "sub_state": "ARCHITECTURE_DESIGN",
  "status": "complete"
}
{
  "transition": "PLANNING -> RESEARCH",
  "research_enabled": true,
  "agents_to_trigger": ["MARKET_RESEARCHER", "TECH_RESEARCHER", "USER_RESEARCHER", "FACT_VALIDATOR"]
}
```

**Validation:**
- [ ] `projectPhase` changes to "RESEARCH" in manifest
- [ ] Research agents listed in execution plan
- [ ] Research requirements loaded from manifest

### MARKET_RESEARCHER Agent

**Expected trigger:** First in research sequence

**Expected queries (from manifest):**
1. "yoga studio booking software market size 2024"
2. "yoga studio management software competitors"
3. "yoga studio owner pain points scheduling"
4. "fitness class booking trends 2024"

**Expected behavior:**

**With Google API:**
```
[MARKET_RESEARCHER] Executing query: "yoga studio booking software market size 2024"
[GoogleSearchClient] Calling Google Custom Search API...
[GoogleSearchClient] Got 10 results
[WebFetchClient] Fetching content from top 3 URLs...
[MARKET_RESEARCHER] Analyzing results...
```

**Without Google API (fallback):**
```
[MARKET_RESEARCHER] Google API not configured
[MARKET_RESEARCHER] Delegating to Claude Code WebSearch...
[Delegation] Please search for: "yoga studio booking software market size 2024"
[Claude Code] (operator provides results via WebSearch tool)
[MARKET_RESEARCHER] Processing delegated results...
```

**Validation:**
- [ ] Query executed (Google API or delegation)
- [ ] Results retrieved (5+ sources expected)
- [ ] Market insights extracted (market size, competitors, trends)
- [ ] Sources cited with URLs

### TECH_RESEARCHER Agent

**Expected trigger:** Second in research sequence

**Expected queries (from manifest):**
1. "best payment gateway for fitness subscriptions"
2. "class scheduling software architecture patterns"
3. "React booking system best practices"
4. "real-time availability sync patterns"

**Expected behavior:**
- [ ] Technical stack research (Stripe vs PayPal comparison)
- [ ] Architecture pattern recommendations
- [ ] Best practices for booking systems
- [ ] Real-time sync strategies

**Expected output format:**
```json
{
  "payment_gateway_recommendation": "Stripe",
  "reasoning": "Better recurring billing support, simpler API",
  "architecture_pattern": "Event-driven with CQRS",
  "sources": [
    {"url": "...", "title": "..."},
    {"url": "...", "title": "..."}
  ]
}
```

**Validation:**
- [ ] Tech stack recommendations provided
- [ ] Architecture patterns identified
- [ ] Best practices documented
- [ ] 5+ technical sources cited

### USER_RESEARCHER Agent

**Expected trigger:** Third in research sequence

**Expected queries (from manifest):**
1. "yoga student booking behavior patterns"
2. "yoga studio software user complaints"
3. "fitness class cancellation policies best practices"

**Expected behavior:**
- [ ] User behavior insights (booking preferences, pain points)
- [ ] Common complaints analysis
- [ ] Cancellation policy recommendations

**Expected output format:**
```json
{
  "booking_behavior": {
    "preferred_time": "Mobile booking 24/7",
    "booking_window": "Last-minute (< 24 hours)",
    "pain_points": ["Complex signup", "No reminder emails"]
  },
  "cancellation_insights": {
    "recommended_policy": "24-hour cancellation window",
    "reasoning": "Industry standard, reduces no-shows"
  },
  "sources": [...]
}
```

**Validation:**
- [ ] User insights extracted
- [ ] Pain points identified
- [ ] UX recommendations provided
- [ ] 3+ user research sources cited

### FACT_VALIDATOR Agent

**Expected trigger:** Fourth (final) in research sequence

**Expected behavior:**
- [ ] Cross-validate claims from MARKET/TECH/USER researchers
- [ ] Check for contradictions
- [ ] Verify source reliability
- [ ] Flag unverified claims

**Expected output format:**
```json
{
  "validated_facts": [
    {
      "claim": "Yoga studio market size is $10B in US",
      "status": "verified",
      "sources": 3,
      "confidence": "high"
    }
  ],
  "contradictions": [
    {
      "claim": "Stripe is the best payment gateway",
      "alternative": "PayPal also recommended by 2 sources",
      "resolution": "Both valid, Stripe preferred for subscriptions"
    }
  ],
  "unverified_claims": []
}
```

**Validation:**
- [ ] Facts cross-validated
- [ ] Contradictions identified and resolved
- [ ] Confidence levels assigned
- [ ] Unverified claims flagged for review

### Research Integration into Artifacts

**During CODING phase:** Research insights should be visible in artifacts

**In `feature_spec.json`:**
```json
{
  "features": [
    {
      "name": "Payment Processing",
      "tech_stack": "Stripe",
      "reasoning": "Based on tech research: better recurring billing support",
      "research_source": "TECH_RESEARCHER recommendation"
    }
  ],
  "market_context": {
    "market_size": "$10B (US yoga studio software market)",
    "source": "MARKET_RESEARCHER findings"
  }
}
```

**In `code_gen_spec.json`:**
```json
{
  "architecture": {
    "payment_integration": "Stripe",
    "rationale": "Research-backed: best for fitness subscriptions"
  },
  "ux_decisions": {
    "booking_flow": "One-click booking (mobile-first)",
    "rationale": "User research: 70% of bookings happen on mobile"
  }
}
```

**Validation:**
- [ ] Research insights cited in feature specs
- [ ] Technical decisions backed by research
- [ ] UX choices aligned with user research
- [ ] Market context incorporated into business model

---

## Post-Test Validation

After test completes, verify research integration was successful.

### Artifact Verification

```bash
# Check if research_summary.json was created
ls -la workspaces/yoga-studio-mvp-001/artifacts/research_summary.json

# View research summary
cat workspaces/yoga-studio-mvp-001/artifacts/research_summary.json | jq .
```

**Expected structure:**
```json
{
  "research_phase": "RESEARCH",
  "timestamp": "2025-11-15T...",
  "agents_executed": [
    "MARKET_RESEARCHER",
    "TECH_RESEARCHER",
    "USER_RESEARCHER",
    "FACT_VALIDATOR"
  ],
  "market_insights": {
    "market_size": "...",
    "competitors": [...],
    "trends": [...],
    "sources": [...]
  },
  "technical_insights": {
    "recommended_stack": {...},
    "architecture_patterns": [...],
    "sources": [...]
  },
  "user_insights": {
    "behavior_patterns": {...},
    "pain_points": [...],
    "sources": [...]
  },
  "fact_validation": {
    "verified_claims": [...],
    "contradictions": [...],
    "confidence_scores": {...}
  }
}
```

### Research Quality Checks

- [ ] **Market research:** At least 5 sources cited
- [ ] **Tech research:** At least 5 sources cited
- [ ] **User research:** At least 3 sources cited
- [ ] **Fact validation:** All major claims verified or flagged
- [ ] **Source quality:** Reputable sources (not just blogs)
- [ ] **Recency:** Most sources from 2023-2024
- [ ] **Relevance:** All sources relate to yoga/fitness industry

### Integration Checks

```bash
# Check if research insights are in feature_spec.json
cat workspaces/yoga-studio-mvp-001/artifacts/feature_spec.json | jq .market_context
cat workspaces/yoga-studio-mvp-001/artifacts/feature_spec.json | jq '.features[] | select(.research_source != null)'

# Check if research insights are in code_gen_spec.json
cat workspaces/yoga-studio-mvp-001/artifacts/code_gen_spec.json | jq .architecture.rationale
cat workspaces/yoga-studio-mvp-001/artifacts/code_gen_spec.json | jq .ux_decisions
```

**Validation:**
- [ ] Market insights visible in lean canvas
- [ ] Technical recommendations in code_gen_spec
- [ ] User insights in feature_spec UX requirements
- [ ] Research sources cited throughout artifacts

---

## Expected Research Agent Behavior

### MARKET_RESEARCHER

**Tool usage:**
- `google_search` (if API configured) or delegation to Claude Code
- `web_fetch` for content extraction
- BeautifulSoup for HTML parsing

**Deliverables:**
- Market size data ($XB in US, YB globally)
- Competitor analysis (Mindbody, Momoyoga, Pike13)
- Pricing trends ($50-150/month per studio)
- Growth projections

**Success criteria:**
- ✅ Market size quantified
- ✅ At least 3 competitors analyzed
- ✅ Pricing benchmarks provided
- ✅ 5+ reputable sources cited

### TECH_RESEARCHER

**Tool usage:**
- `google_search` or delegation
- `web_fetch` for documentation/tutorials
- Code repository analysis (GitHub search)

**Deliverables:**
- Payment gateway comparison (Stripe vs PayPal vs Square)
- Architecture pattern recommendations (Event-driven, CQRS, Microservices)
- Tech stack suggestions (React/Next.js, Django/Node.js, PostgreSQL)
- Best practices (caching, real-time sync, security)

**Success criteria:**
- ✅ Payment gateway recommended with reasoning
- ✅ Architecture pattern selected
- ✅ Tech stack justified
- ✅ 5+ technical sources cited

### USER_RESEARCHER

**Tool usage:**
- `google_search` or delegation
- `web_fetch` for forums, reviews, case studies
- Social media analysis (Reddit, Twitter)

**Deliverables:**
- Booking behavior patterns (mobile-first, last-minute booking)
- Pain points (complex signup, no reminders, inflexible cancellation)
- Feature requests (waitlists, recurring bookings, family accounts)
- Cancellation policy insights (24-hour window standard)

**Success criteria:**
- ✅ Booking behavior quantified
- ✅ Top 3 pain points identified
- ✅ Cancellation policy recommended
- ✅ 3+ user research sources cited

### FACT_VALIDATOR

**Tool usage:**
- Cross-reference checks across multiple sources
- Domain authority verification
- Date/recency checks
- Contradiction detection

**Deliverables:**
- Verified claims with confidence scores
- Contradictions identified and resolved
- Unverified claims flagged
- Source reliability assessment

**Success criteria:**
- ✅ All major claims verified or flagged
- ✅ Contradictions resolved
- ✅ Confidence levels assigned
- ✅ Source quality assessed

---

## Google API Configuration

### Setup Instructions

**Get API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "vibe-agency-research"
3. Enable Custom Search API
4. Create credentials: API Key
5. Copy API key

**Get Search Engine ID:**
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Create new search engine
3. Search the entire web: Yes
4. Copy Search Engine ID (cx parameter)

**Configure locally:**

**Option 1: .env file**
```bash
cat > .env <<EOF
GOOGLE_SEARCH_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_SEARCH_ENGINE_ID=abc123def456
EOF
```

**Option 2: Claude Code settings**
```bash
mkdir -p .claude
cat > .claude/settings.local.json <<EOF
{
  "environment": {
    "GOOGLE_SEARCH_API_KEY": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX",
    "GOOGLE_SEARCH_ENGINE_ID": "abc123def456"
  }
}
EOF
```

**Verify configuration:**
```bash
python scripts/validate_research_tools.py
```

**Expected output:**
```
✅ Google Search API keys found
   API Key: AIzaSyXX...XXXX
   Engine ID: abc123def456
✅ GoogleSearchClient initialized
✅ Got 3 results from Google Search API
```

---

## Fallback Behavior

### When Google API is NOT Available

**System behavior:**
1. Research agents detect missing API keys
2. Log warning: "Google API not configured, using Claude Code WebSearch"
3. Delegate search queries to Claude Code operator
4. Claude Code uses built-in WebSearch tool
5. Research continues without failure

**Example delegation:**
```
[vibe-cli] DELEGATION REQUEST:
Please search for: "yoga studio booking software market size 2024"

[Claude Code Operator] (uses WebSearch tool)
[WebSearch Result] Found 10 results...

[vibe-cli] Received research results from operator
[MARKET_RESEARCHER] Processing results...
```

**Performance impact:**
- ⏱️ Slightly slower (manual delegation overhead)
- 📊 Equally comprehensive (same quality results)
- ✅ Test still passes (no failures)

**Validation:**
- [ ] Warning logged: "using Claude Code WebSearch"
- [ ] Delegations visible in STDOUT
- [ ] Research results still collected
- [ ] Test completes successfully

---

## Troubleshooting

### Google API Errors

**"API key not valid"**
- Verify key copied correctly (no extra spaces)
- Check API is enabled in Google Cloud Console
- Verify billing is enabled on project

**"Quota exceeded"**
- Google API has daily quota limits
- Fallback to Claude Code WebSearch automatically
- Test continues without failure

**"Search engine not found"**
- Verify Search Engine ID is correct
- Ensure search engine is set to "Search the entire web"

### Web Fetch Errors

**"URL blocked by robots.txt"**
- Expected behavior for some sites
- BeautifulSoup respects robots.txt
- Fallback to other sources

**"Connection timeout"**
- Network issue or site blocking bots
- Retry with different source
- Not a test failure

### Research Results Empty

**Symptoms:**
- research_summary.json is empty or minimal
- No sources cited

**Solutions:**
1. Check if research phase actually ran (phase transition logs)
2. Verify research requirements in manifest
3. Check delegation responses from Claude Code
4. Review logs for agent execution errors

---

## Success Criteria

After test completes, research integration is successful if:

- ✅ `research_summary.json` created with complete data
- ✅ Market research: 5+ sources, market size quantified
- ✅ Tech research: 5+ sources, stack recommended
- ✅ User research: 3+ sources, pain points identified
- ✅ Fact validation: Major claims verified
- ✅ Research insights integrated into feature_spec.json
- ✅ Research insights integrated into code_gen_spec.json
- ✅ All research sources cited with URLs
- ✅ Test completed without research-related failures

---

## Related Documentation

- [TEST_EXECUTION_GUIDE.md](./TEST_EXECUTION_GUIDE.md) - Full execution guide
- [EXPECTED_ARTIFACTS.md](./EXPECTED_ARTIFACTS.md) - Artifact specifications
- [scripts/validate_research_tools.py](../../scripts/validate_research_tools.py) - Validation script
