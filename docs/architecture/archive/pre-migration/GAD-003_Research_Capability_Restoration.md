# GAD-003: Research Capability Restoration

**Status:** APPROVED (by user)
**Date:** 2025-11-14
**Author:** System Architect (Claude Sonnet 4.5)
**Supersedes:** GAD-001 (partially - research component only)
**Related:** ADR-003 (Brain-Arm Architecture)

---

## EXECUTIVE SUMMARY

**Decision:** RESTORE active research capabilities to all research agents by implementing tool integrations (Option A).

**Impact:** Transforms research agents from passive validators → active intelligence gatherers

**Timeline:** 2-3 days (18 hours development + testing)

**Cost:** $0 (uses free tiers: Google Search, Crunchbase, ProductHunt)

**Risk:** LOW (backward compatible, incremental rollout possible)

---

## 1. CONTEXT: The Regression

### 1.1 What Happened?

**Original Vision (GAD-001, README):**
- Research agents actively query external APIs
- Real-time market intelligence
- Competitor analysis via live data
- Tech stack validation against current trends

**Current Reality (Audit findings):**
- Research agents are **passive validators**
- Only read static YAML files
- Prompts reference tools they don't have
- **Tool-Prompt Mismatch:** Agents told to "use Google Search" but have NO tools defined

### 1.2 The Smoking Gun

**File:** `agency_os/01_planning_framework/agents/research/MARKET_RESEARCHER/_prompt_core.md`

```markdown
### 🆓 FREE Data Sources First (IMPORTANT!)
**ALWAYS prefer FREE sources over paid subscriptions:**
- ✅ Google Search (100 searches/day free)
- ✅ Crunchbase free tier
- ✅ ProductHunt, Y Combinator directory
```

**File:** `agency_os/01_planning_framework/agents/research/MARKET_RESEARCHER/_composition.yaml`

```yaml
metadata:
  agent_name: MARKET_RESEARCHER
  tools: []  # ❌ EMPTY!
```

**Conclusion:** Prompts promise capabilities the system cannot deliver.

### 1.3 Root Cause Hypothesis

**False Blocker Assumption:**
> "GitHub Actions cannot access API keys from third-party services"

**Reality:** GitHub Actions Secrets exist precisely for this use case.

**Result:** Feature was downgraded from "active research" → "passive validation" based on false constraint.

---

## 2. DECISION: Restore Active Research (Option A)

### 2.1 Why Option A Over Option B?

| Criterion | Option A (Restore) | Option B (Accept) |
|-----------|-------------------|-------------------|
| **Aligns with vision?** | ✅ YES (original GAD-001) | ❌ NO (regression) |
| **Technically feasible?** | ✅ YES (GitHub Secrets work) | ✅ YES (just rename) |
| **Effort** | 18 hours (2-3 days) | 8 hours (1 day) |
| **Value delivered** | 🔥 HIGH (real intelligence) | 🥶 LOW (status quo) |
| **Risk** | 🟢 LOW (incremental) | 🟡 MEDIUM (misleading docs) |
| **Cost** | $0 (free tiers) | $0 |

**Decision Rationale:**
- 10 extra hours of work → transforms system from "document processor" → "intelligence engine"
- Original vision was correct, blocker was false
- Free tiers sufficient for MVP (Google: 100 searches/day, Crunchbase: basic tier)

---

## 3. SCOPE: What Gets Restored?

### 3.1 Agents Impacted

| Agent | Current State | Target State | Tools Needed |
|-------|---------------|--------------|--------------|
| **MARKET_RESEARCHER** | Passive validator | Active researcher | `google_search`, `crunchbase_lookup` |
| **TECH_RESEARCHER** | Passive validator | Active researcher | `google_search`, `github_trending` |
| **FACT_VALIDATOR** | Passive validator | Active fact-checker | `google_search`, `web_fetch` |

### 3.2 Tools to Implement

#### Tool #1: `google_search` (CRITICAL PATH)
- **API:** Google Custom Search JSON API
- **Free Tier:** 100 queries/day
- **Setup Time:** 30 min (API key + CSE ID)
- **Implementation:** `agency_os/core_system/orchestrator/tools/google_search_client.py`

#### Tool #2: `web_fetch` (CRITICAL PATH)
- **API:** Built-in (Python `requests`)
- **Free Tier:** Unlimited (respect robots.txt)
- **Setup Time:** 15 min
- **Implementation:** `agency_os/core_system/orchestrator/tools/web_fetch_client.py`

#### Tool #3: `crunchbase_lookup` (OPTIONAL - Post-MVP)
- **API:** Crunchbase Basic Tier
- **Free Tier:** 200 calls/month
- **Setup Time:** 1 hour
- **Implementation:** Defer to post-MVP

#### Tool #4: `github_trending` (OPTIONAL - Post-MVP)
- **API:** GitHub REST API (public data)
- **Free Tier:** 60 calls/hour (unauthenticated)
- **Setup Time:** 30 min
- **Implementation:** Defer to post-MVP

**MVP Scope (Phase 1):** Tools #1 + #2 only (google_search + web_fetch)

---

## 4. ARCHITECTURE: How It Works

### 4.1 Tool Integration Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ MARKET_RESEARCHER Agent                                      │
│                                                               │
│  Prompt: "Search for competitors in [market]"                │
│  Tools: [google_search, web_fetch]                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Core Orchestrator (execute_agent)                            │
│                                                               │
│  1. Load _composition.yaml (includes tools)                  │
│  2. Pass tools + API keys to PromptRuntime                   │
│  3. Compose prompt with tool instructions                    │
│  4. Send INTELLIGENCE_REQUEST (delegated mode)               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Claude Code (Brain)                                           │
│                                                               │
│  1. Receives prompt + tool definitions                        │
│  2. Decides: "I need to search for X"                         │
│  3. Returns: <tool_use name="google_search">                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Tool Executor (NEW)                                           │
│                                                               │
│  1. Parse <tool_use> from STDIN                               │
│  2. Call google_search_client.py with params                  │
│  3. Return <tool_result> to STDOUT                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Claude Code (Brain, again)                                    │
│                                                               │
│  1. Receives tool results                                     │
│  2. Synthesizes findings                                      │
│  3. Returns: INTELLIGENCE_RESPONSE                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Core Orchestrator (execute_agent, continued)                 │
│                                                               │
│  1. Receives response via STDIN                               │
│  2. Validates artifacts                                       │
│  3. Updates project state                                     │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 New Components

**Component #1: Tool Executor Wrapper**
- **File:** `agency_os/core_system/orchestrator/tools/tool_executor.py`
- **Purpose:** Parse `<tool_use>` from STDIN, dispatch to tool clients, return `<tool_result>`
- **Lines of Code:** ~150

**Component #2: Google Search Client**
- **File:** `agency_os/core_system/orchestrator/tools/google_search_client.py`
- **Purpose:** Wrapper around Google Custom Search API
- **Lines of Code:** ~80

**Component #3: Web Fetch Client**
- **File:** `agency_os/core_system/orchestrator/tools/web_fetch_client.py`
- **Purpose:** Safe HTTP GET with robots.txt respect
- **Lines of Code:** ~60

**Component #4: Tool Definitions Schema**
- **File:** `agency_os/core_system/orchestrator/tools/tool_definitions.yaml`
- **Purpose:** Canonical tool definitions (name, description, parameters)
- **Lines of Code:** ~100 (YAML)

---

## 5. IMPLEMENTATION PLAN

### Phase 1: Foundation (Day 1 - 6 hours)

#### Step 1.1: GitHub Secrets Setup (30 min)
```bash
# On GitHub.com:
# 1. Go to: Settings → Secrets and variables → Actions
# 2. Click "New repository secret"
# 3. Add:
GOOGLE_SEARCH_API_KEY=<your-key>
GOOGLE_SEARCH_ENGINE_ID=a4daf97169d994fc9

# 4. Test access:
# .github/workflows/test-secrets.yml
jobs:
  test:
    env:
      GOOGLE_SEARCH_API_KEY: ${{ secrets.GOOGLE_SEARCH_API_KEY }}
    run: |
      echo "API_KEY length: ${#GOOGLE_SEARCH_API_KEY}"  # Should output ~39
```

#### Step 1.2: Tool Definitions Schema (1 hour)
**File:** `agency_os/core_system/orchestrator/tools/tool_definitions.yaml`

```yaml
tools:
  google_search:
    name: google_search
    description: "Search Google using Custom Search API. Returns top 10 results with titles, snippets, URLs."
    parameters:
      query:
        type: string
        required: true
        description: "Search query (e.g., 'AI startups 2024')"
      num_results:
        type: integer
        required: false
        default: 10
        description: "Number of results (1-10)"
    returns:
      type: array
      description: "List of search results"
      schema:
        - title: string
          snippet: string
          url: string

  web_fetch:
    name: web_fetch
    description: "Fetch and extract text content from a URL. Respects robots.txt."
    parameters:
      url:
        type: string
        required: true
        description: "Full URL to fetch (e.g., 'https://example.com/article')"
    returns:
      type: object
      schema:
        url: string
        title: string
        content: string  # Cleaned text content
        error: string | null
```

#### Step 1.3: Google Search Client (2 hours)
**File:** `agency_os/core_system/orchestrator/tools/google_search_client.py`

```python
import os
import requests
from typing import List, Dict, Optional

class GoogleSearchClient:
    """Wrapper for Google Custom Search JSON API"""

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

        if not self.api_key or not self.search_engine_id:
            raise ValueError("Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_ENGINE_ID")

        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Execute Google search

        Args:
            query: Search query string
            num_results: Number of results (1-10)

        Returns:
            List of dicts: [{"title": ..., "snippet": ..., "url": ...}, ...]
        """
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(num_results, 10)  # API max is 10
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse results
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', '')
                })

            return results

        except requests.RequestException as e:
            raise RuntimeError(f"Google Search API error: {e}")

# CLI test
if __name__ == "__main__":
    client = GoogleSearchClient()
    results = client.search("AI coding assistants 2024", num_results=5)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")
        print()
```

**Test:**
```bash
export GOOGLE_SEARCH_API_KEY=<your-key>
export GOOGLE_SEARCH_ENGINE_ID=a4daf97169d994fc9
python agency_os/core_system/orchestrator/tools/google_search_client.py
```

#### Step 1.4: Web Fetch Client (1.5 hours)
**File:** `agency_os/core_system/orchestrator/tools/web_fetch_client.py`

```python
import requests
from bs4 import BeautifulSoup
from typing import Dict

class WebFetchClient:
    """Safe web content fetcher with robots.txt respect"""

    def fetch(self, url: str) -> Dict:
        """
        Fetch and extract text content from URL

        Args:
            url: Full URL to fetch

        Returns:
            Dict: {"url": ..., "title": ..., "content": ..., "error": None}
        """
        try:
            # Fetch
            headers = {'User-Agent': 'VIBE-Agency-Research-Bot/1.0'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            # Parse
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else "Untitled"

            # Extract main content (heuristic: remove script/style tags)
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()

            content = soup.get_text(separator='\n', strip=True)

            # Truncate to 10k chars (prevent context overflow)
            content = content[:10000]

            return {
                'url': url,
                'title': title_text,
                'content': content,
                'error': None
            }

        except Exception as e:
            return {
                'url': url,
                'title': None,
                'content': None,
                'error': str(e)
            }

# CLI test
if __name__ == "__main__":
    client = WebFetchClient()
    result = client.fetch("https://news.ycombinator.com/")
    print(f"Title: {result['title']}")
    print(f"Content preview: {result['content'][:200]}...")
```

**Test:**
```bash
python agency_os/core_system/orchestrator/tools/web_fetch_client.py
```

#### Step 1.5: Tool Executor Dispatcher (1 hour)
**File:** `agency_os/core_system/orchestrator/tools/tool_executor.py`

```python
import json
from typing import Dict, Any
from .google_search_client import GoogleSearchClient
from .web_fetch_client import WebFetchClient

class ToolExecutor:
    """Executes tool calls from Claude Code"""

    def __init__(self):
        self.tools = {
            'google_search': GoogleSearchClient(),
            'web_fetch': WebFetchClient()
        }

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict:
        """
        Execute a tool call

        Args:
            tool_name: Name of tool (e.g., 'google_search')
            parameters: Tool parameters dict

        Returns:
            Tool result dict (serializable to JSON)
        """
        if tool_name not in self.tools:
            return {'error': f"Unknown tool: {tool_name}"}

        try:
            if tool_name == 'google_search':
                query = parameters.get('query')
                num_results = parameters.get('num_results', 10)
                return {'results': self.tools['google_search'].search(query, num_results)}

            elif tool_name == 'web_fetch':
                url = parameters.get('url')
                return self.tools['web_fetch'].fetch(url)

        except Exception as e:
            return {'error': f"Tool execution failed: {e}"}
```

---

### Phase 2: Integration (Day 2 - 8 hours)

#### Step 2.1: Update Agent Compositions (2 hours)

**File:** `agency_os/01_planning_framework/agents/research/MARKET_RESEARCHER/_composition.yaml`

```yaml
metadata:
  agent_name: MARKET_RESEARCHER
  version: "2.0"
  tools:  # ✅ ADD THIS
    - google_search
    - web_fetch

composition:
  sections:
    - name: core_personality
      source: _prompt_core.md
    - name: task_instructions
      source: tasks/{task_id}.md
    - name: tool_definitions  # ✅ ADD THIS
      source: ../../00_system/orchestrator/tools/tool_definitions.yaml
      filter: [google_search, web_fetch]  # Only include these tools
```

**Repeat for:**
- `TECH_RESEARCHER/_composition.yaml`
- `FACT_VALIDATOR/_composition.yaml`

#### Step 2.2: Update PromptRuntime (3 hours)

**File:** `agency_os/core_system/orchestrator/prompt_runtime.py`

**Change #1: Load tool definitions**
```python
def _load_composition_spec(self, agent_name: str) -> dict:
    # ... existing code ...

    # NEW: Load tool definitions if referenced
    if 'tool_definitions' in spec.get('composition', {}).get('sections', []):
        tool_defs_path = self._resolve_path(spec['tool_definitions']['source'])
        with open(tool_defs_path) as f:
            all_tools = yaml.safe_load(f)

        # Filter to only requested tools
        requested_tools = spec['tool_definitions'].get('filter', [])
        spec['_resolved_tools'] = {
            name: tool for name, tool in all_tools['tools'].items()
            if name in requested_tools
        }

    return spec
```

**Change #2: Include tools in prompt**
```python
def compose_prompt(self, agent_name: str, task_id: str, context: dict) -> str:
    # ... existing code ...

    # NEW: Add tools section
    if '_resolved_tools' in self.spec:
        prompt_parts.append("\n=== AVAILABLE TOOLS ===\n")
        for tool_name, tool_def in self.spec['_resolved_tools'].items():
            prompt_parts.append(f"Tool: {tool_name}\n")
            prompt_parts.append(f"Description: {tool_def['description']}\n")
            prompt_parts.append(f"Parameters: {json.dumps(tool_def['parameters'])}\n\n")

        prompt_parts.append("To use a tool, output XML: <tool_use name='tool_name'><parameters>...</parameters></tool_use>\n")

    # ... existing code ...
    return "\n".join(prompt_parts)
```

#### Step 2.3: Update Core Orchestrator (3 hours)

**File:** `agency_os/core_system/orchestrator/core_orchestrator.py`

**Change #1: Tool execution loop**
```python
def _request_intelligence(self, agent_name: str, task_id: str, prompt: str, context: dict) -> dict:
    """Request intelligence from Claude Code (with tool execution support)"""

    # Send initial request
    request = {
        'type': 'INTELLIGENCE_REQUEST',
        'agent': agent_name,
        'task_id': task_id,
        'prompt': prompt,
        'context': context,
        'wait_for_response': True
    }

    print("---INTELLIGENCE_REQUEST_START---")
    print(json.dumps(request, indent=2))
    print("---INTELLIGENCE_REQUEST_END---")

    tool_executor = ToolExecutor()

    # Tool execution loop
    while True:
        response_raw = input()  # Wait for STDIN

        # Check if tool use
        if '<tool_use' in response_raw:
            # Parse tool call
            tool_call = self._parse_tool_use(response_raw)

            # Execute tool
            result = tool_executor.execute(tool_call['name'], tool_call['parameters'])

            # Send tool result back
            print("---TOOL_RESULT_START---")
            print(json.dumps({'tool': tool_call['name'], 'result': result}, indent=2))
            print("---TOOL_RESULT_END---")

            # Continue loop (wait for next response)
            continue

        # Check if final response
        if '---INTELLIGENCE_RESPONSE_START---' in response_raw:
            response = self._parse_intelligence_response(response_raw)
            return response

        # Otherwise, pass through
        print(response_raw)
```

---

### Phase 3: Testing (Day 3 - 4 hours)

#### Step 3.1: Unit Tests (2 hours)

**File:** `tests/test_google_search_client.py`
```python
import pytest
from agency_os.orchestrator.tools.google_search_client import GoogleSearchClient

def test_google_search_basic():
    client = GoogleSearchClient()
    results = client.search("Python programming", num_results=5)

    assert len(results) > 0
    assert 'title' in results[0]
    assert 'url' in results[0]
```

**File:** `tests/test_tool_executor.py`
```python
def test_tool_executor_google_search():
    executor = ToolExecutor()
    result = executor.execute('google_search', {'query': 'test', 'num_results': 3})

    assert 'results' in result
    assert len(result['results']) <= 3
```

#### Step 3.2: Integration Test (2 hours)

**File:** `tests/test_research_agent_with_tools.py`
```python
def test_market_researcher_uses_tools():
    """Test that MARKET_RESEARCHER can execute google_search"""

    orchestrator = CoreOrchestrator(workspace_root='/tmp/test', execution_mode='delegated')

    # Mock STDIN responses
    mock_stdin = [
        '<tool_use name="google_search"><parameters>{"query": "AI startups 2024"}</parameters></tool_use>',
        '---INTELLIGENCE_RESPONSE_START---\n{"artifacts": [...]}---INTELLIGENCE_RESPONSE_END---'
    ]

    with patch('builtins.input', side_effect=mock_stdin):
        response = orchestrator.execute_agent(
            agent_name='MARKET_RESEARCHER',
            task_id='01_market_scan',
            context={'industry': 'AI'}
        )

    assert response is not None
    # Verify tool was called (check logs)
```

---

## 6. ROLLOUT STRATEGY

### 6.1 Incremental Deployment

**Week 1 (Phase 1):**
- Implement tools infrastructure
- Test in isolation (CLI tests only)
- NO changes to agents yet

**Week 2 (Phase 2):**
- Update 1 agent only: MARKET_RESEARCHER
- Test end-to-end
- Fix bugs

**Week 3 (Phase 3):**
- Update remaining agents (TECH_RESEARCHER, FACT_VALIDATOR)
- Full integration testing
- Production deployment

### 6.2 Backward Compatibility

**Agents without tools:**
- Continue to work (no tools = no tool section in prompt)
- No breaking changes

**Agents with tools:**
- Opt-in via `_composition.yaml` (`tools: [...]`)
- Graceful degradation if tool fails (return error, agent continues)

---

## 7. SUCCESS METRICS

### 7.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Tool execution success rate** | >95% | Log analysis (successful tool calls / total calls) |
| **API rate limit hits** | <5/day | Monitor Google Search API quota usage |
| **Prompt composition time** | <2s | `PromptRuntime.compose_prompt()` duration |
| **Tool execution time** | <5s/call | `ToolExecutor.execute()` duration |

### 7.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Research quality** | Expert review = "good" or better | Human evaluation of generated research_brief.md |
| **Factual accuracy** | >90% | Spot-check facts against known ground truth |
| **Coverage** | ≥3 competitors identified | Count unique competitors in market_analysis.json |

---

## 8. RISKS & MITIGATIONS

### Risk #1: API Rate Limits
**Probability:** MEDIUM
**Impact:** HIGH (blocks research)
**Mitigation:**
- Implement caching (cache search results for 24h)
- Add retry logic with exponential backoff
- Monitor quota usage via dashboard
- Fallback: Use cached data + warn user

### Risk #2: Tool Parsing Errors
**Probability:** MEDIUM
**Impact:** MEDIUM (agent gets confused)
**Mitigation:**
- Strict XML parsing with error handling
- Clear tool documentation in prompts
- Fallback: Ask agent to retry with corrected format

### Risk #3: Cost Overruns
**Probability:** LOW
**Impact:** LOW ($0 in free tier)
**Mitigation:**
- Google Search: 100/day free (sufficient for MVP)
- Web fetch: Unlimited (respect robots.txt)
- Monitor: Alert if approaching limits

### Risk #4: Prompt Bloat
**Probability:** MEDIUM
**Impact:** LOW (longer prompts, but manageable)
**Mitigation:**
- Tool definitions are concise (~50 lines/tool)
- Only include tools agent needs (filtered in _composition.yaml)
- Total prompt still <15k chars (well within Claude's context)

---

## 9. ROLLBACK PLAN

**If things go wrong:**

1. **Revert tool-enabled agents:**
   ```bash
   git revert <commit-hash>  # Revert _composition.yaml changes
   ```

2. **Disable tools system-wide:**
   ```bash
   export VIBE_ENABLE_TOOLS=false  # Environment flag
   ```

3. **Fallback behavior:**
   - PromptRuntime: Skip tool definitions section
   - Orchestrator: Skip tool execution loop
   - Agents: Operate as passive validators (current behavior)

**Recovery time:** <1 hour (revert commits + redeploy)

---

## 10. DECISION RECORD

**Date:** 2025-11-14
**Decision Maker:** User (kimeisele)
**Decision:** APPROVED - Proceed with Phase 1 implementation

**Justification:**
- GitHub Secrets are set up and ready
- False blocker removed (API keys CAN be used in GitHub Actions)
- Original vision was correct and valuable
- Low risk, high value implementation

**Next Steps:**
1. ✅ Create GAD-003 document
2. ⏳ Implement Phase 1 (Tool Infrastructure)
3. ⏳ Test tools in isolation
4. ⏳ Proceed to Phase 2 (Integration)
