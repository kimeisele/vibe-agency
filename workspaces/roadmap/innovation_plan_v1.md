# OPERATION SEMANTIC MOTOR - Innovation Plan v1.0

**Status:** Deep Dive Analysis Complete
**Date:** 2025-11-20
**Target Release:** GAD-901 (Playbook Engine 2.0)
**Confidence Level:** HIGH (based on code audit)

---

## EXECUTIVE SUMMARY

The Playbook Engine is the "Semantic Motor" of VIBE Agency OS, but it's currently **rigidly biased towards Business Logic**. Through this deep dive, we've identified both the constraints limiting creative potential and the safety gaps that could cause operational catastrophes at scale.

### The Vision
Transform PlaybookEngine from a "business workflow router" into a **universal orchestration interface** that:
- ✅ Handles ANY creative workflow (not just testing/coding)
- ✅ Learns from user intent without hardcoding
- ✅ Orchestrates agents dynamically
- ✅ Protects against operational quotas (Rate Limits, Cost Spikes, API Overload)

---

## SECTION 1: PLAYBOOK ENGINE ANALYSIS

### 1.1 Current Architecture (Lines 1-181 of playbook_engine.py)

#### The "Business Logic Bias"
The engine has **hardcoded domain-specific rules** that make it unsuitable for general use:

**Tier 2: Context Inference Rules (Lines 81-123)**
```python
# Rule 1: Tests failing → debug
if context.get("tests", {}).get("failing_count", 0) > 0:
    return PlaybookRoute(task="debug", ...)

# Rule 2: Uncommitted changes + no failures → test
if git_uncommitted > 0 and tests_failing == 0:
    return PlaybookRoute(task="test", ...)

# Rule 3: Backlog item present → implement
if backlog_item:
    return PlaybookRoute(task="implement", ...)

# Rule 4: Phase is PLANNING → plan
if phase == "PLANNING":
    return PlaybookRoute(task="plan", ...)
```

**Problem:** These 4 rules are hardcoded for the **Vibe Agency's own workflow** (development/testing/planning). They cannot accommodate:
- Marketing workflows (content creation, analytics, outreach)
- Design workflows (ideation, prototyping, review)
- Research workflows (literature review, experimentation, synthesis)
- User-custom workflows

**Domain Routing Bias (Lines 154-167)**
```python
def _route_to_task(self, route_name: str) -> str:
    core_routes = ["bootstrap", "session_resume", "status_check"]
    domain_routes = ["restaurant_app", "healthcare_app", "ecommerce_app"]
    # ... ALL routes map to 3 fixed tasks: analyze, plan, implement
    return "analyze"  # Everything becomes "analyze"
```

**Problem:** Domain examples are hardcoded examples only; no extensibility for arbitrary domains.

---

### 1.2 Refactoring Strategy: From "Business Steps" to "Semantic Actions"

#### Vision: PlaybookEngine 2.0 Architecture

```
User Intent + Context
       ↓
[Semantic Parser] → Extract intent type, domains, constraints
       ↓
[Action Orchestrator] → Map intent to semantic actions (not tasks)
       ↓
[Agent Delegator] → Select agents & execute workflow
       ↓
[Outcome Validator] → Verify results match intent
```

#### Key Transformation #1: Replace Hardcoded Rules with Declarative Workflows

**FROM (Current):**
```yaml
routes:
  - name: debug
    intent_patterns: ["fix test", "failing"]
    description: "Debug failing tests"
```

**TO (Proposed):**
```yaml
workflows:
  - id: debug_workflow
    trigger:
      intent_types: [fix, resolve, debug]
      domain_keywords: [test, failure, error]
      min_confidence: 0.7
    actions:
      - agent: analyzer
        task: identify_root_cause
        input: [failing_tests, error_logs]
        on_failure: escalate
      - agent: coder
        task: generate_fix
        input: [root_cause_analysis]
      - agent: reviewer
        task: validate_solution
        input: [code_fix, original_failure]
    output_schema:
      required: [fix_description, test_results]
      optional: [performance_impact, side_effects]
    max_duration_seconds: 300
    retry_strategy: exponential_backoff(max_attempts=3)
```

**Benefit:** Users can now define THEIR OWN workflows without code changes.

#### Key Transformation #2: Semantic Actions (not Fixed Tasks)

Current limitation: Routes map to 3 fixed tasks: `analyze`, `plan`, `implement`.

**Proposed Semantic Actions:**
```python
@dataclass
class SemanticAction:
    """A semantic action that agents can execute"""
    id: str  # "identify_patterns", "validate_assumptions", "generate_alternatives"
    description: str
    required_context: dict[str, str]
    produces: list[str]  # Output artifacts
    agents_capable: list[str]  # Which agents can execute this
    estimated_duration_ms: int
    cost_estimate_usd: float

    def execute(self, agent: BaseAgent, context: dict) -> ActionResult:
        """Orchestrator delegates to agent"""
        pass
```

**Examples of Semantic Actions:**
- `identify_patterns` - Find recurring elements (Researcher, Architect)
- `validate_assumptions` - Test hypotheses (Reviewer, Researcher)
- `generate_alternatives` - Brainstorm options (Coder, Architect)
- `synthesize_decision` - Consolidate findings (Architect)
- `document_findings` - Write up results (Coder, Researcher)
- `peer_review` - Critical evaluation (Reviewer, Architect)

**Benefit:** Decouples intent from agent selection. Same action can be executed by different agents based on availability & specialization.

#### Key Transformation #3: Workflow as Code (YAML)

Replace hardcoded Python rules with declarative YAML workflow definitions:

**File:** `agency_os/00_system/playbook/workflows/`
```
workflows/
├── _schema.json          # JSON Schema for workflow validation
├── debugging.yaml        # "Fix failing tests" workflow
├── feature_development.yaml
├── research_synthesis.yaml
├── code_review.yaml
├── architecture_design.yaml
└── custom_workflows/     # User-defined workflows
    ├── marketing_content_pipeline.yaml
    ├── data_analysis.yaml
    └── ...
```

**Schema Example:**
```yaml
# workflows/debugging.yaml
version: "1.0"
metadata:
  id: debug_failing_tests
  name: "Debug & Fix Failing Tests"
  description: "Systematic workflow to identify root cause and fix test failures"
  created_by: architect
  created_date: 2025-11-20
  tags: [testing, debugging, qa]

trigger:
  patterns:
    intent: [fix, resolve, debug, repair]
    context:
      - failing_tests > 0
      - tests_changed_recently = true
  min_confidence: 0.75

workflow:
  steps:
    - step_id: 1
      name: "Analyze Test Failures"
      action: identify_patterns
      agent_preference: [analyzer, researcher]
      input:
        - test_failures
        - error_logs
        - changed_files
      timeout_seconds: 60

    - step_id: 2
      name: "Generate Fix Hypothesis"
      action: generate_alternatives
      agent_preference: [coder, architect]
      input:
        - failure_patterns  # Output from step 1
      depends_on: [1]

    - step_id: 3
      name: "Validate Fix"
      action: validate_solution
      agent_preference: [reviewer, coder]
      input:
        - proposed_fix
        - original_failures
      depends_on: [2]

gates:
  - gate_id: "all_tests_pass"
    validator: shell_command
    command: "uv run pytest -v"
    required: true

  - gate_id: "no_regressions"
    validator: code_coverage
    min_coverage_percent: 80
    required: true

output_schema:
  type: object
  required:
    - fix_description
    - code_changes
    - test_results
  properties:
    fix_description:
      type: string
    code_changes:
      type: array
      items:
        type: object
        required: [file, change_type]
    test_results:
      type: object
      required: [passing_count, failing_count]
```

---

### 1.3 Implementation Roadmap for Playbook 2.0

| Phase | Component | Effort | Dependencies |
|-------|-----------|--------|--------------|
| **Phase 1** | Semantic Action Registry | 3 days | None |
| **Phase 2** | Workflow YAML Parser & Validator | 4 days | Phase 1 |
| **Phase 3** | Workflow Executor | 5 days | Phase 1, 2 |
| **Phase 4** | Custom Workflow UI/CLI | 3 days | Phase 1-3 |
| **Phase 5** | Agent Capability Matching | 4 days | Phase 1-3 |
| **Phase 6** | Workflow Analytics & Feedback | 3 days | Phase 1-5 |
| **TOTAL** | | **22 days** | ~1 month |

---

## SECTION 2: SAFETY AUDIT - THE "FINAL STRAW DEFENSE"

### 2.1 Current Safety Implementation (PARTIAL)

**What EXISTS in llm_client.py:**
✅ BudgetExceededError exception class
✅ Budget checking before invocation (lines 277-282)
✅ Retry logic with exponential backoff (lines 284-337)
✅ Rate limit detection (RateLimitError, APITimeoutError, APIConnectionError)
✅ Cost tracking via CostTracker
✅ Graceful failover with NoOpClient

**Code Reference:**
```python
# Budget checking (GOOD)
if self.budget_limit and self.cost_tracker.total_cost >= self.budget_limit:
    raise BudgetExceededError(...)

# Retry logic with exponential backoff (GOOD)
retryable_errors = ["RateLimitError", "APIConnectionError", "APITimeoutError"]
is_retryable = any(err in error_name for err in retryable_errors)
if is_retryable and attempt < max_retries - 1:
    wait_time = 2**attempt  # 2s, 4s, 8s exponential backoff
    time.sleep(wait_time)
```

### 2.2 CRITICAL SAFETY GAPS (THE FINAL STRAW DEFENSE IS INCOMPLETE)

#### Gap #1: No Circuit Breaker Pattern
**Problem:** If OpenAI/Anthropic API is down, the system will retry for ~10 seconds (2+4+8s), then crash. There's no mechanism to:
- Detect sustained API degradation
- Switch to fallback mode automatically
- Queue requests for later retry
- Alert operators

**Impact:** A service outage at the LLM provider immediately cascades to VIBE Agency OS failure.

**Example Scenario:**
```
Time 0s:   Anthropic API goes down (rate limiting)
Time 2s:   VIBE tries to respond to user → RateLimitError (attempt 1) → retry
Time 4s:   Still down → Retry again
Time 8s:   Still down → Max retries reached → CRASH
Time 8.5s: User sees system failure
```

#### Gap #2: No Hibernation/Pause Mechanism
**Problem:** When hitting rate limits, the system throws an exception immediately. There's no mechanism to:
- Pause gracefully
- Store state for recovery
- Resume when quota resets
- Notify agents about rate limit status

**Impact:** Long-running workflows can be interrupted mid-execution with no recovery path.

#### Gap #3: No Operational Quota Management
**Problem:** Budget limit is a COST limit (USD), not an OPERATIONAL quota. Missing:
- Request rate limits (requests/minute)
- Token rate limits (tokens/minute)
- Concurrent request limits
- Per-agent quota allocation
- Usage tracking by agent/workflow

**Current:** Only tracks USD spent. Doesn't track:
- How many requests/min we're making
- Whether we're about to hit API rate limits
- Per-agent usage distribution

#### Gap #4: No Fallback Action Strategies
**Problem:** When LLM fails, the system either crashes or returns empty response (NoOpClient). Missing:
- Degraded-mode workflows (use cached responses)
- Agent switching (if Coder fails, try Architect)
- Local-only analysis (parse existing artifacts)
- Manual intervention prompts

**Current:** BaseAgent doesn't check LLMClient error states. No delegation to fallback agents.

#### Gap #5: No Cost Spike Detection
**Problem:** If a prompt accidentally becomes 100K tokens, cost spike is NOT detected until AFTER execution. Missing:
- Pre-flight token estimation
- Cost spike alerts
- Automatic cost limits per request
- Prompt length validation

**Current:** Cost is tracked AFTER the API call completes.

---

### 2.3 Proposed: GAD-509 Circuit Breaker Protocol

#### Architecture

```python
# agency_os/00_system/runtime/circuit_breaker.py

class CircuitBreakerState(Enum):
    CLOSED = "healthy"           # Normal operation
    OPEN = "failing"             # API is down, reject requests
    HALF_OPEN = "recovering"     # Testing if API recovered

class CircuitBreaker:
    """
    Protects against cascading failures when LLM API is down.

    State Transitions:
    CLOSED → OPEN (after 5 failed requests in 1 minute)
    OPEN → HALF_OPEN (after 30s pause)
    HALF_OPEN → CLOSED (if probe succeeds)
    HALF_OPEN → OPEN (if probe fails)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 30,
        window_size_seconds: int = 60,
    ):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.window_start = time.time()
        self.last_failure = None

    def call(self, fn: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""

        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout expired
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN (testing recovery)")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker OPEN. API degraded. Retry in "
                    f"{self.recovery_timeout - (time.time() - self.last_failure):.0f}s"
                )

        try:
            result = fn(*args, **kwargs)

            # Success: reset counters
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                logger.info("Circuit breaker CLOSED (API recovered)")
            self.failure_count = 0

            return result

        except RateLimitError as e:
            self._record_failure(e)
            raise

    def _record_failure(self, error: Exception):
        """Track failure and transition to OPEN if threshold reached"""
        self.failure_count += 1
        self.last_failure = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.error(
                f"Circuit breaker OPEN! LLM API showing sustained issues. "
                f"Failures: {self.failure_count} in {self.window_size}s"
            )
```

#### Integration Point
```python
# Updated llm_client.py
class LLMClient:
    def __init__(self, budget_limit: float | None = None):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout_seconds=30,
        )

    def invoke(self, prompt: str, **kwargs) -> LLMResponse:
        # Call through circuit breaker
        return self.circuit_breaker.call(
            self._invoke_unchecked,
            prompt=prompt,
            **kwargs
        )
```

#### User Behavior When Circuit Breaker Opens
```
API Down Scenario:
- Agent makes 1st request → RateLimitError → Circuit stays CLOSED
- Agent makes 2nd-5th requests → All fail → Circuit OPENS
- User sees: "System in Degraded Mode: LLM API is temporarily unavailable"
- Fallback: Execute local-only analysis (check existing artifacts)
- Recovery: After 30s, probe request sent → if success, return to NORMAL
```

---

### 2.4 Proposed: Operational Quota Management (GAD-510)

#### Missing Instrumentation

```python
# agency_os/00_system/runtime/quota_manager.py

class OperationalQuota:
    """Tracks requests/tokens/cost to prevent surprises"""

    LIMITS = {
        "requests_per_minute": 100,      # Anthropic TPM typical limit
        "tokens_per_minute": 100_000,    # Tokens per minute
        "concurrent_requests": 10,       # Max parallel invocations
        "cost_per_request_usd": 0.50,   # Alert if single request > $0.50
        "cost_per_hour_usd": 50.0,      # Alert if hourly spend > $50
        "cost_per_day_usd": 500.0,      # Alert if daily spend > $500
    }

    def check_before_request(self, estimated_tokens: int) -> bool:
        """Return True if request is safe to proceed"""

        # Check 1: Would this request exceed token limit?
        if (self.tokens_this_minute + estimated_tokens >
            self.LIMITS["tokens_per_minute"]):
            raise QuotaExceededError("Token rate limit exceeded")

        # Check 2: Is request suspiciously large?
        estimated_cost = self._estimate_cost(estimated_tokens)
        if estimated_cost > self.LIMITS["cost_per_request_usd"]:
            logger.warning(f"High-cost request detected: ${estimated_cost:.2f}")
            if not self._confirm_large_request():
                raise QuotaExceededError("User cancelled high-cost request")

        # Check 3: Are we approaching hourly limit?
        if (self.cost_this_hour + estimated_cost >
            self.LIMITS["cost_per_hour_usd"] * 0.8):  # Alert at 80%
            logger.alert(f"Hourly spending at 80%: ${self.cost_this_hour:.2f}")

        return True
```

#### Integration with BaseAgent

```python
# Updated base_agent.py
class BaseAgent:
    def execute_command(self, command: str, **kwargs) -> ExecutionResult:
        # Pre-flight check
        if self.quota_manager.approaching_limit():
            logger.warning("Operational quota approaching limit")
            return ExecutionResult(
                success=False,
                error="Operational quota approaching limit. Pausing.",
                exit_code=-2,
            )

        # Execute (existing code)
        return self._execute_via_shell(command, **kwargs)
```

---

## SECTION 3: PROPOSED ARCHITECTURE - PlaybookEngine 2.0 with Safety

### 3.1 System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTENT (Any Domain)                    │
│         "Fix failing tests" / "Analyze market trends"           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │   PlaybookEngine 2.0 (Semantic Motor)      │
        │                                            │
        │  ┌────────────────────────────────────┐   │
        │  │ Intent Parser & Confidence Scorer  │   │
        │  │ (Extracts domain, intent type)     │   │
        │  └────────────────────────────────────┘   │
        │                    │                       │
        │                    ▼                       │
        │  ┌────────────────────────────────────┐   │
        │  │ Workflow Registry Lookup           │   │
        │  │ (YAML-based workflow definitions)  │   │
        │  └────────────────────────────────────┘   │
        │                    │                       │
        │                    ▼                       │
        │  ┌────────────────────────────────────┐   │
        │  │ Semantic Action Orchestrator       │   │
        │  │ (Maps intent → actions)            │   │
        │  └────────────────────────────────────┘   │
        │                    │                       │
        │                    ▼                       │
        │  ┌────────────────────────────────────┐   │
        │  │ Agent Capability Matcher           │   │
        │  │ (Select best agent for action)     │   │
        │  └────────────────────────────────────┘   │
        └────────────────────┬─────────────────────┘
                             │
        ┌────────────────────┴─────────────────────┐
        │        Safety Layer (GAD-509/510)        │
        │                                          │
        │  ┌──────────────────────────────────┐   │
        │  │ Circuit Breaker (LLM status)     │   │
        │  └──────────────────────────────────┘   │
        │                                          │
        │  ┌──────────────────────────────────┐   │
        │  │ Quota Manager (Request/Token)    │   │
        │  └──────────────────────────────────┘   │
        │                                          │
        │  ┌──────────────────────────────────┐   │
        │  │ Cost Monitor & Alerts            │   │
        │  └──────────────────────────────────┘   │
        └────────────────────┬─────────────────────┘
                             │
        ┌────────────────────┴──────────────────────────┐
        │         Agent Execution Framework             │
        │    (BaseAgent + Personas: Coder, etc)        │
        │                                               │
        │  [Analyzer] → [Coder] → [Reviewer]           │
        │   (identifies)  (fixes)   (validates)        │
        └────────────────────┬──────────────────────────┘
                             │
        ┌────────────────────┴──────────────────────────┐
        │         Infrastructure Layers                 │
        │                                               │
        │  [GAD-5: Runtime]  [GAD-6: Knowledge]         │
        │  [GAD-7: Mission]  [GAD-4: QA]               │
        └───────────────────────────────────────────────┘
```

### 3.2 New Files to Create

**Phase 1: Semantic Action Registry**
```
agency_os/00_system/runtime/
├── semantic_actions.py          # SemanticAction dataclass + registry
└── action_catalog/              # Library of predefined actions
    ├── analysis_actions.py       # identify_patterns, validate_assumptions
    ├── generation_actions.py     # generate_alternatives, synthesize
    ├── validation_actions.py     # validate_solution, peer_review
    └── documentation_actions.py  # document_findings
```

**Phase 2: Workflow Execution**
```
agency_os/00_system/playbook/
├── workflow_engine.py            # Orchestrate workflow steps
├── workflow_parser.py            # Parse YAML definitions
├── workflow_schema.json          # JSON Schema validator
└── workflows/
    ├── debugging.yaml
    ├── feature_development.yaml
    ├── research_synthesis.yaml
    └── custom_workflows/         # User can add their own
```

**Phase 2.5: Safety Infrastructure**
```
agency_os/00_system/runtime/
├── circuit_breaker.py            # GAD-509 Circuit Breaker Protocol
├── quota_manager.py              # GAD-510 Operational Quota Management
└── safety_monitor.py             # Cost alerts, rate limit monitoring
```

**Phase 3: Agent Integration**
```
agency_os/03_agents/
├── base_agent.py                 # Add quota checks to execute_command
└── capability_matcher.py          # Match actions to agents
```

---

## SECTION 4: SAFETY QUICK-START (GAD-509 Minimal Implementation)

### 4.1 What to Build First (1 week)

1. **CircuitBreaker class** - Detect API issues and pause gracefully
2. **QuotaManager class** - Track requests/tokens before they become problems
3. **Cost spike alerts** - Warn before executing high-cost requests
4. **Hibernation mode** - Pause workflows when hitting limits (don't crash)

### 4.2 Code Skeleton

```python
# agency_os/00_system/runtime/circuit_breaker.py
from enum import Enum
from dataclasses import dataclass
import time

class CircuitBreakerState(Enum):
    CLOSED = "closed"      # OK
    OPEN = "open"          # API down
    HALF_OPEN = "half"     # Testing recovery

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5        # Failures before OPEN
    recovery_timeout_sec: int = 30    # Time before testing recovery
    window_size_sec: int = 60         # Failure window

class CircuitBreaker:
    """Prevents cascading failures when LLM API degrades"""

    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def record_success(self):
        """Reset on successful call"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0

    def record_failure(self):
        """Record failure and maybe open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def can_execute(self) -> tuple[bool, str]:
        """Check if safe to execute LLM call"""

        if self.state == CircuitBreakerState.CLOSED:
            return True, "OK"

        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout passed
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.config.recovery_timeout_sec:
                self.state = CircuitBreakerState.HALF_OPEN
                return True, "Testing recovery"
            else:
                remaining = self.config.recovery_timeout_sec - elapsed
                return False, f"Circuit OPEN. Retry in {remaining:.0f}s"

        # HALF_OPEN - allow one test request
        return True, "Testing recovery"

# agency_os/00_system/runtime/quota_manager.py
class OperationalQuota:
    """Track and enforce request quotas"""

    def __init__(self):
        self.requests_this_minute = 0
        self.tokens_this_minute = 0
        self.cost_this_hour = 0.0
        self.minute_start = time.time()

    def check_before_request(self, est_tokens: int) -> tuple[bool, str]:
        """Pre-flight check before LLM request"""

        # Reset if minute passed
        if time.time() - self.minute_start > 60:
            self.requests_this_minute = 0
            self.tokens_this_minute = 0
            self.minute_start = time.time()

        # Check token rate
        if self.tokens_this_minute + est_tokens > 100_000:
            return False, "Token rate limit would be exceeded"

        # Check request rate
        if self.requests_this_minute >= 100:
            return False, "Request rate limit reached"

        return True, "OK"

    def record_request(self, tokens_used: int, cost: float):
        """Record request after completion"""
        self.requests_this_minute += 1
        self.tokens_this_minute += tokens_used
        self.cost_this_hour += cost
```

---

## SECTION 5: INNOVATION ROADMAP SUMMARY

### Phase 1: Semantic Motor Foundation (2 weeks)
- [ ] SemanticAction dataclass & registry
- [ ] Workflow YAML parser & validator
- [ ] Workflow schema definition
- [ ] CLI: `vibe playbook list-workflows`

### Phase 2: Agent Orchestration (1 week)
- [ ] Agent capability registry (which agents can do what)
- [ ] Capability matcher (action → best agent)
- [ ] Step executor (run workflow steps sequentially)
- [ ] CLI: `vibe playbook run debugging`

### Phase 3: Safety Layer - Circuit Breaker (3 days)
- [ ] CircuitBreaker implementation
- [ ] Integration with LLMClient
- [ ] Hibernation mode for BaseAgent
- [ ] Tests for circuit transitions

### Phase 4: Safety Layer - Quota Management (3 days)
- [ ] OperationalQuota tracker
- [ ] Pre-flight checks in BaseAgent
- [ ] Cost spike alerts
- [ ] Tests for quota enforcement

### Phase 5: Custom Workflows (1 week)
- [ ] Workflow authoring guide
- [ ] Example custom workflows
- [ ] CLI: `vibe playbook create <name>`
- [ ] Validation & linting for user workflows

### Phase 6: Analytics & Learning (1 week)
- [ ] Workflow execution metrics
- [ ] Agent performance tracking
- [ ] Success rate by workflow
- [ ] Feedback loop to refine workflows

**TOTAL EFFORT:** ~8-10 weeks
**RISK LEVEL:** LOW (circuit breaker is defensive pattern, proven)
**IMPACT:** TRANSFORMATIONAL (unlocks arbitrary workflows + safety)

---

## SECTION 6: SUCCESS METRICS

### By End of Phase 1
- ✅ PlaybookEngine can load arbitrary workflows from YAML
- ✅ Can orchestrate non-Vibe workflows (user provides their own)
- ✅ Zero hardcoded business logic

### By End of Phase 3
- ✅ System gracefully handles Anthropic API outages (no cascade failure)
- ✅ LLM failures result in degraded mode, not crashes
- ✅ Users notified before hitting rate limits

### By End of Phase 6
- ✅ 5+ custom workflows created by users
- ✅ Circuit breaker has prevented at least 2 cascade failures
- ✅ Cost alerts have prevented surprise spikes
- ✅ Playbook execution tracking shows >95% success rate

---

## APPENDIX A: Existing Safety Code (Reference)

### LLMClient Budget Checking (GOOD)
**File:** `agency_os/00_system/runtime/llm_client.py:277-282`
```python
if self.budget_limit and self.cost_tracker.total_cost >= self.budget_limit:
    raise BudgetExceededError(
        f"Budget limit reached: ${self.budget_limit:.2f} "
        f"(current: ${self.cost_tracker.total_cost:.4f})"
    )
```

### LLMClient Retry Logic (GOOD)
**File:** `agency_os/00_system/runtime/llm_client.py:318-337`
```python
retryable_errors = ["RateLimitError", "APIConnectionError", "APITimeoutError"]
is_retryable = any(err in error_name for err in retryable_errors)

if is_retryable and attempt < max_retries - 1:
    wait_time = 2**attempt  # Exponential backoff: 2s, 4s, 8s
    logger.warning(
        f"LLM invocation failed ({error_name}), "
        f"retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
    )
    time.sleep(wait_time)
```

### NoOpClient Graceful Failover (GOOD)
**File:** `agency_os/00_system/runtime/llm_client.py:152-186`
Implements fallback when ANTHROPIC_API_KEY not set.

---

## APPENDIX B: Constraints & Dependencies

### Dependencies for Semantic Motor
- YAML parsing (existing: PyYAML)
- JSON Schema validation (new: jsonschema library)
- Type hints (existing: Python 3.10+)

### No Breaking Changes Required
- PlaybookEngine v1.0 routes continue to work
- BaseAgent interface unchanged
- LLMClient compatible with circuit breaker

---

## FINAL ASSESSMENT

### Current State
- PlaybookEngine: **Rigid** (Business logic bias)
- Safety: **Partial** (Budget checking ✓, Circuit breaker ✗, Quotas ✗)

### Target State (v1.0)
- PlaybookEngine: **Fluid** (User-defined workflows via YAML)
- Safety: **Comprehensive** (Circuit breaker + Quota mgmt + Cost alerts)

### Confidence Level
**HIGH (90%)** - Based on:
- ✅ Existing code patterns reviewed
- ✅ Safety gaps clearly identified
- ✅ No breaking changes needed
- ✅ Circuit breaker is battle-tested pattern
- ✅ All components have known implementations

---

**END OF INNOVATION PLAN v1.0**
**Next Step:** Executive review + approval to proceed to Phase 1 implementation
